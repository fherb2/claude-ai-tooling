# Probes — Belegstücke zu zwei Entscheidungen

*Stand: 2026-10-02*

Dieser Ordner enthält zwei kurze Python-Programme. Sie sind **kein Produktionscode** und werden auch keiner: Das Skript des Skills entsteht in den Fahrplanschritten 4 und 5 und wird neu geschrieben. Was hier liegt, belegt zwei Entscheidungen der Konzeptphase — nämlich dass sie mechanisch umsetzbar sind und zu welchen Ergebnissen sie führen.

Beide kommen mit der Standardbibliothek aus. Keines von beiden braucht Argumente; ohne Argumente führt jedes seine eigenen Prüffälle vor.

## `fingerprint_classify.py`

Belegt die Entscheidung zum Fingerabdruck (Doku, Kapitel 3.6.7, entschieden am 2026-09-25). Dort ist festgelegt, dass jede Abweichung des Definitionssatzes gemeldet wird — nichts wird unterdrückt —, dass die Meldung aber entscheidungsfertig ankommt: mit dem Wortunterschied selbst und zwei Kennzeichen, ob Zahlen oder Einheiten betroffen sind und ob Normativsignale betroffen sind.

Das Programm zeigt beides an elf Fällen. Sie sind zugleich der Keim für die Prüffälle, die beim Bauen des Skripts entstehen. Zwei davon sind die wichtigsten, weil der erste Entwurf an ihnen gescheitert war: `5 ms` zu `5 s` — das geänderte Wort trägt selbst keine Ziffer, weshalb die Prüfung die Nachbarschaft einer Zahl mit einbeziehen muss — und `**64**` zu `64`, das ohne Entfernen der Markdown-Auszeichnung als Zahländerung gilt.

Die Sätze in den Prüffällen sind deutsch, weil die Signalwörter es sind.

## `project_kind.py`

Belegt die Vorprüfung, ob ein Vorhaben überhaupt Softwareentwicklung ist (Doku, Kapitel 3.5.5 und 1.7.7, entschieden am 2026-10-02). Das Programm legt sechs Vorhaben in einem temporären Verzeichnis an und urteilt über sie; mit einem Pfad als Argument prüft es stattdessen dieses Verzeichnis.

Die Prüfung erkennt bewusst nur das klare Nein. Drei der sechs Fälle bleiben unentschieden — ein reines Doku-Repository, ein LaTeX-Paper und ein neues Projekt mit nur einer README —, und das ist beabsichtigt: Ein Projekt ohne Code kann eines werden, und gerade am Anfang ist die begleitende Doku am wertvollsten.

## Wann dieser Ordner verschwindet

Mit den Fahrplanschritten 4 und 5. Sobald das Skript des Skills die beiden Fähigkeiten enthält und die Prüffälle dort liegen, haben die Belegstücke ihren Zweck erfüllt und werden gelöscht. Die Messwerte, auf die sich die Doku beruft, stehen in der Doku selbst und sind nicht an diesen Ordner gebunden.

## Zur Sprache dieser Datei

Dieses Repository legt neben jeder deutschen Ordner-README eine englische Fassung an, weil es international gehostet wird. Hier ist bewusst keine angelegt: Der Ordner ist entwicklungszeitlich, erreicht nie einen Besucher des Repositories und verschwindet mit den beiden Fahrplanschritten. Soll er doch länger bleiben, ist die englische Fassung nachzuziehen.
