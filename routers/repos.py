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
                    current_user: models.User = Depends(d.get_current_user_no_must)):
    print('current_user', current_user)
    # todo auth
    res = RepoService.repo_list(db)
    return res


@router.get("/{name}/deferred-metadata/")
async def repo_file_content(name: str,
                            branch: t.Optional[str] = "",
                            path: t.Optional[str] = "",
                            db: Session = Depends(d.get_db),
                            current_user: models.User = Depends(d.get_current_user_no_must)):
    repo = RepoService.find_by_unique_name(db, name)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    git_repo = GitRepo(repo.path)
    # 获取指定分支的最后一个 commit 对象
    commit = git_repo.newest_commit_by_branch(branch)
    return git_repo.file_content_by_path(path, commit=commit)


@router.get("/{name}/tree/")
async def repo_tree(name: str,
                    branch: t.Optional[str] = "",
                    commit: t.Optional[str] = "",
                    path: t.Optional[str] = "",
                    db: Session = Depends(d.get_db),
                    current_user: models.User = Depends(d.get_current_user_no_must)):
    repo = RepoService.find_by_unique_name(db, name)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    git_repo = GitRepo(repo.path)
    # 获取指定分支的最后一个 commit 对象
    # print('branch', branch)
    # print('path', path)
    if branch and not commit:
        commit = git_repo.newest_commit_by_branch(branch)
    elif commit:
        commit = git_repo.repo.revparse_single(commit)
    return git_repo.dir_content_by_path(path=path, commit=commit)


@router.get("/{name}/commits")
async def repo_commits(name: str,
                    branch: t.Optional[str] = "",
                    db: Session = Depends(d.get_db),
                    current_user: models.User = Depends(d.get_current_user_no_must),):
    repo = RepoService.find_by_unique_name(db, name)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    git_repo = GitRepo(repo.path)
    # 获取指定分支的最后一个 commit 对象
    commit = git_repo.newest_commit_by_branch(branch)
    return git_repo.all_commits(commit=commit)


@router.get("/{name}/branches")
async def repo_branches(name: str,
                    db: Session = Depends(d.get_db),
                    current_user: models.User = Depends(d.get_current_user_no_must),):
    repo = RepoService.find_by_unique_name(db, name)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    git_repo = GitRepo(repo.path)
    return git_repo.all_branch()
