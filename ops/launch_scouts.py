"""Start the read-only scout sessions (one per target repo) and record their ids."""
import json
import sys
from pathlib import Path

from ops.devin_client import DevinClient, load_env

ROOT = Path(__file__).resolve().parent.parent
TARGETS = {
    "SCOUT-SLUGIFY": ("ryyansafar/python-slugify", "Find where python-slugify turns Malayalam vowel signs and chillus into hyphens or drops them (the allow_unicode path and the regex pattern), and how the text is normalised."),
    "SCOUT-MD": ("ryyansafar/markdown", "Find where Python-Markdown's toc extension builds heading ids (slugify and slugify_unicode) and show how Malayalam headings become empty or lose vowel signs."),
    "SCOUT-SARVA": ("ryyansafar/sarvavijnanakosam", "This is a data repository. Report which files and columns contain the OLD chillu encoding (consonant + virama U+0D4D + ZWJ U+200D) and count the rows. Do not edit anything."),
    "SCOUT-MAP": ("ryyansafar/map.opendatakerala.org", "Find the search, sort and display code (for example site/assets/search.js and any name matching) and report where a chillu written in one encoding cannot match the other, and where a zero-width joiner is dropped."),
}


def main(env_path: str) -> None:
    env = load_env(env_path)
    ids = json.loads((ROOT / ".devin_ids.json").read_text())
    schema = json.loads((ROOT / "devin/scout.schema.json").read_text())
    client = DevinClient(env["DEVIN_TOKEN"], env["DEVIN_ORG"])
    out = {}
    for role, (repo, goal) in TARGETS.items():
        prompt = (
            f"@playbook:{ids['!chillu-scout']}\n"
            f"ROLE: {role}. TARGET REPO: https://github.com/{repo} (a fork; read only, never edit).\n"
            f"GOAL: {goal}\n"
            "Fixtures with sample Malayalam strings: https://github.com/ryyansafar/chillucheck/tree/main/fixtures "
            "(smc-person-names.txt, smc-places.txt). Known samples: 'അടൂർ', 'ക്ഷേത്രം ഉത്സവം', 'അവൻ'.\n"
            "Follow the playbook. Output only the structured JSON. If a message starts with INTERRUPT, commit nothing, "
            "write your notes, end them with NEXT:, and reply STOPPED AT CHECKPOINT."
        )
        res = client.create_session(prompt, title=role, tags=["chillu", "scout", role.lower()],
                                    max_acu_limit=3, playbook_id=ids["!chillu-scout"],
                                    structured_output_schema=schema)
        out[role] = {"session_id": res.get("session_id"), "url": res.get("url")}
        print(role, "->", res.get("url"))
    (ROOT / ".scouts.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
