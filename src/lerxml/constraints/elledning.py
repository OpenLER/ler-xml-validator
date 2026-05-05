from lxml.etree import _Element
from lerxml import ValidationError

#@rule('Elledning.spændingsniveauMåleenhedsrestriktion')
def spaendingsniveauMaaleenhedsrestriktion(feat: _Element) -> list[ValidationError]:
    errors = []

    elm = feat.find("ler:spændingsniveau", namespaces=NS)
    if elm is None:
        return errors


    unit = elm.get("uom")  # eller @enhed afhængigt af schema

    if unit != "kV":
        errors.append(ValidationError(
            field="spændingsniveau",
            message=f"invalid unit: {unit}, expected 'kV'"
        ))


    return errors



