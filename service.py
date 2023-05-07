import asyncio
import subprocess
from typing import Generator, Any, AsyncGenerator

from pydantic import BaseModel
import const


class Repo(BaseModel):
    name: str


def exec_process(exec_str: str, data: bytes = None) -> bytes:
    process = subprocess.Popen(
        exec_str,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # content_length = int(request.headers["Content-Length"])
    # input_data = request.stream.read(content_length)
    # input = None
    print('exec_str', exec_str)
    print('data', data)
    stdout, stderr = process.communicate(input=data)
    if process.returncode == 0:
        # print('output', stdout)
        return stdout
    else:
        # print(stderr.decode("utf-8"))
        print(stdout)
        raise Exception(stderr.decode("utf-8"))


def stream_exec_process(exec_str: str, data: bytes):
    process = subprocess.Popen(
        exec_str,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # print('exec_str', exec_str)
    # print('data', data)
    process.stdin.write(data)
    process.stdin.flush()
    for line in iter(process.stdout.readline, b''):
        yield line

    ret_code = process.wait()
    if ret_code != 0:
        raise Exception(process.stderr.read().decode("utf-8"))


class RepoService:
    @classmethod
    def create_new_repo(cls, repo: Repo):
        # todo 写入数据库
        path = f"{const.repo_root_path}/{repo.name}.git"
        exec_str_1 = f"mkdir {path}"
        m1 = exec_process(exec_str_1)
        exec_str_2 = f"git init --bare {path}"
        m2 = exec_process(exec_str_2)
        print(m1, m2)

    @classmethod
    def refs_info(cls, repo_name: str, git_command: str) -> str:
        """
        pkt-line格式的数据, 客户端需要验证第一首行的四个字符符合正则^[0-9a-f]{4}#，这里的四个字符是代表后面内容的长度
        客户端需要验证第一行是# service=$servicename
        服务端得保证每一行结尾需要包含一个LF换行符
        服务端需要以0000标识结束本次请求响应
        """
        smart_server_advert = f"# service={git_command}"
        content_path = f"{const.repo_root_path}/{repo_name}"
        exec_str = f"git {git_command[4:]} --stateless-rpc --advertise-refs {content_path}"
        m = exec_process(exec_str).decode("utf-8")
        # {:04x}：这是一个整数格式化规则，表示将整数格式化为4位十六进制数，并且不足4位的地方前面补0。
        res = "{:04x}{}0000{}".format(len(smart_server_advert) + 4, smart_server_advert, m)
        return res

    @staticmethod
    def git_pack_command(git_command: str, repo_name: str, stream: bytes) -> Generator[bytes, Any, Any]:
        content_path = f"{const.repo_root_path}/{repo_name}"
        exec_str = f"git {git_command[4:]} --stateless-rpc {content_path}"
        res = stream_exec_process(exec_str, stream)
        return res

    @classmethod
    def repo_info(cls, repo_name: str, stream: bytes) -> Generator[bytes, Any, Any]:
        git_command = "git-upload-pack"
        res = cls.git_pack_command(git_command, repo_name, stream)
        return res

    @classmethod
    def update_repo(cls, repo_name: str, stream: bytes) -> Generator[bytes, Any, Any]:
        # git push 时触发
        git_command = "git-receive-pack"
        res = cls.git_pack_command(git_command, repo_name, stream)
        return res
