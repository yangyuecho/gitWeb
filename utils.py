import json
import pygit2
import typing as t
from datetime import datetime
from const import GitEntityType


class GitEntity:
    def __init__(self, name, path, oid):
        self.name: str = name
        self.path: str = path
        self.type: str = GitEntityType.FILE.value
        self.children: t.Optional[t.List[GitEntity]] = None
        self.oid = str(oid)

    def __repr__(self):
        return f"<{self.type} {self.path} {len(self.children) if self.children else None}>"


class GitRepo:
    def __init__(self, path):
        self.path = path
        self.repo = pygit2.Repository(path)
        self.head = self.repo.head
        self.cur_commit = self.repo[self.head.target]

    def tree(self, commit: pygit2.Commit = None) -> t.List[GitEntity]:
        if commit is None:
            commit = self.cur_commit
        return self.dir_content(commit.tree, '')

    def newest_commit_by_branch(self, branch: str = "") -> pygit2.Commit:
        if branch:
            return self.repo.revparse_single(branch)
        return self.cur_commit

    def revparse_single(self, branch: str) -> pygit2.Commit:
        return self.repo.revparse_single(branch)

    def dir_content_by_path(self, path: str = "", commit: pygit2.Commit = None) -> t.List[GitEntity]:
        if commit is None:
            commit = self.cur_commit
        # path = "" 时是根目录  'path/to/directory'
        tree = commit.tree
        res = []
        if path:
            tree = tree[path]
        for e in tree:
            n = e.name
            p = path + '/' + n if path else n
            if e.type_str == 'blob':
                # 如果是文件
                f = GitEntity(n, p, e.oid)
                res.append(f)
            elif e.type_str == 'tree':
                # 如果是文件夹
                e: pygit2.Tree
                # 递归地处理下一级文件
                # 最终是拼成一个树状结构
                d = GitEntity(n, p, e.oid)
                d.type = GitEntityType.DIR.value
                res.append(d)
        return res

    def file_content_by_path(self, path: str, commit: pygit2.Commit = None) -> str:
        if commit is None:
            commit = self.cur_commit
        tree = commit.tree

        # 从树对象中查找指定路径的 blob
        blob_entry = tree[path]

        # 获取 blob 对象
        blob = self.repo.get(blob_entry.id)
        data = blob.data.decode('utf-8')
        return data

    def file_content(self, path: str, commit: pygit2.Commit = None) -> str:
        repo = self.repo
        if commit is None:
            # 获取最新提交
            commit = self.cur_commit
        # 路径是 'dir1/dir2/a.txt'
        parts = path.split('/')

        # commit.tree 对应的是根目录的 tree
        tree = commit.tree
        for part in parts[:-1]:
            # 层层往下找, 找到最下层文件夹对应的 Tree
            # 获取子目录的 tree
            oid = tree[part].oid
            tree = repo[oid]
        # 获取最底层的文件夹的 tree 获取文件的 blob
        # 比如路径是 'dir1/dir2/a.txt', 最底层的文件夹是 dir2
        name = parts[-1]
        oid = tree[name].oid
        # 获取文件对应的 blob, blob 是 pygit2.Blob 类型
        blob = repo[oid]
        # 现在只处理文本文件, 所以直接返回文本内容
        data = blob.data.decode('utf-8')
        return data

    @classmethod
    def dir_content(cls, tree: pygit2.Tree, path: str) -> t.List[GitEntity]:
        res = []
        # Tree 类型可以直接遍历
        for e in tree:
            n = e.name
            if path == '':
                # 根目录
                p = n
            else:
                # 拼接路径
                p = '{}/{}'.format(path, n)
            if e.type_str == 'blob':
                # 如果是文件
                f = GitEntity(n, p, e.oid)
                res.append(f)
            elif e.type_str == 'tree':
                # 如果是文件夹
                e: pygit2.Tree
                # 递归地处理下一级文件
                # 最终是拼成一个树状结构
                d = GitEntity(n, p, e.oid)
                d.type = GitEntityType.DIR.value
                fs = cls.dir_content(e, p)
                d.children = fs
                res.append(d)
            else:
                # 目前只遇到了 blob 和 tree 两种类型, 希望遇到其他类型能够感知到, 所以抛个错,
                raise Exception('unknown type ({})'.format(e.type_str))
        return res

    def all_branch_names(self) -> t.List[str]:
        return self.repo.branches

    def all_commits(self, commit: pygit2.Commit = None) -> t.Dict[str, t.Any]:
        if commit is None:
            commit = self.cur_commit
        commits = []
        cur_commit = []
        # 从给定提交开始遍历历史记录
        for c in self.repo.walk(commit, pygit2.GIT_SORT_NONE):  # 使用与 git 相同的默认方法对输出进行排序：反向时间顺序。
            data = {
                'hash': c.hex,
                'message': c.message,
                'commit_date': datetime.utcfromtimestamp(
                    c.commit_time).strftime('%Y-%m-%d %H:%M:%S'),
                'author_name': c.author.name,
                'author_email': c.author.email,
                'parents': [c.hex for c in c.parents],
            }
            commits.append(data)
            if c == commit:
                cur_commit = data
        return {"cur_commit": cur_commit, "commits": commits}


if __name__ == "__main__":
    repo_path = '/Users/dongzijuan/projects/gitWeb/data/axe.git'
    repo = GitRepo(repo_path)
    res = repo.tree()
    # repo.all_commits(None)
    branches_list = list(repo.repo.branches)
    print(branches_list)
    print(repo.dir_content_by_path('folder'))
    print(repo.file_content_by_path('folder/readme.md'))
    # print(res)
    # file = res[0]
    # print('111', file, file.path)
    # file_content_str = repo.file_content(file.path)
    # print('2222', file_content_str)