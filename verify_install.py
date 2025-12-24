#!/usr/bin/env python3
"""Verify SoundForge installation and generate a test sound."""

import sys
from soundforge import get_default_pickup, render_wav_bytes

def main():
    print("🔊 SoundForge Installation Verification")
    print("=" * 50)
    
    try:
        # Load default preset
        print("\n1. Loading default pickup preset...")
        spec = get_default_pickup()
        print(f"   ✓ Loaded: {spec.name}")
        print(f"   ✓ Duration: {spec.duration}s")
        print(f"   ✓ Layers: {len(spec.layers)}")
        
        # Render audio
        print("\n2. Rendering audio...")
        wav_bytes = render_wav_bytes(spec)
        print(f"   ✓ Generated {len(wav_bytes)} bytes")
        
        # Save to file
        output_file = "test_sound.wav"
        print(f"\n3. Saving to {output_file}...")
        with open(output_file, 'wb') as f:
            f.write(wav_bytes)
        print(f"   ✓ Saved successfully")
        
        print("\n" + "=" * 50)
        print("✅ Installation verified successfully!")
        print(f"\nYou can now:")
        print(f"  - Play {output_file} to hear the test sound")
        print(f"  - Run 'streamlit run app.py' to start the app")
        print(f"  - Run 'pytest tests/' to run the test suite")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease ensure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
