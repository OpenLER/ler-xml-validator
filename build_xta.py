#!/usr/bin/env python3
"""
build_xta.py — generate per-version xta rule files from featurekatalog's
constraints/{version}/*.yml (natural-language restriction text) plus a
hand-maintained text->XPath dictionary (xta/human_to_xpath.yml).

For every restriction whose exact text is found in the dictionary, emits the
matching XPath into src/lerxml/xta/{version}/{major.minor}_restriktioner.yml.
Restrictions whose text isn't found yet are reported as gaps (not silently
skipped) — the script exits non-zero if there are any, listing exactly what's
missing so the dictionary can be extended.

Usage:
  python build_xta.py
  python build_xta.py --featurekatalog ~/other/path/to/featurekatalog
"""

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent
XTA_DIR = REPO_ROOT / "src" / "lerxml" / "xta"
OUT_DIR = XTA_DIR
DICTIONARY_PATH = REPO_ROOT / "xta" / "human_to_xpath.yml"
VARIABLES_PATH = REPO_ROOT / "xta" / "variabler.yml"

DEFAULT_FEATUREKATALOG = Path("~/a/lerinfo/featurekatalog").expanduser()

VERSIONS = ["2.0.0", "2.0.1", "2.1.0", "2.2.0"]


def to_ascii(name: str) -> str:
    return name.replace("æ", "ae").replace("ø", "oe").replace("å", "aa")


def major_minor(version: str) -> str:
    major, minor, _patch = version.split(".")
    return f"{major}.{minor}"


def normalize(text: str) -> str:
    return text.strip()


def load_dictionary() -> dict[str, dict]:
    """Nøglet på officiel tekst; værdien er enten {"expression": ...} eller
    {"sub_assertions": [...]} - begge tilfælde bliver splattet direkte ind i
    assertion-blokken i build_version()."""
    entries = yaml.safe_load(DICTIONARY_PATH.read_text()) or []
    lookup: dict[str, dict] = {}
    for entry in entries:
        key = normalize(entry["text"])
        if key in lookup:
            raise ValueError(f"human_to_xpath.yml: dublet-tekst: {key!r}")
        if "expression" in entry:
            lookup[key] = {"expression": entry["expression"]}
        else:
            lookup[key] = {"sub_assertions": entry["sub_assertions"]}
    return lookup


def load_variables() -> dict[str, list[dict]]:
    entries = yaml.safe_load(VARIABLES_PATH.read_text()) or []
    return {entry["xsdtype"]: entry.get("variables", []) for entry in entries}


def build_version(
    version: str,
    featurekatalog: Path,
    dictionary: dict[str, dict],
    variables_by_type: dict[str, list[dict]],
) -> tuple[list[dict], list[tuple[str, str, str, str]]]:
    """Return (xta rule blocks, gaps). gaps = [(version, feature_type, assertion_name, text)]."""
    constraints_dir = featurekatalog / "constraints" / version
    blocks = []
    gaps = []

    for yml_path in sorted(constraints_dir.glob("*.yml")):
        feature_type = yml_path.stem
        xsdtype = f"ler:{to_ascii(feature_type)}"

        entries = yaml.safe_load(yml_path.read_text()) or []
        assertions = []
        for entry in entries:
            text = normalize(entry["expression"])
            looked_up = dictionary.get(text)
            if looked_up is None:
                gaps.append((version, feature_type, entry["name"], text))
                continue
            assertions.append({"name": entry["name"], **looked_up})

        if not assertions:
            continue

        block = {"xsdtype": xsdtype}
        if xsdtype in variables_by_type:
            block["variables"] = variables_by_type[xsdtype]
        block["assertions"] = assertions
        blocks.append(block)

    return blocks, gaps


def print_gaps(gaps: list[tuple[str, str, str, str]]) -> None:
    by_text: dict[str, list[tuple[str, str, str]]] = {}
    for version, feature_type, name, text in gaps:
        by_text.setdefault(text, []).append((version, feature_type, name))

    print(f"\nGrupperet efter tekst ({len(by_text)} unikke tekster, flest forekomster først):")
    for text, occurrences in sorted(by_text.items(), key=lambda kv: -len(kv[1])):
        first_line = text.splitlines()[0]
        suffix = "..." if len(text) > len(first_line) or len(first_line) > 90 else ""
        print(f"\n  {len(occurrences)}x  {first_line[:90]}{suffix}")
        for version, feature_type, name in occurrences:
            print(f"        {version:8} {feature_type:20} {name}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--featurekatalog", type=Path, default=DEFAULT_FEATUREKATALOG)
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print alle uoversatte restriktioner, grupperet efter tekst (ikke kun nøgletal)",
    )
    args = parser.parse_args()

    if not (args.featurekatalog / "constraints").is_dir():
        print(f"Finder ikke {args.featurekatalog / 'constraints'}", file=sys.stderr)
        sys.exit(2)

    dictionary = load_dictionary()
    variables_by_type = load_variables()

    all_gaps: list[tuple[str, str, str, str]] = []
    rows: list[tuple[str, int, int]] = []  # (version, total, translated)
    for version in VERSIONS:
        blocks, gaps = build_version(version, args.featurekatalog, dictionary, variables_by_type)
        all_gaps.extend(gaps)

        out_dir = OUT_DIR / version
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{major_minor(version)}_restriktioner.yml"
        out_path.write_text(yaml.dump(blocks, allow_unicode=True, sort_keys=False, width=1000))

        n_translated = sum(len(b["assertions"]) for b in blocks)
        n_total = n_translated + len(gaps)
        rows.append((version, n_total, n_translated))

    col_version = max(len("Version"), max(len(v) for v, _, _ in rows))
    header = f"{'Version':<{col_version}}  {'Restriktioner':>13}  {'Oversat':>7}"
    print(header)
    print("-" * len(header))
    for version, total, translated in rows:
        print(f"{version:<{col_version}}  {total:>13}  {translated:>7}")
    print("-" * len(header))
    print(f"{'Total':<{col_version}}  {sum(t for _, t, _ in rows):>13}  {sum(o for _, _, o in rows):>7}")

    if all_gaps:
        n_unique_texts = len({text for _, _, _, text in all_gaps})
        print(f"\n{len(all_gaps)} restriktioner kunne ikke bygges som xta, fordelt på {n_unique_texts} unikke tekster")
        if args.verbose:
            print_gaps(all_gaps)
        else:
            print("Kør med -v for at se alle restriktioner der ikke kunne bygges, grupperet efter tekst.")
        sys.exit(1)


if __name__ == "__main__":
    main()
