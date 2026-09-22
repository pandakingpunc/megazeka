import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from megazeka.storage import ROOT, configure, ensure_budget, remove_owned, usage
configure()
import argparse
import json
import math
import random
import time
import os
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from peft import LoraConfig, get_peft_model, PeftModel, TaskType
from training.prepare import read_pairs
from megazeka.metrics import measure

def write_json(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    for attempt in range(30):
        try:
            temporary.replace(path)
            return
        except PermissionError:
            # Windows readers/antivirus may briefly hold a non-delete-sharing handle.
            time.sleep(.05)
    if path.name == 'training_status.json':
        print('Durum ekranı meşgul; sonraki adımda güncellenecek.', flush=True)
        return
    temporary.replace(path)

def save_checkpoint(model, optimizer, config, state, name):
    ensure_budget(250_000_000, 'LoRA kontrol noktası: ' + name)
    parent = ROOT / 'models/checkpoints'
    temp, destination = parent / ('temporary-' + name), parent / name
    if temp.exists():
        remove_owned(temp)
    temp.mkdir(parents=True)
    model.save_pretrained(temp, safe_serialization=True)
    write_json(temp / 'training_config.json', config)
    write_json(temp / 'state.json', state)
    if optimizer is not None:
        torch.save({'optimizer': optimizer.state_dict(), 'random': random.getstate(),
                    'numpy': np.random.get_state(), 'torch': torch.get_rng_state(),
                    'cuda': torch.cuda.get_rng_state_all() if torch.cuda.is_available() else []}, temp / 'resume.pt')
    if destination.exists():
        remove_owned(destination)
    temp.replace(destination)

def main():
    parser = argparse.ArgumentParser(description='Megazeka yerel LoRA eğitimi')
    parser.add_argument('--config', default='configs/medium.json')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--steps', type=int)
    args = parser.parse_args()
    config = json.loads((ROOT / args.config).read_text(encoding='utf-8'))
    if args.steps:
        config['steps'] = args.steps
    previous_state = ROOT / 'models/checkpoints/latest/state.json'
    if args.resume and previous_state.exists():
        existing_step = json.loads(previous_state.read_text(encoding='utf-8'))['step']
        if existing_step >= config['steps']:
            print(f'Hedef {config["steps"]} adım zaten tamamlanmış. Devam için --steps değerini artırın.', flush=True)
            return
    random.seed(config['seed']); np.random.seed(config['seed']); torch.manual_seed(config['seed'])
    torch.set_num_threads(6)
    torch.backends.cuda.matmul.allow_tf32 = True
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    if device == 'cpu':
        config['batch_size'] = min(config['batch_size'], 2)
    dtype = torch.bfloat16 if device == 'cuda' and torch.cuda.is_bf16_supported() else torch.float32
    tokenizer = AutoTokenizer.from_pretrained(ROOT / 'models/base', local_files_only=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(ROOT / 'models/base', local_files_only=True, dtype=dtype)
    if not (ROOT / 'models/base/model.safetensors').exists():
        ensure_budget(sum(p.numel() * p.element_size() for p in model.parameters()) + 10_000_000, 'Temel modeli safetensors biçimine dönüştürme')
        model.save_pretrained(ROOT / 'models/base', safe_serialization=True)
        # Exact redundant source file; never touches another model or global cache.
        (ROOT / 'models/base/pytorch_model.bin').unlink(missing_ok=True)
        tokenizer.save_pretrained(ROOT / 'models/base')
    state = {'step': 0, 'best_loss': 1e10, 'bad_evaluations': 0, 'elapsed_seconds': 0, 'examples_processed': 0}
    resume_dir = ROOT / 'models/checkpoints/latest'
    if args.resume:
        state = json.loads((resume_dir / 'state.json').read_text(encoding='utf-8'))
        model = PeftModel.from_pretrained(model, resume_dir, is_trainable=True)
    else:
        model = get_peft_model(model, LoraConfig(task_type=TaskType.SEQ_2_SEQ_LM, r=config['rank'],
                               lora_alpha=config['rank'] * 2, lora_dropout=.05, target_modules='all-linear'))
    model.to(device)
    model.config.use_cache = False
    optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=config['learning_rate'])
    if args.resume:
        # resume.pt is generated only by this project, never downloaded.
        saved = torch.load(resume_dir / 'resume.pt', map_location='cpu', weights_only=False)
        optimizer.load_state_dict(saved['optimizer'])
        random.setstate(saved['random']); np.random.set_state(saved['numpy']); torch.set_rng_state(saved['torch'])
        if device == 'cuda' and saved['cuda']:
            torch.cuda.set_rng_state_all(saved['cuda'])
    train = read_pairs('train'); validation = read_pairs('validation')
    encoded = {}
    for split, rows in [('train', train), ('validation', validation)]:
        encoded[split] = [(tokenizer(r['input']).input_ids, tokenizer(r['target']).input_ids) for r in rows]
    def batch(rows):
        x = tokenizer.pad({'input_ids': [r[0] for r in rows]}, return_tensors='pt')
        y = tokenizer.pad({'input_ids': [r[1] for r in rows]}, return_tensors='pt')['input_ids']
        y[y == tokenizer.pad_token_id] = -100
        return {**{k: v.to(device) for k, v in x.items()}, 'labels': y.to(device)}
    info = {'architecture': 'ByT5-small + LoRA', 'base': 'google/byt5-small',
            'parameters': sum(p.numel() for p in model.parameters()),
            'trainable_parameters': sum(p.numel() for p in model.parameters() if p.requires_grad),
            'device': torch.cuda.get_device_name() if device == 'cuda' else 'CPU',
            'precision': str(dtype), 'tokenizer_vocabulary': len(tokenizer), 'config': config}
    write_json(ROOT / 'reports/model_info.json', info)
    print(json.dumps(info, ensure_ascii=False), flush=True)
    start = time.perf_counter(); previous_time = state['elapsed_seconds']
    losses = []; last_evaluation = state['step']
    stop_file = ROOT / 'reports/stop-training'
    stop_file.unlink(missing_ok=True)
    if not args.resume:
        # A fresh experiment replaces best/latest, so the plotted history starts over too.
        (ROOT / 'reports/history.jsonl').write_text('', encoding='utf-8')
    # Deterministic per-epoch permutations permit resume without huge sampler state.
    effective_batch = config['batch_size'] * config['gradient_accumulation']
    permutation, permutation_epoch = [], -1
    def indices_at(offset, count):
        nonlocal permutation, permutation_epoch
        result = []
        for k in range(offset, offset + count):
            epoch, index = divmod(k, len(train))
            if epoch != permutation_epoch:
                permutation = list(range(len(train)))
                random.Random(config['seed'] + epoch).shuffle(permutation)
                permutation_epoch = epoch
            result.append(permutation[index])
        return result
    model.train()
    for step in range(state['step'] + 1, config['steps'] + 1):
        if step % 25 == 1:
            ensure_budget(300_000_000, 'Eğitim depolama denetimi')
        optimizer.zero_grad(set_to_none=True)
        ids = indices_at(state['examples_processed'], effective_batch)
        total_loss = 0
        for micro in range(config['gradient_accumulation']):
            chosen = ids[micro * config['batch_size']:(micro+1) * config['batch_size']]
            result = model(**batch([encoded['train'][i] for i in chosen]))
            if not torch.isfinite(result.loss):
                raise RuntimeError('Sonlu olmayan eğitim kaybı; en son kontrol noktasından devam edilebilir.')
            loss = result.loss / config['gradient_accumulation']
            loss.backward()
            total_loss += loss.detach().float().item()
        torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad], 1.0)
        # Short warm-up followed by constant LR; resume remains consistent if steps increase.
        lr = config['learning_rate'] * min(1.0, step / 30)
        for group in optimizer.param_groups:
            group['lr'] = lr
        optimizer.step()
        losses.append(total_loss)
        state.update(step=step, examples_processed=state['examples_processed'] + effective_batch,
                     elapsed_seconds=previous_time + time.perf_counter() - start)
        status = {**state, 'epoch': state['examples_processed'] / len(train), 'loss': total_loss,
                  'learning_rate': lr, 'total_steps': config['steps'], 'remaining_steps': config['steps']-step,
                  'running': True, 'pid': os.getpid(), 'device': info['device']}
        write_json(ROOT / 'reports/training_status.json', status)
        if step % 10 == 0:
            print(f'Adım {step}/{config["steps"]} | kayıp {total_loss:.4f} | süre {state["elapsed_seconds"]:.1f}s', flush=True)
        should_stop = stop_file.exists()
        if step % config['eval_every'] == 0 or step == config['steps'] or should_stop:
            model.eval()
            val_loss, val_tokens = 0.0, 0
            with torch.inference_mode():
                for offset in range(0, len(validation), config['batch_size']):
                    inputs = batch(encoded['validation'][offset:offset + config['batch_size']])
                    n = (inputs['labels'] != -100).sum().item()
                    val_loss += model(**inputs).loss.item() * n; val_tokens += n
                observed = []
                # Fixed 16 examples, four of each difficulty, for inexpensive learning graphs.
                sample = []
                for difficulty in ['temiz', 'kolay', 'orta', 'zor']:
                    sample.extend([r for r in validation if r['difficulty'] == difficulty][:4])
                model.config.use_cache = True
                for offset in range(0, len(sample), 8):
                    group = sample[offset:offset+8]
                    x = tokenizer([r['input'] for r in group], return_tensors='pt', padding=True).to(device)
                    out = model.generate(**x, max_new_tokens=192, do_sample=False, num_beams=1)
                    observed.extend({**r, 'output': p} for r, p in zip(group, tokenizer.batch_decode(out, skip_special_tokens=True)))
                model.config.use_cache = False
            val_loss /= max(1, val_tokens)
            met = measure(observed)
            better = val_loss < state['best_loss']
            state['bad_evaluations'] = 0 if better else state['bad_evaluations'] + 1
            if better:
                state['best_loss'] = val_loss
                state['best_step'] = step
                save_checkpoint(model, None, config, state, 'best')
            save_checkpoint(model, optimizer, config, state, 'latest')
            history = {**status, 'loss': sum(losses)/len(losses), 'validation_loss': val_loss,
                       'metrics': met, 'best_step': state.get('best_step'), 'storage': usage()}
            with (ROOT / 'reports/history.jsonl').open('a', encoding='utf-8') as stream:
                stream.write(json.dumps(history, ensure_ascii=False) + '\n')
            write_json(ROOT / 'reports/training_status.json', history)
            print('DOĞRULAMA ' + json.dumps({'step': step, 'loss': val_loss, **met}, ensure_ascii=False), flush=True)
            losses = []
            model.train()
            if state['bad_evaluations'] >= config['patience'] or should_stop:
                break
    write_json(ROOT / 'models/final.json', {'adapter': 'models/checkpoints/best', 'base': 'models/base',
                'best_step': state.get('best_step'), 'note': 'Son model en iyi kontrol noktasına işaret eder; kopya yok.'})
    status.update(state, running=False)
    write_json(ROOT / 'reports/training_status.json', status)
    print('Eğitim tamamlandı.', flush=True)

if __name__ == '__main__':
    from filelock import FileLock, Timeout
    try:
        with FileLock(ROOT / 'reports/training.lock', timeout=0):
            main()
    except Timeout:
        raise SystemExit('Bu proje için başka bir eğitim zaten çalışıyor.')
