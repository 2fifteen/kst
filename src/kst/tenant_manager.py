"""Tenant Manager for Multi-Tenant support in KST"""

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import platformdirs
import typer

from kst.__about__ import APP_NAME
from kst.api import ApiConfig
from kst.console import OutputConsole

console = OutputConsole(logging.getLogger(__name__))


@dataclass
class TenantConfig:
    """Configuration for a Kandji tenant"""
    name: str
    tenant_url: str
    api_token: str
    repo_path: str

    @property
    def api_config(self) -> ApiConfig:
        """Convert to ApiConfig for use with API client"""
        return ApiConfig(tenant_url=self.tenant_url, api_token=self.api_token)


class TenantManager:
    """Manages multiple Kandji tenant configurations"""

    def __init__(self):
        self.config_dir = platformdirs.user_config_path(appname=APP_NAME)
        self.config_file = self.config_dir / 'tenants.json'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._tenants: Dict[str, TenantConfig] = {}
        self._active_tenant: Optional[str] = None
        self._load_config()

    def _load_config(self):
        """Load tenant configuration from file"""
        if not self.config_file.exists():
            self._tenants = {}
            self._active_tenant = None
            return

        try:
            with self.config_file.open('r') as f:
                data = json.load(f)
                self._tenants = {
                    name: TenantConfig(
                        name=name,
                        tenant_url=cfg['tenant_url'],
                        api_token=cfg['api_token'],
                        repo_path=cfg['repo_path'],
                    )
                    for name, cfg in data.get('tenants', {}).items()
                }
                self._active_tenant = data.get('active_tenant')
        except (json.JSONDecodeError, KeyError) as e:
            console.print_error(f"Error loading tenant configuration: {e}")
            self._tenants = {}
            self._active_tenant = None

    def _save_config(self):
        """Save tenant configuration to file"""
        data = {
            'active_tenant': self._active_tenant,
            'tenants': {
                name: {
                    'tenant_url': t.tenant_url,
                    'api_token': t.api_token,
                    'repo_path': t.repo_path,
                }
                for name, t in self._tenants.items()
            }
        }
        
        with self.config_file.open('w') as f:
            json.dump(data, f, indent=2)

    def add_tenant(self, name: str, tenant_url: str, api_token: str, repo_path: str) -> TenantConfig:
        """Add a new tenant configuration"""
        if name in self._tenants:
            raise ValueError(f"Tenant '{name}' already exists")
        
        # Ensure the repository path is absolute
        repo_path = Path(repo_path).expanduser().resolve().as_posix()
        
        # Create tenant configuration
        tenant = TenantConfig(
            name=name,
            tenant_url=tenant_url,
            api_token=api_token,
            repo_path=repo_path
        )
        
        self._tenants[name] = tenant
        
        # Set as active tenant if none is set
        if self._active_tenant is None:
            self._active_tenant = name
            
        self._save_config()
        return tenant

    def update_tenant(self, name: str, tenant_url: Optional[str] = None, 
                     api_token: Optional[str] = None, repo_path: Optional[str] = None) -> TenantConfig:
        """Update an existing tenant configuration"""
        if name not in self._tenants:
            raise ValueError(f"Tenant '{name}' does not exist")
            
        tenant = self._tenants[name]
        
        if tenant_url is not None:
            tenant.tenant_url = tenant_url
            
        if api_token is not None:
            tenant.api_token = api_token
            
        if repo_path is not None:
            # Ensure the repository path is absolute
            tenant.repo_path = Path(repo_path).expanduser().resolve().as_posix()
            
        self._save_config()
        return tenant

    def remove_tenant(self, name: str) -> None:
        """Remove a tenant configuration"""
        if name not in self._tenants:
            raise ValueError(f"Tenant '{name}' does not exist")
            
        del self._tenants[name]
        
        # If the active tenant was removed, set to None or another tenant
        if self._active_tenant == name:
            self._active_tenant = next(iter(self._tenants.keys())) if self._tenants else None
            
        self._save_config()

    def switch_tenant(self, name: str) -> TenantConfig:
        """Switch to a different tenant"""
        if name not in self._tenants:
            raise ValueError(f"Tenant '{name}' does not exist")
            
        self._active_tenant = name
        self._save_config()
        return self._tenants[name]

    def get_tenant(self, name: str) -> Optional[TenantConfig]:
        """Get a tenant configuration by name"""
        return self._tenants.get(name)

    def get_active_tenant(self) -> Optional[TenantConfig]:
        """Get the active tenant configuration"""
        if not self._active_tenant:
            return None
        return self._tenants.get(self._active_tenant)

    def list_tenants(self) -> List[TenantConfig]:
        """List all tenant configurations"""
        return list(self._tenants.values())

    def set_environment_for_active_tenant(self) -> bool:
        """Set environment variables for the active tenant"""
        active_tenant = self.get_active_tenant()
        if not active_tenant:
            return False
            
        os.environ['KST_TENANT'] = active_tenant.tenant_url
        os.environ['KST_TOKEN'] = active_tenant.api_token
        return True

    def change_directory_to_active_tenant(self) -> Optional[str]:
        """Get the repository path for the active tenant"""
        active_tenant = self.get_active_tenant()
        if not active_tenant:
            return None
        return active_tenant.repo_path


# Singleton instance of the tenant manager
_tenant_manager = None

def get_tenant_manager() -> TenantManager:
    """Get the singleton tenant manager instance"""
    global _tenant_manager
    if _tenant_manager is None:
        _tenant_manager = TenantManager()
    return _tenant_manager