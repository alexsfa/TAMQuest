import streamlit as st
from supabase import create_client


def main():
    role = st.selectbox("Login as", ["User", "Admin"])
    if role == "User":
        st.write("Hello, *World!* :sunglasses:")
    else: 
        st.write("Hello")
        
if __name__ == "__main__":
    main()