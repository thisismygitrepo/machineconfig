# GitHub Action PyPI Publishing Setup

This repository is configured with a GitHub Action that automatically builds and publishes the package to PyPI when the version in `pyproject.toml` is updated.

## How it works

The workflow triggers on every push to the `main` branch and:

1. **Version Check**: Compares the current version in `pyproject.toml` with the previous commit
2. **Build & Publish**: If the version changed, it builds the package using `uv` and publishes to PyPI
3. **GitHub Release**: Creates a GitHub release with the new version tag
4. **Test Build**: If version hasn't changed or on PRs, it only tests the build process

## Setup Instructions

### 1. Set up PyPI Token

You need to configure a PyPI API token as a GitHub secret:

1. **Generate PyPI API Token**:
   - Go to [PyPI Account Settings](https://pypi.org/manage/account/token/)
   - Click "Add API Token"
   - Set token name (e.g., "GitHub Actions - machineconfig")
   - Set scope to "Entire account" or limit to your package
   - Copy the generated token (starts with `pypi-`)

2. **Add GitHub Secret**:
   - Go to your GitHub repository
   - Navigate to Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `PYPI_TOKEN`
   - Value: Paste your PyPI API token
   - Click "Add secret"

### 2. Publishing a new version

To publish a new version:

1. Update the version in `pyproject.toml`:
   ```toml
   version = "2.99"  # Increment from current version
   ```

2. Commit and push to main:
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to 2.99"
   git push origin main
   ```

3. The GitHub Action will automatically:
   - Detect the version change
   - Build the package using `uv build`
   - Publish to PyPI using `uv publish`
   - Create a GitHub release with tag `v2.99`

### 3. Monitoring the workflow

- Check the "Actions" tab in your GitHub repository to monitor workflow runs
- The workflow will fail if the PyPI token is missing or invalid
- Build artifacts are attached to GitHub releases

### 4. Manual publishing

If you need to publish manually, you can still use the existing script:

```bash
./build_and_publish.sh
```

This script reads the PyPI token from `~/dotfiles/creds/msc/.pypirc` as before.

## Workflow Features

- **Version Detection**: Only publishes when version in `pyproject.toml` changes
- **Pull Request Testing**: Tests builds on PRs without publishing
- **GitHub Releases**: Automatically creates releases with build artifacts
- **Modern tooling**: Uses `uv` for fast, reliable builds and publishing
- **Error Handling**: Fails fast on build or publish errors

## Troubleshooting

- **"Version unchanged"**: The workflow only publishes when the version in `pyproject.toml` changes compared to the previous commit
- **"PyPI token not found"**: Ensure `PYPI_TOKEN` secret is properly set in GitHub repository settings
- **Build failures**: Check the Actions log for detailed error messages
- **Permission errors**: Ensure your PyPI token has sufficient permissions for the package