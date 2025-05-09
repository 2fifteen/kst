# Multi-Tenant Support for Kandji Sync Toolkit

This document explains how to use the multi-tenant functionality to manage multiple Kandji tenants.

## Overview

The multi-tenant extension allows you to:

1. Add and manage multiple Kandji tenant configurations
2. Easily switch between tenants
3. Automatically use the correct API credentials
4. Organize tenant repositories in separate directories

## Getting Started

### Adding a Tenant

To add a new tenant configuration:

```bash
kst tenant add my-tenant --tenant-url https://my-tenant.api.kandji.io --api-token "your-api-token"
```

This will:
- Store your tenant's API URL and token securely
- Create a mapping to a local repository (by default, a folder with the tenant name in your current directory)

To create a new repository at the same time:

```bash
kst tenant add my-tenant --tenant-url https://my-tenant.api.kandji.io --api-token "your-api-token" --create-repo
```

### Listing Tenants

To see all configured tenants:

```bash
kst tenant list
```

### Switching Tenants

To switch to a different tenant:

```bash
kst tenant switch my-tenant
```

This sets the tenant as active, making its credentials automatically available for all kst commands, and automatically changes to the tenant's repository directory.

If you don't want to change directories when switching tenants:

```bash
kst tenant switch my-tenant --no-change-dir
```

### Working with the Active Tenant

Once you've set an active tenant, all `kst` commands will use its API credentials automatically. You can also use the `--auto-cd` flag to automatically change to the tenant's repository directory:

```bash
kst --auto-cd profile pull --all
```

### Viewing the Current Tenant

To check which tenant is currently active:

```bash
kst tenant current
```

### Updating a Tenant

To update a tenant's configuration:

```bash
kst tenant update my-tenant --tenant-url https://new-url.api.kandji.io --api-token "new-token"
```

### Removing a Tenant

To remove a tenant configuration:

```bash
kst tenant remove my-tenant
```

This only removes the configuration, not the repository. To also delete the repository:

```bash
kst tenant remove my-tenant --delete-repo
```

## Command Reference

```
tenant add NAME [OPTIONS]      # Add a new Kandji tenant
tenant list                    # List all configured Kandji tenants
tenant switch NAME [OPTIONS]   # Switch to a different Kandji tenant and change to its directory
tenant current                 # Show the current active Kandji tenant
tenant update NAME [OPTIONS]   # Update a Kandji tenant configuration (e.g., --api-token)
tenant remove NAME [OPTIONS]   # Remove a Kandji tenant configuration
```

## Global Options

```
--auto-cd   # Automatically change to the active tenant's repository directory
```

## Tips for Multiple Tenants

1. Create a logical naming scheme for your tenants (e.g., "prod", "dev", "client-name")
2. Use the `--auto-cd` flag in scripts or aliases to ensure you're always working in the correct directory
3. Organize your tenant repositories in a dedicated parent directory
4. Consider including the tenant name in your repository naming (e.g., "kandji-clientA", "kandji-clientB")

## Technical Details

- Tenant configurations are stored in `~/.config/kst/tenants.json` (platform-specific location)
- Each tenant maps to a specific local repository directory
- When an active tenant is set, its API credentials are automatically used for all commands
- The implementation doesn't modify any existing kst functionality, only extends it