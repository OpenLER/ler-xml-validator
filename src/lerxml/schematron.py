from typing import Literal, Optional
from collections.abc import Iterator

from dataclasses import dataclass
from importlib.resources import files
from lxml import etree
from lxml.etree import _ElementTree
from pathlib import Path
from pyschematron import validate_document

from . import Violation

ns = {"svrl": "http://purl.oclc.org/dsdl/svrl"}

schematron_dir = files("lerxml") / "schematron"
sch_docs = [
    etree.parse(schematron_dir / "restriktioner" / "restriktioner.sch"),
    etree.parse(schematron_dir / "andre_krav" / "andre_krav.sch"),
]


def validate(doc: _ElementTree) -> Iterator[Violation]:
    for sch_doc in sch_docs:
        result = validate_document(doc, sch_doc)
        svrl_doc = result.get_svrl()

        for failed in svrl_doc.findall(".//svrl:failed-assert", ns):
            yield Violation(
                code=failed.get("id"),
                message=failed.findtext("svrl:text", default="", namespaces=ns),
                location=failed.get("location"),
            )

def validate_file(path: str | Path) -> Iterator[Violation]:
    doc = etree.parse(str(path))
    yield from validate(doc)

def validate_string(xml: str) -> Iterator[Violation]:
    doc = etree.ElementTree(etree.fromstring(xml.encode()))
    yield from validate(doc)
