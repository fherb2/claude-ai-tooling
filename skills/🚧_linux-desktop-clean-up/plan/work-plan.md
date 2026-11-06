# Fahrplan: linux-desktop-clean-up

Die anstehenden Schritte dieses Vorhabens. Erledigte Schritte fliegen raus; die Nummern der übrigen werden dabei nicht neu vergeben, neue Schritte zählen hoch. Die Festlegungen stehen in `concept.md`.

## 15 Analyseskript

Ein Durchlauf durch das Dateisystem; Ausgabe als JSON für den Füllstand und die drei Tabellen (`concept.md`, Abschnitt 3.3). Python, nur Standardbibliothek. Aus dem Test zu Tabelle 3: `.VOB` gehört zu den Videoendungen. Gebaut in drei Lieferungen: 15a Gerüst und Tabelle 3, 15b Tabelle 1 (4.1 bis 4.10, 4.12, 4.13), 15c Software-Erfassung (4.11, Anwendungsordner, Caches ohne Zuordnung).

**Plan 15b (freigegeben, in Ausführung):** Neue Sammler im vorhandenen Durchlauf, je Bereich einer: `AptArchives` (4.1), `FirefoxCache` (4.2), `ChromeCache` (4.3), `VSCodeCache` (4.4), `PipCache` (4.6), `DebFiles` (4.7, Versionsvergleich nach dem Durchlauf), `ImageFiles` (4.8), `DownloadEntries` (4.9), `StrayMedia` (4.10, mit Nachbarendungen je Fundordner), `PyCache` (4.12); nach dem Durchlauf `docker_state()` (4.13, samt Compose-Dateien aus dem Durchlauf). Neuer Parameter `--media-dir` (mehrfach, von der Instanz über XDG aufgelöst). Log-Files und Journal (4.5) gehören zu Schritt 17; offen ist der Vorschlag des Nutzers, schon in der Anfangsanalyse zwei Summen zu erheben (alle Log-Files, Journal). Prüfung: Lauf am Entwicklungsrechner, Abgleich mit früheren Messungen.

**Plan 15a (ausgeführt, Lauf vom 6. November 2026 geprüft):** `analyze.py` im Skill-Ordner, Aufruf mit root-Rechten und niedriger Priorität, Parameter `--home`, `--downloads`, `--threshold` (MiB, eine Zahl für alles) und `--output` (Vorgabe `/tmp/cleanup-analysis.json`); Bildschirmmeldungen englisch. Einheiten: `KNOWN_AREAS` (Bereiche aus Abschnitt 4, eine Stelle), `walk()` (ein Durchlauf, bleibt im Dateisystem, gibt jedem Ordner seine Zugehörigkeit mit), Sammler je Auswertung (Größe je Verzeichnis mit Altanteil, große Einzeldateien, Duplikat-Kandidaten, Git-Reste, Absturzabbilder, Entwicklungsartefakte), `find_duplicates()`, `filesystems()`, `write_result()`. JSON: Kopf (Zeit, Parameter, Laufzeit, Lesefehler), Füllstand, Tabelle 3, Tabelle 1 und Software leer bis 15b/15c. Treffer aus Abschnitt 5 kennzeichnet die Instanz, nicht das Skript. Prüfung: Lauf am Entwicklungsrechner, Abgleich mit den Testläufen.

## 16 Löschskript

Bekommt eine Löschliste und den Bereich und löscht genau das; die Liste schreibt die Instanz nach der Auswahl des Nutzers (Grundsatz 6). Format der Übergabe wird hier entschieden.

## 17 Journal-Auswertung

Eigenes Skript für Abschnitt 4.5: Histogramm, Quellen, Spitzen, auffällige Log-Files; höchstens vier Worker mit niedriger Priorität; liest `journalctl`, nicht das Dateisystem.

## 14 Nachprobe Build-Cache (ab 8. November 2026)

Frühestens 48 Stunden nach dem Testbau vom 5. November 2026, 23:19 UTC, denselben Befehl noch einmal ausführen: `sudo docker builder prune --all --force --filter until=48h`, danach `sudo docker system df`. Erwartung nach `concept.md`, Abschnitt 4.13: Die beiden Ketten aus der Dev-Container-Entwicklung (darunter die Einträge mit 535 MB und 541 MB) verschwinden, weil ihre Endpunkte dann 48 Stunden ruhen. Bleiben sie stehen, trägt die Erklärung "Regel wirkt je Kette" nicht und 4.13 ist zu überarbeiten.
