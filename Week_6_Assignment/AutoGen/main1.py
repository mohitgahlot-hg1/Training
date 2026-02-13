import asyncio
from autogen_agentchat.agents import AssistantAgent, CodeExecutorAgent, UserProxyAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo
from pathlib import Path
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
 
from dotenv import load_dotenv
import os
 
async def main() -> None:
    # Load environment variables
    load_dotenv()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
 
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set in your .env")
 
    # Use OpenAI-compatible client, but point it to Gemini's endpoint
    model_client = OpenAIChatCompletionClient(
        model="gemini-2.5-flash",  # pick any supported Gemini model
        api_key=GEMINI_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",  # Gemini OpenAI-compat endpoint
        # When using a non-OpenAI model name, provide minimal capabilities:
        model_info=ModelInfo(
            vision=True,               # set True if you intend to send images
            function_calling=True,
            json_output=True,
            structured_output=True,
            family="unknown",
        ),
    )
    user = UserProxyAgent("user")
 
    coder = AssistantAgent(
        "coder", model_client = model_client,
        system_message = "You are a senior engineer... output ONLY runnable Python..."
    )
 
    executor = CodeExecutorAgent(
        "executor", model_client = model_client,
        code_executor = LocalCommandLineCodeExecutor(work_dir=Path.cwd() / "runs")
    )
    termination = TextMentionTermination("exit", sources = ["user"])
    team = RoundRobinGroupChat(
        [user, coder, executor],
        termination_condition = termination
    )
   
    try:
        await Console(
            team.run_stream()
        )
    finally:
        await model_client.close()
 
if __name__ == "__main__":
    asyncio.run(main())
 