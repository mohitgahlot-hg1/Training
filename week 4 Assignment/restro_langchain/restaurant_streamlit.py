import streamlit as st
from transformers import AutoTokenizer, pipeline
from langchain_huggingface import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ---------------------------
# Load Model (Simple)
# ---------------------------
model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

tokenizer = AutoTokenizer.from_pretrained(model_id)

pipe = pipeline(
    "text-generation",
    model=model_id,
    tokenizer=tokenizer,
    max_new_tokens=200,
    temperature=0.3,
    do_sample=True,
    return_full_text=False
)

llm = HuggingFacePipeline(pipeline=pipe)

# ---------------------------
# LangChain Prompt + Chain
# ---------------------------
prompt = PromptTemplate.from_template(
    "<|user|>\nList 5 famous dishes from {country}\n<|assistant|>\n"
)

chain = prompt | llm | StrOutputParser()

# ---------------------------
# Streamlit UI
# ---------------------------
st.title("🍽️ Famous Dishes Generator (TinyLlama + LangChain)")
st.write("Enter any country name and get 5 famous dishes generated locally.")

country = st.text_input("Country Name", "India")

if st.button("Generate"):
    with st.spinner("Generating dishes..."):
        output = chain.invoke({"country": country})
    st.subheader(f"🍲 Famous Dishes from {country}:")
    st.write(output)