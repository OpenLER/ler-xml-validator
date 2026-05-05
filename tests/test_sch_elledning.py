from lerxml import ValidationError

import pytest
from lxml import etree
from pathlib import Path

from lerxml.schematron import validate_sch_element

XML_PATH = Path(__file__).parent / "data" / "basic_feature_xml" / "elledning.xml"

def load_xml():
    return XML_PATH.read_text()

NS = {
    "ler": "http://data.gov.dk/schemas/LER/2/gml",
}

@pytest.mark.parametrize(
    "modification, expected_errors",
    [
        (
            lambda root: None,
            []
        ),
        (
            lambda root: [
                e.set("uom", "m")
                for e in root.xpath("//ler:spaendingsniveau", namespaces=NS)
            ],
            ['spændingsniveauMåleenhedsrestriktion']
        ),
        (
            lambda root: [
                e.attrib.pop("uom", None)
                for e in root.xpath("//ler:spaendingsniveau", namespaces=NS)
            ],
            ['spændingsniveauMåleenhedsrestriktion']
        ),
    ]
)

def test_01(modification, expected_errors):
    root = etree.fromstring(load_xml().encode())

    modification(root)

    errors: List[ValidationError] = validate_sch_element(root)
    error_ids = [e.rule for e in errors]

    assert error_ids == expected_errors
