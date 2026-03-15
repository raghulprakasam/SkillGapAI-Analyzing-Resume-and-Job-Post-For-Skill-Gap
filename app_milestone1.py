import streamlit as st
import docx2txt
import PyPDF2
import re
import io # Import io for creating in-memory buffers

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="SkillGapAI - Milestone 1", layout="wide")

st.markdown(
    """
    <h2 style='color:white; background-color:#1E3D59; padding:15px; border-radius:10px'>
    🧠 SkillGapAI - Milestone 1: Data Ingestion & Parsing
    </h2>
    <p><b>Objective:</b> Build a system to upload resumes and job descriptions, extract and clean text, 
    preview parsed content, and download the cleaned data.</p>
    """,
    unsafe_allow_html=True
)

# ------------------------------------------
# FUNCTIONS
# ------------------------------------------
def clean_text(text: str) -> str:
    """Normalize text by removing extra spaces and line breaks"""
    # Replace all whitespace characters (including newlines) with a single space
    text = re.sub(r'\s+', ' ', text)
    # The redundant replace calls are removed since re.sub handles them
    return text.strip()

@st.cache_data(show_spinner=False)
def extract_text(uploaded_file):
    """
    Extract plain text from PDF, DOCX, or TXT using a binary buffer.
    Caching improves performance when the file remains the same.
    """
    text = ""
    file_name = uploaded_file.name.lower()
    
    # Read the file's content into a BytesIO buffer for consistent processing
    file_buffer = io.BytesIO(uploaded_file.read())
    file_buffer.seek(0) # Ensure the pointer is at the start for reliable reading
    
    try:
        if file_name.endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(file_buffer)
            for page in pdf_reader.pages:
                content = page.extract_text()
                if content:
                    text += content + "\n"
                    
        elif file_name.endswith(".docx"):
            # docx2txt can process the memory buffer directly
            text = docx2txt.process(file_buffer)
            
        elif file_name.endswith(".txt"):
            # For TXT, decode the binary content of the buffer
            text = file_buffer.read().decode("utf-8")
            
        else:
            st.error("❌ Unsupported file format.")
            return ""
            
        return clean_text(text)
        
    except Exception as e:
        st.error(f"⚠️ Error extracting text: {e}")
        st.exception(e) # Display the detailed exception for debugging
        return ""

# ------------------------------------------
# LAYOUT
# ------------------------------------------
col1, col2 = st.columns([1.1, 2])

with col1:
    st.markdown("### 📤 Upload Resume or Job Description File")
    uploaded_file = st.file_uploader(
        "Choose a file (PDF, DOCX, TXT)",
        type=["pdf", "docx", "txt"]
    )
    st.info("Supported formats: PDF • DOCX • TXT")

with col2:
    st.markdown("### 🧾 Parsed Document Preview")

    if uploaded_file:
        # Pass the uploaded file object to the cached function
        with st.spinner("🔍 Extracting and cleaning text..."):
            extracted_text = extract_text(uploaded_file)
            
        if extracted_text:
            st.success(f"✅ Successfully parsed: {uploaded_file.name}")

            # Preview parsed data
            st.text_area("Extracted & Cleaned Text", extracted_text[:4000], height=350)
            word_count = len(extracted_text.split())
            st.caption(f"Characters: {len(extracted_text)} | Words: {word_count}")

            # --- Download Parsed Data ---
            st.download_button(
                label="💾 Download Parsed Text",
                data=extracted_text,
                file_name=f"parsed_{uploaded_file.name.split('.')[0]}.txt",
                mime="text/plain"
            )
        else:
            st.error("Extraction failed or file was empty. Check the file content.")
    else:
        st.warning("Upload a file to see and download the parsed text preview here.")

# ------------------------------------------
# MANUAL JOB DESCRIPTION SECTION
# ------------------------------------------
st.markdown("---")
st.subheader("📋 Paste Job Description (Optional)")

jd_text = st.text_area("Paste Job Description here:", "", height=200)

if jd_text:
    cleaned_jd = clean_text(jd_text)
    st.text_area("Cleaned Job Description Output", cleaned_jd, height=200)
    st.caption(f"Characters: {len(cleaned_jd)} | Words: {len(cleaned_jd.split())}")
    
    # Allow download of JD text as well
    st.download_button(
        label="💾 Download Cleaned Job Description",
        data=cleaned_jd,
        file_name="cleaned_job_description.txt",
        mime="text/plain"
    )

# ------------------------------------------
# FOOTER
# ------------------------------------------
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:gray;'>Milestone 1 • Data Ingestion & Parsing • SkillGapAI Project • Developed by Suriya Varshan</p>",
    unsafe_allow_html=True
)
