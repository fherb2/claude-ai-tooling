# Chats-Export

Derzeit (08/2026) unterstützt Anthropic den Umzug von einem Projekt / Konto zu einem anderen Projekt / Konto aber auch zwischen Claude.ai – Claude Desktop – Claude Code völlig unzureichend. Insbesondere lassen sich ganze Chats nicht verschieben. In diesem Ordner werden dafür Hilfsmittel erstellt.

# Stand: Noch in Überarbeitung. Nicht benutzen!

# Anwendung

Es gibt zwei Skripte. **Welches, entscheidet die Umgebung:**

| Werkzeug vorhanden? | Skript |
|---|---|
| `read_conversation` | `chat_read_store.py` — der Regelfall |
| nur `conversation_search` / `recent_chats` | `chat_crawl_store.py` |

## `chat_read_store.py` (bevorzugt)

`read_conversation` liefert einen Chat per UUID, seitenweise, mit numerierten
Turns und der Gesamtzahl im Envelope. Damit ist **Vollständigkeit eine
Rechnung statt einer Vermutung**: gehaltene Turns gegen `total_turns`,
fehlende werden namentlich benannt. Kein Zusammennähen, keine Suchbegriffe,
keine Unklarheit über die Reihenfolge.

Kern ist `protokoll.json` — dieselbe Protokolldatei, die auch der ZIP-Weg führt: Sie führt alle Chats des Bereichs mit Titel,
Zeitstempel, Bearbeitungsrichtung und Status (`listed` / `started` /
`exported` / `stale` / `deleted`) und wandert zwischen zwei Sitzungen durch den Nutzer. `overview`
leitet daraus die Arbeitslage ab und formuliert sie als Handlungsanweisung;
`state` korrigiert von Hand, was kein Skript beurteilen kann.

Drei Grenzen, alle durch Versuche belegt: Das Werkzeug ist **an den Bereich
gebunden** — aus einem Projekt heraus sind nur dessen Chats lesbar, ein
Export über mehrere Projekte sind entsprechend viele Läufe. **Cowork-Chats
sind unerreichbar**, ihre IDs sind keine UUIDs. Und Aufzählung und Lesbarkeit
deckten sich: `recent_chats` listet im Projekt genau die Chats, die dort auch
lesbar sind.

## `chat_crawl_store.py` (überholt, aber lauffähig)

Rekonstruiert Chats aus überlappenden Suchschnipseln, für Umgebungen ohne
`read_conversation`. Am echten Lauf zeigte sich die Schwäche des Verfahrens:
Die Suche liefert feste, **nicht überlappende** Blöcke, sodass die
Overlap-Mechanik kaum etwas zu verbinden hat — der Crawl sammelt Text, ohne
ihn zusammenzusetzen. Beide Skripte teilen die Zustandsdatei-Logik, die
Runden und die Übergabeprozedur; nur die Beschaffung unterscheidet sich.

Gleichzeitig bearbeitet werden höchstens drei Chats — aus zwei
unabhängigen Gründen: der Kontexthaushalt, und dass die Übergabe damit von
selbst innerhalb der dokumentierten Grenze von 20 Uploads je Chat bleibt.

Die Übergabe wird von Runden getrieben, nicht von einem Kontextsignal: auf
claude.ai bricht ein langes Gespräch nicht ab, sondern fasst seine
früheren Teile zusammen — der erwartete Moment träte also vielleicht nie
ein.

Der Docstring des Skripts ist die vollständige Arbeitsanweisung für die
ausführende Claude-Instanz: Startentscheidung, Upload-Probe,
Arbeitsschleife, Fortschrittsmeldungen, Übergabe.

# Selbsttest

    python3 tests/test_crawl_store.py
    python3 -O tests/test_crawl_store.py   # prüft, dass die __debug__-Blöcke wegkompilieren

Der Test findet das Skript relativ zu seinem eigenen Pfad und läuft daher
aus jedem Arbeitsverzeichnis.
