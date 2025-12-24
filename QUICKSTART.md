# SoundForge Quick Start Guide

Get up and running with SoundForge in 5 minutes!

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd gensfx

# Install dependencies
pip install -r requirements.txt

# Verify installation
python verify_install.py
```

## Basic Usage

### 1. Run the Streamlit App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

### 2. Generate Your First Sound

1. Enter a prompt like: "gentle sparkly diamond pickup, soft rising tone"
2. Click "Generate"
3. Adjust the sliders to tweak the sound
4. Click "Render/Play" to hear it
5. Download the WAV or JSON

### 3. Use the Python API

```python
from soundforge import generate_soundspec, render_wav_bytes

# Generate from prompt
spec = generate_soundspec("laser blast with descending pitch")

# Render to WAV
wav_bytes = render_wav_bytes(spec)

# Save to file
with open("laser.wav", "wb") as f:
    f.write(wav_bytes)
```

### 4. Load and Modify Presets

```python
from soundforge import get_default_pickup, render_wav_bytes

# Load preset
spec = get_default_pickup()

# Modify parameters
spec.duration = 1.5
spec.layers[0].osc.freq = 1000.0

# Render
wav_bytes = render_wav_bytes(spec)
```

### 5. Create Custom SoundSpecs

```python
from soundforge.schema import SoundSpec

spec_dict = {
    "version": "soundspec-1",
    "name": "my_sound",
    "description": "A custom sound",
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
wav_bytes = render_wav_bytes(spec)
```

## Example Prompts

Try these prompts to explore different sound types:

- **Pickups**: "gentle sparkly diamond pickup, soft rising tone"
- **Lasers**: "laser blast with descending pitch, bright and harsh"
- **Explosions**: "explosion with deep rumble and crack"
- **UI Sounds**: "clean button click, subtle and professional"
- **Shields**: "shield deflection with metallic ring"
- **Hits**: "painful hit sound, sharp and impactful"

## Configuration

### OpenAI API Key (Optional)

For AI-powered generation, set your OpenAI API key:

```bash
export OPENAI_API_KEY="sk-..."
```

Or create a `.env` file:

```bash
cp .env.example .env
# Edit .env and add your API key
```

Without an API key, SoundForge uses a mock generator with reasonable defaults.

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_validation.py -v
```

## Common Tasks

### Export JSON Schema

```python
from soundforge import export_json_schema
import json

schema = export_json_schema()
print(json.dumps(schema, indent=2))
```

### Update Parameters Dynamically

```python
from soundforge import update_spec_from_param

# Update a parameter by path
success = update_spec_from_param(
    spec,
    "layers_by_id.main.osc.freq",
    880.0
)
```

### Batch Generate Sounds

```python
from soundforge import generate_soundspec, render_wav_bytes

prompts = [
    "laser blast",
    "explosion",
    "pickup sound"
]

for i, prompt in enumerate(prompts):
    spec = generate_soundspec(prompt)
    wav = render_wav_bytes(spec)
    
    with open(f"sound_{i}.wav", "wb") as f:
        f.write(wav)
```

## Troubleshooting

### Import Errors

```bash
# Ensure you're in the project directory
cd gensfx

# Reinstall dependencies
pip install -r requirements.txt
```

### OpenAI API Errors

If you see OpenAI errors, the app will fall back to mock generation. To use AI generation:

1. Get an API key from https://platform.openai.com/api-keys
2. Set the environment variable: `export OPENAI_API_KEY="sk-..."`
3. Restart the app

### Audio Not Playing

- Ensure your browser supports WAV playback
- Check that the audio file was generated (should see file size)
- Try downloading and playing in a media player

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore [EXAMPLES.md](EXAMPLES.md) for more SoundSpec examples
- Check [CONTRIBUTING.md](CONTRIBUTING.md) to add new features
- Run `make help` to see available commands

## Getting Help

- Open an issue on GitHub
- Check existing issues for solutions
- Read the documentation in the `docs/` folder

Happy sound designing! 🔊
