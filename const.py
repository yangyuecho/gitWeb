from enum import Enum

repo_root_path = '/Users/dongzijuan/projects/gitWeb/data'
git_command = ['git-upload-pack', 'git-receive-pack']


class GitEntityType(Enum):
    DIR = 'dir'
    FILE = 'file'
