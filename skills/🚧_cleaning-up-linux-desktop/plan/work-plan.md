# Fahrplan: cleaning-up-linux-desktop

Die anstehenden Schritte dieses Vorhabens. Erledigte Schritte fliegen raus; die Nummern der übrigen werden dabei nicht neu vergeben, neue Schritte zählen hoch. Die Festlegungen stehen in `concept.md`.

## 18 SKILL.md, Regelteil und README (deutsch)

Den Skilltext schreiben, zunächst nur in deutscher Fassung: wie die Instanz den Ablauf aus `concept.md` führt (Beginn mit Abfrage der Parameter, Analyse, Füllstand und drei Tabellen, Bereiche in festgelegter Reihenfolge, Aufträge für `delete.py` mit Probelauf, Ergebnisbericht nach Grundsatz 5). Teilung in eine dünne `SKILL.md` und nachgeladene Regeldateien nach `skill-dev-doc.md`, Kapitel 5.2 (die Bedingungen sind erfüllt; entschieden wird beim Schreiben). Dazu die `README.md` nach `skill-dev-doc.md`, Kapitel 6.1.

## 19 Echter Lauf als Abschluss

Der vollständige Ablauf am Entwicklungsrechner mit echten Löschungen, als finales Debugging. Vorher: Simulationstest `tests/test_delete.py` bestanden, Probeläufe je Bereich angesehen.

## 20 Englische Fassung

Erst wenn die deutsche Fassung samt README fertig ist: `SKILL.en.md`, Regeldateien und `README.en.md` als Übersetzung, die deutschen Dateien erhalten das Sprachkürzel (`skill-dev-doc.md`, Kapitel 5.1); danach die Download-Pakete (Kapitel 5.3).

## 23 Archiv-Skript

`backup.py`: Pfadliste, Zielverzeichnis und Format (tar oder ZIP) entgegennehmen, Platzprüfung mit Reserve, Archiv schreiben und verifizieren; tar je Sicherungsschritt in einem Ordner je Lauf, ZIP als eine Datei je Lauf mit dateiweiser Entscheidung nach Endung; Links nie verfolgen. Dazu `delete.py --with-paths`: Der Probelauf nennt auf Wunsch die Kandidatenpfade. `analyze.py` und `delete.py` nehmen Dateien mit dem Präfix von allen Löschläufen aus. Test mit Simulation im Wegwerfbaum (`concept.md`, 3.2).

## 24 SKILL.md, README und Paket nachziehen

Betriebsarten, Protokoll (3.8 bis 3.10), Sicherung (3.2) und die geänderte Haftungsempfehlung in `SKILL.md` und README; Paket neu bauen; Aktualitätsprüfer.

## 14 Nachprobe Build-Cache (ab 8. November 2026)

Frühestens 48 Stunden nach dem Testbau vom 5. November 2026, 23:19 UTC, denselben Befehl noch einmal ausführen: `sudo docker builder prune --all --force --filter until=48h`, danach `sudo docker system df`. Erwartung nach `concept.md`, Abschnitt 4.13: Die beiden Ketten aus der Dev-Container-Entwicklung (darunter die Einträge mit 535 MB und 541 MB) verschwinden, weil ihre Endpunkte dann 48 Stunden ruhen. Bleiben sie stehen, trägt die Erklärung "Regel wirkt je Kette" nicht und 4.13 ist zu überarbeiten.
