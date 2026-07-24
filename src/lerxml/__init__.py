from dataclasses import dataclass, field

@dataclass
class ValidationError:
    code: str  # E1, EL1, TL1, TL2, etc.
    message: str
    verbose_message: str | None = None
    location: str | None = None  # XPath to node (if available)
    line: int | None = None   # line number (if available)
    sub_codes: list[str] = field(default_factory=list)  # names of failed sub_assertions, if any
