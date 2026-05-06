#!/usr/bin/env python3

from pathlib import Path
from copy import deepcopy
from lxml import etree


SCH_NS = "http://purl.oclc.org/dsdl/schematron"

SRC_DIR = Path("src/lerxml/schematron")
OUT_FILE = SRC_DIR / "2.2_ler.sch"

REQUIRED_QUERY_BINDING = "xslt2"

NSMAP = {
    "sch": SCH_NS,
    "ler": "http://data.gov.dk/schemas/LER/2/gml",
    "gml": "http://www.opengis.net/gml/3.2",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "xs": "http://www.w3.org/2001/XMLSchema",
}


class SchematronBuildError(Exception):
    pass


def validate_input_schema(path: Path, root: etree._Element) -> None:
    if root.tag != f"{{{SCH_NS}}}schema":
        raise SchematronBuildError(
            f"{path}: root element is not sch:schema"
        )

    query_binding = root.get("queryBinding")

    if query_binding != REQUIRED_QUERY_BINDING:
        raise SchematronBuildError(
            f"{path}: expected queryBinding={REQUIRED_QUERY_BINDING!r}, "
            f"got {query_binding!r}"
        )


def make_output_schema() -> etree._Element:
    schema = etree.Element(
        f"{{{SCH_NS}}}schema",
        nsmap=NSMAP,
    )
    schema.set("queryBinding", REQUIRED_QUERY_BINDING)

    for prefix, uri in NSMAP.items():
        if prefix == "sch":
            continue

        ns = etree.SubElement(schema, f"{{{SCH_NS}}}ns")
        ns.set("prefix", prefix)
        ns.set("uri", uri)

    return schema


def main() -> None:
    schema = make_output_schema()

    input_paths = [
        path
        for path in sorted(SRC_DIR.glob("*.sch"))
        if path != OUT_FILE
    ]

    if not input_paths:
        raise SchematronBuildError(f"No input .sch files found in {SRC_DIR}")

    for path in input_paths:
        doc = etree.parse(path)
        root = doc.getroot()

        validate_input_schema(path, root)

        patterns = root.findall(f"{{{SCH_NS}}}pattern")

        if not patterns:
            raise SchematronBuildError(
                f"{path}: no sch:pattern elements found"
            )

        for pattern in patterns:
            schema.append(deepcopy(pattern))

    tree = etree.ElementTree(schema)
    tree.write(
        OUT_FILE,
        pretty_print=True,
        xml_declaration=True,
        encoding="UTF-8",
    )

    print(f"Wrote {OUT_FILE}")


if __name__ == "__main__":
    main()
