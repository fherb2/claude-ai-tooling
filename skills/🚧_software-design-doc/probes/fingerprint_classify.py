#!/usr/bin/env python3
"""Probe: classify a changed definition sentence (see doc/3.6.7).

Belegstueck, kein Produktionscode. It demonstrates that the fingerprint
report can be made decision-ready with the standard library alone -- no
third-party package is required.

Two signals are derived from the word-level diff of the normalised
sentences: whether numbers or units are affected, and whether normative
signal words are affected. Nothing is ever suppressed; the classification
only labels the report.

Run without arguments to print the eleven cases the decision was based on.
"""

import difflib
import re
import unicodedata

# Same list the lint uses; see doc/3.6.6 (lint_signals).
SIGNALS = {
    "muss", "müssen", "soll", "sollen", "immer", "nie", "niemals", "genau",
    "höchstens", "mindestens", "must", "shall", "always", "never",
}
# Two-word forms a set lookup cannot catch.
NEGATIONS = re.compile(r"darf nicht|at most|at least")
DIGIT = re.compile(r"\d")
# Markdown emphasis is not content: without this, **64** vs 64 reads as a change.
MARKUP = re.compile(r"[*_`]+")


def normalise(text):
    """Strip everything that carries no meaning for a definition sentence."""
    text = unicodedata.normalize("NFC", text).replace(" ", " ")
    text = MARKUP.sub("", text)
    return re.sub(r"\s+", " ", text).strip().rstrip(".!?;:").lower()


def classify(old, new):
    """Return (changes, numbers_affected, signals_affected).

    changes -- one "old -> new" string per differing span
    """
    before, after = normalise(old).split(), normalise(new).split()
    changes, touched, near_number = [], [], False

    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, before, after).get_opcodes():
        if tag == "equal":
            continue
        gone, came = before[i1:i2], after[j1:j2]
        changes.append(f"{' '.join(gone) or '0'} -> {' '.join(came) or '0'}")
        touched += gone + came
        # A word right after a number is its unit or referent. Without this
        # check "5 ms -> 5 s" slips through: the changed word has no digit.
        for words, start in ((before, i1), (after, j1)):
            if start > 0 and DIGIT.search(words[start - 1]):
                near_number = True

    numbers = any(DIGIT.search(w) for w in touched) or near_number
    signals = any(w.strip(",;()") in SIGNALS for w in touched) or (
        bool(NEGATIONS.search(normalise(old))) != bool(NEGATIONS.search(normalise(new)))
    )
    return changes, numbers, signals


# The eleven cases the decision of 2026-09-25 rests on. The sentences are
# German because the signal words are.
CASES = [
    ("Tippfehler", "Die Eingangsqeue fasst 64 Einträge.", "Die Eingangsqueue fasst 64 Einträge."),
    ("Zahl geändert", "Die Eingangsqueue fasst 64 Einträge.", "Die Eingangsqueue fasst 128 Einträge."),
    ("Einheit geändert", "Das Latenzbudget beträgt 5 ms.", "Das Latenzbudget beträgt 5 s."),
    ("Bezug geändert", "Die Queue fasst 64 Einträge.", "Die Queue fasst 64 Blöcke."),
    ("Signalwort", "Der Starter muss die Queue reservieren.", "Der Starter soll die Queue reservieren."),
    ("Verneinung", "Der Kernel darf nicht direkt starten.", "Der Kernel darf direkt starten."),
    ("Umformulierung", "Die Eingangsqueue der Pipeline fasst 64 Einträge.",
     "Es fasst die Pipeline in ihrer Eingangsqueue 64 Einträge."),
    ("Nur Formatierung", "Die Queue fasst **64** Einträge.", "Die Queue fasst  64  Einträge"),
    ("Wort ergänzt", "Die Queue fasst 64 Einträge.", "Die Eingangsqueue fasst 64 Einträge."),
    ("Zahl ausgeschrieben", "Die Queue fasst 64 Einträge.", "Die Queue fasst vierundsechzig Einträge."),
    ("Komma entfernt", "Der Starter, der die Queue hält, läuft zuerst.",
     "Der Starter der die Queue hält läuft zuerst."),
]


def main():
    print(f"{'case':22}{'number':8}{'signal':8}{'report':22}diff")
    print("-" * 110)
    for name, old, new in CASES:
        changes, numbers, signals = classify(old, new)
        if not changes:
            report = "no report"
        elif numbers or signals:
            report = "REPORT"
        else:
            report = "probably cosmetic"
        print(f"{name:22}{str(numbers):8}{str(signals):8}{report:22}{'; '.join(changes) or '-'}")


if __name__ == "__main__":
    main()
