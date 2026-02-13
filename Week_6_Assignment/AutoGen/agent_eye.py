# import asyncio
# import sys
# import os
# from dotenv import load_dotenv

# from autogen_agentchat.ui import Console
# from autogen_agentchat.teams import RoundRobinGroupChat

# from autogen_ext.models.openai import OpenAIChatCompletionClient
# from autogen_ext.agents.web_surfer import MultimodalWebSurfer
# from autogen_core.models import ModelInfo

# # (Windows) Recommended for async subprocess/browsers
# if sys.platform == "win32":
#     asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# # Optional: If FFmpeg isn't on PATH, uncomment and set your path:
# # os.environ["PATH"] = r"C:\ffmpeg\bin;" + os.environ["PATH"]

# async def main() -> None:
#     load_dotenv()
#     api_key = os.getenv("GEMINI_API_KEY")
#     if not api_key:
#         raise RuntimeError("GEMINI_API_KEY is not set in your .env")

#     model_client = OpenAIChatCompletionClient(
#         model="gemini-2.5-flash",  # or another Gemini model your key supports
#         api_key=api_key,
#         base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
#         model_info=ModelInfo(
#             vision=True,               # WebSurfer may capture screenshots
#             function_calling=True,
#             json_output=True,
#             structured_output=True,
#             family="gemini",
#         ),
#     )

#     # No system_message here — it's not a supported kwarg for your version
#     web_surfer_agent = MultimodalWebSurfer(
#         name="MultimodalWebSurfer",
#         model_client=model_client,
#         # If your class exposes other optional args (e.g., headless, viewport), you can add them here
#     )

#     team = RoundRobinGroupChat([web_surfer_agent], max_turns=3)

#     try:
#         # Put your behavior instructions in the task
#         task = (
#             task = """
# You are a strict web browsing agent. 
# Follow these ACTIONS exactly using your browser tools:

# 1. OPEN https://www.google.com
# 2. In the SEARCH BOX, TYPE: VIRAT KOHLI
# 3. PRESS Enter
# 4. WAIT for results to load
# 5. EXTRACT the top 3 results:
#    - Title
#    - Summary (1–2 lines)
#    - Source URL
# 6. RETURN only the extracted results in bullet points.
# 7. Do NOT describe what you are doing, ONLY return the extracted results.
# """
#         )
#         stream = team.run_stream(task=task)
#         await Console(stream)
#     finally:
#         await web_surfer_agent.close()

# if __name__ == "__main__":
#     asyncio.run(main())



import asyncio
import sys
import os
from dotenv import load_dotenv

from autogen_agentchat.ui import Console
from autogen_agentchat.teams import RoundRobinGroupChat

from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.agents.web_surfer import MultimodalWebSurfer
from autogen_core.models import ModelInfo

# (Windows) Recommended for async subprocess/browsers
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Optional: If FFmpeg isn't on PATH, uncomment and set your path:
# os.environ["PATH"] = r"C:\ffmpeg\bin;" + os.environ["PATH"]

async def main() -> None:  # fix: -> not -&gt;
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set in your .env")

    model_client = OpenAIChatCompletionClient(
        model="gemini-2.5-flash",  # or another Gemini model your key supports
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        model_info=ModelInfo(
            vision=True,               # WebSurfer may capture screenshots
            function_calling=True,
            json_output=True,
            structured_output=True,
            family="gemini",
        ),
    )

    # No system_message here — it's not a supported kwarg for your version
    web_surfer_agent = MultimodalWebSurfer(
        name="MultimodalWebSurfer",
        model_client=model_client,
        # If your class exposes other optional args (e.g., headless, viewport), you can add them here
    )

    team = RoundRobinGroupChat([web_surfer_agent], max_turns=3)

    try:
        # Put your behavior instructions in the task (single assignment; no nesting)
        task = """
You are a strict web browsing agent.
Follow these ACTIONS exactly using your browser tools:

1. OPEN https://www.google.com
2. In the SEARCH BOX, TYPE: VIRAT KOHLI
3. PRESS Enter
4. WAIT for results to load
5. EXTRACT the top 3 results:
   - Title
   - Summary (1–2 lines)
   - Source URL
6. RETURN only the extracted results in bullet points.
7. Do NOT describe what you are doing, ONLY return the extracted results.
"""
        stream = team.run_stream(task=task)
        await Console(stream)
    finally:
        await web_surfer_agent.close()

if __name__ == "__main__":
    asyncio.run(main())