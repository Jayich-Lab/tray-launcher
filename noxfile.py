import shutil

import nox

nox.options.sessions = ()


@nox.session
def build(session: nox.Session) -> None:
    """Build an sdist and a wheel (by default)."""
    session.install("build")
    # Remove egg-info since an existing egg-info/SOURCES.txt 
    # can affect the data files
    # included in an sdist.
    shutil.rmtree("src/tray_launcher.egg-info", ignore_errors=True)
    session.run("python", "-m", "build", *session.posargs)
