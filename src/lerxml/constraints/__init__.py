from pathlib import Path
from lxml.etree import _Element
from lxml import etree

from .elledning import spaendingsniveauMaaleenhedsrestriktion
from lerxml import ValidationError


def validate_con_element(elm: _Element) -> list[ValidationError]:
    errors = []

    if elm.tag == "{http://www.ler.dk/ler}Elledning":
        errors.extend(spaendingsniveauMaaleenhedsrestriktion(elm))
    else:
        raise NotImplementedError(f"Constraints for feature type {elm.tag} not implemented")

    return errors

def validate_con_file(path: str | Path):
    root = etree.parse(path).getroot()
    return validate_con_element(root)


def validate_con_string(xml: str):
    root = etree.fromstring(xml.encode())
    return validate_con_element(root)
