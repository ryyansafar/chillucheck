# Overview
Turn ONE reproduced finding into a failing test, a minimal fix, and a pull request on the FORK. A human presses merge.

# What you need
The finding block (file, line, pattern, sample, fix class), the fork repository, and the fixtures from https://github.com/ryyansafar/chillucheck.

# Procedure
1. Read the finding. Add a test from the sample that FAILS on main, and show the red run.
2. Fix it minimally: cut and reverse by grapheme clusters (`regex` `\X` in Python, `Intl.Segmenter` in JavaScript); keep vowel signs and viramas (`\p{M}`); fold chillus (old form to atomic) only when COMPARING or SORTING; prefer ICU collation where available.
3. Run all tests, including the repository's own. All must pass.
4. Open the pull request on the FORK. The body contains the output JSON and a line saying a Devin session prepared this pull request.
5. Wait for Devin Review and fix its findings, at most 3 rounds.
6. If you learned something reusable, propose a skill.

# Specifications
- Smallest possible diff, at most 3 files, no new dependencies without asking.
- Never remove a ZWJ or ZWNJ from data. Only change the data column named in the finding.

# Forbidden
Merging, touching the checker or fixtures, removing joiners, changing columns not named, opening pull requests on upstream repositories.
