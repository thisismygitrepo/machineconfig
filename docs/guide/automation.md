# Automation

Automate repetitive tasks and workflows.

---

## Overview

Machineconfig provides automation capabilities for:

- Scheduled tasks
- Multi-machine orchestration
- Job pipelines
- Remote execution

---

## Fire Jobs

Execute jobs using the Fire-based interface:

```bash
fire run my_job
```

### Job Definition

Jobs are Python functions that can be executed:

```python
def my_job(param1: str, param2: int = 10):
    """My automated job."""
    # Job logic here
    pass
```

### Running Jobs

```bash
# With default parameters
fire run my_job

# With custom parameters
fire run my_job --param1 value --param2 20
```

---

## Remote Execution

Execute commands on remote machines:

```bash
sessions exec "hostname" --targets server1,server2
```

### Cluster Operations

Run commands across a cluster:

```bash
croshell cluster-exec "apt update && apt upgrade -y"
```

---

## Session Management

Manage persistent sessions:

```bash
# List sessions
sessions list

# Create session
sessions create dev-session

# Attach to session
sessions attach dev-session
```

---

## Scheduled Tasks

Schedule recurring tasks:

```bash
# Schedule a daily backup
devops schedule "cloud backup ~/data" --cron "0 2 * * *"

# List scheduled tasks
devops schedule-list

# Remove scheduled task
devops schedule-remove backup-task
```

---

## DevOps Workflows

Common DevOps tasks are simplified:

### System Updates

```bash
devops update-system
```

### Service Management

```bash
devops service start nginx
devops service status nginx
devops service logs nginx
```

### Health Checks

```bash
devops health-check
```

---

## Pipeline Example

Create a deployment pipeline:

```python
from machineconfig import pipeline

@pipeline.stage
def build():
    """Build the application."""
    pass

@pipeline.stage
def test():
    """Run tests."""
    pass

@pipeline.stage
def deploy():
    """Deploy to production."""
    pass

# Run pipeline
pipeline.run([build, test, deploy])
```

---

## Integration

Machineconfig integrates with:

- **CI/CD**: GitHub Actions, GitLab CI
- **Containers**: Docker, Podman
- **Orchestration**: Kubernetes (kubectl)
- **Monitoring**: System metrics, alerts
