import os
import time
from enum import Enum
from typing import Optional

import gitlab
from custom_python_logger import get_logger


class GitLabStatus(Enum):
    OPEN = "Opened"
    CLOSE = "Closed"
    MERGE = "Merged"
    LOCKE = "Locked"


class GitLabClient:
    def __init__(self, gitlab_url: str, gitlab_access_token: Optional[str], project_id: str):
        self.logger = get_logger(self.__class__.__name__)
        self.gitlab_url = gitlab_url
        self.gitlab_access_token = gitlab_access_token or os.environ.get("GITLAB_ACCESS_TOKEN")

        self.gitlab = gitlab.Gitlab(self.gitlab_url, private_token=self.gitlab_access_token)
        self.is_connected(raise_if_not_connected=True)

        self.project = self.gitlab.projects.get(project_id)

    def is_connected(self, raise_if_not_connected: bool = False) -> bool:
        try:
            self.gitlab.auth()
            self.logger.info(f"Successfully connected to GitLab at {self.gitlab_url}")
            return True
        except Exception as e:
            msg = f"Failed to authenticate with GitLab: {e}"
            if raise_if_not_connected:
                raise ValueError(msg)
            self.logger.exception(msg)
            return False

    def fetch_file_content(self, project_path: str, branch: str, file_path: str) -> str:
        self.logger.info(f"Fetching file from project: {project_path}, branch: {branch}, path: {file_path}")

        project = self.gitlab.projects.get(project_path)
        return project.files.get(file_path, ref=branch).decode()

    def create_new_branch(self, branch_name: str, from_branch: str):
        branch = self.project.branches.create({'branch': branch_name, 'ref': from_branch})
        self.logger.info(f"✅ Branch '{branch_name}' created from '{from_branch}'")
        return branch

    def create_tag(self, tag_name: str, from_branch: str, message: Optional[str] = None):
        tag = self.project.tags.create(
            {
                'tag_name': tag_name,
                'ref': from_branch,
                'message': message
            }
        )
        self.logger.info(f"✅ Tag '{tag_name}' created from '{from_branch}'")
        return tag

    def create_new_mr(self, title: str, from_branch: str, target: str):
        mr = self.project.mergerequests.create(
            {
                'source_branch': from_branch,
                'target_branch': target,
                'title': title
            }
        )
        self.logger.info(f"✅ Merge Request '{title}' created: !{mr.iid}")
        return mr

    def get_mr_status(self, mr_number: str | int) -> str:
        mr = self.project.mergerequests.get(mr_number)
        return mr.state

    def has_merge_conflicts(self, mr_number: str | int) -> bool:
        mr = self.project.mergerequests.get(mr_number)
        if hasattr(mr, 'has_conflicts') and mr.has_conflicts:
            self.logger.error(f"🔍 MR !{mr_number} has_conflicts = {mr.has_conflicts}")
            return True
        else:
            # Fallback: check detailed_merge_status if has_conflicts not available
            conflict_statuses = ['conflicts', 'cannot_be_merged']
            if hasattr(mr, 'detailed_merge_status') and mr.detailed_merge_status in conflict_statuses:
                self.logger.error(f"🔍 MR !{mr_number} detailed_merge_status = {mr.detailed_merge_status}")
                return True
        return False

    def is_mr_merged(self, mr_number: str | int) -> bool:
        mr = self.project.mergerequests.get(mr_number)

        if mr.state == GitLabStatus.MERGE:
            self.logger.info(f"✅ MR !{mr_number} has been merged")
            return True

        self.logger.error(f"❌ MR !{mr_number} was close without merging.")
        return False

    def is_mr_open(self, mr_number: str | int) -> bool:
        mr = self.project.mergerequests.get(mr_number)

        if mr.state == GitLabStatus.OPEN:
            self.logger.info(f"✅ MR !{mr_number} has been open.")
            return True

        self.logger.error(f"❌ MR !{mr_number} was closed.")
        return False

    def wait_until_mr_finished(self, mr_number: str | int, check_interval=10, timeout: Optional[int] = None) -> None:
        self.logger.info(f"⏳ Waiting for MR !{mr_number} to be merged...")
        close_statuses = [
            GitLabStatus.CLOSE,
            GitLabStatus.MERGE,
            GitLabStatus.LOCKE,
        ]

        start_time = time.time()
        while True:
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"⏰ Timeout reached while waiting for MR !{mr_number} to be merged.")

            mr = self.project.mergerequests.get(mr_number)
            self.logger.debug(f"MR ({mr.iid}) status is: {mr.state}")

            if self.has_merge_conflicts(mr_number):
                raise Exception(f"🔍 MR !{mr_number} has conflicts.")

            if mr.state in close_statuses:
                break
            time.sleep(check_interval)
