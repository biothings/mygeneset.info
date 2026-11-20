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


def write_hub_config(tmp_path):
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


def test_hub_and_plugins_load(tmp_path):
    write_hub_config(tmp_path)
    run_python(
        """\
        from importlib import import_module
        from bin.hub import server
        from utils.runtime import require_free_threading
        import plugins.msigdb
        import plugins.wikipathways

        for name in ("ctd", "do", "go", "kegg", "reactome", "smpdb"):
            import_module(f"plugins.{name}.parser")

        server.configure_ioloop()
        require_free_threading()
        """,
        tmp_path,
        HUB_CONFIG="config",
    )


def test_msigdb_xml_sorting_and_parsing(tmp_path):
    write_hub_config(tmp_path)
    run_python(
        """\
        import logging
        from pathlib import Path
        import xml.etree.ElementTree as ET
        from plugins.msigdb.dump import msigdbDumper
        from plugins.msigdb import parser
        from utils.runtime import require_free_threading

        root = ET.Element("MSIGDB", {"VERSION": "2026.1"})
        originals = {}
        for name, organism in (
            ("MOUSE_FIRST", "Mus musculus"),
            ("HUMAN", "Homo sapiens"),
            ("MOUSE_SECOND", "Mus musculus"),
        ):
            attributes = {
                "STANDARD_NAME": name,
                "ORGANISM": organism,
                "DESCRIPTION_BRIEF": 'TNF & IL <b>response</b> (α)',
                "DESCRIPTION_FULL": 'A "quoted" description',
                "SYSTEMATIC_NAME": name,
                "CATEGORY_CODE": "C2",
                "SUB_CATEGORY_CODE": "CP:REACTOME",
                "AUTHORS": "Test Author",
                "MEMBERS": "1",
                "MEMBERS_MAPPING": "1,GENE1,1",
                "CHIP": "Human_NCBI_Gene_ID",
            }
            originals[name] = attributes
            ET.SubElement(root, "GENESET", attributes)
        ET.SubElement(root, "INFO", {"text": "not a geneset"})
        ET.ElementTree(root).write("source.xml", encoding="utf-8", xml_declaration=True)

        dumper = msigdbDumper()
        dumper.logger = logging.getLogger("test_msigdb")
        dumper.sort_xml("source.xml", "human_genesets.xml")
        result = ET.parse("human_genesets.xml").getroot()
        assert result.attrib == root.attrib
        assert [node.get("STANDARD_NAME") for node in result] == ["HUMAN", "MOUSE_FIRST", "MOUSE_SECOND"]
        for node in result:
            assert node.attrib == originals[node.get("STANDARD_NAME")]
        lines = Path("human_genesets.xml").read_text().splitlines()
        assert sum(line.lstrip().startswith("<GENESET") for line in lines) == 3

        class Lookup:
            def __init__(self, species):
                self.species = species
            def query_mygene(self, ids, scopes):
                pass
            def get_results(self, ids):
                return {"genes": [{"mygene_id": "1", "taxid": self.species}], "count": 1}

        parser.MyGeneLookup = Lookup
        docs = list(parser.parse_msigdb("."))
        assert [doc["_id"] for doc in docs] == ["HUMAN", "MOUSE_FIRST", "MOUSE_SECOND"]
        assert [doc["taxid"] for doc in docs] == [9606, 10090, 10090]
        assert all(doc["description"] == 'TNF & IL <b>response</b> (α)' for doc in docs)
        require_free_threading()
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
        from utils.runtime import require_free_threading

        async def check_app():
            app = TornadoBiothingsAPI.get_app(load(config))
            assert app.biothings.pipeline is not None
            require_free_threading()

        asyncio.run(check_app())
        """,
        tmp_path,
    )
