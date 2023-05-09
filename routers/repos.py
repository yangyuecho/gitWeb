import typing as t
import dependencies as d
import schemas
from fastapi import APIRouter
from fastapi import Response
from fastapi import status
from fastapi import Depends
from services.repos import RepoService
from sqlalchemy.orm import Session


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


@router.get("/", response_model=t.List[schemas.Repo])
async def repo_list(db: Session = Depends(d.get_db),
                    token: str = Depends(d.oauth2_scheme)):
    print('token', token)
    res = RepoService.repo_list(db)
    return res


@router.get("/{repo_id}")
async def repo_tree(repo: schemas.RepoCreate, db: Session = Depends(d.get_db)):
    res = RepoService.create_new_repo(db, repo)
    if isinstance(res, Exception):
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content=str(res))
    else:
        return res


@router.get("/{repo_id}")
async def repo_file_content(repo: schemas.RepoCreate, db: Session = Depends(d.get_db)):
    res = RepoService.create_new_repo(db, repo)
    if isinstance(res, Exception):
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content=str(res))
    else:
        return res
