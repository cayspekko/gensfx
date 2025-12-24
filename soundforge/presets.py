"""Hand-crafted preset SoundSpecs."""

from soundforge.schema import SoundSpec


def get_default_pickup() -> SoundSpec:
    """Get a gentle sparkly pickup sound."""
    return SoundSpec.model_validate({
        "version": "soundspec-1",
        "name": "gentle_pickup",
        "description": "Gentle sparkly diamond pickup with soft rising tone",
        "sample_rate": 44100,
        "duration": 0.8,
        "seed": 42,
        "global": {"amp": 0.7, "normalize": True},
        "layers": [
            {
                "id": "main",
                "type": "osc",
                "amp": 0.8,
                "pan": 0.0,
                "phase": 0.0,
                "env": {"attack": 0.05, "decay": 0.6, "shape": "exp"},
                "osc": {
                    "waveform": "sine",
                    "freq": 800.0,
                    "detune": 0.0,
                    "harmonics": [
                        {"mul": 2.0, "amp": 0.3},
                        {"mul": 3.0, "amp": 0.15}
                    ]
                },
                "mod": {"tremolo_hz": 8.0, "tremolo_depth": 0.2, "pitch_lfo_hz": 0.0, "pitch_lfo_depth": 0.0}
            },
            {
                "id": "sparkle",
                "type": "osc",
                "amp": 0.4,
                "pan": 0.0,
                "phase": 0.0,
                "env": {"attack": 0.02, "decay": 0.4, "shape": "exp"},
                "osc": {"waveform": "sine", "freq": 2400.0, "detune": 5.0}
            }
        ],
        "fx_chain": [],
        "params": [
            {
                "id": "main_freq",
                "label": "Main Frequency",
                "kind": "slider",
                "min": 400.0,
                "max": 1200.0,
                "step": 10.0,
                "default": 800.0,
                "path": "layers_by_id.main.osc.freq"
            },
            {
                "id": "sparkle_freq",
                "label": "Sparkle Frequency",
                "kind": "slider",
                "min": 1800.0,
                "max": 3600.0,
                "step": 50.0,
                "default": 2400.0,
                "path": "layers_by_id.sparkle.osc.freq"
            },
            {
                "id": "tremolo_rate",
                "label": "Tremolo Rate",
                "kind": "slider",
                "min": 0.0,
                "max": 20.0,
                "step": 0.5,
                "default": 8.0,
                "path": "layers_by_id.main.mod.tremolo_hz"
            },
            {
                "id": "duration",
                "label": "Duration",
                "kind": "slider",
                "min": 0.3,
                "max": 2.0,
                "step": 0.1,
                "default": 0.8,
                "path": "duration"
            }
        ]
    })


def get_ui_click() -> SoundSpec:
    """Get a clean UI button click."""
    return SoundSpec.model_validate({
        "version": "soundspec-1",
        "name": "ui_click",
        "description": "Clean UI button click",
        "sample_rate": 44100,
        "duration": 0.08,
        "seed": 100,
        "global": {"amp": 0.6, "normalize": True},
        "layers": [
            {
                "id": "click",
                "type": "impulse",
                "amp": 0.8,
                "pan": 0.0,
                "phase": 0.0,
                "env": {"attack": 0.001, "decay": 0.05, "shape": "exp"},
                "impulse": {"kind": "click", "width": 0.002}
            },
            {
                "id": "tone",
                "type": "osc",
                "amp": 0.5,
                "pan": 0.0,
                "phase": 0.0,
                "env": {"attack": 0.001, "decay": 0.04, "shape": "exp"},
                "osc": {"waveform": "sine", "freq": 1200.0, "detune": 0.0}
            }
        ],
        "fx_chain": [],
        "params": [
            {
                "id": "tone_freq",
                "label": "Tone Frequency",
                "kind": "slider",
                "min": 800.0,
                "max": 2000.0,
                "step": 50.0,
                "default": 1200.0,
                "path": "layers_by_id.tone.osc.freq"
            }
        ]
    })


def get_all_presets() -> dict[str, SoundSpec]:
    """Get all available presets."""
    return {
        "gentle_pickup": get_default_pickup(),
        "ui_click": get_ui_click()
    }
