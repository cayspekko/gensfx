# Contributing to SoundForge

Thank you for your interest in contributing to SoundForge! This document provides guidelines and instructions for contributing.

## Development Setup

1. Clone the repository:
```bash
git clone <repo-url>
cd gensfx
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Verify installation:
```bash
python verify_install.py
```

## Running Tests

Run the full test suite:
```bash
pytest tests/ -v
```

Run specific test files:
```bash
pytest tests/test_validation.py -v
pytest tests/test_determinism.py -v
pytest tests/test_path_update.py -v
```

## Code Style

- Use type hints for all function parameters and return values
- Follow PEP 8 style guidelines
- Keep functions focused and well-documented
- Add docstrings to all public functions and classes

## Adding New Operators

To add a new synthesis operator to SoundSpec:

1. **Update the schema** (`soundforge/schema.py`):
   - Add the operator type to `LayerType` enum
   - Create a Pydantic model for the operator's parameters
   - Add the parameter model to the `Layer` class
   - Update the `check_type_params` validator

2. **Implement rendering** (`soundforge/renderer.py`):
   - Add a `render_<operator>` function
   - Update `render_layer` to handle the new type
   - Ensure deterministic behavior (use the PRNG for randomness)

3. **Update path resolver** (`soundforge/paths.py`):
   - Add an `_update_<operator>_field` function
   - Update `_update_layer_field` to handle the new type

4. **Update LLM prompt** (`soundforge/llm.py`):
   - Add the operator to the `SYSTEM_PROMPT`
   - Provide usage examples and style mappings

5. **Add tests**:
   - Validation test in `tests/test_validation.py`
   - Determinism test in `tests/test_determinism.py`
   - Path update test in `tests/test_path_update.py`

6. **Update documentation**:
   - Add examples to `EXAMPLES.md`
   - Update `README.md` if needed

## Adding New Effects

To add a new effect to the FX chain:

1. **Update schema** (`soundforge/schema.py`):
   - Add effect type to `FXType` enum
   - Add parameters to `FXParams` model

2. **Implement effect** (`soundforge/renderer.py`):
   - Add an `apply_<effect>` function
   - Update `apply_fx` to handle the new type
   - Ensure deterministic behavior

3. **Add tests** for validation and determinism

4. **Update documentation**

## Security Guidelines

SoundForge's core principle is **no arbitrary code execution**. When contributing:

- ✅ DO: Use declarative JSON specifications
- ✅ DO: Validate all inputs with Pydantic
- ✅ DO: Clamp values to safe ranges
- ✅ DO: Use fixed sets of allowed operators
- ❌ DON'T: Execute model-generated code
- ❌ DON'T: Use `eval()` or `exec()`
- ❌ DON'T: Allow arbitrary file system access
- ❌ DON'T: Accept unconstrained parameters

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass: `pytest tests/`
6. Commit with clear messages
7. Push to your fork
8. Open a pull request

## Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] All functions have type hints
- [ ] New features have tests
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] No security vulnerabilities introduced
- [ ] Determinism is maintained (same spec = same output)

## Questions?

Open an issue for:
- Bug reports
- Feature requests
- Questions about the codebase
- Clarification on contribution guidelines

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
