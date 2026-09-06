from __future__ import annotations

import argparse
from pathlib import Path

from tvmanager_v12.migration import export_sickchill_database, write_manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export a read-only SickChill database/config snapshot for TV Manager v12 migration."
    )
    parser.add_argument("database", type=Path, help="Path to the legacy sickbeard.db SQLite database")
    parser.add_argument("--config", type=Path, default=None, help="Optional path to legacy config.ini")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("tv-manager-v12-migration.json"),
        help="Destination JSON manifest (default: tv-manager-v12-migration.json)",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    manifest = export_sickchill_database(args.database, config_path=args.config)
    destination = write_manifest(manifest, args.output)
    print(f"TV Manager v12 migration snapshot written to: {destination}")
    for table, count in sorted(manifest.counts.items()):
        print(f"  {table}: {count}")
    for warning in manifest.warnings:
        print(f"WARNING: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
