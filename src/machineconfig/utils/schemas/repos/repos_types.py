from typing import TypedDict


class GitVersionInfo(TypedDict):
    branch: str
    commit: str


class RepoRemote(TypedDict):
    name: str
    url: str


class RepoRecordDict(TypedDict):
    name: str
    parentDir: str
    currentBranch: str
    remotes: list[RepoRemote]
    version: GitVersionInfo
    isDirty: bool


class RepoRecordFile(TypedDict):
    version: str
    repos: list[RepoRecordDict]
