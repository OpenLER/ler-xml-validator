import nox


@nox.session(python="3.12")
def btest(session: nox.Session) -> None:
    """Run branch tests (subset mode by default)."""
    session.install("-e", ".[dev]")
    session.run("python", "btest.py", *session.posargs)
