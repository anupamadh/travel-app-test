import html
import json
import os

import requests
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

# Local server by default. For the live one: API_URL=https://03-fastapi.vercel.app/api/plan
URL = os.environ.get("API_URL", "http://127.0.0.1:8000/api/plan")


def diagnose(workflow: str) -> str:
    r = requests.post(URL, json={"workflow": workflow}, timeout=90)
    r.raise_for_status()
    return json.dumps(r.json(), indent=2)


def page(workflow: str, itinerary: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Itinerary</title>
  <style>
    body {{ font-family: sans-serif; max-width: 40rem; margin: 2rem auto; padding: 0 1rem; }}
    label {{ display: block; font-weight: 600; margin: 1rem 0 0.4rem; }}
    textarea {{ width: 100%; box-sizing: border-box; font: inherit; }}
    button {{ margin-top: 1rem; }}
  </style>
</head>
<body>
  <form method="post">
    <label for="workflow">Trip Details</label>
    <textarea id="workflow" name="workflow" rows="8">{html.escape(workflow)}</textarea>
    <button type="submit">Submit</button>
    <label for="itinerary">Itinerary</label>
    <textarea id="itinerary" rows="20" readonly>{html.escape(itinerary)}</textarea>
  </form>
</body>
</html>"""


app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def form():
    return page("", "")


@app.post("/", response_class=HTMLResponse)
def submit(workflow: str = Form("")):
    if not workflow.strip():
        return page(workflow, "")
    try:
        itinerary = diagnose(workflow)
    except requests.HTTPError as exc:
        itinerary = f"Error {exc.response.status_code}: {exc.response.text}"
    return page(workflow, itinerary)


if __name__ == "__main__":
    import gradio as gr

    gr.Interface(
        diagnose,
        gr.Textbox(lines=8, label="Trip Details"),
        gr.Textbox(lines=20, label="Itinerary"),
    ).launch()
