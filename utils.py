import re
import os
import pygit2
import typing as t
from datetime import datetime
from const import GitEntityType


class GitEntity:
    def __init__(self, name, path, oid, **kwargs):
        self.name: str = name
        self.path: str = path
        self.type: str = GitEntityType.DIR.value if kwargs.get('is_dir', False) else GitEntityType.FILE.value
        self.children: t.Optional[t.List[GitEntity]] = None
        self.oid = str(oid)
        self.commit_id = kwargs.get('commit_id')
        self.commit_message = kwargs.get('commit_message')
        self.commit_time = kwargs.get('commit_time')

    def __repr__(self):
        return f"<{self.__dict__}>"


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

    def newest_commit_by_branch(self, branch_name: str = "") -> pygit2.Commit:
        if branch_name:
            branch = self.repo.branches[branch_name]
            return branch.peel()
        return self.cur_commit

    def revparse_single(self, branch: str) -> pygit2.Commit:
        return self.repo.revparse_single(branch)

    def dir_content_by_path(self, path: str = "", commit: pygit2.Commit = None) -> t.List[GitEntity]:
        if commit is None:
            commit = self.cur_commit
        # print('commit', commit, commit.commit_time)
        # path = "" 时是根目录  'path/to/directory'
        tree = commit.tree
        res = []
        if path:
            tree = tree[path]
        for e in tree:
            n = e.name
            p = path + '/' + n if path else n
            is_dir = e.type_str == 'tree'
            # print('is_dir', is_dir)
            c = self.entity_latest_commit(p, commit, is_dir)
            # print(c.hex)
            d = {
                'name': n,
                'path': p,
                'oid': e.oid,
                'is_dir': is_dir,
                'commit_id': c.hex,
                'commit_message': c.message,
                'commit_time': datetime.fromtimestamp(
                    c.commit_time).strftime('%Y-%m-%d %H:%M:%S'),
            }
            f = GitEntity(**d)
            res.append(f)
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

    def all_branch(self) -> t.List[t.Dict]:
        res = []
        for branch_name in self.repo.branches:
            b = self.repo.branches[branch_name]
            res.append({
                'name': b.branch_name,
                'is_head': b.is_head(),
                'is_checked_out': b.is_checked_out(),
            })
        return res

    def all_commits(self, commit: pygit2.Commit = None) -> t.Dict[str, t.Any]:
        if commit is None:
            commit = self.cur_commit
        commits = []
        # 从给定提交开始遍历历史记录
        for c in self.repo.walk(commit.oid, pygit2.GIT_SORT_NONE):  # 使用与 git 相同的默认方法对输出进行排序：反向时间顺序。
            data = {
                'hash': c.hex,
                'message': c.message,
                'commit_time': datetime.utcfromtimestamp(
                    c.commit_time).strftime('%Y-%m-%d %H:%M:%S'),
                'author_name': c.author.name,
                'author_email': c.author.email,
                'parents': [c.hex for c in c.parents],
                'oid': str(c.oid),
            }
            commits.append(data)
        return {"commits": commits}

    def compare_commits(self, base: str, compare: str) -> t.Dict[str, t.Any]:
        base_commit = self.get_commit_by_branch_or_tag(base)
        compare_commit = self.get_commit_by_branch_or_tag(compare)
        commits = []
        parents_hex = []
        # 从给定提交开始遍历历史记录
        # print(base_commit.hex, compare_commit.hex)
        for c in self.repo.walk(compare_commit.oid, pygit2.GIT_SORT_NONE):
            if c.hex == base_commit.hex:
                break
            parents = [c.hex for c in c.parents]
            data = {
                'hash': c.hex,
                'message': c.message,
                'commit_time': datetime.utcfromtimestamp(
                    c.commit_time).strftime('%Y-%m-%d %H:%M:%S'),
                'author_name': c.author.name,
                'author_email': c.author.email,
                'parents': parents,
                'oid': str(c.oid),
            }
            if c.hex != compare_commit.hex:
                if c.hex in parents_hex:
                    commits.append(data)
                    parents_hex.extend(parents)
            else:
                commits.append(data)
                parents_hex.extend(parents)
        return {"commits": commits}

    def all_tags(self):
        regex = re.compile('^refs/tags/')
        tags = [r.split('/')[-1] for r in self.repo.references if regex.match(r)]
        res = []
        for tag in tags:
            c = self.repo.revparse_single(tag)
            data = {
                'hash': c.hex,
                'message': c.message,
                'commit_time': datetime.utcfromtimestamp(
                    c.commit_time).strftime('%Y-%m-%d %H:%M:%S'),
                'author_name': c.author.name,
                'author_email': c.author.email,
                'parents': [c.hex for c in c.parents],
                'oid': str(c.oid),
                'tag': tag,
            }
            res.append(data)
        return res

    # 文件或文件夹的最新提交记录
    def entity_latest_commit(self, path: str, commit: pygit2.Commit = None, is_dir: bool = False) -> pygit2.Commit:
        if commit is None:
            commit = self.cur_commit
        # 按照时间顺序获取 commit 列表, commit 的顺序 git log 命令输出的一致, 最新的 commit 在最前
        # walker 可以看作类似元素为 pygit2.Commit 对象的列表
        walker = self.repo.walk(commit.id, pygit2.GIT_SORT_TIME)
        for c in walker:
            # 获取父提交
            parent_ids = c.parent_ids
            # 假设使用了 git merge 命令合并过分支, 合并分支时创建的提交可能会有多个父提交
            for pid in parent_ids:
                parent = self.repo[pid]
                assert isinstance(parent, pygit2.Commit)
                # 相当于命令 git diff parent.hex commit.hex
                diff = self.repo.diff(parent, commit)
                assert isinstance(diff, pygit2.Diff)
                for patch in diff:
                    # 遍历的是所有修改的内容, 都是文件
                    assert isinstance(patch, pygit2.Patch)
                    # 获取改动的文件的路径
                    f = patch.delta.new_file.path
                    # print(f, c.hex, path)
                    # 如果传入的文件路径和改动的路径相等, 说明当前的 commit 和它的 parent commit 相比, 这个文件发生了改动
                    if is_dir:
                        # 如果是文件夹, 则通过文件, 则算出对应的文件夹路径, 然后判断是否相等
                        # commit 是按新到旧的顺序遍历的, 所以返回的是最新的相关提交
                        # os.path.dirname('/a/b/c.txt') => '/a/b'
                        d = os.path.dirname(f)
                        # 文件夹用路径包含判断, 这样能让最外层文件夹获取到内层文件夹的改动
                        if path in d:
                            return c
                    else:
                        if f == path:
                            return c

        # 该文件有可能只在整个分支/标签的第一个 commit 改动过, 这种情况下没有 parent commit
        return commit

    def diff_by_commit(self, commit: pygit2.Commit = None) -> str:
        if commit is None:
            commit = self.cur_commit
        # print('111', commit.hex, commit.parent_ids)
        for pid in commit.parent_ids:
            parent = self.repo[pid]
            assert isinstance(parent, pygit2.Commit)
            # 相当于命令 git diff parent.hex commit.hex
            diff = self.repo.diff(parent, commit)
            diff_string = diff.patch
            if diff_string:
                return diff_string
        return ""

    def get_commit_by_branch_or_tag(self, branch_or_tag: str) -> pygit2.Commit:
        regex = re.compile('^refs/tags/')
        tags = [r.split('/')[-1] for r in self.repo.references if regex.match(r)]
        if branch_or_tag in tags:
            return self.repo.revparse_single(branch_or_tag)
        else:
            return self.newest_commit_by_branch(branch_or_tag)

    def compare_diff(self, base: str, compare: str) -> str:
        # 先判断是 tag 还是 branch, 然后返回对应的 commit
        base_commit = self.get_commit_by_branch_or_tag(base)
        compare_commit = self.get_commit_by_branch_or_tag(compare)
        diff = self.repo.diff(base_commit, compare_commit)
        diff_string = diff.patch
        return diff_string


if __name__ == "__main__":
    repo_path = '/Users/dongzijuan/projects/gitWeb/data/axe.git'
    repo = GitRepo(repo_path)
    # print(repo.all_tags())
    tag = repo.repo.revparse_single('v2.0.0')
    # print(tag.hex, tag.commit_time)
    # res = repo.tree()
    # c = repo.entity_latest_commit('README.md', is_dir=False)
    # print('rr', c.hex, c.message)
    # repo.all_commits(None)
    # branches_list = list(repo.repo.branches)
    # print(branches_list)
    # print(repo.dir_content_by_path('folder'))
    # print(repo.file_content_by_path('folder/readme.md'))