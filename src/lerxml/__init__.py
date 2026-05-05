from dataclasses import dataclass

@dataclass
class ValidationError:
    source: str        # "xsd" | "schematron" | "custom"
    rule: str | None  # rule name (if applicable)
    message: str
    verbose_message: str
    path: str | None  # XPath to node (if available)
    line: int | None   # line number (if available)
