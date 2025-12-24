"""Audio synthesis and rendering engine."""

import math
import random
from typing import List
from soundforge.schema import (
    SoundSpec, Layer, LayerType, Waveform, Curve, NoiseColor,
    ImpulseKind, EnvelopeShape, FilterType, FXType, Filter
)
from soundforge.util_wav import encode_wav


def render_wav_bytes(spec: SoundSpec) -> bytes:
    """Render a SoundSpec to WAV file bytes."""
    samples = render_samples(spec)
    return encode_wav(samples, spec.sample_rate)


def render_samples(spec: SoundSpec) -> List[float]:
    """Render a SoundSpec to float samples."""
    num_samples = int(spec.duration * spec.sample_rate)
    samples = [0.0] * num_samples
    
    # Initialize PRNG with seed
    rng = random.Random(spec.seed)
    
    # Render each layer
    for layer in spec.layers:
        layer_samples = render_layer(layer, spec.duration, spec.sample_rate, rng)
        # Mix layer into output
        for i in range(min(len(samples), len(layer_samples))):
            samples[i] += layer_samples[i]
    
    # Apply global amplitude
    for i in range(len(samples)):
        samples[i] *= spec.global_.amp
    
    # Apply FX chain
    for fx in spec.fx_chain:
        if fx.enabled:
            samples = apply_fx(samples, fx, spec.sample_rate)
    
    # Global normalize if enabled
    if spec.global_.normalize:
        samples = normalize_samples(samples, 0.95)
    
    return samples


def render_layer(layer: Layer, duration: float, sample_rate: int, rng: random.Random) -> List[float]:
    """Render a single layer."""
    num_samples = int(duration * sample_rate)
    
    # Generate base signal
    if layer.type == LayerType.OSC:
        samples = render_osc(layer, num_samples, sample_rate, rng)
    elif layer.type == LayerType.CHIRP:
        samples = render_chirp(layer, num_samples, sample_rate, rng)
    elif layer.type == LayerType.FM:
        samples = render_fm(layer, num_samples, sample_rate, rng)
    elif layer.type == LayerType.NOISE:
        samples = render_noise(layer, num_samples, sample_rate, rng)
    elif layer.type == LayerType.IMPULSE:
        samples = render_impulse(layer, num_samples, sample_rate, rng)
    else:
        samples = [0.0] * num_samples
    
    # Apply modulation
    if layer.mod:
        samples = apply_modulation(samples, layer.mod, sample_rate)
    
    # Apply filters
    if layer.filter:
        for filt in layer.filter:
            samples = apply_filter(samples, filt, sample_rate)
    
    # Apply envelope
    samples = apply_envelope(samples, layer.env, sample_rate, duration)
    
    # Apply layer amplitude
    for i in range(len(samples)):
        samples[i] *= layer.amp
    
    return samples


def render_osc(layer: Layer, num_samples: int, sample_rate: int, rng: random.Random) -> List[float]:
    """Render oscillator."""
    osc = layer.osc
    samples = [0.0] * num_samples
    freq = osc.freq * (2.0 ** (osc.detune / 1200.0))
    phase = layer.phase
    
    for i in range(num_samples):
        t = i / sample_rate
        phase_rad = 2.0 * math.pi * freq * t + phase
        samples[i] = generate_waveform(osc.waveform, phase_rad)
        
        # Add harmonics
        if osc.harmonics:
            for harm in osc.harmonics:
                harm_phase = phase_rad * harm.mul
                samples[i] += generate_waveform(osc.waveform, harm_phase) * harm.amp
    
    return samples


def render_chirp(layer: Layer, num_samples: int, sample_rate: int, rng: random.Random) -> List[float]:
    """Render chirp (frequency sweep)."""
    chirp = layer.chirp
    samples = [0.0] * num_samples
    phase = layer.phase
    
    for i in range(num_samples):
        t = i / sample_rate
        duration = num_samples / sample_rate
        
        # Calculate instantaneous frequency
        if chirp.curve == Curve.LINEAR:
            freq = chirp.f_start + (chirp.f_end - chirp.f_start) * (t / duration)
        else:  # EXPONENTIAL
            ratio = chirp.f_end / chirp.f_start
            freq = chirp.f_start * (ratio ** (t / duration))
        
        # Add vibrato
        if chirp.vibrato_hz > 0:
            vibrato = math.sin(2.0 * math.pi * chirp.vibrato_hz * t)
            freq *= (1.0 + vibrato * chirp.vibrato_depth)
        
        phase_rad = phase
        phase += 2.0 * math.pi * freq / sample_rate
        
        samples[i] = generate_waveform(chirp.waveform, phase_rad)
        
        # Add harmonics
        if chirp.harmonics:
            for harm in chirp.harmonics:
                samples[i] += generate_waveform(chirp.waveform, phase_rad * harm.mul) * harm.amp
    
    return samples


def render_fm(layer: Layer, num_samples: int, sample_rate: int, rng: random.Random) -> List[float]:
    """Render FM synthesis."""
    fm = layer.fm
    samples = [0.0] * num_samples
    
    for i in range(num_samples):
        t = i / sample_rate
        # Modulator
        mod_phase = 2.0 * math.pi * fm.mod_freq * t
        modulator = math.sin(mod_phase) * fm.index
        # Carrier with modulation
        carrier_phase = 2.0 * math.pi * fm.carrier_freq * t + modulator
        samples[i] = math.sin(carrier_phase + layer.phase)
        
        # Apply brightness (subtle softclip)
        if fm.brightness > 0.5:
            drive = 1.0 + (fm.brightness - 0.5) * 2.0
            samples[i] = softclip(samples[i] * drive)
    
    return samples


def render_noise(layer: Layer, num_samples: int, sample_rate: int, rng: random.Random) -> List[float]:
    """Render noise."""
    noise = layer.noise
    samples = [0.0] * num_samples
    
    if noise.color == NoiseColor.WHITE:
        for i in range(num_samples):
            samples[i] = rng.uniform(-1.0, 1.0)
    else:  # PINK - simple approximation
        b0 = b1 = b2 = b3 = b4 = b5 = b6 = 0.0
        for i in range(num_samples):
            white = rng.uniform(-1.0, 1.0)
            b0 = 0.99886 * b0 + white * 0.0555179
            b1 = 0.99332 * b1 + white * 0.0750759
            b2 = 0.96900 * b2 + white * 0.1538520
            b3 = 0.86650 * b3 + white * 0.3104856
            b4 = 0.55000 * b4 + white * 0.5329522
            b5 = -0.7616 * b5 - white * 0.0168980
            samples[i] = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362) * 0.11
            b6 = white * 0.115926
    
    # Apply cutoff sweep if specified
    if noise.cutoff_start is not None:
        cutoff_end = noise.cutoff_end if noise.cutoff_end is not None else noise.cutoff_start
        filt = Filter(
            type=FilterType.BIQUAD_LP,
            cutoff=noise.cutoff_start,
            cutoff_end=cutoff_end,
            curve=noise.cutoff_curve
        )
        samples = apply_filter(samples, filt, sample_rate)
    
    return samples


def render_impulse(layer: Layer, num_samples: int, sample_rate: int, rng: random.Random) -> List[float]:
    """Render impulse."""
    imp = layer.impulse
    samples = [0.0] * num_samples
    width_samples = int(imp.width * sample_rate)
    
    if imp.kind == ImpulseKind.CLICK:
        for i in range(min(width_samples, num_samples)):
            samples[i] = math.exp(-i / (width_samples * 0.3))
    elif imp.kind == ImpulseKind.TAP:
        for i in range(min(width_samples, num_samples)):
            samples[i] = (1.0 - i / width_samples) * (rng.random() * 0.3 + 0.7)
    elif imp.kind == ImpulseKind.METAL_PING:
        freq = imp.tone_freq if imp.tone_freq else 2000.0
        for i in range(min(width_samples * 10, num_samples)):
            t = i / sample_rate
            env = math.exp(-t / imp.width)
            # Inharmonic partials
            tone = math.sin(2.0 * math.pi * freq * t)
            tone += 0.5 * math.sin(2.0 * math.pi * freq * 2.3 * t)
            tone += 0.3 * math.sin(2.0 * math.pi * freq * 3.7 * t)
            samples[i] = tone * env
    
    return samples


def generate_waveform(waveform: Waveform, phase: float) -> float:
    """Generate a single sample of a waveform."""
    phase = phase % (2.0 * math.pi)
    
    if waveform == Waveform.SINE:
        return math.sin(phase)
    elif waveform == Waveform.TRIANGLE:
        return 2.0 * abs(2.0 * (phase / (2.0 * math.pi) - 0.5)) - 1.0
    elif waveform == Waveform.SQUARE:
        return 1.0 if phase < math.pi else -1.0
    elif waveform == Waveform.SAW:
        return 2.0 * (phase / (2.0 * math.pi)) - 1.0
    return 0.0


def apply_envelope(samples: List[float], env, sample_rate: int, duration: float) -> List[float]:
    """Apply envelope to samples."""
    num_samples = len(samples)
    result = samples[:]
    
    for i in range(num_samples):
        t = i / sample_rate
        amp = 1.0
        
        if env.shape == EnvelopeShape.EXP:
            # Exponential attack and decay
            if t < env.attack:
                amp = t / env.attack
            amp *= math.exp(-t / env.decay)
        elif env.shape == EnvelopeShape.LIN:
            # Linear attack and decay
            if t < env.attack:
                amp = t / env.attack
            else:
                decay_t = t - env.attack
                amp = max(0.0, 1.0 - decay_t / env.decay)
        elif env.shape == EnvelopeShape.ADSR:
            # ADSR envelope
            sustain_level = env.sustain if env.sustain is not None else 0.5
            release_time = env.release if env.release is not None else 0.1
            release_start = duration - release_time
            
            if t < env.attack:
                amp = t / env.attack
            elif t < env.attack + env.decay:
                decay_t = t - env.attack
                amp = 1.0 - (1.0 - sustain_level) * (decay_t / env.decay)
            elif t < release_start:
                amp = sustain_level
            else:
                release_t = t - release_start
                amp = sustain_level * (1.0 - release_t / release_time)
        
        result[i] *= max(0.0, amp)
    
    return result


def apply_modulation(samples: List[float], mod, sample_rate: int) -> List[float]:
    """Apply modulation (tremolo, pitch LFO)."""
    result = samples[:]
    
    for i in range(len(samples)):
        t = i / sample_rate
        amp_mod = 1.0
        
        # Tremolo (amplitude modulation)
        if mod.tremolo_hz > 0:
            tremolo = math.sin(2.0 * math.pi * mod.tremolo_hz * t)
            amp_mod *= 1.0 - mod.tremolo_depth * (tremolo + 1.0) / 2.0
        
        result[i] *= amp_mod
    
    # Note: pitch_lfo would require phase modulation during synthesis
    # For simplicity, we skip it here (would need refactoring)
    
    return result


def apply_filter(samples: List[float], filt: Filter, sample_rate: int) -> List[float]:
    """Apply filter to samples."""
    if filt.type == FilterType.LP1:
        return apply_onepole_lp(samples, filt, sample_rate)
    elif filt.type == FilterType.HP1:
        return apply_onepole_hp(samples, filt, sample_rate)
    else:
        return apply_biquad(samples, filt, sample_rate)


def apply_onepole_lp(samples: List[float], filt: Filter, sample_rate: int) -> List[float]:
    """Apply one-pole lowpass filter."""
    result = [0.0] * len(samples)
    y_prev = 0.0
    
    for i in range(len(samples)):
        # Calculate cutoff (with sweep if specified)
        if filt.cutoff_end is not None:
            t = i / len(samples)
            if filt.curve == Curve.LINEAR:
                cutoff = filt.cutoff + (filt.cutoff_end - filt.cutoff) * t
            else:
                ratio = filt.cutoff_end / filt.cutoff
                cutoff = filt.cutoff * (ratio ** t)
        else:
            cutoff = filt.cutoff
        
        # One-pole coefficient
        rc = 1.0 / (2.0 * math.pi * cutoff)
        dt = 1.0 / sample_rate
        alpha = dt / (rc + dt)
        
        y = alpha * samples[i] + (1.0 - alpha) * y_prev
        result[i] = y
        y_prev = y
    
    return result


def apply_onepole_hp(samples: List[float], filt: Filter, sample_rate: int) -> List[float]:
    """Apply one-pole highpass filter."""
    result = [0.0] * len(samples)
    y_prev = 0.0
    x_prev = 0.0
    
    for i in range(len(samples)):
        if filt.cutoff_end is not None:
            t = i / len(samples)
            if filt.curve == Curve.LINEAR:
                cutoff = filt.cutoff + (filt.cutoff_end - filt.cutoff) * t
            else:
                ratio = filt.cutoff_end / filt.cutoff
                cutoff = filt.cutoff * (ratio ** t)
        else:
            cutoff = filt.cutoff
        
        rc = 1.0 / (2.0 * math.pi * cutoff)
        dt = 1.0 / sample_rate
        alpha = rc / (rc + dt)
        
        y = alpha * (y_prev + samples[i] - x_prev)
        result[i] = y
        y_prev = y
        x_prev = samples[i]
    
    return result


def apply_biquad(samples: List[float], filt: Filter, sample_rate: int) -> List[float]:
    """Apply biquad filter (RBJ cookbook)."""
    result = [0.0] * len(samples)
    x1 = x2 = y1 = y2 = 0.0
    
    for i in range(len(samples)):
        if filt.cutoff_end is not None:
            t = i / len(samples)
            if filt.curve == Curve.LINEAR:
                cutoff = filt.cutoff + (filt.cutoff_end - filt.cutoff) * t
            else:
                ratio = filt.cutoff_end / filt.cutoff
                cutoff = filt.cutoff * (ratio ** t)
        else:
            cutoff = filt.cutoff
        
        # Calculate biquad coefficients
        w0 = 2.0 * math.pi * cutoff / sample_rate
        cos_w0 = math.cos(w0)
        sin_w0 = math.sin(w0)
        alpha = sin_w0 / (2.0 * filt.q)
        
        if filt.type == FilterType.BIQUAD_LP:
            b0 = (1.0 - cos_w0) / 2.0
            b1 = 1.0 - cos_w0
            b2 = (1.0 - cos_w0) / 2.0
            a0 = 1.0 + alpha
            a1 = -2.0 * cos_w0
            a2 = 1.0 - alpha
        elif filt.type == FilterType.BIQUAD_HP:
            b0 = (1.0 + cos_w0) / 2.0
            b1 = -(1.0 + cos_w0)
            b2 = (1.0 + cos_w0) / 2.0
            a0 = 1.0 + alpha
            a1 = -2.0 * cos_w0
            a2 = 1.0 - alpha
        elif filt.type == FilterType.BIQUAD_BP:
            b0 = alpha
            b1 = 0.0
            b2 = -alpha
            a0 = 1.0 + alpha
            a1 = -2.0 * cos_w0
            a2 = 1.0 - alpha
        else:  # NOTCH
            b0 = 1.0
            b1 = -2.0 * cos_w0
            b2 = 1.0
            a0 = 1.0 + alpha
            a1 = -2.0 * cos_w0
            a2 = 1.0 - alpha
        
        # Normalize
        b0 /= a0
        b1 /= a0
        b2 /= a0
        a1 /= a0
        a2 /= a0
        
        # Apply filter
        y = b0 * samples[i] + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        result[i] = y
        
        x2 = x1
        x1 = samples[i]
        y2 = y1
        y1 = y
    
    return result


def apply_fx(samples: List[float], fx, sample_rate: int) -> List[float]:
    """Apply an effect."""
    if fx.type == FXType.SOFTCLIP:
        return apply_softclip(samples, fx.params.drive)
    elif fx.type == FXType.BITCRUSH:
        return apply_bitcrush(samples, fx.params.steps, fx.params.hold_samples)
    elif fx.type == FXType.DELAY:
        return apply_delay(samples, fx.params.time_ms, fx.params.feedback, fx.params.mix, sample_rate)
    elif fx.type == FXType.NORMALIZE:
        return normalize_samples(samples, fx.params.target_peak)
    return samples


def apply_softclip(samples: List[float], drive: float) -> List[float]:
    """Apply soft clipping distortion."""
    result = []
    for s in samples:
        x = s * drive
        result.append(softclip(x))
    return result


def softclip(x: float) -> float:
    """Soft clipping function."""
    if x > 1.0:
        return 1.0
    elif x < -1.0:
        return -1.0
    else:
        return x - (x ** 3) / 3.0


def apply_bitcrush(samples: List[float], steps: int, hold_samples: int) -> List[float]:
    """Apply bitcrusher effect."""
    result = []
    held_value = 0.0
    
    for i, s in enumerate(samples):
        if i % hold_samples == 0:
            # Quantize
            if steps > 0:
                quantized = round(s * steps) / steps
            else:
                quantized = s
            held_value = quantized
        result.append(held_value)
    
    return result


def apply_delay(samples: List[float], time_ms: float, feedback: float, mix: float, sample_rate: int) -> List[float]:
    """Apply delay effect."""
    delay_samples = int(time_ms * sample_rate / 1000.0)
    buffer = [0.0] * delay_samples
    result = []
    
    for s in samples:
        delayed = buffer[0]
        output = s + delayed * mix
        buffer.append(s + delayed * feedback)
        buffer.pop(0)
        result.append(output)
    
    return result


def normalize_samples(samples: List[float], target_peak: float) -> List[float]:
    """Normalize samples to target peak."""
    peak = max(abs(s) for s in samples)
    if peak > 0.0:
        gain = target_peak / peak
        return [s * gain for s in samples]
    return samples
