import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM

load_dotenv()

# --- THE FIX ---
# Use "gemini/gemini-1.5-flash" (The provider prefix is essential)
# If flash fails, try "gemini/gemini-1.5-pro"
gemini_llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.5
)

# --- Agents ---
researcher = Agent(
    role="AI Researcher",
    goal="Find 3 major AI breakthroughs of 2024.",
    backstory="Expert at distilling tech research into facts.",
    llm=gemini_llm,
    verbose=True
)

writer = Agent(
    role="Technical Writer",
    goal="Draft an engaging blog post.",
    backstory="Specialist in making tech trends accessible.",
    llm=gemini_llm,
    verbose=True
)

# --- Tasks ---
research_task = Task(
    description="Identify 3 key AI breakthroughs in 2024.",
    expected_output="A list of 3 breakthroughs.",
    agent=researcher
)

write_task = Task(
    description="Write a 200-word blog post based on the research.",
    expected_output="A formatted blog post.",
    agent=writer,
    context=[research_task]
)
crew = Crew(agents=[researcher], tasks=[research_task], verbose=True)


if __name__ == "__main__":
    crew = Crew(agents=[researcher, writer], tasks=[research_task, write_task])
    result = crew.kickoff()
    print(result)
