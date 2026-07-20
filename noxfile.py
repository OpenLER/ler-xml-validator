import nox


@nox.session(python="3.12")
def mutations(session: nox.Session) -> None:
    """Run mutation tests (subset mode by default)."""
    session.install("-e", ".[dev]")
    session.run("python", "mut.py", *session.posargs)


@nox.session(python="3.12", default=False)
def report(session: nox.Session) -> None:
    """Print full mutation report without failing."""
    session.install("-e", ".[dev]")
    session.run("python", "mut.py", "--report")
