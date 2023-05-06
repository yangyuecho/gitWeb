from fastapi import FastAPI
from service import Repo
from service import create_new_repo

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.post("/api/repo")
async def new_repo(repo: Repo):
    create_new_repo(repo)
    return repo


@app.get("/{name}")
async def clone(name: str):
    return {"message": f"Hello {name}"}