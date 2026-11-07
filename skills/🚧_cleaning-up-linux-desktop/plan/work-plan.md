# Fahrplan: cleaning-up-linux-desktop

Die anstehenden Schritte dieses Vorhabens. Erledigte Schritte fliegen raus; die Nummern der übrigen werden dabei nicht neu vergeben, neue Schritte zählen hoch. Die Festlegungen stehen in `concept.md`.

## 26 Einhängepunkte und Links nie anfassen, Stillstand melden (Plan, freigegeben am 7. November 2026)

Anlass: Der erste Lauf mit dem installierten Skill (Sitzung `d2070323-e965-400e-80c5-878f5a08da4b`, Protokoll `~/cleaning-up-linux-desktop-protocol.md`) hing im Probelauf von 4.12: `rule_pycache` in `delete.py` durchlief das Home mit `os.walk` und stieg in die SMB-Freigabe `~/NAS711/home` hinab, deren Server nicht antwortete (Prozess im Zustand `D`, Stack `cifs … wait_for_response`). Gelöscht wurde nichts. Der Lauf steht im Protokoll als abgebrochen; nach diesem Schritt geht es dort mit der Wiederaufnahme weiter.

Abgrenzung von „nie“ (Entscheidung des Entwicklers): Im Home wird nichts angefasst, was auf einem anderen Einhängepunkt als das Home selbst liegt, auch kein fester Pfad. Benannte Systemquellen außerhalb des Homes (Journal, `/var/log`, die Analysewurzeln `/var`, `/opt`, `/usr/local`, `/srv`) sind gewollte Ziele; ein Durchlauf, der dort beginnt, überschreitet keine weitere Grenze. Der Umgebungsblock der `SKILL.md` liest Einzeldateien und bleibt.

- `delete.py`: neuer Durchlauf `walk_local` auf `os.scandir`-Basis; lässt Einhängepunkte (Textvergleich gegen `/proc/self/mountinfo`, vor jedem Systemaufruf), fremde Geräte, Links und das eigene Präfix aus; liest die Einhängeliste höchstens einmal je Sekunde neu. Ihn benutzen `rule_pycache`, `rule_logs`, `newest_mtime`, `tree_size`; `crosses_device` entfällt zugunsten dieser Prüfung. Vor jedem `rmtree` wird die Einhängeliste neu gelesen. `rule_trash` verliert `other_trashes`. Das Home wird über `realpath` aufgelöst. Die Entschlüsselung von `mountinfo` (bisher `unicode_escape`, zerstört Umlaute) wird durch die aus `backup.py` ersetzt.
- `analyze.py`: in `walk` die Textprüfung vor den Stat; dieselbe Entschlüsselungskorrektur; Neueinlesen der Einhängeliste; sicherer Durchlauf auch für Starter-Einträge, flüchtiges Journal und feste Pfade im Home; Papierkörbe auf anderen Datenträgern entfallen; Füllstand ohne `df` aus `mountinfo` und `statvfs` nur für lokale Blockgeräte und ZFS, Doppelte je Gerät wie bei `df`; neue Option `--find-protocol` ersetzt die `grep`-Suche der `SKILL.md` (ohne `sudo`, Ergebnis nach `/tmp/cleanup-protocol-search.txt`).
- `journal_stats.py`: eigene Kopie des sicheren Durchlaufs für `log_candidates` und `journal_files`.
- `backup.py`: Stillstandsmeldung im Durchlauf; `restore` schließt Archivmitglieder an oder unter aktuellen Einhängepunkten aus und meldet sie (tar und zip).
- `snapshots.py`: `restore` kopiert jedes fehlende Element einzeln statt `cp -a quelle/. ziel/`; Pfade an oder unter Einhängepunkten werden ausgelassen und gemeldet.
- Stillstandsmeldung in allen Durchläufen: Ein Hilfsthread prüft alle 5 s, ob der Durchlauf noch im selben (tiefsten) Ordner steckt; dann eine Zeile nach `stderr`, bei jeder weiteren Prüfung erneut mit der Gesamtzeit; beim Weitergehen meldet der Durchlauf sofort. Liste `stalls` (Ordner, Sekunden) im Bericht. Externe Befehle werden nicht überwacht.
- Tests: simulierte Einhängepunkte mit Protokoll jedes Zugriffs (ohne root) für alle Skripte und die Protokollsuche; echter Lauf mit tmpfs-Einhängung (Befehlsblock für den Entwickler); Entschlüsselung (Leerzeichen, Umlaut); `restore` aus Snapshot und Archiv mit Einhängepunkt im Ziel; Füllstand gegen `df`; Stillstand, Wiederholung und Weitergehen; jeweils Leerprobe.
- Doku: `concept.md` Grundsatz 8 mit der Abgrenzung oben, 4.14 ohne fremde Papierkörbe, Abschnitt zur Stillstandsmeldung; `SKILL.md` (Protokollsuche, 4.14, Absatz „Läuft zu lange“); `README.md`; Paket neu bauen.

## 19 Echter Lauf als Abschluss

Der vollständige Ablauf am Entwicklungsrechner mit echten Löschungen, als finales Debugging. Vorher: Simulationstest `tests/test_delete.py` bestanden, Probeläufe je Bereich angesehen.

## 20 Englische Fassung

Erst wenn die deutsche Fassung samt README fertig ist: `SKILL.en.md`, Regeldateien und `README.en.md` als Übersetzung, die deutschen Dateien erhalten das Sprachkürzel (`skill-dev-doc.md`, Kapitel 5.1); danach die Download-Pakete (Kapitel 5.3).

## 14 Nachprobe Build-Cache (ab 8. November 2026)

Frühestens 48 Stunden nach dem Testbau vom 5. November 2026, 23:19 UTC, denselben Befehl noch einmal ausführen: `sudo docker builder prune --all --force --filter until=48h`, danach `sudo docker system df`. Erwartung nach `concept.md`, Abschnitt 4.13: Die beiden Ketten aus der Dev-Container-Entwicklung (darunter die Einträge mit 535 MB und 541 MB) verschwinden, weil ihre Endpunkte dann 48 Stunden ruhen. Bleiben sie stehen, trägt die Erklärung "Regel wirkt je Kette" nicht und 4.13 ist zu überarbeiten.
