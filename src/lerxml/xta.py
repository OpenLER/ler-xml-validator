"""xta — en valideringsengine der knytter assertions (og variabler) til XSD-typer.

Design: traversér XML-dokumentet; for hvert element, slå op (i en
forudberegnet cache) hvilke variabler og assertions der gælder for netop
dét elements type-hierarki, og evaluér dem.

Cachen bygges pr. version (lazily, ved første brug): for hvert konkret
element i den version's skema, gå opad i dets type-kæde
(element.type.base_type.base_type...) og saml variabler/assertions fra
src/lerxml/xta/{version}/*.yml, hvis xsdtype matcher et sted i kæden.
Variabler samles fra mest generel til mest specifik type, så en specifik
types variabel-udtryk kan referere til variabler defineret længere oppe i
kæden (ligesom <let> i schematron.py's .sch-filer, via <extends>).

Regelfilerne pr. version bygges af build_xta.py (se repo-roden) ud fra
featurekatalog/constraints/{version}/*.yml (den officielle, natursprogede
kilde) plus xta/human_to_xpath.yml (den håndholdte tekst->XPath-ordbog).
Dækningen er ikke nødvendigvis 100% for ældre versioner — se
`python build_xta.py` for status.

Samme interface som xsd.py/schematron.py: validate(doc) / validate_file(path)
/ validate_string(xml), alle giver Violation-objekter.
"""

from collections.abc import Iterator
from functools import lru_cache
from importlib.resources import files
from pathlib import Path

import elementpath
import yaml
from elementpath.xpath2 import XPath2Parser
from lxml import etree
from lxml.etree import _ElementTree

from . import Violation
from .xsd import DEFAULT_VERSION, get_schema

XTA_DIR = files("lerxml") / "xta"

NAMESPACES = {
    "ler": "http://data.gov.dk/schemas/LER/2/gml",
    "gml": "http://www.opengis.net/gml/3.2",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "xlink": "http://www.w3.org/1999/xlink",
    "ann": "http://data.gov.dk/schemas/annotations/2/gml",
    "dim": "http://data.gov.dk/schemas/dimensions/2/gml",
}

_PARSER = XPath2Parser(namespaces=NAMESPACES)


def _check_unique_names(xsdtype: str, kind: str, items: list[dict]) -> None:
    """Sanity check: ingen dubletter blandt navnene i én type's egen variables/assertions-liste."""
    seen: set[str] = set()
    for item in items:
        name = item["name"]
        if name in seen:
            raise ValueError(
                f"xta: dublet-navn '{name}' blandt {kind} for xsdtype '{xsdtype}'"
            )
        seen.add(name)


def _check_assertion_shape(xsdtype: str, assertion: dict) -> None:
    """Hver assertion har enten en flad 'expression' eller en liste af 'sub_assertions'
    (aldrig begge, aldrig ingen af delene) - og sub_assertion-navne skal være unikke
    inden for deres egen assertion."""
    has_expression = "expression" in assertion
    has_subs = "sub_assertions" in assertion
    if has_expression == has_subs:
        raise ValueError(
            f"xta: assertion '{assertion['name']}' (xsdtype '{xsdtype}') skal have enten "
            f"'expression' eller 'sub_assertions', ikke begge/ingen"
        )
    if has_subs:
        _check_unique_names(xsdtype, f"sub_assertions of {assertion['name']}", assertion["sub_assertions"])


def _load_by_xsdtype(version: str) -> tuple[dict[str, list[dict]], dict[str, list[dict]]]:
    """Indlæs variabler og assertions fra src/lerxml/xta/{version}/*.yml (bygget af
    build_xta.py), nøglet på xsdtype (uden præfiks)."""
    variables_by_type: dict[str, list[dict]] = {}
    assertions_by_type: dict[str, list[dict]] = {}
    version_dir = XTA_DIR / version
    yml_paths = sorted(p for p in version_dir.iterdir() if p.name.endswith(".yml")) if version_dir.is_dir() else []
    for yml_path in yml_paths:
        entries = yaml.safe_load(yml_path.read_text()) or []
        for entry in entries:
            xsdtype = entry["xsdtype"].split(":")[-1]
            variables = entry.get("variables", [])
            assertions = entry.get("assertions", [])
            _check_unique_names(xsdtype, "variables", variables)
            _check_unique_names(xsdtype, "assertions", assertions)
            for assertion in assertions:
                _check_assertion_shape(xsdtype, assertion)
            variables_by_type.setdefault(xsdtype, []).extend(variables)
            assertions_by_type.setdefault(xsdtype, []).extend(assertions)
    return variables_by_type, assertions_by_type


def _type_ancestry(xsd_type) -> list[str]:
    """Gå opad via base_type, returnér typenavne (mest specifik først), 'Type'-suffiks fjernet."""
    names = []
    t = xsd_type
    while t is not None:
        local = t.local_name or ""
        if local.endswith("Type"):
            local = local[:-4]
        if local:
            names.append(local)
        t = t.base_type
    return names


def _check_xsdtypes_exist(variables_by_type: dict, assertions_by_type: dict, known_types: set[str]) -> None:
    """Sanity check: alle xsdtype-navne brugt i yml-filerne skal faktisk forekomme
    i XSD'ens type-hierarki (ellers anvendes deres variabler/assertions aldrig, stille)."""
    used_types = set(variables_by_type) | set(assertions_by_type)
    unknown = used_types - known_types
    if unknown:
        raise ValueError(
            f"xta: ukendte xsdtype-navne i *.yml (findes ikke i XSD'ens type-hierarki): "
            f"{sorted(unknown)}"
        )


def _build_cache(version: str) -> dict[str, tuple[list[dict], list[dict]]]:
    """For hvert konkret element i den givne versions skema: (variabler mest-generel-først, assertions)."""
    variables_by_type, assertions_by_type = _load_by_xsdtype(version)
    xsd_schema = get_schema(version)

    cache: dict[str, tuple[list[dict], list[dict]]] = {}
    known_types: set[str] = set()

    # xsd_schema.elements only covers the schema's own target namespace (ler:);
    # some feature types (LinearAnnotation, LinearDimension) live in imported
    # namespaces (ann:, dim:), so we need the full cross-namespace element map.
    # validate() looks elements up by local name only, so namespace is dropped here too.
    for qname, xsd_element in xsd_schema.maps.elements.items():
        name = qname.rpartition("}")[2]
        ancestry = _type_ancestry(xsd_element.type)  # mest specifik -> mest generel
        known_types.update(ancestry)

        variables = []
        for type_name in reversed(ancestry):  # mest generel -> mest specifik
            variables.extend(variables_by_type.get(type_name, []))

        assertions = []
        for type_name in ancestry:
            assertions.extend(assertions_by_type.get(type_name, []))

        if assertions:
            cache[name] = (variables, assertions)

    _check_xsdtypes_exist(variables_by_type, assertions_by_type, known_types)

    return cache


@lru_cache(maxsize=None)
def get_cache(version: str) -> dict[str, tuple[list[dict], list[dict]]]:
    return _build_cache(version)


@lru_cache(maxsize=None)
def _parse(expr: str):
    return _PARSER.parse(expr)


def _evaluate(expr: str, node, root_node, variables: dict) -> object:
    token = _parse(expr)
    ctx = elementpath.XPathContext(root=root_node, item=node, variables=variables)
    return token.evaluate(ctx)


def validate(doc: _ElementTree, version: str = DEFAULT_VERSION) -> Iterator[Violation]:
    cache = get_cache(version)

    # Building elementpath's node-tree wrapper is O(document size); doing it once
    # per document (instead of once per expression evaluation, as a naive
    # XPathContext(root=<lxml element>, ...) call would) is what makes bulk
    # validation of many documents practical.
    root_node = elementpath.get_node_tree(doc.getroot(), namespaces=NAMESPACES)

    for elem in doc.iter(tag=etree.Element):
        local_name = etree.QName(elem).localname
        entry = cache.get(local_name)
        if entry is None:
            continue
        variable_defs, assertions = entry

        variables: dict = {}
        for var in variable_defs:
            variables[var["name"]] = _evaluate(var["expression"], elem, root_node, variables)

        for assertion in assertions:
            if "sub_assertions" in assertion:
                failed = [
                    sub for sub in assertion["sub_assertions"]
                    if not _evaluate(sub["expression"], elem, root_node, variables)
                ]
                if failed:
                    yield Violation(
                        code=assertion["name"],
                        message="; ".join(sub["message"] for sub in failed),
                        location=doc.getpath(elem),
                        sub_codes=[sub["name"] for sub in failed],
                    )
                continue

            ok = _evaluate(assertion["expression"], elem, root_node, variables)
            if not ok:
                yield Violation(
                    code=assertion["name"],
                    message=assertion["name"],
                    location=doc.getpath(elem),
                )


def validate_file(path: str | Path, version: str = DEFAULT_VERSION) -> Iterator[Violation]:
    doc = etree.parse(str(path))
    yield from validate(doc, version)


def validate_string(xml: str, version: str = DEFAULT_VERSION) -> Iterator[Violation]:
    doc = etree.ElementTree(etree.fromstring(xml.encode()))
    yield from validate(doc, version)
