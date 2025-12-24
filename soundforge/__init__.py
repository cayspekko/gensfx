"""SoundForge - Safe game SFX generation using structured JSON."""

from soundforge.schema import SoundSpec, export_json_schema
from soundforge.renderer import render_wav_bytes, render_samples
from soundforge.llm import generate_soundspec
from soundforge.presets import get_default_pickup, get_all_presets
from soundforge.paths import update_spec_from_param

__version__ = "1.0.0"

__all__ = [
    "SoundSpec",
    "export_json_schema",
    "render_wav_bytes",
    "render_samples",
    "generate_soundspec",
    "get_default_pickup",
    "get_all_presets",
    "update_spec_from_param",
]
