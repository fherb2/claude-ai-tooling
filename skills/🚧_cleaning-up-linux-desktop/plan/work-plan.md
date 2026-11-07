# Fahrplan: cleaning-up-linux-desktop

Die anstehenden Schritte dieses Vorhabens. Erledigte Schritte fliegen raus; die Nummern der übrigen werden dabei nicht neu vergeben, neue Schritte zählen hoch. Die Festlegungen stehen in `concept.md`.

## 26 Einhängepunkte nie anfassen: Rest (echter Lauf)

Umgesetzt und getestet am 7. November 2026: der sichere Durchlauf und die Stillstandsmeldung in allen fünf Skripten, `analyze.py --find-protocol`, der Füllstand nur für lokale Dateisysteme, `tests/test_mounts.py` mit Leerproben, Konzept (Grundsatz 8, 3.11), `SKILL.md` und README. Anlass war der Hänger im Probelauf zu 4.12 (SMB-Freigabe `~/NAS711/home`).

Offen:

1. Ein echter Lauf mit einer `tmpfs`-Einhängung unter einem Testordner: darin ein `__pycache__` und ein Papierkorb, die nicht gefunden werden dürfen (`delete.py --dry-run`, `analyze.py`). Den `sudo mount`-Block führt der Entwickler aus; danach aushängen.
2. Der unterbrochene Lauf aus der Sitzung `d2070323-e965-400e-80c5-878f5a08da4b` (Protokoll `~/cleaning-up-linux-desktop-protocol.md`, Snapshots `…-20261107-182302-vor-loeschen` auf `/` und `/home`): Mit dem neuen Paket in der Betriebsart Wiederaufnahme fortsetzen, ab 4.12. Das ist zugleich der erste Teil von Schritt 19.

## 19 Echter Lauf als Abschluss

Der vollständige Ablauf am Entwicklungsrechner mit echten Löschungen, als finales Debugging. Vorher: Simulationstest `tests/test_delete.py` bestanden, Probeläufe je Bereich angesehen.

## 20 Englische Fassung

Erst wenn die deutsche Fassung samt README fertig ist: `SKILL.en.md`, Regeldateien und `README.en.md` als Übersetzung, die deutschen Dateien erhalten das Sprachkürzel (`skill-dev-doc.md`, Kapitel 5.1); danach die Download-Pakete (Kapitel 5.3).

## 14 Nachprobe Build-Cache (ab 8. November 2026)

Frühestens 48 Stunden nach dem Testbau vom 5. November 2026, 23:19 UTC, denselben Befehl noch einmal ausführen: `sudo docker builder prune --all --force --filter until=48h`, danach `sudo docker system df`. Erwartung nach `concept.md`, Abschnitt 4.13: Die beiden Ketten aus der Dev-Container-Entwicklung (darunter die Einträge mit 535 MB und 541 MB) verschwinden, weil ihre Endpunkte dann 48 Stunden ruhen. Bleiben sie stehen, trägt die Erklärung "Regel wirkt je Kette" nicht und 4.13 ist zu überarbeiten.
