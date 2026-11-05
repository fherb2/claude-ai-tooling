# Fahrplan: linux-desktop-clean-up

Die anstehenden Schritte dieses Vorhabens. Erledigte Schritte fliegen raus; die Nummern der übrigen werden dabei nicht neu vergeben, neue Schritte zählen hoch. Die Festlegungen stehen in `concept.md`.

1. Aufbau der drei Tabellen und der Löschlisten nach der Analyse festlegen. Daraus entsteht später der Code.
2. Skripte zum Analysieren und Löschen schreiben. Die Sprache (Bash oder Python) ist noch nicht gewählt.
3. Prüfen, ob `/cd` und `/add-dir` in der Claude-Code-Erweiterung von VS Code funktionieren (`concept.md`, Abschnitt 3.1).
4. Behandlung weiterer Chrome-Ordner ermitteln (`concept.md`, Abschnitt 4.3).
5. Für welche Suchläufe der stille Ausschluss gilt, genau diskutieren (`concept.md`, Abschnitt 4.11).
6. Gegenprobe der Ausschlussmuster am Server nach dem ersten Backup mit der neuen Kette. Fehlen dort die ausgeschlossenen Pfade, und wie hat sich der belegte Platz verändert?
7. Partitionsfrage: Wofür werden die NTFS-Partitionen "Reserve" und "Image" gebraucht, und lässt sich dort Platz zurückgewinnen?
8. Die Stellung der vagabundierenden Medien (`concept.md`, Abschnitt 4.10) im Ablauf gegenüber den .deb-Dateien (4.7) und den Image-Dateien und Archiven (4.8) festlegen.
9. Weitere Installationswege von Firefox, Chrome (bzw. Chromium) und VS Code klären, insbesondere Snap und Flatpak: Wo liegen dort Cache und Profile, und gelten die Regeln aus `concept.md`, Abschnitte 4.2 bis 4.4? Getestet sind bisher nur die klassischen Pfade.
