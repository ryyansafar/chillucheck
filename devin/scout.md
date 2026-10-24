# Overview
Find text-handling code in one repository that breaks Malayalam text, and report it as data. You never write files, open pull requests, or run the live site. You only read.

# What you need
- The repository (given in the prompt) and the six checks below.
- The fixtures: `fixtures/` in https://github.com/ryyansafar/chillucheck (read them for sample strings).

# The six checks
1. Truncation: slicing or truncating user text by code points (`s[:n]`, `substr`, `truncate`), which can cut a letter in half.
2. Slugs and anchors: any slug, anchor or id generator that strips non-ASCII or treats vowel signs (Unicode categories Mc and Mn) as punctuation.
3. Search and matching: comparing or searching names where a chillu can be written two ways (atomic U+0D7B-style, or consonant + virama U+0D4D + ZWJ U+200D).
4. Sorting and de-duplication of names with default string comparison.
5. Joiner loss: any `.replace` or regex that removes U+200D or U+200C.
6. Data files that contain the old chillu encoding.

# Procedure
1. Read `docs/scope.md` if present. Search the repository for the patterns above (grep for slug, truncate, slice, substr, sort, search, includes, startsWith, replace of zero-width characters).
2. For each hit, produce one sample string from the fixtures that makes it fail, and say how it fails.
3. Rank by confidence. Report at most 10 findings.

# Specifications
- Every finding must include a failing sample. Do not report a finding you cannot back with a sample.
- Output JSON only, in the structured output schema.

# Forbidden
Writing or editing files, opening pull requests, calling the live website, guessing without a sample.
