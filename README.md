# SoundForge

A Streamlit app that turns natural-language prompts into short game SFX using a safe, structured JSON format called **SoundSpec**.

## Features

- 🎮 Generate game sound effects from text prompts
- 🔒 Safe: No arbitrary code execution - only validated JSON specs
- 🎛️ Dynamic UI controls for tweaking generated sounds
- 🔁 Deterministic: Same spec + seed = same sound
- 📦 Export SoundSpec JSON and WAV files
- 🎵 Pure Python synthesis (no numpy required)

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd gensfx

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Set your OpenAI API key (optional - falls back to mock generator):

```bash
export OPENAI_API_KEY="sk-..."
```

### Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

## Example Prompts

- "gentle sparkly diamond pickup, soft rising tone"
- "laser blast with descending pitch"
- "explosion with rumble and crack"
- "shield deflection with metallic ring"
- "painful hit sound, sharp and harsh"
- "UI button click, subtle and clean"

## SoundSpec Format

SoundSpec is a JSON schema that describes audio synthesis in a safe, declarative way. The model outputs only JSON - never executable code.

### Core Structure

```json
{
  "version": "soundspec-1",
  "name": "pickup",
  "description": "Gentle sparkly pickup sound",
  "sample_rate": 44100,
  "duration": 0.8,
  "seed": 42,
  "global": {
    "amp": 0.7,
    "normalize": true
  },
  "layers": [...],
  "fx_chain": [...],
  "params": [...]
}
```

### Layer Types

- **osc**: Basic oscillator (sine, triangle, square, saw)
- **chirp**: Pitch glide oscillator (great for lasers)
- **fm**: Frequency modulation synthesis
- **noise**: White or pink noise
- **impulse**: Click, tap, or metallic ping

### Effects

- **softclip**: Gentle saturation
- **bitcrush**: Lo-fi degradation
- **delay**: Echo effect
- **normalize**: Peak normalization

### Dynamic Parameters

Each SoundSpec can include tweakable parameters that generate UI controls:

```json
{
  "id": "brightness",
  "label": "Brightness",
  "kind": "slider",
  "min": 0.0,
  "max": 1.0,
  "step": 0.01,
  "default": 0.5,
  "path": "layers_by_id.main.fm.brightness"
}
```

## Development

### Run Tests

```bash
pytest tests/
```

### Project Structure

```
gensfx/
├── app.py                 # Streamlit app
├── soundforge/
│   ├── __init__.py
│   ├── schema.py          # Pydantic models
│   ├── renderer.py        # Audio synthesis
│   ├── paths.py           # Parameter path resolver
│   ├── llm.py             # OpenAI integration
│   ├── presets.py         # Hand-crafted examples
│   └── util_wav.py        # WAV encoding
├── tests/
│   ├── test_validation.py
│   ├── test_determinism.py
│   └── test_path_update.py
├── requirements.txt
└── README.md
```

## Deployment

### Streamlit Cloud

1. Push to GitHub
2. Connect to [Streamlit Cloud](https://streamlit.io/cloud)
3. Add `OPENAI_API_KEY` to secrets

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

## Adding New Operators

To extend SoundSpec with new synthesis operators:

1. Add the operator type to `LayerType` enum in `schema.py`
2. Create a Pydantic model for the operator's parameters
3. Implement rendering logic in `renderer.py`
4. Update the LLM prompt template in `llm.py`
5. Add validation tests

## Security

- ✅ No code execution - only JSON validation
- ✅ All parameters are range-checked and clamped
- ✅ Fixed set of allowed operators
- ✅ CPU limits (max 3 seconds audio)

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please ensure:
- Type hints on all functions
- Tests for new features
- Code passes validation (determinism, schema)
