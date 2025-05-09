# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Kandji Sync Toolkit (kst) is a utility for managing resources via the Kandji API. It allows users to:
- Create and sync a local repository of custom profiles or scripts with a Kandji tenant
- Import existing profiles and scripts
- List or show details of local and remote resources
- Format output as YAML, plist, or JSON for use with other tools
- Manage multiple Kandji tenants with the custom multi-tenant extension

## Development Environment

### Setup

The project uses uv for Python dependency management:

```
# Create virtual environment
uv venv

# Install dev dependencies
uv pip install -e ".[dev]"
```

For development with the multi-tenant extension:
```
# Create a virtual environment
python3 -m venv venv

# Activate and install in development mode
source venv/bin/activate
pip install -e .
```

### Common Commands

```
# Run all linting, formatting, and tests
uv run poe all

# Run just linting
uv run poe lint

# Run just formatting
uv run poe format

# Run tests
uv run poe test

# Run specific test file
uv run pytest tests/path/to/test_file.py -v
```

## Project Structure

- `src/kst/`: Main package code
  - `__about__.py`: Version information
  - `api/`: API client modules for interacting with Kandji API
  - `cli/`: Command-line interface code
    - `tenant.py`: Multi-tenant functionality implementation
  - `repository/`: Local repository management
  - `tenant_manager.py`: Core tenant management functionality

## Architecture

KST follows a layered architecture:

1. **CLI Layer** (`cli/`): Command-line interface using Typer for handling user commands
2. **Repository Layer** (`repository/`): Manages local storage of Kandji resources, including:
   - `custom_profile.py` and `custom_script.py`: Handle specific resource types
   - `repository.py`: Core repository management logic
3. **API Layer** (`api/`): Client for communicating with Kandji API
4. **Tenant Management Layer** (`tenant_manager.py`): Handles multi-tenant functionality

The workflow generally follows:
- User issues a command via CLI
- CLI modules process the command and interact with repository objects
- Repository objects handle local operations and use the API client for remote operations
- Results are displayed to the user through the CLI

## Key Concepts

- **Resources**: Kandji configuration items (profiles, scripts) that can be managed
- **Repository**: Local git-based storage of resources with synchronization capabilities
- **Sync Status**: Comparison state between local and remote resources (new, updated, conflicting)
- **Tenant**: A Kandji tenant configuration including API credentials and repository path

## Multi-Tenant Features

This repository includes a custom extension for managing multiple Kandji tenants. Detailed usage instructions can be found in the `MULTI_TENANT.md` file at the root of the repository.

Key multi-tenant commands:
```
# Add a new tenant
kst tenant add NAME --tenant-url URL --api-token TOKEN [--create-repo]

# List configured tenants
kst tenant list

# Switch active tenant
kst tenant switch NAME [--change-dir]

# View current tenant
kst tenant current

# Use active tenant's repository automatically
kst --auto-cd profile pull --all
```

The multi-tenant functionality allows working with multiple Kandji tenants by:
1. Storing tenant configurations in `~/.config/kst/tenants.json`
2. Maintaining separate repositories for each tenant
3. Automatically using the active tenant's credentials
4. Supporting directory switching based on the active tenant