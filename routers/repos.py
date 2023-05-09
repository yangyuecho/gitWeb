import typing as t
import dependencies as d
import models
import schemas
from fastapi import APIRouter
from fastapi import Response
from fastapi import status
from fastapi import Depends
from fastapi import HTTPException
from services.repos import RepoService
from sqlalchemy.orm import Session
from utils import GitRepo


router = APIRouter(
    prefix="/api/repo",
    tags=["repos"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.Repo)
async def new_repo(repo: schemas.RepoCreate, db: Session = Depends(d.get_db)):
    res = RepoService.create_new_repo(db, repo)
    if isinstance(res, Exception):
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content=str(res))
    else:
        return res


@router.get("/", response_model=t.List[schemas.Repo], responses={404: {"model": schemas.Message}})
async def repo_list(db: Session = Depends(d.get_db),
                    current_user: models.User = Depends(d.get_current_active_user)):
    print('current_user', current_user)
    res = RepoService.repo_list(db)
    return res


@router.get("/{repo_id}")
async def repo_tree(repo_id: int,
                    db: Session = Depends(d.get_db),
                    current_user: models.User = Depends(d.get_current_active_user)):
    repo = RepoService.find_by_id(db, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    git_repo = GitRepo(repo.path)
    return git_repo.tree()


@router.get("/{repo_id}/deferred-metadata/<branch>/<path>")
async def repo_file_content(repo_id: int,
                            branch: str,
                            path: str,
                            db: Session = Depends(d.get_db),
                            current_user: models.User = Depends(d.get_current_active_user)):
    repo = RepoService.find_by_id(db, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    git_repo = GitRepo(repo.path)
    return git_repo.file_content(path)

