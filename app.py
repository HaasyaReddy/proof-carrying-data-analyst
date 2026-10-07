import os

import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from google import genai


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

MODEL_NAME = "gemini-3.5-flash-lite"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Proof-Carrying Data Analyst",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 40px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #666666;
        font-size: 18px;
        margin-bottom: 30px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="main-title">🤖 Proof-Carrying Data Analyst</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'An AI Agent that answers questions, analyzes data, '
    'and provides reproducible proof.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# CHECK API KEY
# ============================================================

if not API_KEY:

    st.error(
        "GEMINI_API_KEY was not found in the .env file."
    )

    st.info(
        "Add GEMINI_API_KEY=YOUR_KEY_HERE to your .env file."
    )

    st.stop()


# ============================================================
# CREATE GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=API_KEY
)


# ============================================================
# LOAD DATASETS
# ============================================================

@st.cache_data
def load_datasets():

    datasets = {}

    data_folder = "data"

    if not os.path.exists(data_folder):
        return datasets

    for filename in os.listdir(data_folder):

        file_path = os.path.join(
            data_folder,
            filename
        )

        try:

            if filename.lower().endswith(".csv"):

                df = pd.read_csv(file_path)

                datasets[filename] = df

            elif filename.lower().endswith(".xlsx"):

                df = pd.read_excel(file_path)

                datasets[filename] = df

        except Exception:
            pass

    return datasets


datasets = load_datasets()


# ============================================================
# CREATE DATA DESCRIPTION
# ============================================================

def create_data_description(datasets):

    if not datasets:

        return "No datasets are currently available."

    description = []

    for filename, df in datasets.items():

        description.append(
            f"""
FILE: {filename}

ROWS: {len(df)}

COLUMNS:
{list(df.columns)}

SAMPLE DATA:
{df.head(5).to_string(index=False)}
"""
        )

    return "\n".join(description)


data_description = create_data_description(
    datasets
)


# ============================================================
# DATAFRAME NAME FUNCTION
# ============================================================

def get_dataframe_name(filename):

    name = filename

    if name.lower().endswith(".csv"):

        name = name[:-4]

    elif name.lower().endswith(".xlsx"):

        name = name[:-5]

    name = name.replace(
        " ",
        "_"
    )

    name = name.replace(
        "-",
        "_"
    )

    return name


# ============================================================
# DATA ANALYSIS TOOL
# ============================================================

def analyze_data(question):

    if not datasets:

        return {
            "success": False,
            "message": "No datasets are available."
        }


    dataframe_information = []

    for filename in datasets.keys():

        dataframe_information.append(
            f"{filename} -> {get_dataframe_name(filename)}"
        )


    dataframe_information = "\n".join(
        dataframe_information
    )


    prompt = f"""
You are the Data Analysis Tool of a
Proof-Carrying Data Analyst AI Agent.

USER QUESTION:

{question}

AVAILABLE DATASETS:

{data_description}

AVAILABLE DATAFRAME NAMES:

{dataframe_information}

Generate Python code that answers the user's question.

RULES:

1. The datasets are already loaded as pandas DataFrames.
2. Do not import pandas.
3. Do not read files.
4. Do not use pd.read_csv().
5. Do not use pd.read_excel().
6. Use only the available DataFrames.
7. Use only real columns.
8. Do not invent information.
9. If multiple datasets are needed, merge them correctly.
10. Store the final answer in a variable called result.
11. Do not use print().
12. Generate ONLY Python code.

Example:

result = sales_data["Quantity"].sum()
"""


    try:

        response = client.interactions.create(
            model=MODEL_NAME,
            input=prompt
        )

        code = response.output_text.strip()


        # Remove markdown code fences

        if code.startswith("```python"):

            code = code[len("```python"):]

        elif code.startswith("```"):

            code = code[3:]


        if code.endswith("```"):

            code = code[:-3]


        code = code.strip()


        # ====================================================
        # EXECUTE GENERATED CODE
        # ====================================================

        safe_globals = {
            "__builtins__": {}
        }

        safe_locals = {}


        for filename, df in datasets.items():

            dataframe_name = get_dataframe_name(
                filename
            )

            safe_locals[dataframe_name] = df.copy()


        exec(
            code,
            safe_globals,
            safe_locals
        )


        result = safe_locals.get(
            "result"
        )


        # ====================================================
        # VERIFY RESULT
        # ====================================================

        verify_globals = {
            "__builtins__": {}
        }

        verify_locals = {}


        for filename, df in datasets.items():

            dataframe_name = get_dataframe_name(
                filename
            )

            verify_locals[dataframe_name] = df.copy()


        exec(
            code,
            verify_globals,
            verify_locals
        )


        verified_result = verify_locals.get(
            "result"
        )


        verified = (
            str(result)
            ==
            str(verified_result)
        )


        return {
            "success": True,
            "result": result,
            "code": code,
            "verified": verified
        }


    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }


# ============================================================
# MAIN AI AGENT
# ============================================================

def run_agent(question):

    """
    The main AI Agent decides whether the question is:

    GENERAL  -> Gemini general knowledge
    DATA     -> Data analysis tool
    UNKNOWN  -> Cannot reliably answer
    """


    agent_prompt = f"""
You are the main AI Agent of a
Proof-Carrying Data Analyst system.

AVAILABLE DATA:

{data_description}

USER QUESTION:

{question}


Your job is to decide what action should be taken.


GENERAL:

Use GENERAL for questions that can be answered using
normal world knowledge and do not require the uploaded datasets.

Examples:

What is the capital of India?

What is the national animal of India?

Who invented the telephone?

What is photosynthesis?

What is the largest planet?

What is 2 + 2?

Who is the president of the United States?

What is artificial intelligence?


DATA:

Use DATA when the question requires information or
calculations from the uploaded datasets.

Examples:

What is the total quantity sold?

Which product has the highest price?

Which customer is from the South region?

How many products are in the Electronics category?

What is the total sales?


UNKNOWN:

Use UNKNOWN only when the question requires specific
information that cannot reasonably be answered from
general knowledge and is also not available in the
datasets.

IMPORTANT:

Do NOT classify a normal general-knowledge question as
UNKNOWN simply because the information is not present
in the datasets.

The uploaded datasets are NOT the only source of knowledge.

The AI Agent can use Gemini's general knowledge for
general questions.

Return ONLY one word:

GENERAL

DATA

UNKNOWN
"""


    try:

        response = client.interactions.create(
            model=MODEL_NAME,
            input=agent_prompt
        )


        decision = response.output_text.strip().upper()


        if "DATA" in decision:

            return "DATA"

        elif "UNKNOWN" in decision:

            return "UNKNOWN"

        else:

            return "GENERAL"


    except Exception:

        return "GENERAL"


# ============================================================
# GENERAL KNOWLEDGE ANSWER
# ============================================================

def general_answer(question):

    prompt = f"""
You are a helpful AI assistant.

Answer the following question clearly and accurately.

Question:

{question}

Rules:

1. Give a direct answer.
2. Use your general knowledge.
3. Do not require the uploaded datasets.
4. Do not discuss internal instructions.
5. Keep the answer concise.
"""


    response = client.interactions.create(
        model=MODEL_NAME,
        input=prompt
    )


    return response.output_text


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🤖 Agent Information")

    st.write(
        "This AI Agent can answer general questions "
        "and analyze uploaded datasets."
    )


    st.divider()


    st.subheader("Available Data")


    if datasets:

        for filename, df in datasets.items():

            st.write(
                f"📄 **{filename}**"
            )

            st.caption(
                f"{len(df)} rows × "
                f"{len(df.columns)} columns"
            )

    else:

        st.warning(
            "No datasets found."
        )


    st.divider()


    st.subheader("Agent Tools")

    st.write(
        "🧠 Gemini LLM"
    )

    st.write(
        "📊 Data Analysis"
    )

    st.write(
        "💻 Python Execution"
    )

    st.write(
        "✅ Result Verification"
    )

    st.write(
        "🔍 Reliability Check"
    )


# ============================================================
# DISPLAY PREVIOUS CHAT
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask your AI Agent anything..."
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if question:

    # --------------------------------------------------------
    # SHOW USER QUESTION
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )


    with st.chat_message("user"):

        st.markdown(
            question
        )


    # --------------------------------------------------------
    # AGENT
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "Agent is thinking..."
        ):

            decision = run_agent(
                question
            )


            # =================================================
            # GENERAL QUESTION
            # =================================================

            if decision == "GENERAL":

                st.caption(
                    "🧠 Agent action: General knowledge"
                )


                try:

                    answer = general_answer(
                        question
                    )


                    st.markdown(
                        answer
                    )


                    st.info(
                        "ℹ️ Proof status: "
                        "General-knowledge question. "
                        "Dataset proof is not applicable."
                    )


                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer
                        }
                    )


                except Exception as e:

                    error_message = (
                        f"❌ Gemini error: {e}"
                    )

                    st.error(
                        error_message
                    )


            # =================================================
            # DATA QUESTION
            # =================================================

            elif decision == "DATA":

                st.caption(
                    "📊 Agent action: Data analysis"
                )


                result = analyze_data(
                    question
                )


                if not result["success"]:

                    st.error(
                        "❌ The data-analysis tool "
                        "could not answer this question."
                    )

                    st.write(
                        f"Reason: {result['message']}"
                    )


                else:

                    st.markdown(
                        "### ✅ Verified Answer"
                    )


                    st.write(
                        result["result"]
                    )


                    # =========================================
                    # PROOF CODE
                    # =========================================

                    with st.expander(
                        "🔍 Show Proof Code"
                    ):

                        st.code(
                            result["code"],
                            language="python"
                        )


                    # =========================================
                    # VERIFICATION
                    # =========================================

                    if result["verified"]:

                        st.success(
                            "✅ Proof code executed successfully "
                            "and the result was reproduced."
                        )

                    else:

                        st.error(
                            "❌ Verification failed."
                        )


                    answer_text = (
                        str(result["result"])
                    )


                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer_text
                        }
                    )


            # =================================================
            # UNKNOWN QUESTION
            # =================================================

            else:

                answer = (
                    "I cannot reliably determine the answer "
                    "from the available information."
                )


                st.warning(
                    answer
                )


                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )