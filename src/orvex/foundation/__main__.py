"""Offline foundation CLI. Does not execute content or contact providers."""

import argparse
import json
from ..core.store import Store
from .services import FoundationServices


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="ORVEX 0.5 foundation · catálogo local (sin autenticación PIN)"
    )
    parser.add_argument("--database", required=True)
    parser.add_argument("--profile", default="adult")
    commands = parser.add_subparsers(dest="command", required=True)
    query = commands.add_parser("list")
    query.add_argument("--kind")
    query.add_argument("--search", default="")
    commands.add_parser("duplicates")
    add = commands.add_parser("register")
    for option in ("kind", "title", "source-type", "source-ref"):
        add.add_argument("--" + option, required=True)
    add.add_argument("--format", default="")
    add.add_argument("--parent")
    add.add_argument("--age", type=int)
    args = parser.parse_args(argv)
    store = Store(args.database)
    try:
        catalog = FoundationServices(store).catalog
        if args.command == "register":
            result = catalog.register(
                args.profile,
                kind=args.kind,
                title=args.title,
                source_type=args.source_type,
                source_ref=args.source_ref,
                format=args.format,
                parent_id=args.parent,
                age=args.age,
            )
            print(
                json.dumps({"id": result.content.id, "created": result.created}, ensure_ascii=False)
            )
        elif args.command == "duplicates":
            print(
                json.dumps(
                    [
                        [{"id": c.id, "title": c.title} for c in group]
                        for group in catalog.find_duplicates(args.profile)
                    ],
                    ensure_ascii=False,
                )
            )
        else:
            print(
                json.dumps(
                    [
                        {
                            "id": c.id,
                            "kind": c.kind,
                            "title": c.title,
                            "age": c.age,
                            "import_state": c.import_state,
                        }
                        for c in catalog.query(args.profile, kind=args.kind, query=args.search)
                    ],
                    ensure_ascii=False,
                )
            )
        return 0
    except (ValueError, PermissionError) as error:
        parser.exit(2, str(error) + "\n")
    finally:
        store.close()


if __name__ == "__main__":
    raise SystemExit(main())
