# Fahrplan: linux-desktop-clean-up

Die anstehenden Schritte dieses Vorhabens. Erledigte Schritte fliegen raus; die Nummern der übrigen werden dabei nicht neu vergeben, neue Schritte zählen hoch. Die Festlegungen stehen in `concept.md`.

## 15 Analyseskript

Ein Durchlauf durch das Dateisystem; Ausgabe als JSON für den Füllstand und die drei Tabellen (`concept.md`, Abschnitt 3.3). Python, nur Standardbibliothek. Aus dem Test zu Tabelle 3: `.VOB` gehört zu den Videoendungen.

## 16 Löschskript

Bekommt eine Löschliste und den Bereich und löscht genau das; die Liste schreibt die Instanz nach der Auswahl des Nutzers (Grundsatz 6). Format der Übergabe wird hier entschieden.

## 17 Journal-Auswertung

Eigenes Skript für Abschnitt 4.5: Histogramm, Quellen, Spitzen, auffällige Log-Files; höchstens vier Worker mit niedriger Priorität; liest `journalctl`, nicht das Dateisystem.

## 14 Nachprobe Build-Cache (ab 8. November 2026)

Frühestens 48 Stunden nach dem Testbau vom 5. November 2026, 23:19 UTC, denselben Befehl noch einmal ausführen: `sudo docker builder prune --all --force --filter until=48h`, danach `sudo docker system df`. Erwartung nach `concept.md`, Abschnitt 4.13: Die beiden Ketten aus der Dev-Container-Entwicklung (darunter die Einträge mit 535 MB und 541 MB) verschwinden, weil ihre Endpunkte dann 48 Stunden ruhen. Bleiben sie stehen, trägt die Erklärung "Regel wirkt je Kette" nicht und 4.13 ist zu überarbeiten.
