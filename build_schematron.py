#!/usr/bin/env python3

from pathlib import Path
from lxml import etree

SCH_NS = "http://purl.oclc.org/dsdl/schematron"

SRC_DIR = Path("src/lerxml/schematron")
OUT_FILE = SRC_DIR / "2.2_ler.sch"


def main():
    # root schema
    schema = etree.Element(
        f"{{{SCH_NS}}}schema",
        nsmap={
            "sch": SCH_NS,
            "ler": "http://data.gov.dk/schemas/LER/2/gml",
            "gml": "http://www.opengis.net/gml/3.2",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        },
    )

    # namespace declarations
    for prefix, uri in schema.nsmap.items():
        if prefix != "sch":
            ns = etree.SubElement(schema, f"{{{SCH_NS}}}ns")
            ns.set("prefix", prefix)
            ns.set("uri", uri)

    # collect patterns
    for path in sorted(SRC_DIR.glob("*.sch")):
        if path == OUT_FILE:
            continue

        doc = etree.parse(path)
        root = doc.getroot()

        for pattern in root.findall(f"{{{SCH_NS}}}pattern"):
            schema.append(pattern)

    # write output
    tree = etree.ElementTree(schema)
    tree.write(OUT_FILE, pretty_print=True, xml_declaration=True, encoding="UTF-8")


if __name__ == "__main__":
    main()
