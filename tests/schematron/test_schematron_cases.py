import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml
from lxml import etree

from pyschematron import validate_document

HERE = Path(__file__).parent
CASES_DIR = HERE / "cases"

DUMP_DIR = HERE / "dumped_xml"

SCHEMATRON_PATH = Path("src/lerxml/schematron/2.2_ler.sch")

XQUERY_NAMESPACES = """
declare namespace ler = "http://data.gov.dk/schemas/LER/2/gml";
declare namespace gml = "http://www.opengis.net/gml/3.2";
declare namespace xsi = "http://www.w3.org/2001/XMLSchema-instance";
"""

XML_NAMESPACES = {
    "ler": "http://data.gov.dk/schemas/LER/2/gml",
    "gml": "http://www.opengis.net/gml/3.2",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}

SVRL_NS = {
    "svrl": "http://purl.oclc.org/dsdl/svrl",
}


def safe_filename(value: str) -> str:
    return (
        value
        .replace("/", "__")
        .replace("\\", "__")
        .replace(":", "__")
        .replace(" ", "_")
    )


def apply_z_mode(root: etree._Element, z_mode: str) -> None:
    if z_mode not in {"xy", "xyz0", "xyz99"}:
        raise ValueError(f"Invalid z_mode: {z_mode}")

    for pos_list in root.xpath(".//gml:posList", namespaces=XML_NAMESPACES):
        values = pos_list.text.split()
        numbers = [float(value) for value in values]
    
        if len(numbers) % 2 != 0:
            raise ValueError(f"Expected XY coordinate pairs, got: {pos_list.text!r}")

        xy_pairs = list(zip(numbers[0::2], numbers[1::2]))

        if z_mode == "xy":
            coords = [
                value
                for x, y in xy_pairs
                for value in (x, y)
            ]

        elif z_mode == "xyz0":
            coords = [
                value
                for x, y in xy_pairs
                for value in (x, y, 0.0)
            ]

        elif z_mode == "xyz99":
            coords = [
                value
                for x, y in xy_pairs
                for value in (x, y, -99)
            ]

        pos_list.text = "\n        " + " ".join(format_coord(v) for v in coords) + "\n      "


def format_coord(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return str(value)


def load_cases():
    params = []
    seen_ids = set()

    for yml_path in sorted(CASES_DIR.glob("*.yml")):
        xml_path = yml_path.with_suffix(".xml")

        if not xml_path.exists():
            raise FileNotFoundError(
                f"Expected XML file next to YAML file: {xml_path}"
            )

        cases = yaml.safe_load(yml_path.read_text(encoding="utf-8")) or []

        for case in cases:
            case_id = case.get("id")
            if not case_id:
                raise ValueError(f"Missing 'id' in {yml_path}")

            pytest_id = f"{xml_path.stem}::{case_id}"
            if pytest_id in seen_ids:
                raise ValueError(f"Duplicate case id: {pytest_id}")
            seen_ids.add(pytest_id)

            params.append(pytest.param(xml_path, case, id=pytest_id))

    return params


def make_query(xml_path: Path, update_expr: str) -> str:
    return f"""
{XQUERY_NAMESPACES}

copy $doc := doc("{xml_path.as_uri()}")
modify (
  {update_expr}
)
return $doc
"""


def apply_xquery_with_basex(xml_path: Path, update_expr: str) -> bytes:
    if shutil.which("basex") is None:
        pytest.skip("BaseX is not installed or not on PATH")

    query = make_query(xml_path, update_expr)

    result = subprocess.run(
        ["basex", "-q", query],
        text=True,
        capture_output=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"BaseX failed for {xml_path}\n\n"
            f"Query:\n{query}\n\n"
            f"STDOUT:\n{result.stdout}\n\n"
            f"STDERR:\n{result.stderr}"
        )

    return result.stdout.encode("utf-8")



@pytest.mark.parametrize("xml_path, case", load_cases())
def test_schematron_case(xml_path: Path, case: dict[str, Any]) -> None:
    xquery_expr = case.get("xquery", "()")

    modified_xml = apply_xquery_with_basex(xml_path, xquery_expr)
    root = etree.fromstring(modified_xml)

    z_mode = case.get("z_mode", "xy")
    apply_z_mode(root, z_mode)

    pytest_id = f"{xml_path.stem}::{case['id']}"
    safe_id = pytest_id.replace("::", "__")

    DUMP_DIR.mkdir(exist_ok=True)

    dump_path = DUMP_DIR / f"{safe_id}.xml"

    dump_path.write_bytes(
        etree.tostring(
            root,
            pretty_print=True,
            xml_declaration=True,
            encoding="utf-8",
        )
    )

    schematron_tree = etree.parse(SCHEMATRON_PATH)

    result = validate_document(
        etree.ElementTree(root),
        schematron_tree,
    )
    svrl = result.get_svrl()

    error_ids = [
        elem.get("id")
        for elem in svrl.findall(".//svrl:failed-assert", SVRL_NS)
    ]

    assert error_ids == case.get("expected_errors", [])
