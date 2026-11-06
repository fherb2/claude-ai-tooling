# Fahrplan: linux-desktop-clean-up

Die anstehenden Schritte dieses Vorhabens. Erledigte Schritte fliegen raus; die Nummern der übrigen werden dabei nicht neu vergeben, neue Schritte zählen hoch. Die Festlegungen stehen in `concept.md`.

## 15 Analyseskript

Ein Durchlauf durch das Dateisystem; Ausgabe als JSON für den Füllstand und die drei Tabellen (`concept.md`, Abschnitt 3.3). Python, nur Standardbibliothek. Aus dem Test zu Tabelle 3: `.VOB` gehört zu den Videoendungen. Gebaut in drei Lieferungen: 15a Gerüst und Tabelle 3, 15b Tabelle 1 (4.1 bis 4.10, 4.12, 4.13), 15c Software-Erfassung (4.11, Anwendungsordner, Caches ohne Zuordnung).

15a und 15b sind ausgeführt und am Entwicklungsrechner geprüft (Läufe vom 6. November 2026, Ergebnisse in `tests/test_results/`); dazu kamen die beiden Summen für Log-Files und Journal (4.5) und der Papierkorb (4.14).

**Plan 15c (freigegeben, in Ausführung):** `desktop_entries()` liest die Starter-Einträge der in 4.11 genannten Orte und wendet die fünf Regeln an (erfasste Programme mit Name, Aufruf, Kategorien, Herkunft, Paket und Version; ausgeschlossene mit Grund); `package_of()` ordnet sie mit einem `dpkg -S` ihren Paketen zu; `other_installs()` liest `flatpak list` und `snap list`; der Sammler `AppFolders` erfasst je Anwendungsordner (direkt unter `~/.config`, `~/.local/share`, `~/.cache`, `~/.var/app` sowie Punkt-Ordner im Home, ohne Bereiche aus Abschnitt 4) Größe und letzte Änderung; `prefilter()` gibt je Ordner den passenden Namen installierter Software oder "kein Treffer" (nur Vorfilter, das Urteil fällt die Instanz). Neuer Parameter `--desktop` (`XDG_CURRENT_DESKTOP`, geht unter `sudo` verloren). Die Namensliste bleibt im Skript. Prüfung: Lauf am Entwicklungsrechner; Abgleich mit 4.11 (74 erfasst, 4 wegen `Terminal=true`, 24 System oder Einstellungen) und mit den Resten aus dem zweiten Test.

## 16 Löschskript

Bekommt eine Löschliste und den Bereich und löscht genau das; die Liste schreibt die Instanz nach der Auswahl des Nutzers (Grundsatz 6). Format der Übergabe wird hier entschieden.

## 17 Journal-Auswertung

Eigenes Skript für Abschnitt 4.5: Histogramm, Quellen, Spitzen, auffällige Log-Files; höchstens vier Worker mit niedriger Priorität; liest `journalctl`, nicht das Dateisystem.

## 14 Nachprobe Build-Cache (ab 8. November 2026)

Frühestens 48 Stunden nach dem Testbau vom 5. November 2026, 23:19 UTC, denselben Befehl noch einmal ausführen: `sudo docker builder prune --all --force --filter until=48h`, danach `sudo docker system df`. Erwartung nach `concept.md`, Abschnitt 4.13: Die beiden Ketten aus der Dev-Container-Entwicklung (darunter die Einträge mit 535 MB und 541 MB) verschwinden, weil ihre Endpunkte dann 48 Stunden ruhen. Bleiben sie stehen, trägt die Erklärung "Regel wirkt je Kette" nicht und 4.13 ist zu überarbeiten.
