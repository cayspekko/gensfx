# SoundSpec Examples

This document contains example SoundSpec JSON files demonstrating various sound effects.

## Example 1: Gentle Pickup Sound

```json
{
  "version": "soundspec-1",
  "name": "gentle_pickup",
  "description": "Gentle sparkly diamond pickup with soft rising tone",
  "sample_rate": 44100,
  "duration": 0.8,
  "seed": 42,
  "global": {
    "amp": 0.7,
    "normalize": true
  },
  "layers": [
    {
      "id": "main",
      "type": "osc",
      "amp": 0.8,
      "pan": 0.0,
      "phase": 0.0,
      "env": {
        "attack": 0.05,
        "decay": 0.6,
        "shape": "exp"
      },
      "osc": {
        "waveform": "sine",
        "freq": 800.0,
        "detune": 0.0,
        "harmonics": [
          {"mul": 2.0, "amp": 0.3},
          {"mul": 3.0, "amp": 0.15}
        ]
      },
      "mod": {
        "tremolo_hz": 8.0,
        "tremolo_depth": 0.2,
        "pitch_lfo_hz": 0.0,
        "pitch_lfo_depth": 0.0
      }
    },
    {
      "id": "sparkle",
      "type": "osc",
      "amp": 0.4,
      "pan": 0.0,
      "phase": 0.0,
      "env": {
        "attack": 0.02,
        "decay": 0.4,
        "shape": "exp"
      },
      "osc": {
        "waveform": "sine",
        "freq": 2400.0,
        "detune": 5.0
      }
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
    }
  ]
}
```

## Example 2: Laser Blast

```json
{
  "version": "soundspec-1",
  "name": "laser_blast",
  "description": "Descending laser blast with exponential pitch sweep",
  "sample_rate": 44100,
  "duration": 0.4,
  "seed": 42,
  "global": {
    "amp": 0.8,
    "normalize": true
  },
  "layers": [
    {
      "id": "main",
      "type": "chirp",
      "amp": 0.9,
      "pan": 0.0,
      "phase": 0.0,
      "env": {
        "attack": 0.01,
        "decay": 0.3,
        "shape": "exp"
      },
      "chirp": {
        "waveform": "saw",
        "f_start": 1200.0,
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
      "enabled": true,
      "params": {
        "drive": 1.5
      }
    }
  ],
  "params": [
    {
      "id": "start_freq",
      "label": "Start Frequency",
      "kind": "slider",
      "min": 800.0,
      "max": 2000.0,
      "step": 10.0,
      "default": 1200.0,
      "path": "layers_by_id.main.chirp.f_start"
    },
    {
      "id": "end_freq",
      "label": "End Frequency",
      "kind": "slider",
      "min": 100.0,
      "max": 500.0,
      "step": 10.0,
      "default": 200.0,
      "path": "layers_by_id.main.chirp.f_end"
    }
  ]
}
```

## Example 3: Explosion

```json
{
  "version": "soundspec-1",
  "name": "explosion",
  "description": "Explosion with low rumble and noise crack",
  "sample_rate": 44100,
  "duration": 1.2,
  "seed": 123,
  "global": {
    "amp": 0.85,
    "normalize": true
  },
  "layers": [
    {
      "id": "rumble",
      "type": "osc",
      "amp": 0.6,
      "pan": 0.0,
      "phase": 0.0,
      "env": {
        "attack": 0.01,
        "decay": 0.8,
        "shape": "exp"
      },
      "osc": {
        "waveform": "sine",
        "freq": 60.0,
        "detune": 0.0
      },
      "filter": [
        {
          "type": "biquad_lp",
          "cutoff": 800.0,
          "cutoff_end": 100.0,
          "curve": "exponential",
          "q": 0.707
        }
      ]
    },
    {
      "id": "crack",
      "type": "noise",
      "amp": 0.8,
      "pan": 0.0,
      "phase": 0.0,
      "env": {
        "attack": 0.001,
        "decay": 0.15,
        "shape": "exp"
      },
      "noise": {
        "color": "white",
        "cutoff_start": 8000.0,
        "cutoff_end": 2000.0,
        "cutoff_curve": "exponential"
      }
    }
  ],
  "fx_chain": [],
  "params": [
    {
      "id": "rumble_freq",
      "label": "Rumble Frequency",
      "kind": "slider",
      "min": 40.0,
      "max": 120.0,
      "step": 5.0,
      "default": 60.0,
      "path": "layers_by_id.rumble.osc.freq"
    }
  ]
}
```

## Example 4: UI Click

```json
{
  "version": "soundspec-1",
  "name": "ui_click",
  "description": "Clean UI button click",
  "sample_rate": 44100,
  "duration": 0.08,
  "seed": 100,
  "global": {
    "amp": 0.6,
    "normalize": true
  },
  "layers": [
    {
      "id": "click",
      "type": "impulse",
      "amp": 0.8,
      "pan": 0.0,
      "phase": 0.0,
      "env": {
        "attack": 0.001,
        "decay": 0.05,
        "shape": "exp"
      },
      "impulse": {
        "kind": "click",
        "width": 0.002
      }
    },
    {
      "id": "tone",
      "type": "osc",
      "amp": 0.5,
      "pan": 0.0,
      "phase": 0.0,
      "env": {
        "attack": 0.001,
        "decay": 0.04,
        "shape": "exp"
      },
      "osc": {
        "waveform": "sine",
        "freq": 1200.0,
        "detune": 0.0
      }
    }
  ],
  "fx_chain": [],
  "params": []
}
```

## Example 5: Shield Deflection

```json
{
  "version": "soundspec-1",
  "name": "shield_deflect",
  "description": "Shield deflection with metallic ring and shimmer",
  "sample_rate": 44100,
  "duration": 0.6,
  "seed": 789,
  "global": {
    "amp": 0.75,
    "normalize": true
  },
  "layers": [
    {
      "id": "ping",
      "type": "impulse",
      "amp": 0.7,
      "pan": 0.0,
      "phase": 0.0,
      "env": {
        "attack": 0.001,
        "decay": 0.3,
        "shape": "exp"
      },
      "impulse": {
        "kind": "metal_ping",
        "width": 0.005,
        "tone_freq": 1800.0
      }
    },
    {
      "id": "shimmer",
      "type": "fm",
      "amp": 0.5,
      "pan": 0.0,
      "phase": 0.0,
      "env": {
        "attack": 0.05,
        "decay": 0.4,
        "shape": "exp"
      },
      "fm": {
        "carrier_freq": 2400.0,
        "mod_freq": 7.0,
        "index": 3.0,
        "brightness": 0.6
      }
    }
  ],
  "fx_chain": [],
  "params": [
    {
      "id": "ping_freq",
      "label": "Ping Frequency",
      "kind": "slider",
      "min": 1000.0,
      "max": 3000.0,
      "step": 100.0,
      "default": 1800.0,
      "path": "layers_by_id.ping.impulse.tone_freq"
    }
  ]
}
```

## Using These Examples

You can load these examples by:

1. Copying the JSON to a file (e.g., `pickup.json`)
2. In Python:
```python
from soundforge import SoundSpec, render_wav_bytes
import json

with open('pickup.json') as f:
    spec_dict = json.load(f)

spec = SoundSpec.model_validate(spec_dict)
wav_bytes = render_wav_bytes(spec)

with open('output.wav', 'wb') as f:
    f.write(wav_bytes)
```

3. Or use the Streamlit app to generate and tweak sounds interactively!
