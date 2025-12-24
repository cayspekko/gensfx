"""Tests for parameter path updates."""

import pytest
from soundforge.schema import SoundSpec
from soundforge.paths import update_spec_from_param


def get_test_spec() -> SoundSpec:
    """Get a test spec with various layer types."""
    spec_dict = {
        "version": "soundspec-1",
        "name": "test",
        "description": "test",
        "sample_rate": 44100,
        "duration": 0.5,
        "seed": 42,
        "global": {"amp": 0.8, "normalize": False},
        "layers": [
            {
                "id": "main",
                "type": "osc",
                "amp": 0.7,
                "pan": 0.0,
                "phase": 0.0,
                "env": {"attack": 0.01, "decay": 0.3, "shape": "exp"},
                "osc": {"waveform": "sine", "freq": 440.0, "detune": 0.0}
            },
            {
                "id": "chirp",
                "type": "chirp",
                "amp": 0.6,
                "pan": 0.0,
                "phase": 0.0,
                "env": {"attack": 0.01, "decay": 0.2, "shape": "exp"},
                "chirp": {
                    "waveform": "saw",
                    "f_start": 1000.0,
                    "f_end": 200.0,
                    "curve": "exponential",
                    "vibrato_hz": 0.0,
                    "vibrato_depth": 0.0
                }
            }
        ],
        "fx_chain": [
            {
                "type": "softclip",
                "enabled": True,
                "params": {"drive": 2.0}
            }
        ]
    }
    return SoundSpec.model_validate(spec_dict)


def test_update_global_amp():
    """Test updating global amplitude."""
    spec = get_test_spec()
    assert spec.global_.amp == 0.8
    
    success = update_spec_from_param(spec, "global.amp", 0.5)
    assert success
    assert spec.global_.amp == 0.5


def test_update_global_normalize():
    """Test updating global normalize."""
    spec = get_test_spec()
    assert spec.global_.normalize == False
    
    success = update_spec_from_param(spec, "global.normalize", True)
    assert success
    assert spec.global_.normalize == True


def test_update_duration():
    """Test updating duration."""
    spec = get_test_spec()
    assert spec.duration == 0.5
    
    success = update_spec_from_param(spec, "duration", 1.0)
    assert success
    assert spec.duration == 1.0


def test_update_layer_by_index():
    """Test updating layer by index."""
    spec = get_test_spec()
    assert spec.layers[0].amp == 0.7
    
    success = update_spec_from_param(spec, "layers[0].amp", 0.9)
    assert success
    assert spec.layers[0].amp == 0.9


def test_update_layer_by_id():
    """Test updating layer by ID."""
    spec = get_test_spec()
    assert spec.layers[0].amp == 0.7
    
    success = update_spec_from_param(spec, "layers_by_id.main.amp", 0.9)
    assert success
    assert spec.layers[0].amp == 0.9


def test_update_osc_freq():
    """Test updating oscillator frequency."""
    spec = get_test_spec()
    assert spec.layers[0].osc.freq == 440.0
    
    success = update_spec_from_param(spec, "layers_by_id.main.osc.freq", 880.0)
    assert success
    assert spec.layers[0].osc.freq == 880.0


def test_update_chirp_params():
    """Test updating chirp parameters."""
    spec = get_test_spec()
    assert spec.layers[1].chirp.f_start == 1000.0
    
    success = update_spec_from_param(spec, "layers_by_id.chirp.chirp.f_start", 1500.0)
    assert success
    assert spec.layers[1].chirp.f_start == 1500.0
    
    success = update_spec_from_param(spec, "layers_by_id.chirp.chirp.f_end", 100.0)
    assert success
    assert spec.layers[1].chirp.f_end == 100.0


def test_update_envelope():
    """Test updating envelope parameters."""
    spec = get_test_spec()
    assert spec.layers[0].env.attack == 0.01
    
    success = update_spec_from_param(spec, "layers_by_id.main.env.attack", 0.05)
    assert success
    assert spec.layers[0].env.attack == 0.05
    
    success = update_spec_from_param(spec, "layers_by_id.main.env.decay", 0.5)
    assert success
    assert spec.layers[0].env.decay == 0.5


def test_update_fx_by_index():
    """Test updating FX by index."""
    spec = get_test_spec()
    assert spec.fx_chain[0].params.drive == 2.0
    
    success = update_spec_from_param(spec, "fx[0].params.drive", 3.0)
    assert success
    assert spec.fx_chain[0].params.drive == 3.0


def test_update_fx_by_type():
    """Test updating FX by type."""
    spec = get_test_spec()
    assert spec.fx_chain[0].params.drive == 2.0
    
    success = update_spec_from_param(spec, "fx_by_type.softclip.params.drive", 3.5)
    assert success
    assert spec.fx_chain[0].params.drive == 3.5


def test_update_fx_enabled():
    """Test updating FX enabled state."""
    spec = get_test_spec()
    assert spec.fx_chain[0].enabled == True
    
    success = update_spec_from_param(spec, "fx[0].enabled", False)
    assert success
    assert spec.fx_chain[0].enabled == False


def test_invalid_path():
    """Test that invalid paths return False."""
    spec = get_test_spec()
    
    success = update_spec_from_param(spec, "invalid.path", 1.0)
    assert not success
    
    success = update_spec_from_param(spec, "layers[99].amp", 1.0)
    assert not success
    
    success = update_spec_from_param(spec, "layers_by_id.nonexistent.amp", 1.0)
    assert not success


def test_update_layer_pan():
    """Test updating layer pan."""
    spec = get_test_spec()
    assert spec.layers[0].pan == 0.0
    
    success = update_spec_from_param(spec, "layers_by_id.main.pan", -0.5)
    assert success
    assert spec.layers[0].pan == -0.5


def test_update_layer_phase():
    """Test updating layer phase."""
    spec = get_test_spec()
    assert spec.layers[0].phase == 0.0
    
    success = update_spec_from_param(spec, "layers_by_id.main.phase", 1.57)
    assert success
    assert spec.layers[0].phase == 1.57


def test_update_with_modulation():
    """Test updating modulation parameters."""
    spec_dict = {
        "version": "soundspec-1",
        "name": "test",
        "description": "test",
        "sample_rate": 44100,
        "duration": 0.5,
        "seed": 42,
        "global": {"amp": 0.8, "normalize": False},
        "layers": [
            {
                "id": "main",
                "type": "osc",
                "amp": 0.7,
                "pan": 0.0,
                "phase": 0.0,
                "env": {"attack": 0.01, "decay": 0.3, "shape": "exp"},
                "osc": {"waveform": "sine", "freq": 440.0, "detune": 0.0},
                "mod": {
                    "tremolo_hz": 5.0,
                    "tremolo_depth": 0.3,
                    "pitch_lfo_hz": 0.0,
                    "pitch_lfo_depth": 0.0
                }
            }
        ]
    }
    spec = SoundSpec.model_validate(spec_dict)
    
    assert spec.layers[0].mod.tremolo_hz == 5.0
    
    success = update_spec_from_param(spec, "layers_by_id.main.mod.tremolo_hz", 10.0)
    assert success
    assert spec.layers[0].mod.tremolo_hz == 10.0
    
    success = update_spec_from_param(spec, "layers_by_id.main.mod.tremolo_depth", 0.5)
    assert success
    assert spec.layers[0].mod.tremolo_depth == 0.5
