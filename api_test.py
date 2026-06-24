from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def greet():
    return "fastapi is running"

@app.get("/hello/name")
def hello(name: str):
    return (f"hello{name}!")