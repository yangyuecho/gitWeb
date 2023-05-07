from fastapi import FastAPI
from fastapi import Request
from fastapi import Response
from fastapi import status
from service import Repo
from service import RepoService
import const


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.post("/api/repo")
async def new_repo(repo: Repo):
    RepoService.create_new_repo(repo)
    return repo


@app.get("/{repo_name}/info/refs")
async def refs_info(repo_name: str, service: str):
    # todo check if repo exists
    if service not in const.git_command:
        return Response(status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
    res = RepoService.refs_info(repo_name, service)
    # application/x-git-upload-pack-advertisement
    content_type = f"application/x-{service}-advertisement"
    return Response(content=res, media_type=content_type)


@app.post("/{repo_name}/git-upload-pack")
async def repo_info(repo_name: str, request: Request):
    # todo check if repo exists
    # b'0098want 5cafe4b73ffd886a63a9cc56703c74ba458ab6f3 multi_ack_detailed no-done side-band-64k thin-pack ofs-delta deepen-since deepen-not agent=git/2.33.0\n00000009done\n'
    body = await request.body()  # await request.stream.read()
    res = RepoService.repo_info(repo_name, body)
    content_type = f"application/x-git-upload-pack-result"
    # todo 流式返回
    return Response(content=res, media_type=content_type)


@app.post("/{repo_name}/git-receive-pack")
async def repo_update(repo_name: str, request: Request):
    # todo check if repo exists
    # b'0098want 5cafe4b73ffd886a63a9cc56703c74ba458ab6f3 multi_ack_detailed no-done side-band-64k thin-pack ofs-delta deepen-since deepen-not agent=git/2.33.0\n00000009done\n'
    body = await request.body()  # await request.stream.read()
    res = RepoService.update_repo(repo_name, body)
    content_type = f"application/x-git-receive-pack-result"
    # todo 流式返回
    return Response(content=res, media_type=content_type)