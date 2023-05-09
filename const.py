import os
from enum import Enum

repo_root_path = '/Users/dongzijuan/projects/gitWeb/data'
git_command = ['git-upload-pack', 'git-receive-pack']
user_salt = os.getenv('USER_SALT', 'asdjf203')


class GitEntityType(Enum):
    DIR = 'dir'
    FILE = 'file'
