# Fahrplan Chats-Export — Befunde der Logikprüfung auflösen

Grundlage sind zwei Dateien: `befunde_logikpruefung_2026-08-22.md` (Befunde einer unabhängigen Prüfung durch eine fremde Instanz) und `befund_pruefung_2026-08-22.md` (meine Nachprüfung jedes einzelnen Befundes gegen Code und Doku, mit Empfehlung). **Kein Befund beruhte auf einem Missverständnis** — alle sind technisch zutreffend, weshalb hier nur noch die Reihenfolge und der Zuschnitt der Arbeitsgänge zu klären waren.

Reihenfolge nach Schwere. Die echten Fehlfunktionen sind erledigt; es bleiben Schritt 1 — Texte auf das zurücknehmen, was belegt ist — und Schritt 2, Doku-Präzisierung ohne Codeänderung. Beide ändern kein Codeverhalten.

**Die Befundnummern werden nicht neu vergeben** (Repo-`CLAUDE.md`): Ein Rückblick auf „Befund 5" muss eindeutig bleiben. Nummer 12 ist **kein Befund** und in der Befundliste als solcher kommentiert.

---

## 1. Vier Texte auf das zurücknehmen, was belegt ist

Ein Arbeitsgang, weil alle vier denselben Kern haben: Sie behaupten mehr, als die Messung oder der Code hergibt. Kein Codeverhalten ändert sich.

**a) Die „Umfang"-Spalte aus beiden SKILL-Dateien entfernen** — löst **Befund 3**. Die Statistik-Vorlage verlangt eine Nachrichtenzahl, die vor dem Abruf niemand kennt, während dieselbe Datei zweimal verbietet, eine Zahl selbst zu bilden. Beide echten Läufe haben deshalb von der Vorlage abweichen müssen. Ersatzlos streichen; die Anwender-READMEs führen die Tabelle längst richtig ohne diese Spalte.

**b) Die Kommandonamen in Doku 1.4 richtigstellen** — **erledigt am 22. August 2026** im Zug der mechanischen Prüfung unten, weil sie genau dieser Fund war. Dort standen `plan`, `overview` und `map`; jetzt stehen die Kommandos, die tatsächlich rechnen (`list` und `diff`).

**c) Den Denkschritte-Absatz beider Skill-READMEs zurücknehmen** — löst **Randnotiz 1**. Sie behaupten kategorisch, Anthropic schreibe die Überlegungen „seit Ende Juli 2026 nicht mehr" aus und bei älteren Chats seien sie „vollständig vorhanden". Doku 3.1.1 sagt dagegen, das Verhältnis schwanke „innerhalb eines einzigen Chats von Tag zu Tag" und die Ursache sei „nicht ermittelt". Die brauchbarere Auskunft für den Nutzer: Überlegungen können fehlen, die Ursache ist unbekannt, ein leeres Ergebnis ist kein Defekt des Werkzeugs.

**d) Den Namens-Join in `inspect_export.py` nachziehen** — löst **Befund 6**. Das Werkzeug zählt sämtliche `files`-Einträge als „content NOT in the export" und überzeichnet den Verlust um mehr als das Doppelte (524 gegen 205). Das ist mehr als eine irreführende Ausgabe: Doku 4.2 kündigt als kalte Prüfung den „Anteil der `files`-Einträge mit Namenspartner" an, und diese Zahl berechnet kein Werkzeug — der Prüfpunkt ist so nicht durchführbar, und wer ihn mit `inspect_export.py` abarbeitet, schlägt falschen Alarm. Beide Zahlen getrennt ausgeben. Die Logik hat der Konverter in `file_references()`, sie darf aber nicht importiert werden (Vorgabe 2.9).

**Prüfung:** Für (d) eine Erwartung in `tests/test_inspect_export.py` — das Fixture trägt eine Datei, die als inhaltsloser `files`-Eintrag *und* als `attachment` mit Inhalt vorkommt; sie darf nicht als Verlust gezählt werden. Für (a) bis (c) genügt der Docstring-Wächter bzw. das Lesen.

## 2. Vier Doku-Präzisierungen

Ein Arbeitsgang, alles Formulierung ohne Codeänderung. Jeder Punkt hält eine Grenze fest, die heute stärker klingt, als sie ist.

- **Befund 4:** Vorgabe 2.4 stuft `created_after` als „exakt" ein. Belastbar ist nur „exakt, sofern die vorherige Liste vollständig war" — betroffen praktisch nur der `--map`-Pfad, weil der Web-Weg deterministisch über `pagination.has_more` blättert.
- **Befund 9:** Vorgabe 2.2 definiert `turns` als „Anzahl importierter Redebeiträge". Bei einer Hülle schreibt der Code die Skelettlänge, während `messages` leer bleibt. Die Zahl ist nützlich — sie sagt, wie groß der Chat vor der Löschung war —, also die **Definition** nachziehen, nicht den Code.
- **Befund 11:** `report` läuft bewusst über den Verzeichnisinhalt, `diff` über das Protokoll. Dass eine Waise in den Summen von `report` mitzählt, ist deshalb konsequent, steht aber nirgends. Ein Satz in 3.1.6.
- **Befund 8:** Der Fallback auf das flache `text`-Feld existiert nur auf der ZIP-Seite; die Web-Form hat dieses Feld nicht. Heute rein latent (0 von 10.779 Nachrichten), aber es ist die eine Stelle, an der die bauliche Gleichheit von einem Feld abhängt, das nur eine Quelle hat. Als bekannte Grenze in 2.5 festhalten, nicht als Fehler.

---

## Nur vermerkt, nichts zu tun

Diese Befunde sind geprüft und zutreffend, aber ohne heutige Fehlfunktion. Sie stehen hier, damit ein späterer Review sie nicht erneut meldet; die Begründung je Fall in `befund_pruefung_2026-08-22.md`.

- **Befund 7** — Die Waisen-Warnung ist praktisch toter Code: Eine Nachricht mit fremdem Elternteil wird als Zweigkopf eingesammelt, `orphans` bleibt leer. Inhaltlich geht nichts verloren. Wer die Meldung je reparieren will, muss zuerst den Test schärfen, dessen „oder" den Verlust verdeckt.
- **Befund 10** — `save_protocol()` stempelt eine fremde, auch höhere `protocol_version` kommentarlos auf 1 zurück. Ohne Wirkung, solange es keine Version 2 gibt.
- **Befund 13** — Die Dubletten-Erkennung vergleicht nur den Text; ein Resend mit gleichem Text und abweichendem Anhang würde samt Anhang verworfen. Konstruierter Fall.
- **Befund 14** — `render()` dedupliziert Verlustverweise je Nachricht über das Label; zwei verschiedene namenlose Dateien gleichen Typs erscheinen als einer, die Verlustzählung untertreibt dann um eins.

## Erledigt am 22. August 2026

**Befund 1 gelöst, in zwei Hälften.** Die Hüllen-Erkennung prüft jetzt auf *alles*, was mitwandert — Gesprächstext, Anhang mit Inhalt, Erzeugnis, behaltener Denkblock —, statt nur auf den Gesprächstext; ein Chat aus einem Upload ohne Begleitworte und einer fehlgeschlagenen Antwort gilt damit nicht mehr als gelöscht. Und ein `deleted`-Eintrag, den eine frische Liste mit **neuerem** Stand führt, geht zurück auf `stale`: Weil ein an der Quelle gelöschter Chat aus der Liste herausfällt (Doku 1.6), ist diese Kombination ein Widerspruch und kann nur eine Fehlklassifikation sein — so heilt sie sich selbst. Ein unveränderter Stand lässt den Eintrag `deleted`, sonst würde jeder Listenlauf jeden gelöschten Chat erneut holen.

Sechs neue Prüfungen, beide Leerproben bestanden (alte Erkennung → der Anhang-Chat gilt wieder als gelöscht; Beförderung ausgeschaltet → die Selbstheilung entfällt), Datei danach per Prüfsumme wiederhergestellt. Die Hilfsfunktion `msg()` im Prüfmaterial nimmt jetzt Anhänge an, analog zu `files`.

**Was das nicht leistet und bewusst offen bleibt:** Eine bestehende Fehlklassifikation heilt nur, wenn der Chat noch einmal wächst. Bleibt er unverändert, liegt die leere Archivdatei weiter da. Das Protokoll ist lesbares JSON, der Status lässt sich von Hand auf `stale` setzen; ein eigenes Kommando dafür wurde absichtlich **nicht** gebaut — verlangt hat es niemand, und in den 211 echten Chats der vorliegenden Exporte ist kein solcher Fall aufgetreten.

**Befunde 2 und 5 in einem Zug gelöst** — sie mussten zusammen, weil der neue Standvergleich in `cmd_convert()` genau das Wertepaar aus Befund 5 benutzt und den Fehler sonst geerbt hätte. Eingeführt sind `utc_key()` als Sortierschlüssel und `is_newer()` als einzige Stelle, an der ein Zeitstempelvergleich entschieden wird — in **beiden** Umsetzungen, weil der Maßstab nichts importieren darf. Drei Aufrufstellen laufen jetzt darüber: der `stale`-Vergleich in `update_from_list()`, die Sortierung in `window_start()` und die neue Standprüfung in `cmd_convert()`. Eine Quelle, die älter ist als die Chatliste, lässt den Eintrag `stale` und wird unter Nennung beider Zeitstempel gemeldet; die Datei wird trotzdem geschrieben, denn sie ist, was diese Quelle hergibt.

Sechs neue Prüfungen in `tests/test_export_convert.py`, ein Formatfall in der gemeinsamen Falltabelle von `tests/test_wegegleichheit.py` (75 Prüfungen dort). Beide Leerproben bestanden: Mit deaktivierter Standprüfung fallen drei Prüfungen, mit deaktivierter Normalisierung zusätzlich bestehende — die Datei wurde per Prüfsumme wiederhergestellt.

**Nebenbefund aus dem Lauf:** Der neue Vergleich hat einen Fehler im Prüfmaterial aufgedeckt. Das Fixture `OLD_WINS` trug als `updated_at` den Standardwert vom 1. Mai, während seine Nachrichten und die Chatliste den 2. Mai nennen — eine Konversation, deren letzte Nachricht jünger ist als ihr eigener Änderungsstand. Korrigiert und im Fixture kommentiert.

**Kommandonamen, Flags und Feldnamen einmal vollständig gegen den Code gehalten**, über alle Dokumente des Bereichs und in beiden Richtungen. Zwei echte Funde, beide behoben: die Kommandonamen in 1.4 (Randnotiz 2, Schritt 1b) und das undokumentierte Metadatenfeld `imported_at`; dazu `chats` als fehlende Strukturangabe in 2.4. Beide Feldmengen sind seither deckungsgleich, maschinell geprüft.

**Das Verfahren und die typischen Falsch-Positiven stehen jetzt in Vorgabe 2.9**, nicht hier — diese Datei verschwindet mit den Befunden, die Regel gilt weiter.
