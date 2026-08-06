# Chats-Export

Derzeit (08/2026) unterstützt Anthropic den Umzug von einem Projekt / Konto zu einem anderen Projekt / Konto aber auch zwischen Claude.ai – Claude Desktop – Claude Code völlig unzureichend. Insbesondere lassen sich ganze Chats nicht verschieben. In diesem Ordner werden dafür Hilfsmittel erstellt.

# Anwendung

Das Skript `chat_crawl_store.py` rekonstruiert Chat-Transkripte aus den
Schnipseln der Suchwerkzeuge. Weil die Suche nie ein ganzes Transkript
liefert, sondern nur überlappende Ausschnitte, setzt das Skript sie über
viele Suchaufrufe hinweg zusammen — und über Chatgrenzen hinweg, denn ein
großer Export passt nicht in eine Sitzung.

Kern ist `crawl-state.json`: Sie führt alle je gesehenen Chats mit Titel,
Zeitstempel, Bearbeitungsrichtung und Status (`untouched` / `started` /
`done`) und wandert zwischen zwei Sitzungen durch den Nutzer. Das Kommando
`overview` leitet daraus die Arbeitslage ab und formuliert sie als
Handlungsanweisung; `state` korrigiert von Hand, was kein Skript
beurteilen kann.

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
