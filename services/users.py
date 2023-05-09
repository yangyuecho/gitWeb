import hashlib
import re
import typing as t
import schemas
import schemas as s
import models
import const
from sqlalchemy.orm import Session


class UserService:
    @classmethod
    def find_user_by_username(cls, db: Session, username: str) -> t.Optional[models.User]:
        return db.query(models.User).filter(models.User.username == username).first()

    @classmethod
    def salted_password(cls, password):
        salt = const.user_salt
        hash1 = hashlib.md5(password.encode('ascii')).hexdigest()
        hash2 = hashlib.md5((hash1 + salt).encode('ascii')).hexdigest()
        return hash2

    @staticmethod
    def username_content(username):
        """
        用户名只能包含汉字、字母、数字和下划线
        """
        username = username
        pattern = re.compile(r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$')
        match = pattern.match(username)
        if match:
            return True
        else:
            return False

    @classmethod
    def valid_register(cls, db: Session, form: s.UserCreate) -> tuple[bool | t.Any, list[str]]:
        """
        验证注册信息的正确与否
        """
        username = form.username
        password = form.password
        valid_username = cls.find_user_by_username(db, username) is None
        valid_username_len = 3 <= len(username) <= 10
        valid_password_len = len(password) >= 6
        valid_username_content = cls.username_content(username)
        msgs = []
        if not valid_username:
            message = '用户名已经存在'
            msgs.append(message)
        elif not valid_username_content:
            message = '用户名只能包含汉字、字母、数字和下划线'
            msgs.append(message)
        elif not valid_username_len:
            message = '用户名长度必须大于等于3并小于等于10'
            msgs.append(message)
        elif not valid_password_len:
            message = '密码长度必须大于等于6'
            msgs.append(message)
        status = valid_username and valid_username_len and valid_password_len and valid_username_content
        return status, msgs

    @classmethod
    def register(cls, db: Session, form: s.UserCreate):
        """
        处理注册表单中的信息
        """
        status, msgs = cls.valid_register(db, form)
        if status:
            db_item = models.User(username=form.username)
            db_item.hashed_password = cls.salted_password(form.password)
            db.add(db_item)
            db.commit()
            db.refresh(db_item)
            return db_item
        else:
            msg = ','.join(msgs)
            return schemas.Message(message=msg)
