# pdf_gemini_embed.py
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from crewai_tools import PDFSearchTool
 
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise EnvironmentError("Set GEMINI_API_KEY in .env")
 
# 1) Build a Gemini TEXT LLM for your agent (not for embeddings)
gemini_llm = LLM(
    model="gemini/gemini-2.5-flash",  # text-only, free-tier friendly
    api_key=GEMINI_API_KEY,
    temperature=0.2,
    max_tokens=700,
)
 
# 2) Configure PDFSearchTool to use Google Generative AI for embeddings + ChromaDB
pdf_tool = PDFSearchTool(
    pdf=r"C:\Users\Mohit.gahlot\Desktop\crew ai\financial_report_15_pages 2.pdf",  # <-- correct param name is 'pdf'
    config={
        "embedding_model": {
            "provider": "google-generativeai",
            "config": {
                # Example model name for Gemini embeddings:
                # docs reference 'gemini-embedding-001'
                "model": "gemini-embedding-001"
            }
        },
        "vectordb": {
            "provider": "chromadb",
            "config": {
                # optional: where to persist your local index
                "persist_directory": "./pdf_index"
            }
        }
    }
)
 
analyst = Agent(
    role="Financial Analyst",
    goal="Extract revenue trends from the report.",
    backstory="An expert at analyzing financial documents.",
    tools=[pdf_tool],
    llm=gemini_llm,
    verbose=True
)
 
task = Task(
    description="Read the attached PDF and summarize the revenue trends.",
    expected_output="A short summary of revenue numbers and patterns with page references if possible.",
    agent=analyst,
    verbose=True
)
 
crew = Crew(agents=[analyst], tasks=[task], verbose=True)
print(crew.kickoff())
