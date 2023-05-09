from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)


class Repo(Base):
    name = Column(String, index=True)
    path = Column(String, index=True, unique=True)
    is_private = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("user.id"))


class RepoAuth(Base):
    readable = Column(Boolean, default=False)
    writable = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("user.id"))
    repo_id = Column(Integer, ForeignKey("repo.id"))