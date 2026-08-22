# Fahrplan Chats-Export — Befunde der Logikprüfung auflösen

Grundlage sind zwei Dateien: `befunde_logikpruefung_2026-08-22.md` (Befunde einer unabhängigen Prüfung durch eine fremde Instanz) und `befund_pruefung_2026-08-22.md` (meine Nachprüfung jedes einzelnen Befundes gegen Code und Doku, mit Empfehlung). **Kein Befund beruhte auf einem Missverständnis** — alle sind technisch zutreffend, weshalb hier nur noch die Reihenfolge und der Zuschnitt der Arbeitsgänge zu klären waren.

**Alle Befunde sind abgearbeitet.** Was blieb, steht unter „Nur vermerkt“ — geprüft, zutreffend, ohne heutige Fehlfunktion — und unter „Erledigt“, wie es gelöst wurde. Diese Datei kann fallen, sobald du das für richtig hältst: Ihr bleibender Teil steht in der Doku und in den Docstrings.

**Die Befundnummern werden nicht neu vergeben** (Repo-`CLAUDE.md`): Ein Rückblick auf „Befund 5" muss eindeutig bleiben. Nummer 12 ist **kein Befund** und in der Befundliste als solcher kommentiert.

---

## Nur vermerkt, nichts zu tun

Diese Befunde sind geprüft und zutreffend, aber ohne heutige Fehlfunktion. Sie stehen hier, damit ein späterer Review sie nicht erneut meldet; die Begründung je Fall in `befund_pruefung_2026-08-22.md`.

- **Befund 7** — Die Waisen-Warnung ist praktisch toter Code: Eine Nachricht mit fremdem Elternteil wird als Zweigkopf eingesammelt, `orphans` bleibt leer. Inhaltlich geht nichts verloren. Wer die Meldung je reparieren will, muss zuerst den Test schärfen, dessen „oder" den Verlust verdeckt.
- **Befund 10** — `save_protocol()` stempelt eine fremde, auch höhere `protocol_version` kommentarlos auf 1 zurück. Ohne Wirkung, solange es keine Version 2 gibt.
- **Befund 13** — Die Dubletten-Erkennung vergleicht nur den Text; ein Resend mit gleichem Text und abweichendem Anhang würde samt Anhang verworfen. Konstruierter Fall.
- **Befund 14** — `render()` dedupliziert Verlustverweise je Nachricht über das Label; zwei verschiedene namenlose Dateien gleichen Typs erscheinen als einer, die Verlustzählung untertreibt dann um eins.

## Erledigt am 22. August 2026

**Befunde 3, 6 und Randnotiz 1 gelöst — Texte auf das Belegte zurückgenommen, kein Codeverhalten geändert außer bei Befund 6.** Die „Umfang"-Spalte ist aus beiden SKILL-Tabellen entfernt, mit einem Satz, warum es sie nicht gibt: Die Chatliste trägt den Nachrichtenumfang nicht, das Protokoll kennt `turns` erst nach dem Umwandeln, und eine geschätzte Zahl ist verboten. Der Denkschritte-Absatz beider Skill-READMEs sagt jetzt, was gemessen ist — die Überlegungen *können* fehlen, es wechselte innerhalb eines Chats von Tag zu Tag, die Ursache ist unbekannt —, statt ein Datum zu versprechen.

`inspect_export.py` zählt den Verlust nicht mehr pauschal: Es gibt drei Zahlen getrennt aus — `files` mit Inhaltspartner in derselben Nachricht samt Anteil, `files` ohne Partner, `attachments` ohne extrahierten Inhalt. Damit ist der Prüfpunkt aus Doku 4.2 erstmals ablesbar statt nur angekündigt. Die Join-Regel ist bewusst zweimal gehalten statt importiert (Vorgabe 2.9).

**Dabei ein Fund im Prüfmaterial:** Das Fixture des Selbsttests deckte den Paar-Fall gar nicht ab — `attachments` trug `code.py`, `files` trug `nur-name.bin`, also verschiedene Namen. Der Fahrplan hatte das Gegenteil behauptet. Jetzt kommt `code.py` in beiden Arrays vor, wie im echten Export, und zwei Prüfungen messen den Anteil. Leerprobe bestanden.

**Befunde 4, 8, 9 und 11 als Doku-Präzisierung**, ohne Codeänderung: `created_after` ist „exakt, **sofern die vorherige Liste vollständig war**", mit einem Absatz, was bei einer unvollständigen Liste geschieht und warum praktisch nur `--map` betroffen ist. Die Felddefinition von `turns` sagt jetzt, dass bei einer Hülle die Gerüstlänge stehen bleibt. `report` liest ausdrücklich das Verzeichnis, `diff` das Protokoll — deshalb zählt eine Waise dort mit. Und 2.5 nennt die bekannte Grenze der baulichen Gleichheit: Der `text`-Fallback hat nur eine Quelle.

**Befund 1 gelöst, in zwei Hälften.** Die Hüllen-Erkennung prüft jetzt auf *alles*, was mitwandert — Gesprächstext, Anhang mit Inhalt, Erzeugnis, behaltener Denkblock —, statt nur auf den Gesprächstext; ein Chat aus einem Upload ohne Begleitworte und einer fehlgeschlagenen Antwort gilt damit nicht mehr als gelöscht. Und ein `deleted`-Eintrag, den eine frische Liste mit **neuerem** Stand führt, geht zurück auf `stale`: Weil ein an der Quelle gelöschter Chat aus der Liste herausfällt (Doku 1.6), ist diese Kombination ein Widerspruch und kann nur eine Fehlklassifikation sein — so heilt sie sich selbst. Ein unveränderter Stand lässt den Eintrag `deleted`, sonst würde jeder Listenlauf jeden gelöschten Chat erneut holen.

Sechs neue Prüfungen, beide Leerproben bestanden (alte Erkennung → der Anhang-Chat gilt wieder als gelöscht; Beförderung ausgeschaltet → die Selbstheilung entfällt), Datei danach per Prüfsumme wiederhergestellt. Die Hilfsfunktion `msg()` im Prüfmaterial nimmt jetzt Anhänge an, analog zu `files`.

**Was das nicht leistet und bewusst offen bleibt:** Eine bestehende Fehlklassifikation heilt nur, wenn der Chat noch einmal wächst. Bleibt er unverändert, liegt die leere Archivdatei weiter da. Das Protokoll ist lesbares JSON, der Status lässt sich von Hand auf `stale` setzen; ein eigenes Kommando dafür wurde absichtlich **nicht** gebaut — verlangt hat es niemand, und in den 211 echten Chats der vorliegenden Exporte ist kein solcher Fall aufgetreten.

**Befunde 2 und 5 in einem Zug gelöst** — sie mussten zusammen, weil der neue Standvergleich in `cmd_convert()` genau das Wertepaar aus Befund 5 benutzt und den Fehler sonst geerbt hätte. Eingeführt sind `utc_key()` als Sortierschlüssel und `is_newer()` als einzige Stelle, an der ein Zeitstempelvergleich entschieden wird — in **beiden** Umsetzungen, weil der Maßstab nichts importieren darf. Drei Aufrufstellen laufen jetzt darüber: der `stale`-Vergleich in `update_from_list()`, die Sortierung in `window_start()` und die neue Standprüfung in `cmd_convert()`. Eine Quelle, die älter ist als die Chatliste, lässt den Eintrag `stale` und wird unter Nennung beider Zeitstempel gemeldet; die Datei wird trotzdem geschrieben, denn sie ist, was diese Quelle hergibt.

Sechs neue Prüfungen in `tests/test_export_convert.py`, ein Formatfall in der gemeinsamen Falltabelle von `tests/test_wegegleichheit.py` (75 Prüfungen dort). Beide Leerproben bestanden: Mit deaktivierter Standprüfung fallen drei Prüfungen, mit deaktivierter Normalisierung zusätzlich bestehende — die Datei wurde per Prüfsumme wiederhergestellt.

**Nebenbefund aus dem Lauf:** Der neue Vergleich hat einen Fehler im Prüfmaterial aufgedeckt. Das Fixture `OLD_WINS` trug als `updated_at` den Standardwert vom 1. Mai, während seine Nachrichten und die Chatliste den 2. Mai nennen — eine Konversation, deren letzte Nachricht jünger ist als ihr eigener Änderungsstand. Korrigiert und im Fixture kommentiert.

**Kommandonamen, Flags und Feldnamen einmal vollständig gegen den Code gehalten**, über alle Dokumente des Bereichs und in beiden Richtungen. Zwei echte Funde, beide behoben: die Kommandonamen in 1.4 (Randnotiz 2, Schritt 1b) und das undokumentierte Metadatenfeld `imported_at`; dazu `chats` als fehlende Strukturangabe in 2.4. Beide Feldmengen sind seither deckungsgleich, maschinell geprüft.

**Das Verfahren und die typischen Falsch-Positiven stehen jetzt in Vorgabe 2.9**, nicht hier — diese Datei verschwindet mit den Befunden, die Regel gilt weiter.
