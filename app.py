
from fastapi import FastAPI

app = FastAPI()
@app.get("/")
async  def greet_json():
    return {"Hello": "World!"}