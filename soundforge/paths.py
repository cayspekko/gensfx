"""Parameter path resolver for updating SoundSpec values."""

import re
from typing import Any
from soundforge.schema import SoundSpec


def update_spec_from_param(spec: SoundSpec, path: str, value: Any) -> bool:
    """
    Update a SoundSpec field using a JSONPath-like path.
    
    Supported paths:
    - global.amp
    - duration
    - layers[0].amp
    - layers_by_id.main.amp
    - fx[0].params.drive
    - fx_by_type.softclip.params.drive
    
    Returns True if update succeeded, False otherwise.
    """
    try:
        # Check for array notation before splitting
        if '[' in path:
            # Handle paths like "layers[0].amp" or "fx[0].enabled"
            match = re.match(r'(\w+)\[(\d+)\]\.?(.*)', path)
            if match:
                prefix, index, remainder = match.groups()
                if prefix == 'layers':
                    idx = int(index)
                    if idx >= len(spec.layers):
                        return False
                    layer = spec.layers[idx]
                    if not remainder:
                        return False
                    return _update_layer_field(layer, remainder.split('.'), value)
                elif prefix == 'fx':
                    idx = int(index)
                    if idx >= len(spec.fx_chain):
                        return False
                    fx = spec.fx_chain[idx]
                    if not remainder:
                        return False
                    return _update_fx_field(fx, remainder.split('.'), value)
        
        # Normal dot-separated paths
        parts = path.split('.')
        
        if parts[0] == 'global':
            return _update_global(spec, parts[1:], value)
        elif parts[0] == 'duration':
            spec.duration = float(value)
            return True
        elif parts[0] == 'layers_by_id':
            return _update_layers_by_id(spec, parts[1:], value)
        elif parts[0] == 'fx_by_type':
            return _update_fx_by_type(spec, parts[1:], value)
        
        return False
    except Exception:
        return False


def _update_global(spec: SoundSpec, parts: list[str], value: Any) -> bool:
    """Update global settings."""
    if not parts:
        return False
    
    field = parts[0]
    if field == 'amp':
        spec.global_.amp = float(value)
        return True
    elif field == 'normalize':
        spec.global_.normalize = bool(value)
        return True
    
    return False



def _update_layers_by_id(spec: SoundSpec, parts: list[str], value: Any) -> bool:
    """Update layer by ID."""
    if not parts:
        return False
    
    layer_id = parts[0]
    layer = next((l for l in spec.layers if l.id == layer_id), None)
    if not layer:
        return False
    
    return _update_layer_field(layer, parts[1:], value)


def _update_layer_field(layer, parts: list[str], value: Any) -> bool:
    """Update a field within a layer."""
    if not parts:
        return False
    
    field = parts[0]
    
    # Direct layer fields
    if field == 'amp':
        layer.amp = float(value)
        return True
    elif field == 'pan':
        layer.pan = float(value)
        return True
    elif field == 'phase':
        layer.phase = float(value)
        return True
    
    # Nested type-specific params
    if len(parts) < 2:
        return False
    
    subfield = parts[1]
    
    if field == 'osc' and layer.osc:
        return _update_osc_field(layer.osc, subfield, value)
    elif field == 'chirp' and layer.chirp:
        return _update_chirp_field(layer.chirp, subfield, value)
    elif field == 'fm' and layer.fm:
        return _update_fm_field(layer.fm, subfield, value)
    elif field == 'noise' and layer.noise:
        return _update_noise_field(layer.noise, subfield, value)
    elif field == 'impulse' and layer.impulse:
        return _update_impulse_field(layer.impulse, subfield, value)
    elif field == 'env':
        return _update_env_field(layer.env, subfield, value)
    elif field == 'mod' and layer.mod:
        return _update_mod_field(layer.mod, subfield, value)
    
    return False


def _update_osc_field(osc, field: str, value: Any) -> bool:
    """Update oscillator field."""
    if field == 'freq':
        osc.freq = float(value)
        return True
    elif field == 'detune':
        osc.detune = float(value)
        return True
    elif field == 'waveform':
        osc.waveform = value
        return True
    return False


def _update_chirp_field(chirp, field: str, value: Any) -> bool:
    """Update chirp field."""
    if field == 'f_start':
        chirp.f_start = float(value)
        return True
    elif field == 'f_end':
        chirp.f_end = float(value)
        return True
    elif field == 'vibrato_hz':
        chirp.vibrato_hz = float(value)
        return True
    elif field == 'vibrato_depth':
        chirp.vibrato_depth = float(value)
        return True
    elif field == 'waveform':
        chirp.waveform = value
        return True
    return False


def _update_fm_field(fm, field: str, value: Any) -> bool:
    """Update FM field."""
    if field == 'carrier_freq':
        fm.carrier_freq = float(value)
        return True
    elif field == 'mod_freq':
        fm.mod_freq = float(value)
        return True
    elif field == 'index':
        fm.index = float(value)
        return True
    elif field == 'brightness':
        fm.brightness = float(value)
        return True
    return False


def _update_noise_field(noise, field: str, value: Any) -> bool:
    """Update noise field."""
    if field == 'cutoff_start':
        noise.cutoff_start = float(value)
        return True
    elif field == 'cutoff_end':
        noise.cutoff_end = float(value)
        return True
    return False


def _update_impulse_field(impulse, field: str, value: Any) -> bool:
    """Update impulse field."""
    if field == 'width':
        impulse.width = float(value)
        return True
    elif field == 'tone_freq' and impulse.tone_freq is not None:
        impulse.tone_freq = float(value)
        return True
    return False


def _update_env_field(env, field: str, value: Any) -> bool:
    """Update envelope field."""
    if field == 'attack':
        env.attack = float(value)
        return True
    elif field == 'decay':
        env.decay = float(value)
        return True
    elif field == 'sustain':
        env.sustain = float(value)
        return True
    elif field == 'release':
        env.release = float(value)
        return True
    return False


def _update_mod_field(mod, field: str, value: Any) -> bool:
    """Update modulation field."""
    if field == 'tremolo_hz':
        mod.tremolo_hz = float(value)
        return True
    elif field == 'tremolo_depth':
        mod.tremolo_depth = float(value)
        return True
    elif field == 'pitch_lfo_hz':
        mod.pitch_lfo_hz = float(value)
        return True
    elif field == 'pitch_lfo_depth':
        mod.pitch_lfo_depth = float(value)
        return True
    return False



def _update_fx_by_type(spec: SoundSpec, parts: list[str], value: Any) -> bool:
    """Update FX by type."""
    if not parts:
        return False
    
    fx_type = parts[0]
    fx = next((f for f in spec.fx_chain if f.type.value == fx_type), None)
    if not fx:
        return False
    
    return _update_fx_field(fx, parts[1:], value)


def _update_fx_field(fx, parts: list[str], value: Any) -> bool:
    """Update FX field."""
    if not parts:
        return False
    
    if parts[0] == 'enabled':
        fx.enabled = bool(value)
        return True
    
    if parts[0] == 'params' and len(parts) > 1:
        field = parts[1]
        if field == 'drive':
            fx.params.drive = float(value)
            return True
        elif field == 'steps':
            fx.params.steps = int(value)
            return True
        elif field == 'hold_samples':
            fx.params.hold_samples = int(value)
            return True
        elif field == 'time_ms':
            fx.params.time_ms = float(value)
            return True
        elif field == 'feedback':
            fx.params.feedback = float(value)
            return True
        elif field == 'mix':
            fx.params.mix = float(value)
            return True
        elif field == 'target_peak':
            fx.params.target_peak = float(value)
            return True
    
    return False
