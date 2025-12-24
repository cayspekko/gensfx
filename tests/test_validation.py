"""Tests for SoundSpec validation."""

import pytest
from pydantic import ValidationError
from soundforge.schema import SoundSpec, Layer, LayerType, Envelope, OscParams, Waveform


def test_valid_soundspec():
    """Test that a valid SoundSpec validates correctly."""
    spec_dict = {
        "version": "soundspec-1",
        "name": "test_sound",
        "description": "A test sound",
        "sample_rate": 44100,
        "duration": 0.5,
        "seed": 42,
        "global": {"amp": 0.8, "normalize": True},
        "layers": [
            {
                "id": "main",
                "type": "osc",
                "amp": 0.7,
                "pan": 0.0,
                "phase": 0.0,
                "env": {"attack": 0.01, "decay": 0.3, "shape": "exp"},
                "osc": {"waveform": "sine", "freq": 440.0, "detune": 0.0}
            }
        ],
        "fx_chain": [],
        "params": []
    }
    
    spec = SoundSpec.model_validate(spec_dict)
    assert spec.name == "test_sound"
    assert spec.duration == 0.5
    assert len(spec.layers) == 1


def test_invalid_version():
    """Test that invalid version is rejected."""
    spec_dict = {
        "version": "soundspec-2",
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
            }
        ]
    }
    
    with pytest.raises(ValidationError):
        SoundSpec.model_validate(spec_dict)


def test_duration_bounds():
    """Test that duration is clamped to valid range."""
    spec_dict = {
        "version": "soundspec-1",
        "name": "test",
        "description": "test",
        "sample_rate": 44100,
        "duration": 5.0,  # Too long
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
            }
        ]
    }
    
    with pytest.raises(ValidationError):
        SoundSpec.model_validate(spec_dict)


def test_layer_type_params_required():
    """Test that layer type-specific params are required."""
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
                "env": {"attack": 0.01, "decay": 0.3, "shape": "exp"}
                # Missing osc params
            }
        ]
    }
    
    with pytest.raises(ValidationError):
        SoundSpec.model_validate(spec_dict)


def test_unique_layer_ids():
    """Test that layer IDs must be unique."""
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
                "id": "main",  # Duplicate ID
                "type": "osc",
                "amp": 0.5,
                "pan": 0.0,
                "phase": 0.0,
                "env": {"attack": 0.01, "decay": 0.3, "shape": "exp"},
                "osc": {"waveform": "sine", "freq": 880.0, "detune": 0.0}
            }
        ]
    }
    
    with pytest.raises(ValidationError):
        SoundSpec.model_validate(spec_dict)


def test_frequency_bounds():
    """Test that frequencies are within valid range."""
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
                "osc": {"waveform": "sine", "freq": 25000.0, "detune": 0.0}  # Too high
            }
        ]
    }
    
    with pytest.raises(ValidationError):
        SoundSpec.model_validate(spec_dict)


def test_chirp_layer():
    """Test chirp layer validation."""
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
                "id": "laser",
                "type": "chirp",
                "amp": 0.8,
                "pan": 0.0,
                "phase": 0.0,
                "env": {"attack": 0.01, "decay": 0.3, "shape": "exp"},
                "chirp": {
                    "waveform": "saw",
                    "f_start": 1000.0,
                    "f_end": 200.0,
                    "curve": "exponential",
                    "vibrato_hz": 5.0,
                    "vibrato_depth": 0.05
                }
            }
        ]
    }
    
    spec = SoundSpec.model_validate(spec_dict)
    assert spec.layers[0].chirp.f_start == 1000.0
    assert spec.layers[0].chirp.curve.value == "exponential"


def test_fm_layer():
    """Test FM layer validation."""
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
                "id": "fm_tone",
                "type": "fm",
                "amp": 0.7,
                "pan": 0.0,
                "phase": 0.0,
                "env": {"attack": 0.01, "decay": 0.3, "shape": "exp"},
                "fm": {
                    "carrier_freq": 440.0,
                    "mod_freq": 220.0,
                    "index": 5.0,
                    "brightness": 0.5
                }
            }
        ]
    }
    
    spec = SoundSpec.model_validate(spec_dict)
    assert spec.layers[0].fm.carrier_freq == 440.0
    assert spec.layers[0].fm.index == 5.0


def test_noise_layer():
    """Test noise layer validation."""
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
                "id": "noise",
                "type": "noise",
                "amp": 0.6,
                "pan": 0.0,
                "phase": 0.0,
                "env": {"attack": 0.001, "decay": 0.2, "shape": "exp"},
                "noise": {
                    "color": "white",
                    "cutoff_start": 5000.0,
                    "cutoff_end": 1000.0,
                    "cutoff_curve": "exponential"
                }
            }
        ]
    }
    
    spec = SoundSpec.model_validate(spec_dict)
    assert spec.layers[0].noise.color.value == "white"


def test_impulse_layer():
    """Test impulse layer validation."""
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
                "id": "click",
                "type": "impulse",
                "amp": 0.8,
                "pan": 0.0,
                "phase": 0.0,
                "env": {"attack": 0.001, "decay": 0.05, "shape": "exp"},
                "impulse": {
                    "kind": "metal_ping",
                    "width": 0.005,
                    "tone_freq": 2000.0
                }
            }
        ]
    }
    
    spec = SoundSpec.model_validate(spec_dict)
    assert spec.layers[0].impulse.kind.value == "metal_ping"
    assert spec.layers[0].impulse.tone_freq == 2000.0
