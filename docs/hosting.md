# Hosting Your Documentation

This guide covers all options for hosting MkDocs documentation, from local development to free global hosting.

---

## Local Development

### Quick Serve

```bash
uv run mkdocs serve
```

Opens at `http://127.0.0.1:8000`

### Custom Port

```bash
uv run mkdocs serve --dev-addr=0.0.0.0:8080
```

### Live Reload (default)

MkDocs automatically reloads when you edit files. To disable:

```bash
uv run mkdocs serve --no-livereload
```

### Build Static Files

```bash
uv run mkdocs build
```

Creates a `site/` directory with static HTML files.

---

## Free Hosting Options

### 1. GitHub Pages (Recommended)

**Best for**: Open source projects on GitHub

**Pros**:
- Completely free
- Automatic HTTPS
- Custom domain support
- Direct integration with MkDocs

**Setup**:

=== "One Command Deploy"

    ```bash
    uv run mkdocs gh-deploy
    ```

    This builds and pushes to the `gh-pages` branch automatically.

=== "GitHub Actions (Automated)"

    Create `.github/workflows/docs.yml`:

    ```yaml
    name: Deploy Docs
    on:
      push:
        branches: [main]
      workflow_dispatch:

    permissions:
      contents: write

    jobs:
      deploy:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          
          - name: Setup Python
            uses: actions/setup-python@v5
            with:
              python-version: '3.13'
              
          - name: Install uv
            uses: astral-sh/setup-uv@v4
            
          - name: Install dependencies
            run: uv sync --group dev
            
          - name: Deploy to GitHub Pages
            run: uv run mkdocs gh-deploy --force
    ```

**Enable GitHub Pages**:

1. Go to repository **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: **gh-pages** / **(root)**
4. Save

**Your docs will be at**: `https://thisismygitrepo.github.io/machineconfig/`

---

### 2. Cloudflare Pages

**Best for**: Fast global CDN, unlimited bandwidth

**Pros**:
- Unlimited bandwidth (free tier)
- Global CDN (300+ locations)
- Automatic HTTPS
- Custom domains
- Preview deployments for PRs

**Setup**:

1. Go to [Cloudflare Pages](https://pages.cloudflare.com/)
2. Connect your GitHub repository
3. Configure build settings:

| Setting | Value |
|---------|-------|
| Build command | `pip install mkdocs-material mkdocstrings[python] && mkdocs build` |
| Build output directory | `site` |
| Root directory | `/` |

**Or use a build script** - create `build_docs.sh`:

```bash
#!/bin/bash
pip install uv
uv sync --group dev
uv run mkdocs build
```

Then set build command to: `bash build_docs.sh`

---

### 3. Netlify

**Best for**: Easy setup, good free tier

**Pros**:
- 100GB bandwidth/month (free)
- Automatic HTTPS
- Custom domains
- Deploy previews
- Form handling

**Setup**:

1. Go to [Netlify](https://www.netlify.com/)
2. Import your GitHub repository
3. Configure:

| Setting | Value |
|---------|-------|
| Build command | `pip install mkdocs-material mkdocstrings[python] && mkdocs build` |
| Publish directory | `site` |

**Or create `netlify.toml`**:

```toml
[build]
  command = "pip install mkdocs-material mkdocstrings[python] mkdocs-autorefs && mkdocs build"
  publish = "site"

[build.environment]
  PYTHON_VERSION = "3.11"
```

---

### 4. Vercel

**Best for**: Fast deployments, serverless functions

**Pros**:
- Unlimited bandwidth (fair use)
- Global edge network
- Automatic HTTPS
- Preview deployments

**Setup**:

1. Go to [Vercel](https://vercel.com/)
2. Import repository
3. Create `vercel.json`:

```json
{
  "buildCommand": "pip install mkdocs-material mkdocstrings[python] && mkdocs build",
  "outputDirectory": "site",
  "installCommand": "pip install mkdocs"
}
```

---

### 5. GitLab Pages

**Best for**: GitLab users

**Pros**:
- Free for public/private repos
- Automatic HTTPS
- CI/CD integration

**Setup** - create `.gitlab-ci.yml`:

```yaml
image: python:3.11

pages:
  stage: deploy
  script:
    - pip install mkdocs-material mkdocstrings[python]
    - mkdocs build --site-dir public
  artifacts:
    paths:
      - public
  only:
    - main
```

---

### 6. Read the Docs

**Best for**: Python projects, versioned docs

**Pros**:
- Free for open source
- Automatic versioning
- PDF/ePub generation
- Search across versions

**Setup**:

1. Go to [Read the Docs](https://readthedocs.org/)
2. Import your repository
3. Create `.readthedocs.yaml`:

```yaml
version: 2

build:
  os: ubuntu-22.04
  tools:
    python: "3.11"

mkdocs:
  configuration: mkdocs.yml

python:
  install:
    - requirements: docs/requirements.txt
```

Create `docs/requirements.txt`:

```
mkdocs>=1.6.0
mkdocs-material>=9.7.0
mkdocstrings[python]>=1.0.0
mkdocs-autorefs>=1.0.0
```

---

### 7. Render

**Best for**: Simple static hosting

**Pros**:
- 100GB bandwidth/month
- Automatic HTTPS
- Custom domains

**Setup**:

1. Go to [Render](https://render.com/)
2. New → Static Site
3. Connect repository
4. Configure:

| Setting | Value |
|---------|-------|
| Build Command | `pip install mkdocs-material mkdocstrings[python] && mkdocs build` |
| Publish Directory | `site` |

---

### 8. Surge.sh

**Best for**: Quick CLI deployments

**Pros**:
- Simple CLI
- Free custom domains
- Unlimited publishing

**Setup**:

```bash
# Install surge
npm install -g surge

# Build docs
uv run mkdocs build

# Deploy
cd site && surge
```

First time will prompt for email/password. Your docs will be at `https://random-name.surge.sh`

**Custom domain**:

```bash
surge site/ yourdomain.surge.sh
```

---

### 9. Firebase Hosting

**Best for**: Google ecosystem users

**Pros**:
- 10GB storage, 360MB/day transfer (free)
- Global CDN
- Custom domains

**Setup**:

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login
firebase login

# Initialize
firebase init hosting

# Build docs
uv run mkdocs build

# Deploy
firebase deploy --only hosting
```

Configure `firebase.json`:

```json
{
  "hosting": {
    "public": "site",
    "ignore": ["firebase.json", "**/.*", "**/node_modules/**"]
  }
}
```

---

## Comparison Table

| Platform | Bandwidth | Custom Domain | HTTPS | Build Time | Best For |
|----------|-----------|---------------|-------|------------|----------|
| **GitHub Pages** | 100GB/mo | Yes | Yes | ~1 min | GitHub projects |
| **Cloudflare Pages** | Unlimited | Yes | Yes | ~30 sec | Performance |
| **Netlify** | 100GB/mo | Yes | Yes | ~1 min | Ease of use |
| **Vercel** | Unlimited* | Yes | Yes | ~30 sec | Speed |
| **GitLab Pages** | Unlimited | Yes | Yes | ~2 min | GitLab users |
| **Read the Docs** | Unlimited | Yes | Yes | ~2 min | Versioned docs |
| **Render** | 100GB/mo | Yes | Yes | ~1 min | Simplicity |
| **Surge** | Unlimited | Yes | Yes | Instant | Quick deploys |
| **Firebase** | 360MB/day | Yes | Yes | ~1 min | Google users |

*Fair use policy applies

---

## Custom Domain Setup

Most platforms follow similar steps:

1. **Add domain in platform settings**
2. **Configure DNS**:
   
   For apex domain (example.com):
   ```
   A     @     185.199.108.153  (GitHub Pages IP)
   A     @     185.199.109.153
   A     @     185.199.110.153
   A     @     185.199.111.153
   ```
   
   For subdomain (docs.example.com):
   ```
   CNAME docs  thisismygitrepo.github.io
   ```

3. **Wait for DNS propagation** (up to 24 hours)
4. **Enable HTTPS** in platform settings

---

## Recommended Setup

For **machineconfig**, I recommend **GitHub Pages** with GitHub Actions:

1. **Free** and integrated with your repo
2. **Automatic deploys** on every push
3. **No configuration** needed beyond the workflow file
4. **Custom domain** support when ready

### Quick Start

```bash
# Deploy now
uv run mkdocs gh-deploy

# Your docs are live at:
# https://thisismygitrepo.github.io/machineconfig/
```

---

## Local Network Sharing

Share docs on your local network:

```bash
# Find your local IP
ip addr | grep "inet " | grep -v 127.0.0.1

# Serve on all interfaces
uv run mkdocs serve --dev-addr=0.0.0.0:8000
```

Others on your network can access at `http://YOUR_IP:8000`

---

## Docker Deployment

For self-hosted scenarios:

```dockerfile
FROM python:3.13-slim

WORKDIR /docs
COPY . .

RUN pip install mkdocs-material mkdocstrings[python] mkdocs-autorefs
RUN mkdocs build

FROM nginx:alpine
COPY --from=0 /docs/site /usr/share/nginx/html
EXPOSE 80
```

Build and run:

```bash
docker build -t machineconfig-docs .
docker run -p 8080:80 machineconfig-docs
```
