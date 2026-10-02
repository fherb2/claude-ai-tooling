#!/usr/bin/env python3
"""Probe: decide whether a directory holds a software project (see doc/3.5.5).

Belegstueck, kein Produktionscode. The check is deliberately asymmetric: it
only has to recognise the clear no. A new project without code yet must keep
the skill running, because that is where the accompanying documentation is
worth the most.

Run without arguments to build six fixtures in a temporary directory and
print the verdicts; pass a path to check that directory instead.
"""

import pathlib
import sys
import tempfile
import time

MANIFESTS = {
    "pyproject.toml", "setup.py", "package.json", "Cargo.toml", "go.mod",
    "pom.xml", "build.gradle", "CMakeLists.txt", "Makefile", "composer.json",
    "Gemfile", "pubspec.yaml", "mix.exs", "Dockerfile", "docker-compose.yml",
}
CODE = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".c", ".h", ".cpp", ".hpp", ".cs",
    ".java", ".kt", ".rs", ".go", ".rb", ".php", ".swift", ".scala", ".ex",
    ".lua", ".sh", ".ps1", ".sql", ".vue", ".dart", ".cu", ".f90", ".jl", ".r",
}
SKIP = {".git", ".venv", "node_modules", "__pycache__", ".claude", ".idea", ".vscode", "downloads"}


def scan(root, limit=4000):
    """Return (manifests, code counts, other counts) below root."""
    manifests, code, other = [], {}, {}
    for path in pathlib.Path(root).rglob("*"):
        if any(part in SKIP for part in path.parts) or not path.is_file():
            continue
        limit -= 1
        if limit < 0:
            break
        suffix = path.suffix.lower()
        if path.name in MANIFESTS or suffix == ".csproj":
            manifests.append(path.name)
        elif suffix in CODE:
            code[suffix] = code.get(suffix, 0) + 1
        else:
            other[suffix or "(none)"] = other.get(suffix or "(none)", 0) + 1
    return manifests, code, other


def verdict(manifests, code):
    if manifests:
        return "SOFTWARE", f"manifest: {', '.join(sorted(set(manifests))[:3])}"
    if code:
        return "SOFTWARE", f"source files: {sum(code.values())} ({', '.join(sorted(code))})"
    return "UNDECIDED", "neither manifest nor source file"


FIXTURES = {
    "py_projekt": ["pyproject.toml", "README.md", "src/app.py", "src/util.py"],
    "config_repo": ["docker-compose.yml", "Makefile", "README.md"],
    "paper_mit_skripten": ["main.tex", "lit.bib", "eval/plot.py"],
    "nur_doku": ["README.md", "kapitel1.md", "kapitel2.md", "bild.png"],
    "paper": ["main.tex", "lit.bib", "README.md"],
    "neues_projekt": ["README.md"],
}


def build_fixtures(base):
    for name, files in FIXTURES.items():
        for rel in files:
            target = pathlib.Path(base, name, rel)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.touch()


def report(path, label=None):
    started = time.perf_counter()
    manifests, code, _ = scan(path)
    decision, why = verdict(manifests, code)
    elapsed = (time.perf_counter() - started) * 1000
    print(f"{label or path:22}{decision:11}{elapsed:6.0f} ms  {why}")


def main():
    print(f"{'case':22}{'verdict':11}{'time':>9}  reason")
    print("-" * 92)
    if len(sys.argv) > 1:
        report(sys.argv[1])
        return
    with tempfile.TemporaryDirectory() as tmp:
        build_fixtures(tmp)
        for name in sorted(FIXTURES):
            report(pathlib.Path(tmp, name), name)


if __name__ == "__main__":
    main()
