import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from crewai_tools import SerpApiGoogleSearchTool

# 1. Load Environment Variables
load_dotenv()

gemini_key = os.getenv("GEMINI_API_KEY")
serpapi_key = os.getenv("SERPAPI_API_KEY")

if not gemini_key:
    raise EnvironmentError("GEMINI_API_KEY is missing in .env file")
if not serpapi_key:
    raise EnvironmentError("SERPAPI_API_KEY is missing in .env file")

# 2. Configure Gemini LLM
# The code uses "gemini/gemini-1.5-flash" as it is the most stable current version.
# You can try "gemini/gemini-2.0-flash" if your API key supports it.
gemini_llm = LLM(
    model="gemini/gemini-1.5-flash", 
    api_key=gemini_key,
    temperature=0.2,
    verbose=True
)

# 3. Configure SerpApi Tool
# This tool automatically grabs 'SERPAPI_API_KEY' from the environment,
# but we can also pass it explicitly to be safe.
search_tool = SerpApiGoogleSearchTool(
    n_results=5,
    serp_api_key=serpapi_key 
)

# 4. Define Agents
researcher = Agent(
    role="AI News Researcher",
    goal="Find 5 important AI news stories from the last 7 days.",
    backstory=(
        "You are a seasoned tech journalist who digs deep into search results "
        "to find the most impactful Artificial Intelligence trends."
    ),
    tools=[search_tool], # Give the researcher the search tool
    llm=gemini_llm,      # Bind Gemini
    verbose=True
)

writer = Agent(
    role="LinkedIn Content Creator",
    goal="Write an engaging LinkedIn post from the AI news summary.",
    backstory=(
        "You are a viral content creator. You take technical news and turn it "
        "into engaging, professional posts for engineering leaders."
    ),
    llm=gemini_llm,      # Bind Gemini (Writers don't usually need search tools)
    verbose=True
)

# 5. Define Tasks
research_task = Task(
    description=(
        "Use the search tool to find the top 5 AI news stories from the past week. "
        "Focus on 'Generative AI', 'LLMs', and 'AI Regulations'. "
        "Provide a summary that includes the headline and a source link for each."
    ),
    expected_output="A structured list of 5 news items with URLs.",
    agent=researcher
)

write_post_task = Task(
    description=(
        "Using the news summaries provided by the Researcher, write a "
        "professional LinkedIn post. The post should have a catchy hook, "
        "bullet points for the news, and a call to action. "
        "Keep it under 200 words."
    ),
    expected_output="A formatted LinkedIn post ready for publication.",
    agent=writer,
    context=[research_task] # Wait for the researcher's output
)

# 6. Create and Kickoff the Crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_post_task],
    verbose=True
)

if __name__ == "__main__":
    print("### Starting Crew... ###")
    result = crew.kickoff()
    print("\n\n########################")
    print("## FINAL LINKEDIN POST ##")
    print("########################\n")
    print(result)
