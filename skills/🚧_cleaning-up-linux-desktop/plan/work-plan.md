# Fahrplan: cleaning-up-linux-desktop

Die anstehenden Schritte dieses Vorhabens. Erledigte Schritte fliegen raus; die Nummern der übrigen werden dabei nicht neu vergeben, neue Schritte zählen hoch. Die Festlegungen stehen in `concept.md`.

## 18 SKILL.md, Regelteil und README (deutsch)

Den Skilltext schreiben, zunächst nur in deutscher Fassung: wie die Instanz den Ablauf aus `concept.md` führt (Beginn mit Abfrage der Parameter, Analyse, Füllstand und drei Tabellen, Bereiche in festgelegter Reihenfolge, Aufträge für `delete.py` mit Probelauf, Ergebnisbericht nach Grundsatz 5). Teilung in eine dünne `SKILL.md` und nachgeladene Regeldateien nach `skill-dev-doc.md`, Kapitel 5.2 (die Bedingungen sind erfüllt; entschieden wird beim Schreiben). Dazu die `README.md` nach `skill-dev-doc.md`, Kapitel 6.1.

## 19 Echter Lauf als Abschluss

Der vollständige Ablauf am Entwicklungsrechner mit echten Löschungen, als finales Debugging. Vorher: Simulationstest `tests/test_delete.py` bestanden, Probeläufe je Bereich angesehen.

## 20 Englische Fassung

Erst wenn die deutsche Fassung samt README fertig ist: `SKILL.en.md`, Regeldateien und `README.en.md` als Übersetzung, die deutschen Dateien erhalten das Sprachkürzel (`skill-dev-doc.md`, Kapitel 5.1); danach die Download-Pakete (Kapitel 5.3).

## 21 Erkennung von Snapshot-Fähigkeit und -Werkzeugen

`analyze.py`: btrfs, ZFS und LVM erkennen, Timeshift und Snapper (installiert, eingerichtet), vorhandene Snapshots und freien Platz je Dateisystem ausgeben (`concept.md`, 3.2 und 3.3). Nur lesend.

**Plan 21 (freigegeben, in Ausführung):** `filesystems()` liefert je Einhängepunkt zusätzlich den verfügbaren Platz (`statvfs`). Nach dem Durchlauf, geschützt über `safe()`, ein neuer Schlüssel `safeguards` neben `fill_level` mit `detect_btrfs()` (je Gerät: Einhängepunkte, Subvolume am Einhängepunkt über `btrfs subvolume show`, Snapshots über `btrfs subvolume list -s`: Zahl und Namen mit Präfix, fremde nur gezählt), `detect_zfs()` (`zfs list -H -t snapshot -o name`) und `detect_lvm()` (`lvs` mit den Feldern `lv_name`, `vg_name`, `lv_attr`, `origin`, `lv_size`, `vg_free`, `lv_path`) — ZFS und LVM mit `tested: false`, nur an nachgebauten Ausgaben geprüft — sowie `detect_tools()` (Timeshift und Snapper nur nach Installation und Konfiguration, ohne Aufruf der Werkzeuge, ihre Snapshots zählt `detect_btrfs()` mit). `run()` bekommt eine Zeitgrenze. Test `tests/test_safeguards.py` mit nachgebauten Ausgaben; Lauf am Entwicklungsrechner (zwei btrfs-Dateisysteme, keine Snapshots, Timeshift und Snapper nicht installiert). Für den Test von Timeshift und Snapper werden sie vorher installiert und danach wieder entfernt (beides in den Paketquellen vorhanden). In der README steht ein kurzer Hinweis, dass ZFS und LVM mangels Testsystem ungeprüft sind (Schritt 24).

## 22 Snapshot-Skript

`snapshots.py` im Skill-Ordner: `list` (lesend), `create` und `remove`, je mit `--dry-run`. Zuerst btrfs. Namenspräfix `cleaning-up-linux-desktop-` mit Datum und Uhrzeit; Snapshots ohne Präfix lehnt das Skript ab. Schreibgeschützte Snapshots. Test: an einem Wegwerf-Subvolume am Entwicklungsrechner (`concept.md`, 3.2, 3.9, 3.10).

## 23 Archiv-Skript

`backup.py`: Pfadliste, Zielverzeichnis und Format (tar oder ZIP) entgegennehmen, Platzprüfung mit Reserve, Archiv schreiben und verifizieren; tar je Sicherungsschritt in einem Ordner je Lauf, ZIP als eine Datei je Lauf mit dateiweiser Entscheidung nach Endung; Links nie verfolgen. Dazu `delete.py --with-paths`: Der Probelauf nennt auf Wunsch die Kandidatenpfade. `analyze.py` und `delete.py` nehmen Dateien mit dem Präfix von allen Löschläufen aus. Test mit Simulation im Wegwerfbaum (`concept.md`, 3.2).

## 24 SKILL.md, README und Paket nachziehen

Betriebsarten, Protokoll (3.8 bis 3.10), Sicherung (3.2) und die geänderte Haftungsempfehlung in `SKILL.md` und README; Paket neu bauen; Aktualitätsprüfer.

## 25 ZFS und LVM

Befehle für Snapshots anlegen, listen, entfernen und selektiv zurückholen aus der Dokumentation belegen und erproben; braucht eine Testumgebung mit ZFS beziehungsweise LVM.

## 14 Nachprobe Build-Cache (ab 8. November 2026)

Frühestens 48 Stunden nach dem Testbau vom 5. November 2026, 23:19 UTC, denselben Befehl noch einmal ausführen: `sudo docker builder prune --all --force --filter until=48h`, danach `sudo docker system df`. Erwartung nach `concept.md`, Abschnitt 4.13: Die beiden Ketten aus der Dev-Container-Entwicklung (darunter die Einträge mit 535 MB und 541 MB) verschwinden, weil ihre Endpunkte dann 48 Stunden ruhen. Bleiben sie stehen, trägt die Erklärung "Regel wirkt je Kette" nicht und 4.13 ist zu überarbeiten.
