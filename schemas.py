from pydantic import BaseModel
from typing import Optional


class RepoBase(BaseModel):
    name: str
    path: Optional[str] = None
    is_private: Optional[bool] = False
    owner_id: Optional[int] = None


class RepoCreate(RepoBase):
    pass


class Repo(RepoBase):
    id: int

    class Config:
        orm_mode = True


# class UserBase(BaseModel):
#     email: str
#
#
# class UserCreate(UserBase):
#     password: str
#
#
# class User(UserBase):
#     id: int
#     is_active: bool
#     items: list[Item] = []
#
#     class Config:
#         orm_mode = True