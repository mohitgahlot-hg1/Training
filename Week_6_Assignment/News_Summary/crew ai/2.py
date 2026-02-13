import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
 
load_dotenv()
gemini_key = os.getenv("GEMINI_API_KEY")
if not gemini_key:
    raise EnvironmentError("GEMINI_API_KEY not set")
 
# Pick a supported model your account has access to:
gemini_llm = LLM(
    model="gemini/gemini-2.5-flash",     # or "gemini/gemini-2.0-flash"
    api_key=gemini_key,
    temperature=0.2,
)
 
researcher = Agent(
    role="AI Researcher",
    goal="Find credible, recent AI trends and summarize them with citations.",
    backstory="You analyze reputable sources and write concise summaries.",
    llm=gemini_llm,                    # important: bind Gemini, avoid OpenAI default
    verbose=True,
)
 
research_task = Task(
    description="Identify the top 3 AI trends in 2024 using reputable online sources.",
    expected_output=(
        "A numbered list of the top 3 trends in 2024. For each: "
        "• Trend name • 2–3 sentence summary • 1–2 source links"
    ),
    agent=researcher,
    verbose=True,
)
 
crew = Crew(agents=[researcher], tasks=[research_task], verbose=True)
 
if __name__ == "__main__":
    # Newer CrewAI uses kickoff()/kickoff_async()
    result = crew.kickoff(inputs={"format_hint": "Use markdown bullets and clickable links."})
    print(result)
 