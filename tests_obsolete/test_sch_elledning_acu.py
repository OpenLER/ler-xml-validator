from lerxml import ValidationError

import pytest
from lxml import etree
from pathlib import Path

from lerxml.schematron import validate_sch_element

XML_PATH = Path(__file__).parent / "data" / "basic_feature_xml" / "elledning_acu.xml"

NS = {
    "ler": "http://data.gov.dk/schemas/LER/2/gml",
}

@pytest.mark.parametrize(
    "modification, expected_errors",
    [
        pytest.param(
            lambda root: None,
            [],
            id="valid"
        ),
        pytest.param(
            lambda root: [
                e.set("uom", "m")
                for e in root.xpath("//ler:spaendingsniveau", namespaces=NS)
            ],
            ["spændingsniveauMåleenhedsrestriktion"],
            id="wrong-uom"
        ),
        pytest.param(
            lambda root: [
                e.attrib.pop("uom", None)
                for e in root.xpath("//ler:spaendingsniveau", namespaces=NS)
            ],
            ["spændingsniveauMåleenhedsrestriktion"],
            id="missing-uom"
        ),
        pytest.param(
            lambda root: [
                e.getparent().remove(e)
                for e in root.xpath("//ler:udvendigDiameter", namespaces=NS)
            ],
            ["udvendigDiameterBetingelse"],
            id="missing-udvendigDiameter"
        ),
        pytest.param(
            lambda root: [
                e.getparent().remove(e)
                for e in root.xpath("//ler:udvendigDiameter", namespaces=NS)
            ],
            ["udvendigDiameterBetingelse"],
            id="missing-udvendigDiameter"
        ),
    ],
)
def test_01(modification, expected_errors):
    root = etree.fromstring(XML_PATH.read_text().encode())

    modification(root)

    errors: List[ValidationError] = validate_sch_element(root)
    error_ids = [e.rule for e in errors]

    assert error_ids == expected_errors
