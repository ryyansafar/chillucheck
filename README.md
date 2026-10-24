# Chillu Check

**Type your name or town in Malayalam and watch real software mangle it.** Chillu Check runs the text through nine real code paths that websites use to make links, cut text short, search and sort, shows what breaks, and shows the patched behaviour next to it.

Built for Devin Hacks Kochi (24 Oct 2026), Track: *Make the invisible visible* and *Works anyway*.

## Why
Malayalam letters are often several Unicode code points, and the chillu letters (ൺ ൻ ർ ൽ ൾ ൿ) have **two encodings** that look identical but never compare equal, even after NFC, NFD, NFKC or NFKD. So software that "supports Unicode" still empties links, cuts letters in half, and cannot find a name searched in the other encoding.

Across 2,921 real Malayalam names and places (SMC corpus), **every one** is broken by at least one of the nine paths. Run `python -m chillucheck.corpus` or open the board to see the numbers.

## The nine paths
| Path | What breaks |
|---|---|
| python-slugify (default) | transliterates to ASCII and drops letters |
| python-slugify (allow_unicode) | vowel signs become hyphens |
| Python-Markdown heading anchor | the anchor is empty |
| Python-Markdown anchor (unicode option) | all vowel signs and viramas are stripped |
| Cut to N characters | `s[:5]` cuts a letter in half |
| Search across the two chillu encodings | the old and new spelling never match |
| Default sort | the two spellings sort far apart |
| Strip the joiner (U+200D) | a chillu becomes a bare virama |
| Reverse the text | vowel signs jump to the wrong letter |

## Run it
```bash
python3 -m venv .venv && .venv/bin/pip install python-slugify markdown regex fonttools pytest fastapi uvicorn httpx
.venv/bin/python -m pytest -q                         # the suite
.venv/bin/python -m uvicorn board.app:app --port 8791 # the type-your-name board
```
Open http://127.0.0.1:8791/ and type a name. Everything runs locally; fonts are self-hosted, so it works with the network off.

## How it is checked
Plain code is the judge: the fixtures, the checks and the merge gate are not written by the agents whose work they judge. A fix is accepted only if the suite goes from red to green and nothing that preserves a joiner is removed. Automated checks cover a few behaviours, not all of Malayalam, and no Malayalam linguist has reviewed the rules yet.

## Devin
Devin sessions find the offending code in real open-source projects, write the failing test and the fix on forks, and review each other's pull requests; a human presses merge. The list of sessions and pull requests is in `docs/devin.md`.

## Licences
Code: MIT. Fixtures in `fixtures/` come from the SMC Malayalam corpus, CC BY-SA 3.0 (https://gitlab.com/smc/corpus). Font: Manjari, SIL OFL 1.1.

## Socials & Support
- Portfolio: https://ryyansafar.site
- GitHub: https://github.com/ryyansafar
- Buy Me a Coffee: https://buymeacoffee.com/ryyansafar
- PayPal: https://www.paypal.com/paypalme/ryyansafar
- Razorpay: https://razorpay.me/@ryyansafar
