import logging
import logging.handlers
from pathlib import Path
from typing import Annotated

import platformdirs
import typer

from kst.__about__ import APP_NAME, __version__
from kst.console import OutputConsole, epilog_text

from .new import app as new_app
from .profile import app as profile_app
from .script import app as script_app
from .tenant import app as tenant_app

__all__ = ["app"]

console = OutputConsole(logging.getLogger(__name__))

app = typer.Typer(name=APP_NAME, rich_markup_mode="rich", pretty_exceptions_show_locals=False)
app.add_typer(new_app)
app.add_typer(
    profile_app,
    name="profile",
    help="Interact with Kandji Custom Profiles",
    epilog=epilog_text,
    no_args_is_help=True,
)
app.add_typer(
    script_app,
    name="script",
    help="Interact with Kandji Custom Scripts",
    epilog=epilog_text,
    no_args_is_help=True,
)
app.add_typer(
    tenant_app,
    name="tenant",
    help="Manage multiple Kandji tenants",
    epilog=epilog_text,
    no_args_is_help=True,
)


def version_callback(value: bool) -> None:
    """Callback for the --version flag."""
    if value:
        console.print(f"{APP_NAME}, version {__version__}")
        raise typer.Exit(code=0)


VersionFlag = Annotated[
    bool,
    typer.Option(
        "--version",
        show_default=False,
        help="Show the version.",
        callback=version_callback,
        is_eager=True,
    ),
]
LogPathOption = Annotated[
    str,
    typer.Option(
        "--log",
        show_default=False,
        help="Path to the log file. (use '-' for stdout)",
        rich_help_panel="Logging",
        resolve_path=True,
        allow_dash=True,
    ),
]
DebugFlag = Annotated[
    bool,
    typer.Option(
        "--debug",
        help="Enable debug logging.",
        rich_help_panel="Logging",
    ),
]


AutoCdFlag = Annotated[
    bool,
    typer.Option(
        "--auto-cd",
        help="Automatically change to the active tenant's directory.",
        rich_help_panel="Multi-Tenant",
    ),
]


@app.callback(no_args_is_help=True, epilog=epilog_text)
def main(
    log: LogPathOption = str(platformdirs.user_log_path(appname=APP_NAME) / f"{APP_NAME}.log"),
    debug: DebugFlag = False,
    version: VersionFlag = False,  # noqa: ARG001
    auto_cd: AutoCdFlag = False,
) -> None:
    """Kandji Sync Toolkit, a utility for local management of Kandji resources."""

    if log == "-":
        handlers = [logging.StreamHandler()]
    else:
        log_path = Path(log).expanduser().resolve()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers: list[logging.Handler] = [
            logging.handlers.RotatingFileHandler(filename=log_path, maxBytes=5120000, backupCount=3)
        ]

    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers,
    )
    console.info("--- Starting Kandji Sync Toolkit ---")

    # Handle auto-cd to active tenant's repository if requested
    if auto_cd:
        try:
            from kst.tenant_manager import get_tenant_manager
            from kst.utils import change_directory

            tenant_manager = get_tenant_manager()
            active_tenant = tenant_manager.get_active_tenant()

            if active_tenant:
                try:
                    change_directory(active_tenant.repo_path)
                    console.info(f"Changed directory to active tenant '{active_tenant.name}' repo: {active_tenant.repo_path}")
                except ValueError as e:
                    console.error(f"Failed to change directory: {e}")
            else:
                console.info("No active tenant configured, staying in current directory")
        except (ImportError, Exception) as e:
            console.debug(f"Error during auto-cd: {e}")
            pass  # Don't fail app startup if auto-cd fails


__all__ = ["app"]
