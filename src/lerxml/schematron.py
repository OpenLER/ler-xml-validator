from importlib.resources import files
from lxml import etree
from lxml.etree import _Element
from pathlib import Path
from lxml.isoschematron import Schematron  # ← VIGTIG

from . import ValidationError

sch_path = files("lerxml") / "schematron" / "Elledning.sch"


def validate_sch_element(elm: _Element) -> list[ValidationError]:
    errors: list[ValidationError] = []

    with open(sch_path, "rb") as f:
        sch_doc = etree.parse(f)

    sch = Schematron(sch_doc, store_report=True)

    xml_doc = etree.ElementTree(elm)

    if sch.validate(xml_doc):
        return errors

    report = sch.validation_report
    ns = {"svrl": "http://purl.oclc.org/dsdl/svrl"}

    for failed in report.findall(".//svrl:failed-assert", ns):
        message = failed.findtext("svrl:text", default="", namespaces=ns)
        message = " ".join(message.split())

        location = failed.get("location")
        rule = failed.get("id") or failed.get("test")

        errors.append(
            ValidationError(
                source="schematron",
                rule=rule,
                message=message,
                verbose_message=etree.tostring(failed, encoding="unicode"),
                path=location,
                line=None,  # Schematron giver typisk ikke linjenummer
            )
        )

    return errors


def validate_sch_file(path: str | Path):
    root = etree.parse(path).getroot()
    return validate_sch_element(root)


def validate_sch_string(xml: str):
    root = etree.fromstring(xml.encode())
    return validate_sch_element(root)
