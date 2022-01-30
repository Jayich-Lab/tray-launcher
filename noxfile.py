import shutil

import nox

nox.options.sessions = ("lint",)
src_paths = ("src", "noxfile.py")


@nox.session
def fmt(session: nox.Session) -> None:
    """Run code formatters."""
    session.install(
        "black",
        "isort",
        "codespell",
    )
    args = session.posargs or src_paths
    session.run("black", *args)
    session.run("isort", *args)
    session.run("codespell", "-w", *args)


@nox.session
def lint(session: nox.Session) -> None:
    """Lint files."""
    session.install(
        "flake8-black==0.2.4",
        "flake8-isort",
        "flake8",
        "flake8-bugbear",
        "codespell",
    )
    args = session.posargs or src_paths
    failed = False
    try:
        session.run("flake8", *args)
    except nox.command.CommandFailed:
        failed = True
    try:
        session.run("codespell", *args)
    except nox.command.CommandFailed:
        failed = True
    if failed:
        raise nox.command.CommandFailed


@nox.session
def build(session: nox.Session) -> None:
    """Build an sdist and a wheel (by default)."""
    session.install("build")
    # Remove egg-info since an existing egg-info/SOURCES.txt
    # can affect the data files
    # included in an sdist.
    shutil.rmtree("src/tray_launcher.egg-info", ignore_errors=True)
    session.run("python", "-m", "build", *session.posargs)
