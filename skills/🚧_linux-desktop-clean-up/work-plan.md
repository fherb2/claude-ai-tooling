# Fahrplan: linux-desktop-clean-up

Die anstehenden Schritte dieses Vorhabens. Erledigte Schritte fliegen raus; die Nummern der übrigen werden dabei nicht neu vergeben, neue Schritte zählen hoch. Die Festlegungen stehen in `concept.md`.

## 2 Skripte

Skripte zum Analysieren und Löschen schreiben. Die Sprache (Bash oder Python) ist noch nicht gewählt; ebenso das Format der Übergabe an das Löschskript. Aus dem Test zu Tabelle 3: `.VOB` gehört zu den Videoendungen.

## 10 Ergebnisse lesen in VS Code

Klären, wie der Skill in der Claude-Code-Erweiterung von VS Code die Ergebnisdateien liest; dort gibt es weder `/cd` noch `/add-dir` (`concept.md`, Abschnitt 3.1). Möglichkeiten:

- a) jeden Lesezugriff auf `/tmp` einzeln freigeben;
- b) ein weiteres Verzeichnis über die `settings.json` freigeben (Einstellung `additionalDirectories` vermutet, gegen die offizielle Doku prüfen);
- c) Ergebnisse in das Arbeitsverzeichnis der Sitzung statt nach `/tmp` schreiben.

## 14 Test: Docker

Den Ablauf aus `concept.md`, Abschnitt 4.13, am Entwicklungsrechner erproben. Testobjekte (vom Nutzer freigegeben): der beendete Container `objective_payne`, die Images aus `vsc-testprojekt` und der zwei Monate alte Build-Cache. Zu klären:

- Wie grenzt `docker builder prune --all --filter until=48h` ab: nach Erstellung oder nach letzter Benutzung?
- Welchen Namen gibt `docker compose config --images` für einen Dienst mit `build:` und ohne `image:` aus, und stimmt er mit dem Namen des gebauten Images überein? (Braucht ein kleines Compose-Projekt zum Test.)
- Lassen sich Projektname und Zustand eines Compose-Projekts mit Compose-Befehlen bestimmen, ohne die Datei selbst zu lesen?
- Entfernt `docker rm -v` die anonymen Volumes, und bleibt `vscode` erhalten?
- Löscht die zweite Image-Prüfung danach genau die Images ohne Container?

Gelingt der Test, gehört 4.13 in Tabelle 1.
