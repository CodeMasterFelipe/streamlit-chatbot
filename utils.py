import streamlit as st


def load_css(filename):
    with open(filename) as f:
        return st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
