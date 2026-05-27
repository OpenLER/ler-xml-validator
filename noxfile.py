import nox


@nox.session(python="3.12")
def mutations(session: nox.Session) -> None:
    """Run mutation tests (subset mode by default)."""
    generate_test_data(session)
    session.install("-e", ".[dev]")
    session.run("python", "run_mutation_tests.py", *session.posargs)


@nox.session(python="3.12")
def report(session: nox.Session) -> None:
    """Print full mutation report without failing."""
    generate_test_data(session)
    session.install("-e", ".[dev]")
    session.run("python", "run_mutation_tests.py", "--report")


@nox.session(name="generate-test-data")
def generate_test_data(session: nox.Session) -> None:
    """Generate derived XML test files from YAML mutation specs."""
    session.run("mvn", "-f", "tests/generate-test-data/pom.xml", "compile", "exec:java", external=True)
