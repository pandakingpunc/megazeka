"""Paired report comparison. Differences always mean B minus A."""
import argparse
import json
import math
import sys
from pathlib import Path
import numpy as np


def mcnemar_exact(a_only, b_only):
    """Exact two-sided binomial test on the discordant pairs."""
    if min(a_only, b_only) < 0 or int(a_only) != a_only or int(b_only) != b_only:
        raise ValueError('Uyumsuz çift sayıları negatif olmayan tamsayı olmalı.')
    n = int(a_only + b_only)
    tail = sum(math.comb(n, k) for k in range(int(min(a_only, b_only)) + 1))
    return min(1., 2 * tail / (1 << n))


def paired_bootstrap(differences, groups, resamples=10_000, seed=42):
    """Percentile CI for a row mean, sampling whole target groups with replacement."""
    values = np.asarray(differences, dtype=float)
    if values.ndim != 1 or not len(values) or len(values) != len(groups) or resamples < 1:
        raise ValueError('Boş veya uyumsuz eşleştirilmiş veri.')
    ids = {}
    indices = np.array([ids.setdefault(group, len(ids)) for group in groups])
    totals = np.bincount(indices, weights=values)
    counts = np.bincount(indices)
    rng = np.random.default_rng(seed)
    means = np.empty(resamples)
    for offset in range(0, resamples, 256):
        draw = rng.integers(0, len(ids), size=(min(256, resamples-offset), len(ids)))
        means[offset:offset+len(draw)] = totals[draw].sum(axis=1) / counts[draw].sum(axis=1)
    return {'difference': float(values.mean()), 'ci95': np.quantile(means, [.025, .975]).tolist()}


def character_distance(a, b):
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j-1] + (ca != cb)))
        previous = current
    return previous[-1]


def report_rows(report):
    if 'examples' in report:
        return report['examples']
    return [{**row, 'input': row['source']} for row in report['rows']]


def paired_rows(a, b):
    left, right = report_rows(a), report_rows(b)
    assert len(left) == len(right) and left, 'Raporlar aynı sayıda, sıfırdan fazla örnek içermeli.'
    for index, (old, new) in enumerate(zip(left, right)):
        assert (old['input'], old['target']) == (new['input'], new['target']), f'Girdi/hedef uyuşmuyor: satır {index}'
        for key in ('source', 'difficulty', 'category'):
            assert old.get(key) == new.get(key), f'{key} uyuşmuyor: satır {index}'
    return list(zip(left, right))


def compare_pairs(pairs, resamples=10_000, seed=42):
    a_correct = [a['output'] == a['target'] for a, _ in pairs]
    b_correct = [b['output'] == b['target'] for _, b in pairs]
    a_only = sum(a and not b for a, b in zip(a_correct, b_correct))
    b_only = sum(b and not a for a, b in zip(a_correct, b_correct))
    groups = [a['target'] for a, _ in pairs]
    exact = paired_bootstrap([int(b) - int(a) for a, b in zip(a_correct, b_correct)], groups, resamples, seed)
    a_cer = [character_distance(a['output'], a['target']) / max(1, len(a['target'])) for a, _ in pairs]
    b_cer = [character_distance(b['output'], b['target']) / max(1, len(b['target'])) for _, b in pairs]
    cer = paired_bootstrap([b-a for a, b in zip(a_cer, b_cer)], groups, resamples, seed)
    return {'examples': len(pairs), 'target_groups': len(set(groups)),
            'a_only_correct': a_only, 'b_only_correct': b_only, 'mcnemar_p': mcnemar_exact(a_only, b_only),
            'exact_match': {'a': sum(a_correct)/len(pairs), 'b': sum(b_correct)/len(pairs), **exact},
            'mean_cer': {'a': sum(a_cer)/len(pairs), 'b': sum(b_cer)/len(pairs), **cer}}


def compare_reports(a, b, resamples=10_000, seed=42):
    pairs = paired_rows(a, b)
    result = {'difference_direction': 'B - A', 'resamples': resamples, 'seed': seed,
              'bootstrap_unit': 'target', 'overall': compare_pairs(pairs, resamples, seed),
              'subsets': {}, 'difficulty': {}, 'categories': {}}
    for name, prefix in [('common_voice', 'Common Voice'), ('gündelik', 'Megazeka')]:
        chosen = [(a, b) for a, b in pairs if a.get('source', '').startswith(prefix)]
        if chosen:
            result['subsets'][name] = compare_pairs(chosen, resamples, seed)
    for key, section in [('difficulty', 'difficulty'), ('category', 'categories')]:
        for name in sorted({a[key] for a, _ in pairs if key in a}):
            result[section][name] = compare_pairs([(a, b) for a, b in pairs if a.get(key) == name], resamples, seed)
    return result


def verdict(result):
    lo, hi = result['exact_match']['ci95']
    if lo <= 0 <= hi:
        return 'fark gürültü sınırında'
    return ('B' if lo > 0 else 'A') + ' lehine fark var'


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument('a', type=Path)
    parser.add_argument('b', type=Path)
    parser.add_argument('--audited', action='store_true', help='Denetim listesini iki raporun hedeflerine de uygula.')
    args = parser.parse_args()
    a, b = [json.loads(path.read_text(encoding='utf-8')) for path in (args.a, args.b)]
    if args.audited:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from evaluation.audit import audited_rows
        paired_rows(a, b)
        a, b = [{**r, 'examples': audited_rows(r['examples'])} for r in (a, b)]
    result = compare_reports(a, b)
    result['targets'] = 'audited' if args.audited else 'original'
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print('Tam eşleşme: ' + verdict(result['overall']) + '.')
    print('Farklar B - A; CER cümle ortalamasıdır. Alt grup p değerleri çoklu karşılaştırma için düzeltilmemiştir.')


if __name__ == '__main__':
    main()
