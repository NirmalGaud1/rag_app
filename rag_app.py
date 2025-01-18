#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import os
import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# Configure Google Gemini API key
genai.configure(api_key="AIzaSyA-9-lTQTWdNM43YdOXMQwGKDy0SrMwo6c")

# Function to read the PDF file
def read_pdf(file_path):
    """Reads the text from a PDF file."""
    with open(file_path, 'rb') as file:
        reader = PdfReader(file)
        text = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

# Function to query the Gemini LLM with preloaded context (CAG)
def query_with_cag(context: str, query: str) -> str:
    """
    Query the Gemini LLM with preloaded context using Cache-Augmented Generation.
    """
    prompt = f"Context:\n{context}\n\nQuery: {query}\nAnswer:"
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()

# Streamlit app interface
st.title("RAG Application with Google Gemini - by Nirmal Gaud")
st.header("Upload a PDF and Ask Your Query")

# Step 1: Ask the user to upload a PDF file
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
    st.session_state.pdf_text = None

uploaded_file = st.file_uploader("Please upload a PDF file", type="pdf")

if uploaded_file is not None:
    # Ensure the directory exists
    temp_dir = "temp"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # Save the uploaded file to a temporary location
    temp_file_path = os.path.join(temp_dir, uploaded_file.name)
    
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Step 2: Extract text from the uploaded PDF
    pdf_text = read_pdf(temp_file_path)
    st.session_state.uploaded_file = uploaded_file
    st.session_state.pdf_text = pdf_text

    # Step 3: Show a preview of the content of the PDF (optional)
    st.text_area("PDF Content Preview", value=pdf_text[:1000], height=150)

    # Step 4: Ask if the user wants to continue with the current file or upload a new one
    continue_or_upload = st.radio("Do you want to continue or upload a new file?", 
                                 ("Continue", "Upload New File"))

    if continue_or_upload == "Upload New File":
        st.session_state.uploaded_file = None
        st.session_state.pdf_text = None
        st.experimental_rerun()  # Restart app to upload a new file

    # Step 5: Ask the user to enter a query based on the uploaded PDF
    if st.session_state.uploaded_file is not None:
        query = st.text_input("Ask a question based on the content of the PDF:")

        if query:
            # Step 6: Get the answer from Gemini LLM with the context of the PDF
            response = query_with_cag(st.session_state.pdf_text, query)
            st.write("Answer:", response)
