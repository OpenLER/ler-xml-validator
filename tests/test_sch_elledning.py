from lerxml import ValidationError

import pytest
from lxml import etree
from pathlib import Path

from lerxml.schematron import validate_sch_element

XML_PATH = Path(__file__).parent / "data" / "basic_feature_xml" / "elledning.xml"

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
    ]
)
def test_01(modification, expected_errors):
    root = etree.fromstring(XML_PATH.read_text().encode())

    modification(root)

    errors: List[ValidationError] = validate_sch_element(root)
    error_ids = [e.rule for e in errors]

    assert error_ids == expected_errors
