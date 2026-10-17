import json
import os
from pathlib import Path
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

PROMPT = """Find family-friendly things to do for the destination and details below.
Reply with one JSON object only, with these keys:
destination, dates, travelers, pace, transport, comfort, diet,
days (list of objects with day, base, and activities),
stays (list of objects with place, name, and why),
food (list of objects with place, name, and dishes).
Finish every day and every list. Do not stop mid-sentence.

"""


def diagnose(workflow: str) -> dict:
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"},
        json={
            "model": "openai/gpt-oss-120b",
            "messages": [{"role": "user", "content": PROMPT + workflow}],
            "response_format": {"type": "json_object"},
            "max_completion_tokens": 16384,
            "reasoning_effort": "low",
        },
        timeout=90,
    )
    r.raise_for_status()  # a Groq error, such as a 429 rate limit, shows by name in the logs
    choice = r.json()["choices"][0]
    if choice.get("finish_reason") == "length":
        raise HTTPException(status_code=502, detail="plan was truncated")
    return json.loads(choice["message"]["content"])


app = FastAPI()


class WorkflowIn(BaseModel):
    workflow: str


@app.post("/api/plan")
def diagnose_route(body: WorkflowIn):
    return diagnose(body.workflow)
