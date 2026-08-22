# Fahrplan Chats-Export — Befunde der Logikprüfung auflösen

Grundlage sind zwei Dateien: `befunde_logikpruefung_2026-08-22.md` (Befunde einer unabhängigen Prüfung durch eine fremde Instanz) und `befund_pruefung_2026-08-22.md` (meine Nachprüfung jedes einzelnen Befundes gegen Code und Doku, mit Empfehlung). **Kein Befund beruhte auf einem Missverständnis** — alle sind technisch zutreffend, weshalb hier nur noch die Reihenfolge und der Zuschnitt der Arbeitsgänge zu klären waren.

Reihenfolge nach Schwere. Schritte 1 bis 3 sind echte Fehlfunktionen, Schritt 4 bringt Texte auf das zurück, was belegt ist, Schritt 5 ist Doku-Präzisierung ohne Codeänderung.

**Die Befundnummern werden nicht neu vergeben** (Repo-`CLAUDE.md`): Ein Rückblick auf „Befund 5" muss eindeutig bleiben. Nummer 12 ist **kein Befund** und in der Befundliste als solcher kommentiert.

---

## 1. `convert` darf einen `stale`-Chat nicht ohne Standprüfung auf `exported` setzen

**Löst Befund 2.** Die höchste Eintrittswahrscheinlichkeit der ganzen Liste, und der Fehler bleibt still.

`cmd_convert()` setzt den Status bedingungslos auf `exported`. Wird versehentlich ein **älteres** ZIP konvertiert — und der Skill sucht die ZIP im Download-Ordner, wo bei diesem Nutzer sechs Exporte verschiedener Zeiträume liegen —, fällt `exported_updated_at` auf den alten Stand zurück und `diff` meldet „nichts offen". Das Werkzeug behauptet einen Abgleich, den es nicht geleistet hat.

**Zu ändern:** In `cmd_convert()` vor dem Setzen von `exported` prüfen, ob das `updated_at` der verarbeiteten Quelle den bereits gelisteten Stand erreicht. Tut es das nicht, bleibt der Eintrag `stale`, und der Lauf sagt es in der Ausgabe. Die dafür nötige Information liegt im Protokoll direkt daneben (`listed_updated_at`) und wird heute nicht gelesen.

**Prüfung:** Regressionstest in `tests/test_export_convert.py` — ein als `stale` geführter Chat, konvertiert aus einer Quelle mit älterem `updated_at`, muss `stale` bleiben und das melden. Leerprobe: Mit zurückgeschriebener Bedingung muss genau dieser Test anschlagen.

## 2. Zeitstempel normalisieren, bevor sie verglichen werden

**Löst Befund 5.** Bestes Verhältnis von Risiko zu Aufwand: Die Zutat liegt im echten Protokoll, und heute geht es nur durch einen ASCII-Zufall gut aus.

Der `stale`-Vergleich ist ein roher Stringvergleich, und die verglichenen Werte kommen in **verschiedenen Schreibweisen** derselben Zeit: `listed_updated_at` endet auf `+00:00` (aus der Chatliste), `exported_updated_at` auf `Z` (aus dem ZIP) — nachgesehen in `tests/test_results/freecad/protokoll.json`. Dass der zeitgleiche Fall nicht als gewachsen kippt, hängt allein daran, dass `+` in ASCII vor `Z` liegt. Vertauschten die Quellen ihre Formate, würde jeder unveränderte Chat bei jedem `list` erneut geholt.

**Zu ändern:** Beide Werte vor dem Vergleich auf eine Form bringen. **Die Normalisierung gehört in beide Umsetzungen** — Konverter und Maßstab (`tests/wegegleichheit_referenz.py`) —, weil der Maßstab nichts importieren darf (Vorgabe 2.5). Genau dafür gibt es `tests/test_wegegleichheit.py`: Eine einseitige Änderung fällt dort durch.

**Dazu ein Prüfpunkt nach Kapitel 4:** Führen die Quellen ihre Zeitstempel weiterhin in derselben Form? Heute nirgends geführt. Art: kalt, am nächsten Protokoll ablesbar.

**Prüfung:** Falltabelle in `tests/test_wegegleichheit.py` um die gemischten Formate erweitern — gleiche Zeit in beiden Schreibweisen darf nicht `stale` ergeben, und zwar in beiden Richtungen.

## 3. Hüllen-Erkennung: Anhänge, Erzeugnisse und Denkschritte sind Lebenszeichen

**Löst Befund 1.**

`conversation_record()` erklärt jeden Chat mit Nachrichten, aber ohne gerenderten Gesprächstext zur Hülle. Ein Chat, dessen Nachrichten nur Anhänge tragen, wird als gelöscht archiviert — und weil `update_from_list()` nur `exported`-Einträge nach `stale` befördert, wird er **nie wieder geholt**, ohne Meldung. Die Absicht in Doku 3.1.3 war „kein Inhalt irgendwo", umgesetzt ist „kein Gesprächstext".

**Zu ändern:** Die `deleted`-Entscheidung um die übrigen Inhaltsträger erweitern — ein Anhang mit `extracted_content`, ein Erzeugnis oder ein behaltener Denkblock schließt die Hüllen-These aus. Das ist ein **strukturelles** Merkmal und verletzt Vorgabe 2.7 nicht. Die Messung stützt es: Die 15 echten Hüllen in den vorliegenden ZIPs tragen keine Anhänge.

**Zu entscheiden ist dabei eine zweite Frage**, die der Befund aufwirft: Soll ein `deleted`-Eintrag überhaupt für immer aus der Aktualisierung fallen? Ein an der Quelle gelöschter Chat kann nicht wiederkehren — ein fälschlich so markierter schon. Ein Weg wäre, `deleted` bei einem neueren `listed_updated_at` ebenfalls nach `stale` zu befördern; dann heilt sich der Fehler selbst. **Vor dem Kodieren zu klären.**

**Prüfung:** Prüfstück in `tests/test_export_convert.py` — ein Chat, dessen einzige Nachricht einen Anhang mit Inhalt und keinen Text trägt, darf nicht als Hülle gelten. Dazu die Gegenprobe, dass eine echte Hülle weiterhin erkannt wird.

## 4. Vier Texte auf das zurücknehmen, was belegt ist

Ein Arbeitsgang, weil alle vier denselben Kern haben: Sie behaupten mehr, als die Messung oder der Code hergibt. Kein Codeverhalten ändert sich.

**a) Die „Umfang"-Spalte aus beiden SKILL-Dateien entfernen** — löst **Befund 3**. Die Statistik-Vorlage verlangt eine Nachrichtenzahl, die vor dem Abruf niemand kennt, während dieselbe Datei zweimal verbietet, eine Zahl selbst zu bilden. Beide echten Läufe haben deshalb von der Vorlage abweichen müssen. Ersatzlos streichen; die Anwender-READMEs führen die Tabelle längst richtig ohne diese Spalte.

**b) Die Kommandonamen in Doku 1.4 richtigstellen** — **erledigt am 22. August 2026** im Zug der mechanischen Prüfung unten, weil sie genau dieser Fund war. Dort standen `plan`, `overview` und `map`; jetzt stehen die Kommandos, die tatsächlich rechnen (`list` und `diff`).

**c) Den Denkschritte-Absatz beider Skill-READMEs zurücknehmen** — löst **Randnotiz 1**. Sie behaupten kategorisch, Anthropic schreibe die Überlegungen „seit Ende Juli 2026 nicht mehr" aus und bei älteren Chats seien sie „vollständig vorhanden". Doku 3.1.1 sagt dagegen, das Verhältnis schwanke „innerhalb eines einzigen Chats von Tag zu Tag" und die Ursache sei „nicht ermittelt". Die brauchbarere Auskunft für den Nutzer: Überlegungen können fehlen, die Ursache ist unbekannt, ein leeres Ergebnis ist kein Defekt des Werkzeugs.

**d) Den Namens-Join in `inspect_export.py` nachziehen** — löst **Befund 6**. Das Werkzeug zählt sämtliche `files`-Einträge als „content NOT in the export" und überzeichnet den Verlust um mehr als das Doppelte (524 gegen 205). Das ist mehr als eine irreführende Ausgabe: Doku 4.2 kündigt als kalte Prüfung den „Anteil der `files`-Einträge mit Namenspartner" an, und diese Zahl berechnet kein Werkzeug — der Prüfpunkt ist so nicht durchführbar, und wer ihn mit `inspect_export.py` abarbeitet, schlägt falschen Alarm. Beide Zahlen getrennt ausgeben. Die Logik hat der Konverter in `file_references()`, sie darf aber nicht importiert werden (Vorgabe 2.9).

**Prüfung:** Für (d) eine Erwartung in `tests/test_inspect_export.py` — das Fixture trägt eine Datei, die als inhaltsloser `files`-Eintrag *und* als `attachment` mit Inhalt vorkommt; sie darf nicht als Verlust gezählt werden. Für (a) bis (c) genügt der Docstring-Wächter bzw. das Lesen.

## 5. Vier Doku-Präzisierungen

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

**Kommandonamen, Flags und Feldnamen einmal vollständig gegen den Code gehalten**, über alle Dokumente des Bereichs und in beiden Richtungen. Zwei echte Funde, beide behoben: die Kommandonamen in 1.4 (Randnotiz 2, Schritt 4b) und das undokumentierte Metadatenfeld `imported_at`; dazu `chats` als fehlende Strukturangabe in 2.4. Beide Feldmengen sind seither deckungsgleich, maschinell geprüft.

**Das Verfahren und die typischen Falsch-Positiven stehen jetzt in Vorgabe 2.9**, nicht hier — diese Datei verschwindet mit den Befunden, die Regel gilt weiter.
