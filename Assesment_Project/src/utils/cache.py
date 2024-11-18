import streamlit as st
from typing import Any

def cache_data(key: str, data: Any) -> None:
    st.session_state[f"cache_{key}"] = data

def get_cached_data(key: str) -> Any:
    return st.session_state.get(f"cache_{key}")
