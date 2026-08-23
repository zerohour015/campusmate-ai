import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader

# =========================================================
# SETUP
# =========================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = None

if not api_key:
    st.error("Gemini API key not found.")
    st.stop()

client = genai.Client(api_key=api_key)

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="CampusMate AI",
    page_icon="🎓",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 18px;
        margin-top: 0;
        opacity: 0.75;
    }

    .feature-card {
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(128,128,128,0.25);
        margin-bottom: 15px;
    }

    .notice-card {
        padding: 25px;
        border-radius: 18px;
        border: 1px solid rgba(128,128,128,0.3);
        margin-top: 20px;
    }

    .small-text {
        font-size: 14px;
        opacity: 0.7;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🎓 CampusMate AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Your AI-powered college information assistant.</div>',
    unsafe_allow_html=True
)

st.write("")

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("⚙️ Settings")

    language = st.selectbox(
        "Response language",
        ["English", "Hinglish", "Hindi"]
    )

    st.divider()

    st.subheader("📚 CampusMate")

    st.write(
        "Upload a college document and use AI "
        "to understand, summarize and study from it."
    )

    st.divider()

    st.caption("Built with Python + Gemini + Streamlit")

# =========================================================
# FILE UPLOAD
# =========================================================

st.subheader("📄 Upload your college document")

uploaded_file = st.file_uploader(
    "Upload a PDF",
    type=["pdf"],
    help="Upload a syllabus, notice, academic calendar, exam schedule, etc."
)

# =========================================================
# PROCESS PDF
# =========================================================

if uploaded_file:

    reader = PdfReader(uploaded_file)

    pdf_text = ""

    for page in reader.pages:

        text = page.extract_text()

        if text:
            pdf_text += text + "\n"

    if not pdf_text.strip():

        st.error(
            "I couldn't extract text from this PDF. "
            "Please upload a text-based PDF."
        )

        st.stop()

    st.success(
        f"✅ {uploaded_file.name} loaded successfully "
        f"({len(reader.pages)} pages)"
    )

    st.divider()

    # =====================================================
    # TABS
    # =====================================================

    ask_tab, study_tab, notice_tab = st.tabs(
        [
            "💬 Ask CampusMate",
            "📚 Study Tools",
            "📌 Notice Mode"
        ]
    )

    # =====================================================
    # ASK TAB
    # =====================================================

    with ask_tab:

        st.subheader("💬 Ask anything about your document")

        question = st.text_area(
            "Your question",
            placeholder="Example: What are the topics in Unit 3?"
        )

        if st.button(
            "Ask CampusMate 🤖",
            use_container_width=True
        ):

            if not question.strip():

                st.warning("Please enter a question.")

            else:

                prompt = f"""
You are CampusMate AI, a college document assistant.

Answer the student's question using ONLY the information
provided in the document.

If the answer cannot be found in the document, say:

"I couldn't find that information in the uploaded document."

Do not invent information.

Respond in {language}.

Keep the answer simple and useful for a college student.

DOCUMENT:
{pdf_text}

QUESTION:
{question}
"""

                with st.spinner("CampusMate is thinking..."):

                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=prompt
                    )

                st.subheader("🤖 Answer")

                st.write(response.text)

    # =====================================================
    # STUDY TAB
    # =====================================================

    with study_tab:

        st.subheader("📚 Study Tools")

        col1, col2 = st.columns(2)

        # -------------------------------------------------
        # SUMMARY
        # -------------------------------------------------

        with col1:

            st.markdown(
                '<div class="feature-card">'
                '<b>📑 Document Summary</b><br>'
                '<span class="small-text">'
                'Turn your document into simple notes.'
                '</span>'
                '</div>',
                unsafe_allow_html=True
            )

            if st.button(
                "Summarize PDF",
                use_container_width=True
            ):

                prompt = f"""
Summarize the following college document.

Respond in {language}.

Create:

1. Main topics
2. Important points
3. Important dates if present
4. Key things students should remember

Use clear headings and bullet points.

DOCUMENT:
{pdf_text}
"""

                with st.spinner("Creating summary..."):

                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=prompt
                    )

                st.subheader("📑 Summary")

                st.write(response.text)

        # -------------------------------------------------
        # QUESTIONS
        # -------------------------------------------------

        with col2:

            st.markdown(
                '<div class="feature-card">'
                '<b>📝 Exam Questions</b><br>'
                '<span class="small-text">'
                'Generate practice questions from your document.'
                '</span>'
                '</div>',
                unsafe_allow_html=True
            )

            if st.button(
                "Generate Questions",
                use_container_width=True
            ):

                prompt = f"""
Create exam preparation questions from this college document.

Respond in {language}.

Generate:

5 MCQs with answers
5 short-answer questions
3 long-answer questions

Use ONLY information from the document.

DOCUMENT:
{pdf_text}
"""

                with st.spinner("Generating questions..."):

                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=prompt
                    )

                st.subheader("📝 Practice Questions")

                st.write(response.text)

        st.write("")

        # -------------------------------------------------
        # IMPORTANT DATES
        # -------------------------------------------------

        if st.button(
            "📅 Find Important Dates",
            use_container_width=True
        ):

            prompt = f"""
Find all important dates from this college document.

Look for:

- Examinations
- Assignment deadlines
- Registration dates
- Events
- Submission deadlines
- Holidays
- Other important dates

For every date provide:

Date:
Event:
Details:

Respond in {language}.

If no dates are found, say so.

DOCUMENT:
{pdf_text}
"""

            with st.spinner("Finding important dates..."):

                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt
                )

            st.subheader("📅 Important Dates")

            st.write(response.text)

    # =====================================================
    # NOTICE MODE
    # =====================================================

    with notice_tab:

        st.subheader("📌 College Notice Mode")

        st.write(
            "Turn a long college notice into a simple "
            "student-friendly announcement."
        )

        if st.button(
            "Analyze This Notice 🚀",
            use_container_width=True
        ):

            notice_prompt = f"""
You are CampusMate AI's College Notice Analyzer.

Analyze the following college notice.

Extract the most important information.

Return the result using exactly these sections:

📌 EVENT
📅 DATE
⏰ TIME
📍 LOCATION
👥 WHO SHOULD ATTEND
⚠️ IMPORTANT
📋 OTHER DETAILS

If a field is not mentioned, write:

Not mentioned

Do not invent information.

Keep the language simple.

NOTICE:

{pdf_text}
"""

            with st.spinner("Analyzing college notice..."):

                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=notice_prompt
                )

            st.markdown(
                '<div class="notice-card">',
                unsafe_allow_html=True
            )

            st.subheader("📌 Notice Summary")

            st.write(response.text)

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )

else:

    st.info(
        "👆 Upload a college PDF above to get started."
    )

    st.divider()

    st.subheader("What can CampusMate do?")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            '<div class="feature-card">'
            '<h3>💬 Ask</h3>'
            'Ask questions about your college documents.'
            '</div>',
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            '<div class="feature-card">'
            '<h3>📚 Study</h3>'
            'Summarize documents and generate exam questions.'
            '</div>',
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            '<div class="feature-card">'
            '<h3>📌 Notices</h3>'
            'Turn long notices into useful information.'
            '</div>',
            unsafe_allow_html=True
        )