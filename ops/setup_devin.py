"""One-time setup: create the two playbooks and save their ids (never the token)."""
import json
import sys
from pathlib import Path

from ops.devin_client import DevinClient, load_env

ROOT = Path(__file__).resolve().parent.parent


def main(env_path: str) -> None:
    env = load_env(env_path)
    client = DevinClient(env["DEVIN_TOKEN"], env["DEVIN_ORG"])
    ids = {}
    for macro, title, body_file, schema_file in (
        ("!chillu-scout", "Chillu scout (read-only)", "devin/scout.md", "devin/scout.schema.json"),
        ("!chillu-fix", "Chillu fix (test, fix, fork PR)", "devin/fix.md", "devin/fix.schema.json"),
    ):
        body = (ROOT / body_file).read_text()
        schema = json.loads((ROOT / schema_file).read_text())
        out = client.create_playbook(title, body, macro, schema)
        ids[macro] = out.get("playbook_id") or out.get("id") or out
        print(macro, "->", ids[macro])
    (ROOT / ".devin_ids.json").write_text(json.dumps(ids, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
