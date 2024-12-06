from fastapi import FastAPI
import gradio as gr
from dotenv import load_dotenv
load_dotenv() 

app = FastAPI()
@app.get("/")
async  def greet_json():
    return {"Hello": "World!"}