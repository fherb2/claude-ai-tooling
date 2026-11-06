# Fahrplan: linux-desktop-clean-up

Die anstehenden Schritte dieses Vorhabens. Erledigte Schritte fliegen raus; die Nummern der übrigen werden dabei nicht neu vergeben, neue Schritte zählen hoch. Die Festlegungen stehen in `concept.md`.

## 16 Löschskript

Bekommt eine Löschliste und den Bereich und löscht genau das; die Liste schreibt die Instanz nach der Auswahl des Nutzers (Grundsatz 6). Format der Übergabe wird hier entschieden.

**Plan 16 (freigegeben, in Ausführung):** `delete.py` im Skill-Ordner, ein Lauf je Bereich, Auftrag als JSON-Datei von der Instanz. Zwei Arten von Aufträgen: **Liste** (vom Nutzer ausgewählte Pfade bzw. Container: 4.7 bis 4.10, 4.13) und **Regel** (der Bereich mit seinen Parametern; das Skript wendet die Regel aus `concept.md` an: 4.1, 4.2 bis 4.4, 4.5, 4.6, 4.12, 4.13 Build-Cache und zweite Image-Prüfung, 4.14). `running()` prüft laufende Programme über `/proc`. Festes Verbot unabhängig vom Auftrag: `/`, das Home selbst, Ordner direkt unter `/` oder direkt unter dem Home, alles unter `/boot`, alles außerhalb der von der Analyse durchlaufenen Wurzeln (Home, `/var`, `/opt`, `/usr/local`, `/srv`), andere Dateisysteme und symbolische Links (beides hat die Analyse nicht betreten). `--dry-run` führt alles aus außer dem Löschen und meldet, was gelöscht würde. Ergebnisbericht je Lauf als JSON nach `/tmp` (gelöscht, entfernte Datenmenge, übersprungen mit Grund; Docker ohne Größe); den Gesamtbericht nach Grundsatz 5 stellt die Instanz zusammen. Prüfung: jede Regel an einem Test-Home im Scratchpad, danach beim Nutzer Probelauf und echter Lauf je Bereich.

## 17 Journal-Auswertung

Eigenes Skript für Abschnitt 4.5: Histogramm, Quellen, Spitzen, auffällige Log-Files; höchstens vier Worker mit niedriger Priorität; liest `journalctl`, nicht das Dateisystem.

## 14 Nachprobe Build-Cache (ab 8. November 2026)

Frühestens 48 Stunden nach dem Testbau vom 5. November 2026, 23:19 UTC, denselben Befehl noch einmal ausführen: `sudo docker builder prune --all --force --filter until=48h`, danach `sudo docker system df`. Erwartung nach `concept.md`, Abschnitt 4.13: Die beiden Ketten aus der Dev-Container-Entwicklung (darunter die Einträge mit 535 MB und 541 MB) verschwinden, weil ihre Endpunkte dann 48 Stunden ruhen. Bleiben sie stehen, trägt die Erklärung "Regel wirkt je Kette" nicht und 4.13 ist zu überarbeiten.
