"""SoundForge Streamlit App - Generate game SFX from text prompts."""

import streamlit as st
import json
from soundforge import (
    SoundSpec,
    generate_soundspec,
    render_wav_bytes,
    update_spec_from_param,
    get_default_pickup
)

st.set_page_config(
    page_title="SoundForge",
    page_icon="🔊",
    layout="wide"
)

# Initialize session state
if 'current_spec' not in st.session_state:
    st.session_state.current_spec = None
if 'current_wav' not in st.session_state:
    st.session_state.current_wav = None
if 'history' not in st.session_state:
    st.session_state.history = []
if 'auto_render' not in st.session_state:
    st.session_state.auto_render = False


def render_current_spec():
    """Render the current spec to WAV."""
    if st.session_state.current_spec:
        try:
            st.session_state.current_wav = render_wav_bytes(st.session_state.current_spec)
        except Exception as e:
            st.error(f"Rendering error: {e}")
            st.session_state.current_wav = None


def add_to_history(spec: SoundSpec):
    """Add a spec to history."""
    st.session_state.history.insert(0, spec)
    if len(st.session_state.history) > 10:
        st.session_state.history.pop()


# Header
st.title("🔊 SoundForge")
st.markdown("Generate game sound effects from natural language prompts using safe, structured JSON.")

# Sidebar
with st.sidebar:
    st.header("Settings")
    st.session_state.auto_render = st.checkbox("Auto-render on parameter change", value=st.session_state.auto_render)
    
    st.divider()
    st.header("History")
    
    if st.session_state.history:
        for i, spec in enumerate(st.session_state.history):
            if st.button(f"{i+1}. {spec.name}", key=f"history_{i}"):
                st.session_state.current_spec = spec
                render_current_spec()
                st.rerun()
    else:
        st.info("No history yet")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Generate Sound")
    
    # Prompt input
    prompt = st.text_area(
        "Describe the sound you want:",
        placeholder="e.g., gentle sparkly diamond pickup, soft rising tone",
        height=100
    )
    
    # Style selector
    style = st.selectbox(
        "Style (optional):",
        ["", "pickup", "laser", "explosion", "hit", "shield", "hurt", "ui"]
    )
    
    # Generate button
    if st.button("🎵 Generate", type="primary", use_container_width=True):
        if prompt:
            with st.spinner("Generating SoundSpec..."):
                try:
                    spec = generate_soundspec(prompt, style if style else None)
                    st.session_state.current_spec = spec
                    add_to_history(spec)
                    render_current_spec()
                    st.success(f"Generated: {spec.name}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Generation error: {e}")
        else:
            st.warning("Please enter a prompt")
    
    # Load default button
    if st.button("Load Default Pickup"):
        st.session_state.current_spec = get_default_pickup()
        render_current_spec()
        st.rerun()

with col2:
    st.header("Quick Info")
    if st.session_state.current_spec:
        spec = st.session_state.current_spec
        st.metric("Name", spec.name)
        st.metric("Duration", f"{spec.duration:.2f}s")
        st.metric("Layers", len(spec.layers))
        st.metric("Sample Rate", f"{spec.sample_rate} Hz")
    else:
        st.info("Generate or load a sound to see details")

# Dynamic parameters
if st.session_state.current_spec and st.session_state.current_spec.params:
    st.divider()
    st.header("🎛️ Tweak Parameters")
    
    spec = st.session_state.current_spec
    param_cols = st.columns(min(3, len(spec.params)))
    
    for i, param in enumerate(spec.params):
        col_idx = i % len(param_cols)
        with param_cols[col_idx]:
            if param.kind == "slider":
                value = st.slider(
                    param.label,
                    min_value=param.min,
                    max_value=param.max,
                    value=param.default if param.default is not None else param.min,
                    step=param.step,
                    key=f"param_{param.id}"
                )
                if update_spec_from_param(spec, param.path, value):
                    if st.session_state.auto_render:
                        render_current_spec()
            
            elif param.kind == "select":
                value = st.selectbox(
                    param.label,
                    options=param.options,
                    index=param.options.index(param.default) if param.default in param.options else 0,
                    key=f"param_{param.id}"
                )
                if update_spec_from_param(spec, param.path, value):
                    if st.session_state.auto_render:
                        render_current_spec()
            
            elif param.kind == "checkbox":
                value = st.checkbox(
                    param.label,
                    value=param.default if param.default is not None else False,
                    key=f"param_{param.id}"
                )
                if update_spec_from_param(spec, param.path, value):
                    if st.session_state.auto_render:
                        render_current_spec()

# Render/Play section
if st.session_state.current_spec:
    st.divider()
    st.header("🎵 Render & Play")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🔄 Render/Update", use_container_width=True):
            render_current_spec()
            st.rerun()
    
    with col2:
        if st.session_state.current_wav:
            st.download_button(
                "💾 Download WAV",
                data=st.session_state.current_wav,
                file_name=f"{st.session_state.current_spec.name}.wav",
                mime="audio/wav",
                use_container_width=True
            )
    
    # Audio player
    if st.session_state.current_wav:
        st.audio(st.session_state.current_wav, format="audio/wav")
    else:
        st.info("Click 'Render/Update' to generate audio")
    
    # Expandable sections
    with st.expander("📄 View SoundSpec JSON"):
        spec_json = st.session_state.current_spec.model_dump(by_alias=True, mode='json')
        st.json(spec_json)
        
        st.download_button(
            "💾 Download JSON",
            data=json.dumps(spec_json, indent=2),
            file_name=f"{st.session_state.current_spec.name}.json",
            mime="application/json"
        )
    
    with st.expander("🔍 Layer Details"):
        for layer in st.session_state.current_spec.layers:
            st.subheader(f"Layer: {layer.id}")
            st.write(f"Type: {layer.type}")
            st.write(f"Amplitude: {layer.amp}")
            st.write(f"Envelope: attack={layer.env.attack}s, decay={layer.env.decay}s, shape={layer.env.shape}")

# Footer
st.divider()
st.markdown("""
**SoundForge** - Safe game SFX generation using structured JSON.  
No arbitrary code execution. Only validated SoundSpec JSON.  
[GitHub](https://github.com/yourusername/soundforge) | [Docs](https://github.com/yourusername/soundforge#readme)
""")
