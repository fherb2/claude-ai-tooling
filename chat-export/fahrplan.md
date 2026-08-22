# Fahrplan Chats-Export — Befunde der Logikprüfung auflösen

Grundlage sind zwei Dateien: `befunde_logikpruefung_2026-08-22.md` (Befunde einer unabhängigen Prüfung durch eine fremde Instanz) und `befund_pruefung_2026-08-22.md` (meine Nachprüfung jedes einzelnen Befundes gegen Code und Doku, mit Empfehlung). **Kein Befund beruhte auf einem Missverständnis** — alle sind technisch zutreffend, weshalb hier nur noch die Reihenfolge und der Zuschnitt der Arbeitsgänge zu klären waren.

**Ein Schritt ist offen** — Schritt 7. Er kam durch eine Neubewertung zurück in den Fahrplan, nicht durch einen neuen Befund: Befund 13 lag als „konstruierter Fall" ab, bis Befund 1 zeigte, dass **textlose Nachrichten mit Anhang real sind** — 22 von 10.779 in den vorliegenden Exporten. Bei denen ist Textgleichheit trivial erfüllt. Erledigt (Schritt 6).

**Die Befundnummern werden nicht neu vergeben** (Repo-`CLAUDE.md`): Ein Rückblick auf „Befund 5" muss eindeutig bleiben. Nummer 12 ist **kein Befund** und in der Befundliste als solcher kommentiert. Die **Schrittnummern** dieser Datei wurden entgegen derselben Regel unterwegs zweimal neu vergeben (1–5 → 1–3 → 1–2); „Schritt 3" ist im Chatverlauf dadurch schon zweideutig. Deshalb zählen die neuen Schritte ab 6 weiter, damit keine Nummer ein drittes Mal kollidiert.

---

## 7. Zwei kleine Zusagen einhalten

**Befunde 7 und 10 in einem Zug** — beide klein, beide Robustheit, beide ohne heutigen Inhaltsverlust.

- **Befund 7:** Die Waisen-Warnung ist toter Code. Eine Nachricht mit fremdem Elternteil fällt in `split_branches()` unter den Zweig `parent not in path_uuids and parent in {…}` und wird als Zweigkopf eingesammelt, bevor sie je in `orphans` landen könnte. Inhaltlich geht nichts verloren — verletzt ist nur eine Zusage: Die Doku kündigt eine Meldung an, die nie kommt. Zu klären ist dabei zuerst, ob die Warnung überhaupt bleiben soll oder ob die richtige Reaktion ist, sie samt Doku-Zusage zu **entfernen**; ein Code-Doku-Widerspruch lässt sich in beide Richtungen auflösen. Wer sie behält, muss den Prüffall schärfen, dessen „oder" den Verlust heute verdeckt.
- **Befund 10:** `save_protocol()` stempelt eine fremde, auch höhere `protocol_version` kommentarlos auf 1 zurück. Ohne Version 2 ohne Wirkung — aber das Protokoll ist die zentrale Zustandsdatei, und ein stilles Zurückstempeln wäre teuer. Eine Warnung bei unbekannter Version, kein Abbruch.

---

## Nur vermerkt

Geprüft und zutreffend, aber ohne heutige Fehlfunktion. Steht hier, damit ein späterer Review es nicht erneut meldet; die Begründung in `befund_pruefung_2026-08-22.md`.

- **Befund 14** — `render()` dedupliziert Verlustverweise je Nachricht über das Label; zwei verschiedene namenlose Dateien gleichen Typs erscheinen als einer, die Verlustzählung untertreibt dann um eins. **Kein Inhaltsverlust** — es geht nichts weg, was ohne den Befund mitgekommen wäre; zu klein ist allein die *gemeldete* Verlustzahl.

  Gemessen über alle vorliegenden Archive: **13 solche Kollisionen**, bei 49 namenlosen von 463 `attachments` und 65 namenlosen von 667 `files`-Verweisen. Namenlose Verweise sind also **nicht** selten — eine frühere Fassung dieser Notiz behauptete das mit einer Zahl, die ich nicht gemessen hatte. Der Befund bleibt hier stehen, weil er den Bericht betrifft und nicht das Archiv; bei 13 zu wenig gezählten Verweisen ist das aber eine Entscheidung und keine Selbstverständlichkeit.

## Erledigt am 22. August 2026

**Befund 13 gelöst — eine Dublette ist nur, was in allem gleich ist (Schritt 6).** Neu ist `is_resend()`, das der Reihe nach Text, Anhänge, Erzeugnisse und behaltene Denkblöcke vergleicht; `split_branches()` ruft es statt des Textvergleichs. Verglichen werden bewusst die **ganzen** Rückgabewerte der vier bestehenden Funktionen, nicht nur ihre ersten Elemente: Damit fallen die Verlustnotizen und die verworfenen Blockzahlen mit in die Gleichheit, und der Code wird dabei kürzer statt länger. Vorgabe 2.5 ist nicht berührt — `wegegleichheit_referenz.py` trägt den Web-Weg, keinen Nachrichtenbaum, die Regel steht also nur an einer Stelle.

Drei neue Prüfungen (259 in der Datei), Leerprobe bestanden: mit dem alten Textvergleich fallen genau die zwei neuen Verlustprüfungen, die Gegenprobe „echter Resend wird weiter verworfen" hält — die Erweiterung schaltet die Regel also nicht ab. Datei per Prüfsumme wiederhergestellt.

**Zwei Fehler in meinen eigenen neuen Texten, beide beim Nachmessen gefunden:** Ich hatte „22 von 10.779" dem Drei-Monats-Export zugeschrieben; es sind 22 über **alle** vorliegenden Archive, davon 9 im Drei-Monats-Export und 13 in einem weiteren. Korrigiert in Doku 3.1.2, im Docstring und im Prüfmaterial-Kommentar. Und in der Notiz zu Befund 14 stand eine Zahl, die ich gar nicht gemessen hatte; die echte Messung steht jetzt dort. Die Befundliste selbst hatte beide Zahlen richtig — die Fehlzuordnung war meine.

**Mitgezogen, weil es sonst stehengeblieben wäre:** Die Rezepttabelle in 4.1 führte „Sendewiederholung — kein bekanntes Rezept" und schloss daraus, der Codeweg bleibe ungeprüft. Für die neu abgedeckte Hälfte von Regel 2 gibt es jetzt sehr wohl ein Rezept — eine textlose Upload-Nachricht nachbearbeiten und die Datei tauschen —, weil dafür nur eine Gabelung nötig ist und die ist erprobt. Zeile ergänzt, der Absatz darunter auf die verwerfende Hälfte eingeschränkt.

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
