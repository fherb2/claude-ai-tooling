"""The one place that resolves a message key into text (doku 2.4).

Which language the watcher speaks is decided by **which catalogue lies next to
this module**, not by a setting and not by the environment. The reason is
measured: the unit sets no locale, and a systemd user service starts with a
sparse environment in which LANG can be missing altogether -- a detection
resting on it would fail exactly where the tool lives.

A package therefore carries exactly one catalogue, and installing it is the
choice of language. Only the repository holds both, and that is the
development state: there ``use()`` takes the language named by ``--lang`` and
falls back to German, because the tool began as a local German one.

Loading goes through the file path, not the module name: the check script
imports the watcher by path as well, and a module name would only resolve when
the folder happens to sit on sys.path.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Optional

DEFAULT_LANGUAGE = "de"
_PREFIX = "messages_"

_texts: dict[str, str] = {}
_language = ""


def available() -> list[str]:
    """The language codes whose catalogue lies next to this module."""
    here = Path(__file__).resolve().parent
    return sorted(p.stem[len(_PREFIX):] for p in here.glob(f"{_PREFIX}*.py"))


def _load(code: str) -> dict[str, str]:
    path = Path(__file__).resolve().parent / f"{_PREFIX}{code}.py"
    spec = importlib.util.spec_from_file_location(f"{_PREFIX}{code}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.TEXTS


def use(preferred: Optional[str] = None) -> str:
    """Pick the language once, at startup, and return its code.

    One catalogue present: that is the language, whatever *preferred* says --
    an installed package cannot speak a language it does not carry. Several
    present: *preferred* decides, and German if it is empty. None present is a
    structural failure, like a missing watch library: without texts the
    watcher cannot report anything, and guessing would be worse than refusing.
    """
    global _texts, _language
    codes = available()
    if not codes:
        raise FileNotFoundError(
            f"No message catalogue ({_PREFIX}*.py) next to {Path(__file__).name}"
        )
    if len(codes) == 1:
        code = codes[0]
    elif preferred in codes:
        code = preferred
    elif DEFAULT_LANGUAGE in codes:
        code = DEFAULT_LANGUAGE
    else:
        code = codes[0]
    _texts = _load(code)
    _language = code
    return code


def language() -> str:
    """The code picked by use(), empty before that."""
    return _language


def T(key: str, **fields) -> str:
    """The text for *key*, with its named placeholders filled in.

    An unknown key raises instead of returning the key itself. A message that
    silently degrades into a key would be the kind of failure this tool exists
    to avoid; the completeness check in the test script makes sure it cannot
    happen, and the guard around every pass reports it with a traceback if it
    ever does (doku 2.6).
    """
    if not _texts:
        use()
    try:
        text = _texts[key]
    except KeyError:
        raise KeyError(f"No message for key {key!r} in catalogue "
                       f"{_PREFIX}{_language}.py") from None
    return text.format(**fields) if fields else text
