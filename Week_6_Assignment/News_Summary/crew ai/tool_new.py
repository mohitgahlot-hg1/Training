import os
from crewai import Agent, Task, Crew
from crewai.tools import tool
from crewai_tools import PDFSearchTool


# 2. Configure PDF Tool to use Gemini
# Ensure 'indian_recipes.pdf' is in your VS Code folder
pdf_tool = PDFSearchTool(
    pdf_path='indian_recipes.pdf',
    config={
        "llm": {
            "provider": "google",
            "config": {
                "model": "gemini/gemini-1.5-flash",
            },
        },
        "embedder": {
            "provider": "google",
            "config": {
                "model": "models/embedding-001",
                "task_type": "retrieval_document",
            }
        }
    }
)

# 3. Agent using Gemini (default if LLM is not specified or configured)
chef_researcher = Agent(
    role="Indian Cuisine Expert",
    goal="Extract and summarize specific food recipes from documents.",
    backstory="You are a master chef specialized in traditional Indian flavors.",
    tools=[pdf_tool],
    verbose=True
)

# 4. Task to find 4 recipes
recipe_task = Task(
    description="Search the PDF and find the recipes for 4 Indian dishes. Include ingredients and steps.",
    expected_output="A detailed recipe list for 4 different Indian foods found in the document.",
    agent=chef_researcher
)

if __name__ == "__main__":
    crew = Crew(agents=[chef_researcher], tasks=[recipe_task])
    result = crew.kickoff()
    print(result)

