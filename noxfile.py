import nox
import urllib.request
from pathlib import Path

BASEX_VERSION = "11.7"
BASEX_JAR_URL = f"https://files.basex.org/releases/{BASEX_VERSION}/BaseX{BASEX_VERSION.replace('.', '')}.jar"
BASEX_JAR = Path(".basex-jar") / f"basex-{BASEX_VERSION}.jar"


def ensure_basex(session: nox.Session) -> Path:
    if not BASEX_JAR.exists():
        BASEX_JAR.parent.mkdir(exist_ok=True)
        session.log(f"Downloading BaseX {BASEX_VERSION}...")
        urllib.request.urlretrieve(BASEX_JAR_URL, BASEX_JAR)
        session.log(f"Saved to {BASEX_JAR}")
    return BASEX_JAR


@nox.session(python="3.12")
def mutations(session: nox.Session) -> None:
    """Run mutation tests (subset mode by default)."""
    session.install("-e", ".[dev]")
    jar = ensure_basex(session)
    session.run("python", "run_mutation_tests.py", f"--basex-jar={jar}", *session.posargs)


@nox.session(python="3.12")
def report(session: nox.Session) -> None:
    """Print full mutation report without failing."""
    session.install("-e", ".[dev]")
    jar = ensure_basex(session)
    session.run("python", "run_mutation_tests.py", f"--basex-jar={jar}", "--report")
