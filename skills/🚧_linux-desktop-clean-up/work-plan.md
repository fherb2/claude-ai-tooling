# Fahrplan: linux-desktop-clean-up

Die anstehenden Schritte dieses Vorhabens. Erledigte Schritte fliegen raus; die Nummern der übrigen werden dabei nicht neu vergeben, neue Schritte zählen hoch. Die Festlegungen stehen in `concept.md`.

## 2 Skripte

Skripte zum Analysieren und Löschen schreiben. Die Sprache (Bash oder Python) ist noch nicht gewählt; ebenso das Format der Übergabe an das Löschskript. Aus dem Test zu Tabelle 3: `.VOB` gehört zu den Videoendungen.

## 9 Weitere Installationswege

Weitere Installationswege von Firefox, Chrome (bzw. Chromium) und VS Code klären, insbesondere Snap und Flatpak: Wo liegen dort Cache und Profile, und gelten die Regeln aus `concept.md`, Abschnitte 4.2 bis 4.4? Getestet sind bisher nur die klassischen Pfade.

## 10 Ergebnisse lesen in VS Code

Klären, wie der Skill in der Claude-Code-Erweiterung von VS Code die Ergebnisdateien liest; dort gibt es weder `/cd` noch `/add-dir` (`concept.md`, Abschnitt 3.1). Möglichkeiten:

- a) jeden Lesezugriff auf `/tmp` einzeln freigeben;
- b) ein weiteres Verzeichnis über die `settings.json` freigeben (Einstellung `additionalDirectories` vermutet, gegen die offizielle Doku prüfen);
- c) Ergebnisse in das Arbeitsverzeichnis der Sitzung statt nach `/tmp` schreiben.

## 11 Caches ohne zugeordnete Anwendersoftware

Klären, wie der Skill Ordner unter `~/.cache` behandelt, die keiner nach `concept.md`, Abschnitt 4.11, erfassten Anwendersoftware zuzuordnen sind (Programme ohne Starter-Eintrag, Erweiterungen, Kommandozeilenwerkzeuge). Anlass: Der Test zu Tabelle 3 fand `~/.cache/markdown-pdf-m` mit einem eigenen Chrome (251 MiB), das zu einer VS-Code-Erweiterung gehört und durch alle drei Tabellen fällt.

## 14 Docker

Behandlung von Docker festlegen (`concept.md`, Abschnitt 5): Was belegen Images, Build-Cache, angehaltene Container und Volumes; welche davon lassen sich nach Grundsatz 3 gezielt aufräumen; wie wird das Zwischenspeicher-Volume der Dev-Container behandelt. Zu beachten: Mit dem containerd-Snapshotter liegen die Daten unter `/var/lib/containerd`, nicht nur unter `/var/lib/docker`.
