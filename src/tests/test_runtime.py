"""Exercise startup imports with isolated configuration and no external services."""

import os
from pathlib import Path
import subprocess
import sys
import textwrap


SRC = Path(__file__).resolve().parents[1]


def run_python(code, tmp_path, **env):
    result = subprocess.run(
        [sys.executable, "-c", textwrap.dedent(code)],
        cwd=tmp_path,
        env={
            **os.environ,
            "PYTHONPATH": os.pathsep.join((str(tmp_path), str(SRC), str(SRC / "plugins"))),
            **env,
        },
        capture_output=True,
        text=True,
        timeout=45,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_hub_and_plugins_load(tmp_path):
    (tmp_path / "config.py").write_text(
        textwrap.dedent(
            f"""\
            from config_hub import *
            HUB_DB_BACKEND = {{"module": "biothings.utils.sqlite3", "sqlite_db_folder": {str(tmp_path)!r}}}
            DATA_HUB_DB_DATABASE = "runtime_hub"
            DATA_SRC_DATABASE = "runtime_sources"
            DATA_ARCHIVE_ROOT = {str(tmp_path)!r}
            LOG_FOLDER = {str(tmp_path)!r}
            """
        )
    )
    run_python(
        """\
        from importlib import import_module
        from biothings.hub import HubServer
        import hub.dataload.sources
        import plugins.msigdb
        import plugins.wikipathways

        for name in ("ctd", "do", "go", "kegg", "reactome", "smpdb"):
            import_module(f"plugins.{name}.parser")

        server = HubServer(hub.dataload.sources)
        server.configure_ioloop()
        """,
        tmp_path,
        HUB_CONFIG="config",
    )


def test_web_application_loads(tmp_path):
    (tmp_path / "config.py").write_text("from config_web import *\n")
    run_python(
        """\
        import asyncio
        import config
        from biothings.web.applications import TornadoBiothingsAPI
        from biothings.web.settings.configs import load

        async def check_app():
            app = TornadoBiothingsAPI.get_app(load(config))
            assert app.biothings.pipeline is not None

        asyncio.run(check_app())
        """,
        tmp_path,
    )
