"""SoundSpec JSON schema and validation using Pydantic."""

from enum import Enum
from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


class Waveform(str, Enum):
    SINE = "sine"
    TRIANGLE = "triangle"
    SQUARE = "square"
    SAW = "saw"


class Curve(str, Enum):
    LINEAR = "linear"
    EXPONENTIAL = "exponential"


class NoiseColor(str, Enum):
    WHITE = "white"
    PINK = "pink"


class ImpulseKind(str, Enum):
    CLICK = "click"
    TAP = "tap"
    METAL_PING = "metal_ping"


class EnvelopeShape(str, Enum):
    EXP = "exp"
    LIN = "lin"
    ADSR = "adsr"


class FilterType(str, Enum):
    LP1 = "lp1"
    HP1 = "hp1"
    BIQUAD_LP = "biquad_lp"
    BIQUAD_HP = "biquad_hp"
    BIQUAD_BP = "biquad_bp"
    NOTCH = "notch"


class FXType(str, Enum):
    SOFTCLIP = "softclip"
    BITCRUSH = "bitcrush"
    DELAY = "delay"
    NORMALIZE = "normalize"


class LayerType(str, Enum):
    OSC = "osc"
    CHIRP = "chirp"
    FM = "fm"
    NOISE = "noise"
    IMPULSE = "impulse"


class ParamKind(str, Enum):
    SLIDER = "slider"
    SELECT = "select"
    CHECKBOX = "checkbox"


class Harmonic(BaseModel):
    mul: float = Field(ge=1.0, le=10.0)
    amp: float = Field(ge=0.0, le=1.0)


class Envelope(BaseModel):
    attack: float = Field(ge=0.0, le=0.2)
    decay: float = Field(ge=0.001, le=2.0)
    sustain: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    release: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    shape: EnvelopeShape = EnvelopeShape.EXP


class Modulation(BaseModel):
    tremolo_hz: float = Field(default=0.0, ge=0.0, le=30.0)
    tremolo_depth: float = Field(default=0.0, ge=0.0, le=0.8)
    pitch_lfo_hz: float = Field(default=0.0, ge=0.0, le=30.0)
    pitch_lfo_depth: float = Field(default=0.0, ge=0.0, le=0.10)


class Filter(BaseModel):
    type: FilterType
    cutoff: float = Field(ge=20.0, le=20000.0)
    q: float = Field(default=0.707, ge=0.1, le=10.0)
    cutoff_end: Optional[float] = Field(default=None, ge=20.0, le=20000.0)
    curve: Curve = Curve.LINEAR


class OscParams(BaseModel):
    waveform: Waveform
    freq: float = Field(ge=20.0, le=20000.0)
    detune: float = Field(default=0.0, ge=-50.0, le=50.0)
    harmonics: Optional[List[Harmonic]] = Field(default=None, max_length=8)


class ChirpParams(BaseModel):
    waveform: Waveform
    f_start: float = Field(ge=20.0, le=20000.0)
    f_end: float = Field(ge=20.0, le=20000.0)
    curve: Curve = Curve.EXPONENTIAL
    vibrato_hz: float = Field(default=0.0, ge=0.0, le=40.0)
    vibrato_depth: float = Field(default=0.0, ge=0.0, le=0.10)
    harmonics: Optional[List[Harmonic]] = Field(default=None, max_length=8)


class FMParams(BaseModel):
    carrier_freq: float = Field(ge=20.0, le=20000.0)
    mod_freq: float = Field(ge=1.0, le=20000.0)
    index: float = Field(ge=0.0, le=20.0)
    waveform: Literal["sine"] = "sine"
    brightness: float = Field(default=0.5, ge=0.0, le=1.0)


class NoiseParams(BaseModel):
    color: NoiseColor
    cutoff_start: Optional[float] = Field(default=None, ge=50.0, le=20000.0)
    cutoff_end: Optional[float] = Field(default=None, ge=50.0, le=20000.0)
    cutoff_curve: Curve = Curve.LINEAR


class ImpulseParams(BaseModel):
    kind: ImpulseKind
    width: float = Field(ge=0.0002, le=0.02)
    tone_freq: Optional[float] = Field(default=None, ge=20.0, le=20000.0)


class Layer(BaseModel):
    id: str
    type: LayerType
    amp: float = Field(ge=0.0, le=1.0)
    pan: float = Field(default=0.0, ge=-1.0, le=1.0)
    env: Envelope
    mod: Optional[Modulation] = None
    filter: Optional[List[Filter]] = Field(default=None, max_length=4)
    phase: float = Field(default=0.0, ge=0.0, le=6.283185307179586)
    
    # Type-specific params
    osc: Optional[OscParams] = None
    chirp: Optional[ChirpParams] = None
    fm: Optional[FMParams] = None
    noise: Optional[NoiseParams] = None
    impulse: Optional[ImpulseParams] = None

    @model_validator(mode='after')
    def check_type_params(self):
        type_map = {
            LayerType.OSC: 'osc',
            LayerType.CHIRP: 'chirp',
            LayerType.FM: 'fm',
            LayerType.NOISE: 'noise',
            LayerType.IMPULSE: 'impulse'
        }
        required_field = type_map[self.type]
        if getattr(self, required_field) is None:
            raise ValueError(f"Layer type '{self.type}' requires '{required_field}' params")
        return self


class FXParams(BaseModel):
    # Softclip
    drive: Optional[float] = Field(default=None, ge=0.0, le=4.0)
    # Bitcrush
    steps: Optional[int] = Field(default=None, ge=0, le=1024)
    hold_samples: Optional[int] = Field(default=None, ge=1, le=64)
    # Delay
    time_ms: Optional[float] = Field(default=None, ge=5.0, le=200.0)
    feedback: Optional[float] = Field(default=None, ge=0.0, le=0.85)
    mix: Optional[float] = Field(default=None, ge=0.0, le=0.7)
    # Normalize
    target_peak: Optional[float] = Field(default=None, ge=0.1, le=0.99)


class FX(BaseModel):
    type: FXType
    enabled: bool = True
    params: FXParams


class Param(BaseModel):
    id: str
    label: str
    kind: ParamKind
    path: str
    # Slider
    min: Optional[float] = None
    max: Optional[float] = None
    step: Optional[float] = None
    default: Optional[Union[float, bool, str]] = None
    # Select
    options: Optional[List[str]] = None


class GlobalSettings(BaseModel):
    amp: float = Field(ge=0.0, le=1.0)
    normalize: bool = False


class SoundSpec(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    version: Literal["soundspec-1"] = "soundspec-1"
    name: str
    description: str
    sample_rate: Literal[22050, 44100, 48000]
    duration: float = Field(ge=0.03, le=3.0)
    seed: int = Field(ge=0, le=2147483647)
    global_: GlobalSettings = Field(alias="global")
    layers: List[Layer] = Field(min_length=1, max_length=16)
    fx_chain: List[FX] = Field(default_factory=list, max_length=8)
    params: List[Param] = Field(default_factory=list, max_length=24)

    @field_validator('layers')
    @classmethod
    def check_unique_layer_ids(cls, v):
        ids = [layer.id for layer in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Layer IDs must be unique")
        return v

    @field_validator('params')
    @classmethod
    def check_unique_param_ids(cls, v):
        ids = [param.id for param in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Param IDs must be unique")
        return v


def export_json_schema() -> dict:
    """Export the JSON schema for SoundSpec."""
    return SoundSpec.model_json_schema()
