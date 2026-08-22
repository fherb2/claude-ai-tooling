# Prüfung der Befunde aus `befunde_logikpruefung_2026-08-22.md`

**Erstellt:** 2026-08-22, von der Sitzung, die diesen Bereich gebaut und dokumentiert hat — also mit Kenntnis der Ziele und der Entstehungsgeschichte, die dem prüfenden Modell fehlte.

**Auftrag:** Für jeden Befund entscheiden, ob er ein echter Fehler ist, ob er auf einem Missverständnis des Ziels oder der Doku beruht, oder ob nicht der Code, sondern die Doku falsch bzw. unverständlich ist. Danach: Was ist wesentlich genug, um es aufzulösen.

**Vorgehen:** Jeder Befund an der genannten Codestelle nachgesehen, die Gegenstelle in der Doku gelesen, drei Fälle am laufenden System gegengeprüft (Zeitstempelformate im echten Protokoll, die Kommandoliste des Skripts, die Tabellen in SKILL gegen README).

## Gesamturteil

**Kein Befund beruht auf einem Missverständnis.** Alle vierzehn Befunde und beide Randnotizen sind technisch zutreffend; die Codestellen, Zeilennummern und Schlussfolgerungen stimmen. Auch die Schweregrade sind vertretbar gesetzt — insbesondere ist die Einstufung „kein Befund der Stufe Hoch" nach meiner Prüfung richtig: Die Kernpfade tragen.

Das ist ein Ergebnis, das ich so nicht erwartet hatte, und es verschiebt die Bewertung von zwei Befunden nach oben: **Randnotiz 2 und Befund 3 sind Fehler, die ich selbst verursacht und bei meiner eigenen Verweisprüfung am 22. August übersehen habe.** Ich hatte alle 198 Kapitelverweise der Doku und alle 72 Code-Verweise inhaltlich geprüft — aber nur *Verweise*. Kommandonamen und Ausgabevorlagen habe ich nicht gegen den Code gehalten. Genau dort liegen beide Funde.

**Vier Befunde halte ich für wesentlich genug, sie aufzulösen** (2, 3, 5 und Randnotiz 2), **zwei weitere für lohnend** (1, 6). Der Rest ist korrekt festgehalten und kann liegen bleiben, solange er als bekannt vermerkt ist — dafür ist diese Datei da.

---

## Mittel

### Befund 1 — bestätigt, echter Code-Fehler. Auflösen lohnt.

Verifiziert: `conversation_record()` setzt `"deleted": bool(messages) and text_total == 0`, und `text_total` zählt allein den gerenderten Gesprächstext. Ein Chat, dessen Nachrichten nur Anhänge tragen, wird als gelöscht archiviert. Der Folgeschaden ist ebenfalls verifiziert: `update_from_list()` befördert nur `STATUS_EXPORTED` nach `stale`, ein `deleted`-Eintrag also nie — der Chat wird nie wieder geholt, ohne Meldung.

**Kein Missverständnis, und die Doku steht dem nicht entgegen:** 3.1.3 definiert Hüllen als „Nachrichten vorhanden, aber `text` und `content` leer" — die Absicht war „kein Inhalt irgendwo", umgesetzt ist „kein Gesprächstext". Das ist eine echte Lücke zwischen Absicht und Code, nicht bloß eine unglückliche Formulierung.

**Der Vorschlag des Befundes ist gut und regelkonform:** Ein Anhang mit `extracted_content` als Gegenindiz zur Hüllen-These ist ein **strukturelles** Merkmal und verletzt Vorgabe 2.7 (Auswahl nie inhaltlich) nicht. Dasselbe gilt für Erzeugnisse und behaltene Denkblöcke. Die Messung des Befundes stützt das zusätzlich: Die 15 echten Hüllen in den vorliegenden ZIPs tragen keine Anhänge.

**Warum trotzdem nicht dringend:** Es braucht einen Chat, der *ausschließlich* aus textlosen Nachrichten besteht. Die 22 gefundenen Einzelnachrichten sind die Zutat, kein Beleg für einen betroffenen Chat. In 211 echten Chats ist keiner aufgetreten.

### Befund 2 — bestätigt, echter Code-Fehler. Der wesentlichste der Liste.

Verifiziert: `cmd_convert()` schreibt `"status": STATUS_DELETED if record["deleted"] else STATUS_EXPORTED` ohne jeden Vergleich mit `listed_updated_at`. Das Protokoll weiß in diesem Moment, dass die Quelle neuer ist — der Wert steht direkt daneben und wird nicht gelesen.

**Was diesen Befund über die anderen hebt, ist die Eintrittswahrscheinlichkeit.** Das Szenario ist nicht konstruiert: Der Skill sucht die ZIP **im Download-Ordner**, und dort liegen bei diesem Nutzer nachweislich sechs Export-ZIPs verschiedener Zeiträume nebeneinander (am 21. August gezählt). Wird das falsche genommen, meldet `diff` anschließend „nichts offen" — das Werkzeug behauptet einen Abgleich, den es nicht geleistet hat. Genau die Klasse stiller Fehler, gegen die der ganze Entwurf gebaut ist (Doku 1.4: „Hinge die Entscheidung ‚was fehlt noch' daran, dass sie richtig zählt, wäre der Fehler still").

**Auflösung wäre klein:** Beim Setzen von `exported` prüfen, ob `record["updated_at"]` den gelisteten Stand erreicht; sonst `stale` beibehalten und es sagen. Das ist eine Bedingung an einer Stelle, kein Umbau.

### Befund 3 — bestätigt, und der Fehler liegt in einer Datei, die ich geschrieben habe.

Verifiziert bis in die Zeilennummern: Die Statistik-Vorlage in `SKILL.de.md:65-66` und `SKILL.en.md:65-66` führt eine Spalte „Umfang ~310 N." bzw. „Scope ~310 msg.", die kein Skriptlauf hergibt — die Chatliste trägt keine Nachrichtenzahl, das Protokoll kennt `turns` erst nach der Konvertierung, `list` und `diff` geben keinen Umfang aus. Dieselben Dateien verbieten zweimal ausdrücklich, eine Zahl selbst zu bilden. Die Anwender-READMEs führen die Tabelle korrekt ohne diese Spalte.

**Der Widerspruch hat sich in der Praxis bereits gezeigt**, und das ist der eigentliche Beleg: Beim Nachfüll-Lauf am 21. August schrieb die ausführende Instanz in die Spalte „unbekannt\*" und setzte eine Fußnote, dass die Chatliste den Umfang vorab nicht liefert. Sie hat also richtig gehandelt und dabei von der Vorlage abweichen müssen. Beim Großimport zuvor tat eine andere Instanz dasselbe. Zwei von zwei Läufen sind gegen die Vorlage gelaufen.

**Auflösung: Spalte ersatzlos aus beiden SKILL-Dateien entfernen.** Kein Ersatz nötig — die Wegempfehlung hängt an der Chatzahl, nicht am Nachrichtenumfang, und die Anhangsgröße kennt vorab ebenfalls niemand.

---

## Niedrig

### Befund 4 — Logik bestätigt, aber es ist ein Doku-Fehler, kein Code-Fehler.

Die Herleitung stimmt: `created_after` ist nur dann eine exakte Untergrenze, wenn die frühere Liste vollständig war. Denselben Fall — nicht bis zum Ende geblättert — führt das Vorhaben bei den verschwundenen Chats ausdrücklich als reale Bedienlage (Vorgabe 2.4), für `created_after` aber nicht.

**Hier liegt der Fehler in der Doku, nicht im Code.** Vorgabe 2.4 stuft die Quelle als „exakt" ein; belastbar ist sie nur als „exakt, sofern die vorherige Liste vollständig war". Der Code selbst kann das nicht wissen und rät auch nicht — er tut, was die Vorgabe sagt.

**Einschränkung, die der Befund selbst nennt und die ich bestätige:** Betroffen ist praktisch nur der `--map`-Pfad. Der Web-Weg blättert deterministisch über `pagination.has_more`, dort kann die Liste nicht unbemerkt unvollständig sein. Da `--map` inzwischen der Rückfall für Konten ohne Browser-Anbindung ist, halte ich eine Präzisierung der Vorgabe für ausreichend — Codeänderung wäre Aufwand für einen Weg, den kaum jemand geht.

### Befund 5 — bestätigt, latent, aber mit realer Zutat. Auflösen empfohlen.

Am echten Protokoll nachgesehen und bestätigt: In `tests/test_results/freecad/protokoll.json` stehen für dieselben Chats `listed_updated_at` mit `+00:00` und `exported_updated_at` mit `Z`. Der `stale`-Vergleich ist ein roher Stringvergleich. Nachgerechnet: `'…984103+00:00' > '…984103Z'` ergibt `False`, weil `+` (0x2B) in ASCII vor `Z` (0x5A) liegt — der zeitgleiche Fall kippt heute also **zufällig richtig**. Vertauschten die Quellen ihre Formate, ergäbe derselbe Vergleich `True`, und jeder unveränderte Chat würde bei jedem `list` als gewachsen gemeldet: eine Dauerschleife „erneut holen", die Serverlast erzeugt und den Nutzer in die Irre führt.

**Das ist der Befund mit dem besten Verhältnis von Risiko zu Aufwand.** Die Formatmischung ist nicht hypothetisch, sie liegt vor. Eine Normalisierung beider Werte vor dem Vergleich schließt zusätzlich den zweiten genannten Fall (gekürzte Präzision). Dass die Normalisierung dann in **beiden** Umsetzungen stehen muss, ist kein Hindernis, sondern genau der Zweck von Vorgabe 2.5 — `tests/test_wegegleichheit.py` fängt eine einseitige Änderung.

Zusätzlich richtig: Der Formatgleichlauf der Quellen gehört als Prüfpunkt nach Kapitel 4. Er ist heute nirgends geführt.

### Befund 6 — bestätigt, echter Fehler, und er macht einen dokumentierten Prüfpunkt undurchführbar.

Verifiziert: `inspect_export.py` addiert `files_name_only += len(m.get("files") or [])` — sämtliche `files`-Einträge, ohne den Namens-Join gegen `attachments` — und beschriftet die Summe mit „content NOT in the export". Genau die Verwechslung, gegen die der Konverter mit `file_references()` gebaut wurde, nachdem sie am 17. August aufgefallen war (Doku 1.7 führt sie als gekippte Annahme).

**Der praktische Schaden ist größer als „irreführende Ausgabe":** Doku 4.2 kündigt als kalte Prüfung den „Anteil der `files`-Einträge mit Namenspartner" an. Diese Zahl berechnet kein Werkzeug. Wer den Prüfpunkt mit `inspect_export.py` abarbeitet, hält 524 gegen die dokumentierten 205 und schlägt Alarm, wo nichts gekippt ist — ein Frühwarnsystem, das falsch anschlägt, ist schlechter als keines.

**Auflösung:** Den Namens-Join in `inspect_export.py` nachziehen und beide Zahlen getrennt ausgeben (mit Partner / ohne Partner). Der Konverter hat die Logik bereits; sie darf nicht importiert werden (Vorgabe 2.9), aber sie ist kurz.

### Befund 7 — bestätigt, tote Warnung. Liegen lassen, aber vermerken.

Verifiziert durch Lesen von `split_branches()`: Die Bedingung `parent not in path_uuids and parent in {m["uuid"] for m in messages}` überspringt nur Nachrichten, deren Elternteil **in** der Konversation liegt. Eine Nachricht mit fremdem Elternteil fällt durch und wird als Zweigkopf eingesammelt; `orphans` bleibt leer. Die Warnung kann nur ein Elternzyklus erreichen, und für den stimmt ihr Wortlaut nicht.

**Inhaltlich geht nichts verloren** — der Zweig wird mitgenommen, die Integritätsrechnung stimmt weiter. Das ist der Grund, warum ich die Einstufung „Niedrig" für richtig halte und keine Auflösung empfehle. Zutreffend ist aber die Beobachtung zum Test: `an orphan is either placed or reported` ist durch das „oder" nicht in der Lage, den Verlust der Meldung zu bemerken. Wer die Warnung je reparieren will, muss zuerst den Test schärfen.

### Befund 8 — bestätigt, rein latent. Liegen lassen.

Verifiziert: `message_text()` greift bei `if not blocks` auf das flache `text`-Feld zurück, das nur die ZIP-Form hat. Die Messung des Befundes ist der entscheidende Teil: 0 von 10.779 echten Nachrichten sind blocklos mit Text. Der Fall ist konstruierbar, aber nicht beobachtet.

**Die Einordnung ist präzise und die Formulierung fair** („die Zusage ‚baulich gleich' hängt an dieser einen Stelle von einem Feld ab, das nur eine Quelle hat"). Genau so würde ich es in die Doku schreiben, wenn wir es festhalten wollen — als bekannte Grenze der baulichen Gleichheit, nicht als Fehler.

---

## Kleinkram

Alle sechs verifiziert. Einordnung je Fall:

**Befund 9** (`turns` bei Hüllen) ist streng genommen der einzige echte **Doku-Code-Widerspruch** im Kleinkram und nach unserer eigenen Regel damit ein Defekt: Vorgabe 2.2 definiert `turns` als „Anzahl importierter Redebeiträge", der Code schreibt bei einer Hülle die Skelettlänge, während `messages` leer bleibt. Ich würde die **Doku** ändern, nicht den Code — die Zahl ist nützlich, sie sagt, wie groß der Chat war, bevor er gelöscht wurde. Die Felddefinition muss das dann sagen.

**Befund 10** (`protocol_version` wird zurückgestempelt) ist ein legitimer Robustheitsbefund ohne heutige Wirkung; es gibt keine Version 2. Vermerken genügt.

**Befund 11** (`report` läuft über das Verzeichnis) ist bewusst so, aber die Begründung fehlt in der Doku: `report` beschreibt den *Bestand*, `diff` das *Protokoll*. Dass eine Waise in den Summen mitzählt, ist damit konsequent — nur nirgends gesagt. Ein Satz in 3.1.6 würde es auflösen.

**Befund 13** (Dublette nur über Text) und **Befund 14** (Verlustverweise über das Label dedupliziert) sind beide verifiziert und beide von der prüfenden Instanz selbst als konstruiert markiert. Vermerken genügt.

---

## Die beiden Randnotizen — wichtiger als ihre Platzierung vermuten lässt

Die prüfende Instanz hat sie außerhalb des Auftrags geführt, weil Doku-Qualität nicht Gegenstand war. Beide sind aber **Tatsachenfehler in Texten, die ich geschrieben habe**, und der zweite ist ein Fund, den meine eigene Prüfung hätte liefern müssen.

### Randnotiz 1 — bestätigt: Die Skill-README behauptet mehr, als die Messung hergibt.

`skills/chat-export/README.de.md:192` (und die englische Fassung) sagt kategorisch: Anthropic schreibe die Überlegungen „seit Ende Juli 2026 nicht mehr" aus, und „bei älteren Chats sind sie vollständig vorhanden". Doku 3.1.1 sagt dagegen: Das Verhältnis „schwankt erheblich", wechselte „innerhalb **eines einzigen** Chats von Tag zu Tag", und „woran es hängt, ist nicht ermittelt und wird hier auch nicht vermutet."

**Das ist ein Widerspruch zwischen Anwenderdokumentation und Messung, und er geht in die für den Nutzer schädliche Richtung:** Wer der README glaubt, sucht in älteren Chats nach Überlegungen, die dort fehlen können, und sucht in neueren nicht, wo welche sein können. Der Satz „Es lohnt sich also nicht, danach zu suchen" ist die stärkste und am schlechtesten belegte Aussage der ganzen README.

**Auflösung: den Absatz auf das zurücknehmen, was gemessen ist.** Dass Überlegungen fehlen *können* und dass die Ursache unbekannt ist, ist für den Nutzer die brauchbarere Auskunft — sie sagt ihm, dass ein leeres Ergebnis kein Defekt des Werkzeugs ist, ohne ihm ein Datum zu versprechen.

### Randnotiz 2 — bestätigt, und das ist der Fund, der mir selbst durchgegangen ist.

Doku 1.4 schreibt: „Deshalb rechnen `plan`, `overview` und `map` in dem Skript, das die JSON parst." Das Skript hat fünf Kommandos: `list`, `convert`, `diff`, `report`, `analyse`. `plan` und `overview` waren Kommandos des entfallenen Lese-Wegs; `map` existiert nur als Flag `list --map`.

**Warum meine Prüfung am 22. August das nicht gefunden hat:** Ich habe alle 198 Kapitelverweise und alle 72 Code-Verweise inhaltlich geprüft — aber nur Verweise. Kommandonamen sind keine Verweise, und ich habe sie nicht gegen den Parser gehalten, obwohl `tests/test_docstrings.py` genau das für die Docstrings tut. Die Prüfung hätte die Kommandoliste einschließen müssen.

**Auflösung: den Satz auf die tatsächlichen Kommandos bringen.** Und die Lehre gehört festgehalten: Bei der nächsten Doku-Prüfung sind Kommandonamen, Flags und Feldnamen genauso gegen den Code zu halten wie Kapitelverweise — mechanisch geht das, `test_docstrings.py` zeigt wie.

---

## Empfehlung

**Auflösen (vier Punkte, jeder klein):**

1. **Befund 2** — `convert` darf `stale` nicht ohne Prüfung des Stands auf `exported` setzen. Höchste Eintrittswahrscheinlichkeit der ganzen Liste, stiller Fehler, kleine Änderung.
2. **Befund 5** — Zeitstempel vor dem Vergleich normalisieren, in beiden Umsetzungen; Formatgleichlauf als Prüfpunkt nach Kapitel 4.
3. **Befund 3** — die „Umfang"-Spalte aus beiden SKILL-Dateien entfernen.
4. **Randnotiz 2** — die Kommandonamen in Doku 1.4 richtigstellen.

**Lohnend, wenn wir dabei sind (zwei Punkte):**

5. **Befund 1** — Anhänge, Erzeugnisse und Denkblöcke als strukturelles Gegenindiz zur Hüllen-These.
6. **Befund 6** — Namens-Join in `inspect_export.py`, damit Prüfpunkt 4.2 durchführbar wird. Dazu **Randnotiz 1** (README-Absatz zurücknehmen), weil beides denselben Kern hat: eine Zahl bzw. eine Aussage, die mehr behauptet als belegt ist.

**Doku-Präzisierungen ohne Codeänderung:** Befund 4 (`created_after` „exakt, sofern die Liste vollständig war"), Befund 9 (Felddefinition `turns` bei Hüllen), Befund 11 (`report` beschreibt den Bestand, nicht das Protokoll), Befund 8 (bekannte Grenze der baulichen Gleichheit).

**Nur vermerken, nichts tun:** Befunde 7, 10, 13, 14.

**Nummer 12 ist kein Befund** und als solcher in `befunde_logikpruefung_2026-08-22.md` kommentiert; er kommt hier nicht mehr vor.
