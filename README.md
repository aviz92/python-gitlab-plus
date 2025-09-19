# Python GitLab Plus
An enhanced Python client for GitLab that extends the functionality of the official `python-gitlab` package, providing better error handling, merge request management, branch operations, and more.

---

## Features
- ✅ Simplified connection to GitLab Cloud and Self-hosted instances
- ✅ Robust error handling with comprehensive logging
- ✅ Branch management (create, fetch content)
- ✅ Merge Request operations (create, status checking, conflict detection)
- ✅ Tag creation and management
- ✅ File content fetching from repositories
- ✅ Merge Request monitoring with timeout support

---

## Installation
```bash
pip install python-gitlab-plus
```

---

## Configuration
The package uses environment variables for authentication and configuration:

```bash
# Required environment variables
GITLAB_ACCESS_TOKEN=your_gitlab_access_token
GITLAB_URL=https://gitlab.com  # Your GitLab instance URL (default: gitlab.com)
```

## Examples

### Basic Setup and Connection
```python
from python_gitlab_plus import GitLabClient

# Initialize GitLab client
gitlab_client = GitLabClient(
    gitlab_url="https://gitlab.com",
    gitlab_access_token="your_access_token",
    project_id="your-project-id"
)
```

### Creating a New Branch
```python
from python_gitlab_plus import GitLabClient

gitlab_client = GitLabClient(
    gitlab_url="https://gitlab.com",
    gitlab_access_token="your_access_token",
    project_id="your-project-id"
)

# Create a new branch from main
branch = gitlab_client.create_new_branch(
    branch_name="feature/new-feature",
    from_branch="main"
)
print(f"Created branch: {branch.name}")
```

### Creating a Merge Request
```python
from python_gitlab_plus import GitLabClient

gitlab_client = GitLabClient(
    gitlab_url="https://gitlab.com",
    gitlab_access_token="your_access_token",
    project_id="your-project-id"
)

# Create a merge request
mr = gitlab_client.create_new_mr(
    title="Add new feature",
    from_branch="feature/new-feature",
    target="main"
)
print(f"Created MR: !{mr.iid}")
```

### Checking Merge Request Status and Conflicts
```python
from python_gitlab_plus import GitLabClient

gitlab_client = GitLabClient(
    gitlab_url="https://gitlab.com",
    gitlab_access_token="your_access_token",
    project_id="your-project-id"
)

mr_number = 123

# Check MR status
status = gitlab_client.get_mr_status(mr_number)
print(f"MR status: {status}")

# Check for merge conflicts
has_conflicts = gitlab_client.has_merge_conflicts(mr_number)
if has_conflicts:
    print("MR has merge conflicts!")
else:
    print("MR is ready to merge")

# Wait for MR to be merged (with timeout)
try:
    gitlab_client.wait_until_mr_finished(mr_number, check_interval=30, timeout=3600)
    print("MR has been processed!")
except TimeoutError:
    print("Timeout waiting for MR to be merged")
except Exception as e:
    print(f"Error: {e}")
```

### Creating Tags and Fetching File Content
```python
from python_gitlab_plus import GitLabClient

gitlab_client = GitLabClient(
    gitlab_url="https://gitlab.com",
    gitlab_access_token="your_access_token",
    project_id="your-project-id"
)

# Create a tag
tag = gitlab_client.create_tag(
    tag_name="v1.0.0",
    from_branch="main",
    message="Release version 1.0.0"
)
print(f"Created tag: {tag.name}")

# Fetch file content
content = gitlab_client.fetch_file_content(
    project_path="your-project-id",
    branch="main",
    file_path="FILE_README.md"
)
print(f"File content: {content[:100]}...")
```

---

## 🤝 Contributing
If you have a helpful tool, pattern, or improvement to suggest:
Fork the repo <br>
Create a new branch <br>
Submit a pull request <br>
I welcome additions that promote clean, productive, and maintainable development. <br>

---

## 🙏 Thanks
Thanks for exploring this repository! <br>
Happy coding! <br>
