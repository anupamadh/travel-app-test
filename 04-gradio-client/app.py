import json
import os

import gradio as gr
import requests
from fastapi import FastAPI

# Local server by default. For the live one: API_URL=https://03-fastapi.vercel.app/api/plan
URL = os.environ.get("API_URL", "http://127.0.0.1:8000/api/plan")


def diagnose(workflow):
    r = requests.post(URL, json={"workflow": workflow}, timeout=90)
    r.raise_for_status()
    return json.dumps(r.json(), indent=2)


demo = gr.Interface(
    diagnose,
    gr.Textbox(lines=8, label="Workflow"),
    gr.Textbox(lines=20, label="Plan"),
)
app = gr.mount_gradio_app(FastAPI(), demo, path="/", ssr_mode=False)

if __name__ == "__main__":
    demo.launch(ssr_mode=False)
