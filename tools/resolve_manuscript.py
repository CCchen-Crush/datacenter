#!/usr/bin/env python3
"""Numbered manuscript from its source: paper/manuscript_source.md -> paper/manuscript.md and paper/labels.json.

Usage: python3 tools/resolve_manuscript.py

The source carries symbolic keys that this script numbers in order of first appearance:
  equations   $$ ... \\label{eq:key}$$ -> \\tag{n}, \\eqref{eq:key} -> (n); keys eqB:... in Appendix B -> (B.n)
  references  [@key] and [@key1; @key2] -> [n] and [n1,n2] (three or more consecutive numbers as a range [n1–n3]);
              the list "## References" holds one entry per line, "[@key]: text", and is written in citation order
labels.json maps every equation key to its number (read by tools/plot_paper.py for the labels of Fig. 2).
Every label must be unique and referenced keys must exist; every reference must be cited.
"""
import json, os, re, sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SRC, OUT, LABELS = (os.path.join(ROOT, "paper", p) for p in ("manuscript_source.md", "manuscript.md", "labels.json"))
NOTE = ("> Draft for *Applied Energy*. Generated from `paper/manuscript_source.md` by `tools/resolve_manuscript.py`; edit the source, "
        "not this file. The numbers of the Abstract, Section 5 and Section 6 come from `tools/paper_numbers.py` applied to "
        "`matlab/results/` (see `paper/numbers.md`), and all figures from `tools/plot_paper.py` (`paper/figures/`).")
LABEL = re.compile(r"\\label\{(eqB?:[^}]+)\}")
EQREF = re.compile(r"\\eqref\{(eqB?:[^}]+)\}")
CITE = re.compile(r"\[(@[\w-]+(?:;\s*@[\w-]+)*)\]")


def compress(nums):
    """[1, 2, 3, 5] -> '1–3,5' (runs of three or more as a range)."""
    nums, out, k = sorted(set(nums)), [], 0
    while k < len(nums):
        j = k
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1: j += 1
        out += [f"{nums[k]}–{nums[j]}"] if j - k >= 2 else [str(n) for n in nums[k:j + 1]]
        k = j + 1
    return ",".join(out)


def resolve(src):
    lines = src.split("\n")
    assert lines[2].startswith("> Source of the manuscript"), "unexpected header note"
    lines[2] = NOTE
    body, refs = "\n".join(lines).split("\n## References\n")
    entries = dict(re.findall(r"^\[@([\w-]+)\]: (.+)$", refs, re.M))
    assert len(entries) == len([l for l in refs.split("\n") if l.strip()]), "malformed reference entry"

    # equations: number the labels in order of appearance (main text, then Appendix B)
    eq = {}
    for key in LABEL.findall(body):
        assert key not in eq, f"duplicate label {key}"
        main = [k for k in eq if k.startswith("eq:")]; app = [k for k in eq if k.startswith("eqB:")]
        eq[key] = str(len(main) + 1) if key.startswith("eq:") else f"B.{len(app) + 1}"
    missing = sorted(set(EQREF.findall(body)) - set(eq))
    assert not missing, f"undefined equation keys: {missing}"
    body = LABEL.sub(lambda m: "\\tag{%s}" % eq[m.group(1)], body)
    body = EQREF.sub(lambda m: f"({eq[m.group(1)]})", body)

    # references: number in order of first citation
    order = []
    for m in CITE.finditer(body):
        for key in re.findall(r"@([\w-]+)", m.group(1)):
            assert key in entries, f"cited key without entry: {key}"
            if key not in order: order.append(key)
    unused = sorted(set(entries) - set(order))
    assert not unused, f"references never cited: {unused}"
    num = {k: i + 1 for i, k in enumerate(order)}
    body = CITE.sub(lambda m: "[" + compress(num[k] for k in re.findall(r"@([\w-]+)", m.group(1))) + "]", body)
    assert "[@" not in body and "\\label" not in body and "\\eqref" not in body
    out = body.rstrip("\n") + "\n\n## References\n\n" + "\n".join(f"[{num[k]}] {entries[k]}" for k in order) + "\n"
    return out, eq, order


def main():
    out, eq, order = resolve(open(SRC).read())
    open(OUT, "w").write(out)
    json.dump({"equations": eq, "references": {k: i + 1 for i, k in enumerate(order)}}, open(LABELS, "w"), indent=1)
    n_main = sum(k.startswith("eq:") for k in eq)
    print(f"wrote {os.path.relpath(OUT, ROOT)}: {n_main} equations, {len(eq) - n_main} in Appendix B, {len(order)} references")


if __name__ == "__main__":
    sys.exit(main())
