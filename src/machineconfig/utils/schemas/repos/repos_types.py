

from typing import TypedDict



class GitVersionInfo(TypedDict):
    branch: str
    commit: str


class RepoRemote(TypedDict):
    name: str
    url: str


class RepoRecordDict(TypedDict):
    name: str
    parent_dir: str
    current_branch: str
    remotes: list[RepoRemote]
    version: GitVersionInfo


class RepoRecordFile(TypedDict):
    version: str
    repos: list[RepoRecordDict]
