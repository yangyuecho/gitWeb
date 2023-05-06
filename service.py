import subprocess
from pydantic import BaseModel
import const


class Repo(BaseModel):
    name: str


def exec_process(exec_str: str) -> str:
    process = subprocess.Popen(
        exec_str,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # content_length = int(request.headers['Content-Length'])
    # input_data = request.stream.read(content_length)
    # input = None
    stdout, stderr = process.communicate()
    if process.returncode == 0:
        return stdout.decode('utf-8')
    else:
        raise Exception(stderr.decode('utf-8'))


def create_new_repo(repo: Repo):
    # todo 写入数据库
    path = f'{const.repo_root_path}/{repo.name}.git'
    exec_str_1 = f'mkdir {path}'
    m1 = exec_process(exec_str_1)
    exec_str_2 = f'git init --bare {path}'
    m2 = exec_process(exec_str_2)
    print(m1, m2)