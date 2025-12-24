"""Tests for deterministic rendering."""

import pytest
from soundforge.schema import SoundSpec
from soundforge.renderer import render_samples, render_wav_bytes


def test_deterministic_rendering():
    """Test that same spec produces identical samples."""
    spec_dict = {
        "version": "soundspec-1",
        "name": "test",
        "description": "test",
        "sample_rate": 44100,
        "duration": 0.1,
        "seed": 42,
        "global": {"amp": 0.8, "normalize": False},
        "layers": [
            {
                "id": "main",
                "type": "osc",
                "amp": 0.7,
                "pan": 0.0,
                "phase": 0.0,
                "env": {"attack": 0.01, "decay": 0.08, "shape": "exp"},
                "osc": {"waveform": "sine", "freq": 440.0, "detune": 0.0}
            }
        ]
    }
    
    spec = SoundSpec.model_validate(spec_dict)
    
    # Render twice
    samples1 = render_samples(spec)
    samples2 = render_samples(spec)
    
    # Should be identical
    assert len(samples1) == len(samples2)
    assert samples1 == samples2


def test_deterministic_noise():
    """Test that noise is deterministic with same seed."""
    spec_dict = {
        "version": "soundspec-1",
        "name": "test",
        "description": "test",
        "sample_rate": 44100,
        "duration": 0.1,
        "seed": 123,
        "global": {"amp": 0.8, "normalize": False},
        "layers": [
            {
                "id": "noise",
                "type": "noise",
                "amp": 0.6,
                "pan": 0.0,
                "phase": 0.0,
                "env": {"attack": 0.001, "decay": 0.08, "shape": "exp"},
                "noise": {"color": "white"}
            }
        ]
    }
    
    spec = SoundSpec.model_validate(spec_dict)
    
    samples1 = render_samples(spec)
    samples2 = render_samples(spec)
    
    assert samples1 == samples2


def test_different_seeds_produce_different_noise():
    """Test that different seeds produce different noise."""
    spec_dict1 = {
        "version": "soundspec-1",
        "name": "test",
        "description": "test",
        "sample_rate": 44100,
        "duration": 0.1,
        "seed": 42,
        "global": {"amp": 0.8, "normalize": False},
        "layers": [
            {
                "id": "noise",
                "type": "noise",
                "amp": 0.6,
                "pan": 0.0,
                "phase": 0.0,
                "env": {"attack": 0.001, "decay": 0.08, "shape": "exp"},
                "noise": {"color": "white"}
            }
        ]
    }
    
    spec_dict2 = spec_dict1.copy()
    spec_dict2["seed"] = 999
    
    spec1 = SoundSpec.model_validate(spec_dict1)
    spec2 = SoundSpec.model_validate(spec_dict2)
    
    samples1 = render_samples(spec1)
    samples2 = render_samples(spec2)
    
    # Should be different
    assert samples1 != samples2


def test_wav_bytes_deterministic():
    """Test that WAV encoding is deterministic."""
    spec_dict = {
        "version": "soundspec-1",
        "name": "test",
        "description": "test",
        "sample_rate": 44100,
        "duration": 0.1,
        "seed": 42,
        "global": {"amp": 0.8, "normalize": False},
        "layers": [
            {
                "id": "main",
                "type": "osc",
                "amp": 0.7,
                "pan": 0.0,
                "phase": 0.0,
                "env": {"attack": 0.01, "decay": 0.08, "shape": "exp"},
                "osc": {"waveform": "sine", "freq": 440.0, "detune": 0.0}
            }
        ]
    }
    
    spec = SoundSpec.model_validate(spec_dict)
    
    wav1 = render_wav_bytes(spec)
    wav2 = render_wav_bytes(spec)
    
    assert wav1 == wav2


def test_chirp_deterministic():
    """Test that chirp rendering is deterministic."""
    spec_dict = {
        "version": "soundspec-1",
        "name": "test",
        "description": "test",
        "sample_rate": 44100,
        "duration": 0.2,
        "seed": 42,
        "global": {"amp": 0.8, "normalize": False},
        "layers": [
            {
                "id": "chirp",
                "type": "chirp",
                "amp": 0.8,
                "pan": 0.0,
                "phase": 0.0,
                "env": {"attack": 0.01, "decay": 0.15, "shape": "exp"},
                "chirp": {
                    "waveform": "saw",
                    "f_start": 1000.0,
                    "f_end": 200.0,
                    "curve": "exponential",
                    "vibrato_hz": 0.0,
                    "vibrato_depth": 0.0
                }
            }
        ]
    }
    
    spec = SoundSpec.model_validate(spec_dict)
    
    samples1 = render_samples(spec)
    samples2 = render_samples(spec)
    
    assert samples1 == samples2


def test_fm_deterministic():
    """Test that FM synthesis is deterministic."""
    spec_dict = {
        "version": "soundspec-1",
        "name": "test",
        "description": "test",
        "sample_rate": 44100,
        "duration": 0.1,
        "seed": 42,
        "global": {"amp": 0.8, "normalize": False},
        "layers": [
            {
                "id": "fm",
                "type": "fm",
                "amp": 0.7,
                "pan": 0.0,
                "phase": 0.0,
                "env": {"attack": 0.01, "decay": 0.08, "shape": "exp"},
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
    
    samples1 = render_samples(spec)
    samples2 = render_samples(spec)
    
    assert samples1 == samples2


def test_normalize_deterministic():
    """Test that normalization is deterministic."""
    spec_dict = {
        "version": "soundspec-1",
        "name": "test",
        "description": "test",
        "sample_rate": 44100,
        "duration": 0.1,
        "seed": 42,
        "global": {"amp": 0.8, "normalize": True},
        "layers": [
            {
                "id": "main",
                "type": "osc",
                "amp": 0.7,
                "pan": 0.0,
                "phase": 0.0,
                "env": {"attack": 0.01, "decay": 0.08, "shape": "exp"},
                "osc": {"waveform": "sine", "freq": 440.0, "detune": 0.0}
            }
        ]
    }
    
    spec = SoundSpec.model_validate(spec_dict)
    
    samples1 = render_samples(spec)
    samples2 = render_samples(spec)
    
    assert samples1 == samples2


def test_fx_deterministic():
    """Test that effects are deterministic."""
    spec_dict = {
        "version": "soundspec-1",
        "name": "test",
        "description": "test",
        "sample_rate": 44100,
        "duration": 0.1,
        "seed": 42,
        "global": {"amp": 0.8, "normalize": False},
        "layers": [
            {
                "id": "main",
                "type": "osc",
                "amp": 0.7,
                "pan": 0.0,
                "phase": 0.0,
                "env": {"attack": 0.01, "decay": 0.08, "shape": "exp"},
                "osc": {"waveform": "sine", "freq": 440.0, "detune": 0.0}
            }
        ],
        "fx_chain": [
            {
                "type": "softclip",
                "enabled": True,
                "params": {"drive": 2.0}
            },
            {
                "type": "delay",
                "enabled": True,
                "params": {"time_ms": 50.0, "feedback": 0.3, "mix": 0.2}
            }
        ]
    }
    
    spec = SoundSpec.model_validate(spec_dict)
    
    samples1 = render_samples(spec)
    samples2 = render_samples(spec)
    
    assert samples1 == samples2
