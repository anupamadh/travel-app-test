import json
import os

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")

import gradio as gr
import requests
from fastapi import FastAPI

# Local server by default. For the live one: API_URL=https://03-fastapi.vercel.app/api/plan
URL = os.environ.get("API_URL", "http://127.0.0.1:8000/api/plan")


def diagnose(workflow: str) -> str:
    r = requests.post(URL, json={"workflow": workflow}, timeout=55)
    r.raise_for_status()
    return json.dumps(r.json(), indent=2)


def clear():
    return "", ""


with gr.Blocks(title="Itinerary") as demo:
    workflow = gr.Textbox(lines=8, label="Trip Details")
    itinerary = gr.Textbox(lines=20, label="Itinerary")
    with gr.Row():
        gr.Button("Clear").click(clear, outputs=[workflow, itinerary], queue=False)
        gr.Button("Submit", variant="primary").click(
            diagnose, workflow, itinerary, queue=False, api_name="diagnose"
        )

# queue=False makes Submit call /run in one request, so Vercel does not have to
# keep Gradio's in-memory queue across separate function instances.
app = gr.mount_gradio_app(FastAPI(), demo, path="/", ssr_mode=False)

if __name__ == "__main__":
    demo.launch(ssr_mode=False)
