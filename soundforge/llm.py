"""LLM integration for generating SoundSpec from prompts."""

import os
import json
from typing import Optional
from soundforge.schema import SoundSpec
from soundforge.presets import get_default_pickup

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


SYSTEM_PROMPT = """You are a sound design AI. Output ONLY valid JSON matching this EXACT schema:

{
  "version": "soundspec-1",
  "name": "sound_name",
  "description": "Brief description",
  "sample_rate": 44100,
  "duration": 0.5,
  "seed": 42,
  "global": {"amp": 0.8, "normalize": true},
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
  "params": [
    {"id": "freq", "label": "Frequency", "kind": "slider", "min": 200.0, "max": 2000.0, "step": 10.0, "default": 440.0, "path": "layers_by_id.main.osc.freq"}
  ]
}

CRITICAL: Match layer type to its params:
- type "osc" → "osc": {"waveform": "sine", "freq": 440.0, "detune": 0.0}
- type "chirp" → "chirp": {"waveform": "saw", "f_start": 1000.0, "f_end": 200.0, "curve": "exponential", "vibrato_hz": 0.0, "vibrato_depth": 0.0}
- type "fm" → "fm": {"carrier_freq": 440.0, "mod_freq": 220.0, "index": 5.0, "brightness": 0.5}
- type "noise" → "noise": {"color": "white"}
- type "impulse" → "impulse": {"kind": "click", "width": 0.005}

ALL layers MUST have: id, type, amp, pan, phase, env
Output ONLY the JSON."""


def generate_soundspec(prompt: str, style: Optional[str] = None) -> SoundSpec:
    """
    Generate a SoundSpec from a natural language prompt.
    
    Args:
        prompt: User's description of the desired sound
        style: Optional style hint (pickup, laser, explosion, etc.)
    
    Returns:
        A validated SoundSpec object
    """
    api_key = os.environ.get('OPENAI_API_KEY')
    
    if not api_key:
        print("Warning: OPENAI_API_KEY not set, using mock generator")
        return _mock_generator(prompt, style)
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        user_prompt = prompt
        if style:
            user_prompt = f"Style: {style}\n{prompt}"
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if content.startswith('```'):
            lines = content.split('\n')
            content = '\n'.join(lines[1:-1]) if len(lines) > 2 else content
            if content.startswith('json'):
                content = content[4:].strip()
        
        # Parse and validate
        spec_dict = json.loads(content)
        
        # Debug: print the received JSON
        print(f"Received JSON keys: {spec_dict.keys()}")
        if 'layers' in spec_dict and spec_dict['layers']:
            print(f"First layer type: {spec_dict['layers'][0].get('type')}")
            print(f"First layer keys: {spec_dict['layers'][0].keys()}")
        
        spec = SoundSpec.model_validate(spec_dict)
        return spec
        
    except Exception as e:
        print(f"Error generating SoundSpec: {e}")
        return _mock_generator(prompt, style)


def _mock_generator(prompt: str, style: Optional[str]) -> SoundSpec:
    """Fallback mock generator when OpenAI API is unavailable."""
    # Return a reasonable default based on keywords
    prompt_lower = prompt.lower()
    
    if 'laser' in prompt_lower:
        return _create_laser_spec()
    elif 'explosion' in prompt_lower or 'boom' in prompt_lower:
        return _create_explosion_spec()
    elif 'shield' in prompt_lower or 'deflect' in prompt_lower:
        return _create_shield_spec()
    else:
        # Default to gentle pickup
        return get_default_pickup()


def _create_laser_spec() -> SoundSpec:
    """Create a laser sound spec."""
    return SoundSpec.model_validate({
        "version": "soundspec-1",
        "name": "laser_blast",
        "description": "Descending laser blast",
        "sample_rate": 44100,
        "duration": 0.4,
        "seed": 42,
        "global": {"amp": 0.8, "normalize": True},
        "layers": [
            {
                "id": "main",
                "type": "chirp",
                "amp": 0.9,
                "pan": 0.0,
                "phase": 0.0,
                "env": {"attack": 0.01, "decay": 0.3, "shape": "exp"},
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
                "enabled": True,
                "params": {"drive": 1.5}
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
            },
            {
                "id": "duration",
                "label": "Duration",
                "kind": "slider",
                "min": 0.1,
                "max": 1.0,
                "step": 0.05,
                "default": 0.4,
                "path": "duration"
            }
        ]
    })


def _create_explosion_spec() -> SoundSpec:
    """Create an explosion sound spec."""
    return SoundSpec.model_validate({
        "version": "soundspec-1",
        "name": "explosion",
        "description": "Explosion with rumble",
        "sample_rate": 44100,
        "duration": 1.2,
        "seed": 123,
        "global": {"amp": 0.85, "normalize": True},
        "layers": [
            {
                "id": "rumble",
                "type": "osc",
                "amp": 0.6,
                "pan": 0.0,
                "phase": 0.0,
                "env": {"attack": 0.01, "decay": 0.8, "shape": "exp"},
                "osc": {"waveform": "sine", "freq": 60.0, "detune": 0.0},
                "filter": [
                    {"type": "biquad_lp", "cutoff": 800.0, "cutoff_end": 100.0, "curve": "exponential", "q": 0.707}
                ]
            },
            {
                "id": "crack",
                "type": "noise",
                "amp": 0.8,
                "pan": 0.0,
                "phase": 0.0,
                "env": {"attack": 0.001, "decay": 0.15, "shape": "exp"},
                "noise": {"color": "white", "cutoff_start": 8000.0, "cutoff_end": 2000.0, "cutoff_curve": "exponential"}
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
            },
            {
                "id": "crack_amp",
                "label": "Crack Intensity",
                "kind": "slider",
                "min": 0.0,
                "max": 1.0,
                "step": 0.05,
                "default": 0.8,
                "path": "layers_by_id.crack.amp"
            }
        ]
    })


def _create_shield_spec() -> SoundSpec:
    """Create a shield deflection sound spec."""
    return SoundSpec.model_validate({
        "version": "soundspec-1",
        "name": "shield_deflect",
        "description": "Shield deflection with ring",
        "sample_rate": 44100,
        "duration": 0.6,
        "seed": 789,
        "global": {"amp": 0.75, "normalize": True},
        "layers": [
            {
                "id": "ping",
                "type": "impulse",
                "amp": 0.7,
                "pan": 0.0,
                "phase": 0.0,
                "env": {"attack": 0.001, "decay": 0.3, "shape": "exp"},
                "impulse": {"kind": "metal_ping", "width": 0.005, "tone_freq": 1800.0}
            },
            {
                "id": "shimmer",
                "type": "fm",
                "amp": 0.5,
                "pan": 0.0,
                "phase": 0.0,
                "env": {"attack": 0.05, "decay": 0.4, "shape": "exp"},
                "fm": {"carrier_freq": 2400.0, "mod_freq": 7.0, "index": 3.0, "brightness": 0.6}
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
            },
            {
                "id": "shimmer_brightness",
                "label": "Shimmer Brightness",
                "kind": "slider",
                "min": 0.0,
                "max": 1.0,
                "step": 0.05,
                "default": 0.6,
                "path": "layers_by_id.shimmer.fm.brightness"
            }
        ]
    })
