from __future__ import annotations

import configparser
import json
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


KNOWN_TABLES = (
    "tv_shows",
    "tv_episodes",
    "history",
    "scene_exceptions",
    "scene_numbering",
    "info",
)


@dataclass(slots=True)
class TableExport:
    name: str
    columns: list[str]
    rows: list[dict[str, Any]]


@dataclass(slots=True)
class MigrationManifest:
    source_database: str
    sqlite_user_version: int
    tables: list[TableExport]
    config: dict[str, dict[str, str]]
    warnings: list[str]

    @property
    def counts(self) -> dict[str, int]:
        return {table.name: len(table.rows) for table in self.tables}

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["counts"] = self.counts
        payload["format"] = "tv-manager-v12-migration-manifest"
        payload["format_version"] = 1
        return payload


def _quote_identifier(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def _table_names(connection: sqlite3.Connection) -> set[str]:
    rows = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()
    return {str(row[0]) for row in rows}


def _export_table(connection: sqlite3.Connection, name: str) -> TableExport:
    cursor = connection.execute(f"SELECT * FROM {_quote_identifier(name)}")
    columns = [item[0] for item in cursor.description or ()]
    rows = [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]
    return TableExport(name=name, columns=columns, rows=rows)


def read_config(path: str | Path | None) -> dict[str, dict[str, str]]:
    if path is None:
        return {}
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(config_path)
    parser = configparser.ConfigParser(interpolation=None)
    parser.optionxform = str
    parser.read(config_path, encoding="utf-8")
    return {section: dict(parser.items(section)) for section in parser.sections()}


def export_sickchill_database(
    database: str | Path,
    *,
    config_path: str | Path | None = None,
    include_tables: Iterable[str] = KNOWN_TABLES,
) -> MigrationManifest:
    """Create a lossless JSON-friendly snapshot of migration-relevant data.

    The exporter opens SQLite in read-only mode and does not mutate the legacy
    SickChill database. Unknown tables are left in place and reported so v12 can
    add explicit migration handlers before cutover.
    """

    database_path = Path(database).expanduser().resolve()
    if not database_path.exists():
        raise FileNotFoundError(database_path)

    uri = f"file:{database_path.as_posix()}?mode=ro"
    warnings: list[str] = []
    exports: list[TableExport] = []

    with sqlite3.connect(uri, uri=True) as connection:
        connection.row_factory = None
        user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
        existing = _table_names(connection)
        requested = list(dict.fromkeys(include_tables))
        for name in requested:
            if name in existing:
                exports.append(_export_table(connection, name))
            else:
                warnings.append(f"expected table not present: {name}")

        unhandled = sorted(existing - set(requested))
        if unhandled:
            warnings.append("unhandled legacy tables: " + ", ".join(unhandled))

    return MigrationManifest(
        source_database=str(database_path),
        sqlite_user_version=user_version,
        tables=exports,
        config=read_config(config_path),
        warnings=warnings,
    )


def write_manifest(manifest: MigrationManifest, destination: str | Path) -> Path:
    destination_path = Path(destination).expanduser().resolve()
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    destination_path.write_text(json.dumps(manifest.to_dict(), indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    return destination_path
