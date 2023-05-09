import const
from typing import Annotated
from fastapi import FastAPI
from fastapi import Request
from fastapi import Response
from fastapi import status
from fastapi import Depends
from fastapi.responses import StreamingResponse
from service import RepoService
import models
import schemas
from fastapi.security import HTTPBasicCredentials

from sqlalchemy.orm import Session

from setup import security
from setup import get_db

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/api/repo", response_model=schemas.Repo)
async def new_repo(repo: schemas.RepoCreate, db: Session = Depends(get_db)):
    res = RepoService.create_new_repo(db, repo)
    if isinstance(res, Exception):
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content=str(res))
    else:
        return res


@app.get("/{repo_name}/info/refs")
async def refs_info(repo_name: str,
                    service: str,
                    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
                    db: Session = Depends(get_db)):
    if not RepoService.has_repo_auth(db, repo_name, credentials):
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)
    if service not in const.git_command:
        return Response(status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
    res = RepoService.refs_info(repo_name, service)
    # application/x-git-upload-pack-advertisement
    content_type = f"application/x-{service}-advertisement"
    return Response(content=res, media_type=content_type)


@app.post("/{repo_name}/git-upload-pack")
async def repo_info(repo_name: str, request: Request):
    # b'0098want 5cafe4b73ffd886a63a9cc56703c74ba458ab6f3 multi_ack_detailed no-done side-band-64k thin-pack ofs-delta deepen-since deepen-not agent=git/2.33.0\n00000009done\n'
    body = await request.body()
    res = RepoService.repo_info(repo_name, body)
    content_type = f"application/x-git-upload-pack-result"
    return StreamingResponse(content=res, media_type=content_type)


@app.post("/{repo_name}/git-receive-pack")
async def repo_update(repo_name: str, request: Request):
    data = await request.body()
    res = RepoService.update_repo(repo_name, data)
    content_type = f"application/x-git-receive-pack-result"
    return StreamingResponse(content=res, media_type=content_type)