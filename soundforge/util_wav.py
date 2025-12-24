"""WAV file encoding utilities."""

import struct
import io


def float_to_pcm16(samples: list[float]) -> bytes:
    """Convert float samples in [-1, 1] to 16-bit PCM."""
    pcm_data = bytearray()
    for sample in samples:
        # Clamp to [-1, 1]
        sample = max(-1.0, min(1.0, sample))
        # Convert to 16-bit signed integer
        pcm_value = int(sample * 32767)
        pcm_data.extend(struct.pack('<h', pcm_value))
    return bytes(pcm_data)


def encode_wav(samples: list[float], sample_rate: int) -> bytes:
    """Encode float samples as WAV file bytes (mono, 16-bit PCM)."""
    pcm_data = float_to_pcm16(samples)
    num_samples = len(samples)
    num_channels = 1
    bits_per_sample = 16
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8
    data_size = len(pcm_data)
    
    # Build WAV file
    wav = io.BytesIO()
    
    # RIFF header
    wav.write(b'RIFF')
    wav.write(struct.pack('<I', 36 + data_size))
    wav.write(b'WAVE')
    
    # fmt chunk
    wav.write(b'fmt ')
    wav.write(struct.pack('<I', 16))  # Chunk size
    wav.write(struct.pack('<H', 1))   # Audio format (PCM)
    wav.write(struct.pack('<H', num_channels))
    wav.write(struct.pack('<I', sample_rate))
    wav.write(struct.pack('<I', byte_rate))
    wav.write(struct.pack('<H', block_align))
    wav.write(struct.pack('<H', bits_per_sample))
    
    # data chunk
    wav.write(b'data')
    wav.write(struct.pack('<I', data_size))
    wav.write(pcm_data)
    
    return wav.getvalue()
