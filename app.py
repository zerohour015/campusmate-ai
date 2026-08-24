import os
import json
import re
import streamlit as st
import urllib.parse
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader

# Initialize session state
if "syllabus_topics" not in st.session_state:
    st.session_state["syllabus_topics"] = ""

# ==============================
# STUDY PROGRESS
# ==============================

if "quiz_history" not in st.session_state:
    st.session_state.quiz_history = []

if "total_questions" not in st.session_state:
    st.session_state.total_questions = 0

if "correct_answers" not in st.session_state:
    st.session_state.correct_answers = 0
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

ask_tab, study_tab, notice_tab, learn_tab, progress_tab = st.tabs(
    [
        "💬 Ask CampusMate",
        "📚 Study Tools",
        "📌 Notice Mode",
        "🧠 Learn & Practice",
        "📊 Progress"
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
                        model="gemini-3.5-flash-lite",
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
                        model="gemini-3.5-flash-lite",
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
                        model="gemini-3.5-flash-lite",
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
                    model="gemini-3.5-flash-lite",
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
                    model="gemini-3.5-flash-lite",
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
            # =====================================================
    # YOUTUBE LEARNING
    # =====================================================

# =========================================================
# LEARN & PRACTICE
# =========================================================

with learn_tab:

    st.subheader("🎓 Learn & Practice")

    st.write(
        "Learn each topic using YouTube resources and "
        "test your understanding with an AI-generated quiz."
    )

    # =====================================================
    # ANALYZE SYLLABUS
    # =====================================================

    if st.button(
        "🔍 Analyze My Syllabus",
        use_container_width=True
    ):

        topic_prompt = f"""
You are an expert college academic advisor.

Read the ENTIRE uploaded syllabus carefully.

Identify the actual academic subjects, units and
individual study topics that students need to learn.

Ignore:

- Administrative information
- Dates
- Notices
- Assignments
- Exam schedules
- Faculty information

Return ONLY a clean numbered list of study topics.

Example:

1. C Programming - Arrays
2. C Programming - Pointers
3. Data Structures - Linked Lists
4. Data Structures - Stacks
5. Data Structures - Queues
6. Data Structures - Merge Sort

Respond in {language}.

DOCUMENT:
{pdf_text}
"""

        with st.spinner("🔍 Analyzing your complete syllabus..."):

            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=topic_prompt
            )

        st.session_state["syllabus_topics"] = response.text

        st.success("✅ Syllabus analyzed successfully!")

    # =====================================================
    # SHOW TOPICS
    # =====================================================

    if "syllabus_topics" in st.session_state:

        st.subheader("📚 Topics Found in Your Syllabus")

        st.write(
            st.session_state["syllabus_topics"]
        )

        st.divider()

        # =================================================
        # SELECT TOPIC
        # =================================================

        st.subheader("🎯 Choose What You Want to Study")

# Convert AI-generated syllabus topics into a list
raw_topics = st.session_state.get("syllabus_topics", "")

topics = []

if raw_topics:
    try:
        cleaned = raw_topics.strip()

        # Remove Markdown code fences
        cleaned = re.sub(r"^```json\s*", "", cleaned)
        cleaned = re.sub(r"^```\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

        parsed = json.loads(cleaned)

        if isinstance(parsed, list):
            topics = [
                str(t).strip()
                for t in parsed
                if str(t).strip()
            ]

        elif isinstance(parsed, dict):
            topic_list = parsed.get("topics", [])

            if isinstance(topic_list, list):
                topics = [
                    str(t).strip()
                    for t in topic_list
                    if str(t).strip()
                ]

    except (json.JSONDecodeError, TypeError):
        # Fallback for normal text
        for line in raw_topics.splitlines():
            line = line.strip()

            line = re.sub(
                r'^\s*(?:[-•*]|\d+[.)])\s*',
                '',
                line
            )

            if line and len(line) > 2:
                topics.append(line)

# Remove duplicates
topics = list(dict.fromkeys(topics))
# Remove duplicates while keeping order
topics = list(dict.fromkeys(topics))

if topics:
    topic = st.selectbox(
        "📚 Select a topic to learn and practice",
        topics
    )
else:
    st.warning("No topics could be extracted from the syllabus.")
    topic = ""



        # =================================================
        # LEARNING + QUIZ
        # =================================================

if topic.strip():

            learn_section, quiz_section = st.tabs(
                [
                    "📺 Learn",
                    "🧠 Quiz"
                ]
            )

            # =============================================
            # YOUTUBE LEARNING
            # =============================================

            with learn_section:

                st.subheader(
                    f"📺 Learn: {topic}"
                )

                st.write(
                    "Find suitable YouTube resources "
                    "for this syllabus topic."
                )

                if st.button(
                    "🔎 Find YouTube Resources",
                    use_container_width=True
                ):

                    import urllib.parse

                    searches = [
                        f"{topic} tutorial for college students",
                        f"{topic} complete tutorial",
                        f"{topic} explained",
                        f"{topic} exam preparation"
                    ]

                    st.subheader(
                        "🎥 Recommended YouTube Searches"
                    )

                    for i, search in enumerate(
                        searches,
                        1
                    ):

                        encoded = urllib.parse.quote_plus(
                            search
                        )

                        youtube_url = (
                            "https://www.youtube.com/results"
                            "?search_query="
                            + encoded
                        )

                        st.markdown(
                            f"""
                            ### {i}. {search}

                            [▶️ Search YouTube for this topic]({youtube_url})
                            """
                        )

                    st.success(
                        "Start with the tutorial search, "
                        "then use the exam-preparation search "
                        "for revision."
                    )

            # =============================================
            # QUIZ
            # =============================================

            with quiz_section:

                st.subheader(
                    f"🧠 Quiz: {topic}"
                )

                st.write(
                    "Test your knowledge specifically "
                    "on this syllabus topic."
                )

                difficulty = st.selectbox(
                    "🎚️ Difficulty",
                    [
                        "Easy",
                        "Medium",
                        "Hard"
                    ]
                )

                question_count = st.selectbox(
                    "📝 Number of Questions",
                    [5, 10, 15]
                )

                if st.button(
                    "🚀 Generate Quiz",
                    use_container_width=True
                ):

                    quiz_prompt = f"""
You are CampusMate AI, an expert college
quiz generator.

The student uploaded a college syllabus.

The student selected this topic:

{topic}

Difficulty:

{difficulty}

Create exactly {question_count} multiple-choice
questions ONLY about the selected topic.

IMPORTANT:

1. Questions must be relevant to the topic.
2. Questions should test actual understanding.
3. Do not ask questions about unrelated topics.
4. Use the uploaded syllabus as the academic context.
5. Do not invent syllabus topics.
6. Questions may use general academic knowledge
   needed to test the selected topic.
7. Each question must have exactly 4 options.
8. There must be exactly ONE correct answer.
9. Include a clear explanation for the correct answer.
10. Match the requested difficulty.

Return ONLY valid JSON.

Use exactly this format:

[
  {{
    "question": "Question here",
    "options": [
      "Option A",
      "Option B",
      "Option C",
      "Option D"
    ],
    "answer": 0,
    "explanation": "Explain why this answer is correct."
  }}
]

The answer field must be:

0 = Option A
1 = Option B
2 = Option C
3 = Option D

SELECTED TOPIC:
{topic}

SYLLABUS:
{pdf_text}
"""

                    with st.spinner(
                        "🧠 Creating your quiz..."
                    ):

                        response = client.models.generate_content(
                            model="gemini-3.5-flash-lite",
                            contents=quiz_prompt
                        )

                    try:

                        quiz_text = response.text.strip()

                        if quiz_text.startswith("```"):

                            quiz_text = (
                                quiz_text
                                .replace("```json", "")
                                .replace("```", "")
                                .strip()
                            )

                        quiz_data = json.loads(
                            quiz_text
                        )

                        st.session_state[
                            "current_quiz"
                        ] = quiz_data

                        st.session_state[
                            "quiz_topic"
                        ] = topic

                        st.session_state[
                            "quiz_submitted"
                        ] = False

                        st.success(
                            "✅ Quiz generated!"
                        )

                    except Exception:

                        st.error(
                            "⚠️ I couldn't create the quiz "
                            "in the correct format. "
                            "Please try again."
                        )

                # =========================================
                # DISPLAY QUIZ
                # =========================================

                if "current_quiz" in st.session_state:

                    quiz_data = st.session_state[
                        "current_quiz"
                    ]

                    st.divider()

                    st.subheader(
                        f"📝 {st.session_state['quiz_topic']} Quiz"
                    )

                    st.write(
                        f"Questions: {len(quiz_data)}"
                    )

                    for i, q in enumerate(
                        quiz_data
                    ):

                        st.markdown(
                            f"### Question {i + 1}"
                        )

                        st.write(
                            q["question"]
                        )

                        # Use radio buttons so only
                        # one answer can be selected.

                        st.radio(
                            "Select your answer:",
                            q["options"],
                            key=f"quiz_answer_{i}",
                            index=None
                        )

                        st.write("")

                    # =====================================
                    # SUBMIT QUIZ
                    # =====================================

                    if st.button(
                        "✅ Submit Quiz",
                        use_container_width=True
                    ):

                        score = 0

                        results = []

                        for i, q in enumerate(
                            quiz_data
                        ):

                            selected = st.session_state.get(
                                f"quiz_answer_{i}"
                            )

                            correct = q["options"][
                                q["answer"]
                            ]

                            if selected == correct:

                                score += 1

                                results.append(
                                    {
                                        "correct": True,
                                        "selected": selected,
                                        "correct_answer": correct,
                                        "explanation": q[
                                            "explanation"
                                        ]
                                    }
                                )

                            else:

                                results.append(
                                    {
                                        "correct": False,
                                        "selected": selected,
                                        "correct_answer": correct,
                                        "explanation": q[
                                            "explanation"
                                        ]
                                    }
                                )

                        st.session_state[
                            "quiz_score"
                        ] = score

                        st.session_state[
                            "quiz_results"
                        ] = results

                        st.session_state[
                            "quiz_submitted"
                        ] = True

                        # Save quiz to history
                        st.session_state.quiz_history.append({
                             "topic": 
                        st.session_state["quiz_topic"],
                            "score": score,
                            "total": len(quiz_data),
                            "accuracy": (score / len(quiz_data)) * 100
                        })

                    # =====================================
                    # SHOW SCORE
                    # =====================================

                    if st.session_state.get(
                        "quiz_submitted",
                        False
                    ):

                        score = st.session_state[
                            "quiz_score"
                        ]

                        total = len(
                            quiz_data
                        )

                        percentage = int(
                            (score / total) * 100
                        )

                        st.divider()

                        st.subheader(
                            "🏆 Your Result"
                        )

                        st.metric(
                            "Score",
                            f"{score} / {total}"
                        )

                        st.progress(
                            percentage / 100
                        )

                        st.write(
                            f"### 📊 {percentage}%"
                        )

                        if percentage >= 80:

                            st.success(
                                "🔥 Excellent! "
                                "You understand this topic very well."
                            )

                        elif percentage >= 50:

                            st.warning(
                                "👍 Good attempt! "
                                "Revise the incorrect questions."
                            )

                        else:

                            st.error(
                                "📚 You should revise this topic "
                                "before attempting the quiz again."
                            )

                        # =================================
                        # EXPLANATIONS
                        # =================================

                        st.divider()

                        st.subheader(
                            "📖 Answer Review"
                        )

                        results = st.session_state[
                            "quiz_results"
                        ]

                        for i, result in enumerate(
                            results
                        ):

                            if result["correct"]:

                                st.success(
                                    f"Question {i + 1} — ✅ Correct"
                                )

                            else:

                                st.error(
                                    f"Question {i + 1} — ❌ Incorrect"
                                )

                                st.write(
                                    "**Your answer:** "
                                    + str(
                                        result["selected"]
                                    )
                                    if result["selected"]
                                    else
                                    "**Your answer:** Not answered"
                                )

                                st.write(
                                    "**Correct answer:** "
                                    + result[
                                        "correct_answer"
                                    ]
                                )

                                st.info(
                                    "💡 **Why?** "
                                    + result[
                                        "explanation"
                                    ]
                                )
# =====================================================
# NO PDF UPLOADED
# =====================================================
# ==========================================
# PROGRESS TAB
# ==========================================

with progress_tab:

    st.subheader("📊 Your Study Progress")

    total_questions = st.session_state.total_questions
    correct_answers = st.session_state.correct_answers

    if total_questions > 0:
        accuracy = (correct_answers / total_questions) * 100
    else:
        accuracy = 0
best_score = 0

if st.session_state.quiz_history:
    best_score = max(
        quiz["accuracy"]
        for quiz in st.session_state.quiz_history
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "📝 Questions Attempted",
            total_questions
        )

    with col2:
        st.metric(
            "✅ Correct Answers",
            correct_answers
        )

    with col3:
        st.metric(
            "🎯 Accuracy",
            f"{accuracy:.1f}%"
        )

    with col4:
        st.metric(
            "🏆 Best Score",
            f"{best_score:.1f}%"
        )

    st.divider()

    st.subheader("🏆 Quiz History")

if st.session_state.quiz_history:
    for quiz in reversed(st.session_state.quiz_history):

        accuracy = quiz["accuracy"]

        if accuracy >= 80:
            status = "🟢 Excellent"
        elif accuracy >= 50:
            status = "🟡 Needs Practice"
        else:
            status = "🔴 Needs Revision"

        st.markdown(
            f"""
            ### 📘 {quiz['topic']}

            **Score:** {quiz['score']}/{quiz['total']}  
            **Accuracy:** {accuracy:.1f}%  
            **Performance:** {status}
            """
        )

        st.divider()

else:
    st.info(
        "Complete your first quiz to see your progress here."
    )


if not uploaded_file:

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