"""CLI commands for managing Kandji tenants"""

import logging
import os
import shutil
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich import box
from rich.table import Table

from kst import git
from kst.cli.common import RepoPathOption
from kst.cli.new import new_repo
from kst.console import OutputConsole, epilog_text
from kst.tenant_manager import get_tenant_manager
from kst.utils import change_directory

console = OutputConsole(logging.getLogger(__name__))

app = typer.Typer(rich_markup_mode="rich")


@app.command(name="add", epilog=epilog_text)
def add_tenant(
    name: Annotated[
        str, 
        typer.Argument(help="Unique name for this tenant")
    ],
    tenant_url: Annotated[
        str, 
        typer.Option(
            "--tenant-url", 
            "-u", 
            help="Kandji tenant API URL",
            prompt="Enter Kandji Tenant API URL"
        )
    ],
    api_token: Annotated[
        str, 
        typer.Option(
            "--api-token", 
            "-t", 
            help="Kandji API token",
            prompt="Enter API Token",
            hide_input=True
        )
    ],
    repo_path: Annotated[
        Optional[str], 
        typer.Option(
            "--repo-path", 
            "-r", 
            help="Path for the tenant repository. If not provided, a directory with the tenant name will be created in the current directory."
        )
    ] = None,
    create_repo: Annotated[
        bool,
        typer.Option(
            "--create-repo",
            help="Create a new repository if it doesn't exist"
        )
    ] = False,
):
    """Add a new Kandji tenant"""
    
    tenant_manager = get_tenant_manager()
    
    # Set default repo path to tenant name in current directory if not provided
    if repo_path is None:
        repo_path = str(Path.cwd() / name)
    
    repo_path = Path(repo_path).expanduser().resolve()
    
    # Create repository if requested and it doesn't exist
    if create_repo and not repo_path.exists():
        console.print(f"Creating new repository at {repo_path}...")
        new_repo(str(repo_path))
    
    # Check if repository exists
    if not repo_path.exists():
        msg = f"Repository path {repo_path} does not exist. Use --create-repo to create it automatically."
        console.error(msg)
        raise typer.BadParameter(msg)
    
    # Add the tenant
    try:
        tenant = tenant_manager.add_tenant(name, tenant_url, api_token, str(repo_path))
        console.print_success(f"Added tenant '{name}' with repository at {tenant.repo_path}")
        console.print(f"Use 'kst tenant switch {name}' to activate this tenant and change to its directory")
    except ValueError as e:
        console.error(str(e))
        raise typer.Exit(code=1)


@app.command(name="list", epilog=epilog_text)
def list_tenants():
    """List all configured Kandji tenants"""
    
    tenant_manager = get_tenant_manager()
    tenants = tenant_manager.list_tenants()
    active_tenant = tenant_manager.get_active_tenant()
    
    if not tenants:
        console.print("No tenants configured. Use 'kst tenant add' to add a tenant.")
        return
    
    table = Table(title="Configured Kandji Tenants", box=box.SIMPLE)
    table.add_column("Name", style="bold")
    table.add_column("Active", width=8)
    table.add_column("Tenant URL")
    table.add_column("Repository Path")
    
    for tenant in tenants:
        is_active = tenant.name == active_tenant.name if active_tenant else False
        table.add_row(
            tenant.name,
            "[green]✓" if is_active else "",
            tenant.tenant_url,
            tenant.repo_path
        )
    
    console.print(table)


@app.command(name="switch", epilog=epilog_text)
def switch_tenant(
    name: Annotated[str, typer.Argument(help="Name of the tenant to switch to")],
    no_change_dir: Annotated[
        bool,
        typer.Option(
            "--no-change-dir",
            "-n",
            help="Do not change to the tenant's repository directory"
        )
    ] = False,
):
    """Switch to a different Kandji tenant"""

    tenant_manager = get_tenant_manager()

    try:
        tenant = tenant_manager.switch_tenant(name)
        console.print_success(f"Switched to tenant '{tenant.name}'")

        # Change directory by default unless --no-change-dir is specified
        if not no_change_dir:
            change_directory(tenant.repo_path)
            console.print(f"Changed directory to {tenant.repo_path}")
    except ValueError as e:
        console.error(str(e))
        raise typer.Exit(code=1)


@app.command(name="current", epilog=epilog_text)
def show_current_tenant():
    """Show the current active Kandji tenant"""
    
    tenant_manager = get_tenant_manager()
    tenant = tenant_manager.get_active_tenant()
    
    if tenant is None:
        console.print("No active tenant configured. Use 'kst tenant switch' to activate a tenant.")
        return
    
    table = Table(title=f"Active Tenant: {tenant.name}", box=box.SIMPLE)
    table.add_column("Property", style="bold")
    table.add_column("Value")
    
    table.add_row("Name", tenant.name)
    table.add_row("Tenant URL", tenant.tenant_url)
    table.add_row("Repository Path", tenant.repo_path)
    
    console.print(table)


@app.command(name="remove", epilog=epilog_text)
def remove_tenant(
    name: Annotated[str, typer.Argument(help="Name of the tenant to remove")],
    delete_repo: Annotated[
        bool,
        typer.Option(
            "--delete-repo",
            help="Delete the repository directory as well (DANGEROUS!)"
        )
    ] = False,
):
    """Remove a Kandji tenant configuration"""
    
    tenant_manager = get_tenant_manager()
    
    # Get the tenant before removing it
    tenant = tenant_manager.get_tenant(name)
    if tenant is None:
        console.error(f"Tenant '{name}' does not exist")
        raise typer.Exit(code=1)
    
    repo_path = tenant.repo_path
    
    try:
        tenant_manager.remove_tenant(name)
        console.print_success(f"Removed tenant '{name}'")
        
        # Delete repository if requested
        if delete_repo and Path(repo_path).exists():
            confirm = typer.confirm(
                f"Are you sure you want to delete the repository at {repo_path}?",
                default=False
            )
            
            if confirm:
                shutil.rmtree(repo_path)
                console.print_success(f"Deleted repository at {repo_path}")
    except ValueError as e:
        console.error(str(e))
        raise typer.Exit(code=1)


@app.command(name="update", epilog=epilog_text)
def update_tenant(
    name: Annotated[str, typer.Argument(help="Name of the tenant to update")],
    tenant_url: Annotated[
        Optional[str], 
        typer.Option(
            "--tenant-url", 
            "-u", 
            help="New Kandji tenant API URL"
        )
    ] = None,
    api_token: Annotated[
        Optional[str], 
        typer.Option(
            "--api-token", 
            "-t", 
            help="New Kandji API token"
        )
    ] = None,
    repo_path: Annotated[
        Optional[str], 
        typer.Option(
            "--repo-path", 
            "-r", 
            help="New path for the tenant repository"
        )
    ] = None,
):
    """Update a Kandji tenant configuration"""
    
    tenant_manager = get_tenant_manager()
    
    # Validate the repository path if provided
    if repo_path is not None:
        repo_path = str(Path(repo_path).expanduser().resolve())
        
        if not Path(repo_path).exists():
            msg = f"Repository path {repo_path} does not exist"
            console.error(msg)
            raise typer.BadParameter(msg)
    
    try:
        tenant = tenant_manager.update_tenant(
            name, 
            tenant_url=tenant_url, 
            api_token=api_token, 
            repo_path=repo_path
        )
        console.print_success(f"Updated tenant '{tenant.name}'")
    except ValueError as e:
        console.error(str(e))
        raise typer.Exit(code=1)