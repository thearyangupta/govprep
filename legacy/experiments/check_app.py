import time
import streamlit as st

st.title("My first app") 
st.write("Hello, Aryan!")

name = st.text_input("What's your name?")
if name:
    st.write(f"Nice to meet you, {name}!")

if st.button("Click me"):
    st.write("Button was clicked!")

# st.write(f"Script ran at : {time.strftime('%H:%M:%S')}")