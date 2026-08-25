*Stand: 2026-08-25*

# Vorrang der Anweisungsebenen

Es gilt die speziellere Ebene: Diese Datei ergänzt die übergeordneten Anweisungsdateien und überschreibt sie dort, wo sie ihnen widerspricht. Organisationsweit verwaltete Vorgaben stehen über allen und gelten immer.

Ein geladener Skill regelt die Aufgabe, für die er gilt, und geht dort einer allgemeinen Anweisung vor. Widerspricht er einer projektspezifischen Schutzregel, gilt die Schutzregel — der Widerspruch wird benannt, nicht stillschweigend aufgelöst.

Grund: Die Anweisungsdateien werden aneinandergehängt, nicht gegeneinander verrechnet, und bei widersprüchlichen Regeln wird sonst willkürlich eine ausgewählt (für Claude Code belegt, [memory](https://code.claude.com/docs/en/memory)). Ohne diese Festlegung entscheidet der Zufall.

# Sprachen

## Chat und Dokumente außerhalb von Softwareprojekten

Wenn nicht anders vereinbart, versuche die Sprache im Chat an

- dem ersten Prompt oder
- anderen Chats im Projekt

zu erkennen. Ist das nicht möglich, beginne mit Englisch und schalte später um, falls der Nutzer eine andere Sprache bevorzugt.

Wenn nicht anders vereinbart und keine schriftlichen Dokumente im Projekt vorhanden sind, nutze in Dokumenten die gleiche Sprache wie im Chat.

Sonst: Sind Dokumente unterschiedlicher Sprachen im Projekt vorhanden (berücksichtige dabei keine offensichtlich fremd-erzeugten Dokumente) und ergibt sich die Sprache des neuen Dokuments nicht aus dem Kontext des Schreibauftrages, frage den Nutzer vor der Erstellung des neuen Dokuments nach der Sprache.

Sonst: Sind bereits Dokumente in einer einheitlichen Sprache im Projekt (berücksichtige dabei keine offensichtlich fremd-erzeugten Dokumente) und aus dem Arbeitsauftrag ergibt sich kein Wunsch des Nutzers nach einer anderen Sprache, dann nimm die Sprache derjenigen Dokumente, die offensichtlich in diesem Chat oder in anderen Chats erzeugt wurden.

## Quellcode und Dokumente in Softwareprojekten

Falls für die einzelnen Punkte nicht an anderer Stelle oder im Chat anders vereinbart, gilt:

- Quellcode und darin enthaltene Kommentare und Docstrings -> Englisch
- README-Files -> Englisch
- projektbegleitende Dokumentation -> Englisch

# Memory/Speicher

Wenn Du erlangtes Wissen über den Nutzer, seine Vorlieben, Interessen, Themen, Rollen, weitere Personen im Umfeld des Nutzers in den Memory/Speicher schreiben willst, frage vorher immer den Nutzer, ob er das möchte. Das erspart dem Nutzer in zukünftigen Sitzungen Überraschungen und die Arbeit, den Speicher vom Nutzer per Hand regelmäßig aufräumen zu müssen.
