# Using Multi-Tenant KST

This document provides practical instructions for using the multi-tenant version of KST that you've installed.

## Starting KST

You have several options to start the multi-tenant KST:

### Option 1: Direct execution from the virtual environment (recommended for scripting)

```bash
cd ~/GitHub/kst
source venv/bin/activate
kst tenant list
```

### Option 2: Using the wrapper script

```bash
~/bin/kst-multi tenant list
```

Add this to your PATH in ~/.zshrc for easier access:
```bash
export PATH="$HOME/bin:$PATH"
```

Then you can simply use:
```bash
kst-multi tenant list
```

## Getting Started with Multi-Tenant Features

1. **Add your first tenant**:
   ```bash
   kst-multi tenant add client1 --tenant-url https://client1.api.kandji.io --api-token "your-token" --create-repo
   ```

2. **List configured tenants**:
   ```bash
   kst-multi tenant list
   ```

3. **Switch to a tenant**:
   ```bash
   kst-multi tenant switch client1
   ```

4. **Use the active tenant's credentials automatically**:
   ```bash
   kst-multi profile pull --all
   ```

5. **Automatically change directory to tenant's repository**:
   ```bash
   kst-multi --auto-cd profile list
   ```

6. **Show the current active tenant**:
   ```bash
   kst-multi tenant current
   ```

## Detailed Documentation

For more detailed instructions, see:
- [MULTI_TENANT.md](/Users/robbybarnes/GitHub/kst/MULTI_TENANT.md) for comprehensive multi-tenant documentation
- [README.md](/Users/robbybarnes/GitHub/kst/README.md) for general KST documentation