# Proof-Carrying Data Analyst
## Reliability-Aware Proof-Carrying Data Analyst using Agentic GenAI

### HackNex 2026 – PSI08

A reliability-aware AI data analyst that answers questions about messy, real-world data and provides executable verification code along with numerical answers.

The system is designed to reduce incorrect or unsupported numerical answers by analyzing the available data, generating Python code for calculations, executing the code, and presenting the result together with its proof.

---

## 1. Problem Statement

Real-world data is often messy and may contain:

- Duplicate records
- Missing values
- Conflicting information
- Multiple tables
- Incorrect or inconsistent data
- Ambiguous questions
- Insufficient information

A normal AI system may confidently provide an incorrect numerical answer.

This project addresses this problem by building a **Proof-Carrying Data Analyst** that verifies numerical results before presenting them to the user.

---

## 2. What the Project Does

The system allows a user to ask questions about the provided datasets.

The agent:

1. Receives the user's question.
2. Understands whether the question requires data analysis.
3. Inspects the available datasets.
4. Detects possible data-quality problems.
5. Generates Python/Pandas analysis code.
6. Executes the generated code.
7. Verifies the calculated result.
8. Provides the final answer along with executable proof code.
9. Refuses to provide a confident answer when the available evidence is insufficient or unreliable.

---

## 3. Key Features

### AI-Powered Data Analysis

The system uses an AI model to understand natural-language questions and determine the required analysis.

### Multi-Table Data Handling

The project supports multiple CSV datasets and can use the available data for analysis.

### Data Quality Checking

The system checks for issues such as:

- Duplicate rows
- Duplicate IDs
- Missing values
- Potentially unreliable data

### Proof-Carrying Answers

Numerical answers are accompanied by Python code that can be executed to reproduce the calculation.

### Verification

The generated code is executed and the result is checked before presenting the answer.

### Reliability-Aware Refusal

When the system cannot reliably determine an answer, it can indicate that the available data is insufficient or unreliable instead of producing a confident unsupported answer.

---

## 4. Technologies Used

- **Python** – Core programming language
- **Streamlit** – Web interface
- **Pandas** – Data loading, processing and analysis
- **Python Code Execution** – Execution of generated analytical code
- **AI/LLM Model** – Natural-language understanding and analysis planning
- **CSV** – Dataset format

---

## 5. Project Structure

```text
proof-carrying-data-analyst/
│
├── data/
│   ├── customers.csv
│   ├── products.csv
│   └── sales_data.csv
│
├── app.py
├── data_analyzer.py
├── requirements.txt
├── README.md
└── .gitignore
