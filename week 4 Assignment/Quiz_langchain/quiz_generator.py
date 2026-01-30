import streamlit as st
from transformers import AutoTokenizer, pipeline
from langchain_huggingface import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# -----------------------------
# Load TinyLlama model
# -----------------------------
MODEL_ID = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

pipe = pipeline(
    "text-generation",
    model=MODEL_ID,
    tokenizer=tokenizer,
    max_new_tokens=250,
    temperature=0.4,
    do_sample=True,
    return_full_text=False
)

llm = HuggingFacePipeline(pipeline=pipe)

# -----------------------------
# LangChain Prompt
# -----------------------------
prompt = PromptTemplate.from_template(
    "<|user|>\n"
    "Generate a quiz on the topic '{topic}' with difficulty '{difficulty}'.\n"
    "Output EXACTLY {num_questions} questions.\n\n"
    "Format rules:\n"
    "- Each question must be numbered.\n"
    "- Each should have 4 options (A, B, C, D)\n"
    "- After all questions, give the answers in this format:\n"
    "Answers: 1-A, 2-C, 3-B, ...\n"
    "<|assistant|>\n"
)

chain = prompt | llm | StrOutputParser()

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🧠 AI-Powered Quiz Generator (TinyLlama + LangChain)")
st.write("Generate high‑quality quiz questions using a local open‑source LLM.")

topic = st.text_input("Enter a topic:", "Python Basics")
difficulty = st.selectbox("Difficulty:", ["Easy", "Medium", "Hard"])
num_questions = st.slider("Number of Questions:", 3, 10, 5)

if st.button("Generate Quiz"):
    with st.spinner("Creating your quiz..."):
        quiz = chain.invoke({
            "topic": topic,
            "difficulty": difficulty,
            "num_questions": num_questions
        })

    st.subheader("📘 Generated Quiz")
    st.text_area("Quiz Output", quiz, height=350)