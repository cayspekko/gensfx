# SoundForge - Project Summary

## Overview

SoundForge is a complete Streamlit application that generates game sound effects from natural language prompts using a safe, structured JSON format called **SoundSpec**. The system ensures security by never executing model-generated code - only validated JSON specifications.

## Repository Structure

```
gensfx/
├── soundforge/              # Core library
│   ├── __init__.py         # Package exports
│   ├── schema.py           # Pydantic models for SoundSpec validation
│   ├── renderer.py         # Audio synthesis engine (pure Python)
│   ├── util_wav.py         # WAV file encoding
│   ├── paths.py            # Parameter path resolver for dynamic UI
│   ├── llm.py              # OpenAI integration + mock generator
│   └── presets.py          # Hand-crafted example sounds
├── tests/                   # Test suite
│   ├── test_validation.py  # Schema validation tests
│   ├── test_determinism.py # Reproducibility tests
│   └── test_path_update.py # Parameter update tests
├── app.py                   # Streamlit web application
├── verify_install.py        # Installation verification script
├── requirements.txt         # Python dependencies
├── Makefile                 # Development commands
├── README.md                # Main documentation
├── QUICKSTART.md            # Quick start guide
├── EXAMPLES.md              # Example SoundSpec files
├── CONTRIBUTING.md          # Contribution guidelines
├── LICENSE                  # MIT License
├── .gitignore              # Git ignore rules
└── .env.example            # Environment variable template
```

## Key Features

### 1. Safe Architecture
- **No code execution**: Model outputs only JSON, never Python code
- **Schema validation**: All inputs validated with Pydantic
- **Range checking**: All parameters clamped to safe values
- **Fixed operator set**: Only predefined synthesis operators allowed

### 2. SoundSpec Format
A declarative JSON schema for audio synthesis with:
- **5 layer types**: osc, chirp, fm, noise, impulse
- **Envelopes**: attack, decay, sustain, release with multiple shapes
- **Filters**: 1-pole and biquad filters with sweeps
- **Effects**: softclip, bitcrush, delay, normalize
- **Dynamic parameters**: Auto-generated UI controls

### 3. Deterministic Rendering
- Same spec + seed = identical audio output
- Seeded PRNG for all randomness
- Pure Python synthesis (no numpy required)
- Comprehensive test coverage

### 4. LLM Integration
- OpenAI API integration with structured prompts
- Fallback mock generator (works without API key)
- Style mappings for common game SFX types
- JSON-only output with validation

### 5. Streamlit UI
- Natural language prompt input
- Dynamic parameter sliders
- Real-time audio playback
- Export WAV and JSON
- Sound history (last 10 generations)
- Auto-render option

## Technical Implementation

### Audio Synthesis (renderer.py)
- **Oscillators**: sine, triangle, square, saw with harmonics
- **Chirp**: frequency sweeps (linear/exponential)
- **FM synthesis**: carrier + modulator with brightness control
- **Noise**: white and pink noise with filtering
- **Impulse**: click, tap, metal ping
- **Envelopes**: exp, linear, ADSR
- **Filters**: 1-pole LP/HP, biquad LP/HP/BP/notch
- **Effects**: softclip, bitcrush, delay, normalize

### Schema Validation (schema.py)
- Pydantic v2 models with strict typing
- Enum-based operator types
- Field validation with ranges
- Unique ID enforcement
- JSON schema export

### Parameter System (paths.py)
- JSONPath-like syntax for updates
- Support for array indices: `layers[0].amp`
- Support for ID lookup: `layers_by_id.main.amp`
- Type-safe value updates
- Graceful error handling

### LLM Prompting (llm.py)
- Comprehensive system prompt with operator descriptions
- Style mappings (laser, explosion, pickup, etc.)
- JSON-only output enforcement
- Fallback to mock generator
- Error recovery

## Test Coverage

### Validation Tests (33 tests, all passing)
- ✅ Schema validation for all layer types
- ✅ Range checking and bounds enforcement
- ✅ Unique ID validation
- ✅ Type-specific parameter requirements

### Determinism Tests
- ✅ Identical output for same spec
- ✅ Seeded noise generation
- ✅ WAV byte-level reproducibility
- ✅ All operators deterministic

### Path Update Tests
- ✅ Global settings updates
- ✅ Layer updates by index and ID
- ✅ Nested parameter updates
- ✅ FX chain updates
- ✅ Invalid path handling

## Usage Examples

### Command Line
```bash
# Install
pip install -r requirements.txt

# Verify
python verify_install.py

# Run app
streamlit run app.py

# Run tests
pytest tests/ -v
```

### Python API
```python
from soundforge import generate_soundspec, render_wav_bytes

# Generate from prompt
spec = generate_soundspec("laser blast with descending pitch")

# Render to WAV
wav_bytes = render_wav_bytes(spec)

# Save
with open("laser.wav", "wb") as f:
    f.write(wav_bytes)
```

### Custom SoundSpec
```python
from soundforge.schema import SoundSpec

spec = SoundSpec.model_validate({
    "version": "soundspec-1",
    "name": "my_sound",
    "sample_rate": 44100,
    "duration": 0.5,
    "seed": 42,
    "global": {"amp": 0.8, "normalize": True},
    "layers": [...]
})
```

## Security Guarantees

1. ✅ **No eval/exec**: Never executes arbitrary code
2. ✅ **Schema validation**: All inputs validated before processing
3. ✅ **Range clamping**: All numeric values bounded
4. ✅ **Fixed operators**: Only predefined synthesis types
5. ✅ **CPU limits**: Max 3 seconds audio (144k samples)
6. ✅ **No file access**: Controlled I/O only

## Performance

- Pure Python implementation (no numpy required)
- Handles up to 3 seconds of audio at 48kHz
- Typical generation time: <1 second
- Typical rendering time: <0.5 seconds
- Memory efficient (streaming synthesis)

## Deployment Options

### Local Development
```bash
streamlit run app.py
```

### Streamlit Cloud
1. Push to GitHub
2. Connect to Streamlit Cloud
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

## Extension Points

### Adding New Operators
1. Update `LayerType` enum in schema.py
2. Create Pydantic model for parameters
3. Implement `render_<operator>` in renderer.py
4. Update path resolver in paths.py
5. Update LLM prompt in llm.py
6. Add tests

### Adding New Effects
1. Update `FXType` enum in schema.py
2. Add parameters to `FXParams`
3. Implement `apply_<effect>` in renderer.py
4. Update `apply_fx` dispatcher
5. Add tests

## Dependencies

- **streamlit**: Web UI framework
- **pydantic**: Schema validation
- **openai**: LLM integration (optional)
- **pytest**: Testing framework

No audio libraries required - pure Python synthesis!

## License

MIT License - see LICENSE file

## Contributing

See CONTRIBUTING.md for guidelines on:
- Development setup
- Code style
- Adding operators/effects
- Security requirements
- Pull request process

## Support

- GitHub Issues for bug reports
- Discussions for questions
- Pull requests welcome!

---

**Built with safety and simplicity in mind. No arbitrary code execution, ever.**
