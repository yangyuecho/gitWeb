from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    # id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)


class Repo(Base):
    # id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    path = Column(String, index=True)
    test = Column(String, index=True)
    is_private = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("user.id"))


class RepoAuth(Base):
    # id = Column(Integer, primary_key=True, index=True)
    readable = Column(Boolean, default=False)
    writable = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("user.id"))
    repo_id = Column(Integer, ForeignKey("repo.id"))