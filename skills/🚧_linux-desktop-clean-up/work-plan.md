# Fahrplan: linux-desktop-clean-up

Die anstehenden Schritte dieses Vorhabens. Erledigte Schritte fliegen raus; die Nummern der übrigen werden dabei nicht neu vergeben, neue Schritte zählen hoch. Die Festlegungen stehen in `concept.md`.

## 1 Inhalt von Tabelle 3

Per Test ermitteln, welche systemweiten Statistiken Tabelle 3 enthält und welche Spalten sie hat (`concept.md`, Abschnitt 3.3). Aufbau von Tabelle 1 und 2 ist festgelegt; das Format der Übergabe an das Löschskript entscheidet Schritt 2.

## 2 Skripte

Skripte zum Analysieren und Löschen schreiben. Die Sprache (Bash oder Python) ist noch nicht gewählt.

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
