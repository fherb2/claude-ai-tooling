# Fahrplan: linux-desktop-clean-up

Die anstehenden Schritte dieses Vorhabens. Erledigte Schritte fliegen raus; die Nummern der übrigen werden dabei nicht neu vergeben, neue Schritte zählen hoch. Die Festlegungen stehen in `concept.md`.

## 2 Skripte

Skripte zum Analysieren und Löschen schreiben. Die Sprache (Bash oder Python) ist noch nicht gewählt; ebenso das Format der Übergabe an das Löschskript. Aus dem Test zu Tabelle 3: `.VOB` gehört zu den Videoendungen.

## 4 Weitere Chrome-Ordner

Behandlung weiterer Chrome-Ordner ermitteln (`concept.md`, Abschnitt 4.3).

## 5 Stiller Ausschluss

Für welche Suchläufe der stille Ausschluss gilt, genau diskutieren (`concept.md`, Abschnitt 4.11).

## 6 Gegenprobe am Backup-Server

Gegenprobe der Ausschlussmuster am Server nach dem ersten Backup mit der neuen Kette. Fehlen dort die ausgeschlossenen Pfade, und wie hat sich der belegte Platz verändert?

## 7 Partitionsfrage

Wofür werden die NTFS-Partitionen "Reserve" und "Image" gebraucht, und lässt sich dort Platz zurückgewinnen?

## 8 Stellung der vagabundierenden Medien

Die Stellung der vagabundierenden Medien (`concept.md`, Abschnitt 4.10) im Ablauf gegenüber den .deb-Dateien (4.7) und den Image-Dateien und Archiven (4.8) festlegen.

## 9 Weitere Installationswege

Weitere Installationswege von Firefox, Chrome (bzw. Chromium) und VS Code klären, insbesondere Snap und Flatpak: Wo liegen dort Cache und Profile, und gelten die Regeln aus `concept.md`, Abschnitte 4.2 bis 4.4? Getestet sind bisher nur die klassischen Pfade.

## 10 Ergebnisse lesen in VS Code

Klären, wie der Skill in der Claude-Code-Erweiterung von VS Code die Ergebnisdateien liest; dort gibt es weder `/cd` noch `/add-dir` (`concept.md`, Abschnitt 3.1). Möglichkeiten:

- a) jeden Lesezugriff auf `/tmp` einzeln freigeben;
- b) ein weiteres Verzeichnis über die `settings.json` freigeben (Einstellung `additionalDirectories` vermutet, gegen die offizielle Doku prüfen);
- c) Ergebnisse in das Arbeitsverzeichnis der Sitzung statt nach `/tmp` schreiben.

## 11 Caches ohne zugeordnete Anwendersoftware

Klären, wie der Skill Ordner unter `~/.cache` behandelt, die keiner nach `concept.md`, Abschnitt 4.11, erfassten Anwendersoftware zuzuordnen sind (Programme ohne Starter-Eintrag, Erweiterungen, Kommandozeilenwerkzeuge). Anlass: Der Test zu Tabelle 3 fand `~/.cache/markdown-pdf-m` mit einem eigenen Chrome (251 MiB), das zu einer VS-Code-Erweiterung gehört und durch alle drei Tabellen fällt.

## 13 Test: Python-Bytecode-Cache

In einem Projekt im Home die `__pycache__`-Ordner löschen, das Projekt starten und prüfen, ob sie neu entstehen. Gelingt das, gehört 4.12 (`concept.md`) in Tabelle 1.
