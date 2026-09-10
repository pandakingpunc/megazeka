import pytest
from megazeka.storage import ROOT

@pytest.mark.skipif(not (ROOT/'models/checkpoints/best/adapter_config.json').exists(), reason='Eğitilmiş model gerekli')
def test_real_local_model_interface(monkeypatch):
    import socket
    def disallow_network(*args, **kwargs):
        raise AssertionError('Çıkarım sırasında ağ bağlantısı yasak.')
    monkeypatch.setattr(socket.socket, 'connect', disallow_network)
    from megazeka.inference import CorrectionEngine
    engine = CorrectionEngine()
    result = engine.correct('Bugün hava çok güzel.\n\nMerhaba!')
    assert result['output'].strip()
    assert result['output'].count('\n') == 2
    assert result['tokens'] and result['generated']
    assert all(0 <= t['probability'] <= 1 for t in result['generated'])
    assert all(result['timings_ms'][key] >= 0 for key in result['timings_ms'])
    assert len(engine.correct_batch(['Merhaba!', 'Nasılsın?'])) == 2
    with pytest.raises(ValueError): engine.correct(' ')
    with pytest.raises(ValueError): engine.correct('a'*4001)
    with pytest.raises(TypeError): engine.correct(None)
