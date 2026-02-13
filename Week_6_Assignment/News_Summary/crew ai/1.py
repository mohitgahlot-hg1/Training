from crewai import Agent
from dotenv import load_dotenv
load_dotenv()
# Define an agent
researcher = Agent(
    role="AI Researcher",
    goal="Gather the latest AI trends from 2024",
    backstory="You are an expert AI researcher who writes reports on emerging AI trends.",
    verbose=True  # Shows the agent's thought process
)