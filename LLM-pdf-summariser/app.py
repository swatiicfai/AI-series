import streamlit as st
import os
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai_api_key)

st.set_page_config(page_title="PDF Summarizer", layout="centered")
st.title("📄 Notebook LLM Summarizer")

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text

def summarize_text_with_openai(text):
    prompt = f"Summarize the following PDF content in clear, concise bullet points:\n\n{text}"
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or "gpt-3.5-turbo"
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error: {str(e)}"

uploaded_file = st.file_uploader("Upload your PDF file", type="pdf")

if uploaded_file is not None:
    st.success("✅ PDF uploaded successfully!")
    with st.spinner("🔍 Extracting text..."):
        raw_text = extract_text_from_pdf(uploaded_file)

    if raw_text:
        st.subheader("📑 Extracted Text (Preview)")
        st.text_area("PDF Text", raw_text[:1000] + "...", height=200)

        if st.button("📝 Generate Summary"):
            with st.spinner("Generating summary using OpenAI..."):
                summary = summarize_text_with_openai(raw_text)
                st.subheader("📌 Summary")
                st.write(summary)
    else:
        st.error("❌ Failed to extract any text from the PDF.")
