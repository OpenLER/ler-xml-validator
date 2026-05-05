from importlib.resources import files
import xmlschema
from lxml import etree
from lxml.etree import _Element
from pathlib import Path

from . import ValidationError

xsd_path = files("lerxml") / "xsd" / "2.2_ler.xsd"
schema = xmlschema.XMLSchema(xsd_path)


def validate_xsd_element(elm: _Element) -> list[ValidationError]:
    errors = []

    for err in schema.iter_errors(elm):
        errors.append(
            ValidationError(
                source="xsd",
                rule=None,
                message=err.reason,
                verbose_message=str(err),
                path=err.path,
                line=getattr(err, "position", (None, None))[0],
            )
        )

    return errors

def validate_xsd_file(path: str | Path):
    root = etree.parse(path).getroot()
    return validate_xsd_element(root)


def validate_xsd_string(xml: str):
    root = etree.fromstring(xml.encode())
    return validate_xsd_element(root)
