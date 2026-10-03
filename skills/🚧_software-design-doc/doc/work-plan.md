# Fahrplan des Vorhabens `software-design-doc`

Die anstehenden Schritte. Erledigte Schritte fliegen raus; die Nummern der übrigen werden dabei nicht neu vergeben, neue Schritte zählen hoch. Die Reihenfolge der Schritte im Dokument ist maßgeblich, wo Abhängigkeiten bestehen; sie stehen bei jedem Schritt.

Dieser Fahrplan folgt dem bisherigen Schema (Kapitel 2.14 der Vorgaben). Sitzungsschätzungen sind grob; eine Sitzung ist ein zusammenhängender Arbeitsblock mit Freigaben. Vor Schritt 1 sind die Punkte unter „Klärungsbedarf" zu entscheiden oder bewusst offen zu lassen.

## Offene Entscheidungen

**Es gibt keine `[Q-nn]`-Blöcke mehr** (umgestellt am 2026-09-25). Bis dahin standen offene Punkte als eigene Blöcke am Ende der Kapitel von Segment 3 — mit Kontext, Optionen, Vorschlag und einer leeren Zeile **Antwort:**. Das erwies sich als falscher Ort: Segment 3 trägt die Umsetzungsbeschreibung, und eine dort auftauchende Frage bedeutet fast immer, dass etwas Funktionales oder eine Vorgabe noch nicht entschieden ist. Alle verbliebenen Punkte sind deshalb an die Stelle gewandert, an der die Entscheidung hingehört, und dort so in den Text eingearbeitet, dass sich die Frage aus dem Gedankengang selbst ergibt (Festlegung des Entwicklers vom 2026-09-25).

Vorgehen seitdem: Der Entwickler geht die Kapitel in Leseordnung durch und antwortet dort, wo die Frage steht. Eine beantwortete Entscheidung wird zum Entscheidungstext an derselben Stelle und in `status.md` vermerkt; die Nummern der früheren Blöcke werden nicht neu vergeben.

| Offener Punkt | Wo er steht | Blockiert |
|---|---|---|
| Ob der Zustandsbericht am Sitzungsstart gebaut wird (vormals Q-27) | `1_overview.md`, 1.7.6 — Bauweise in `3_7_hooks.md` | 6 |
| Welche Ausgabeform der Standard ist (vormals Q-23) | `2_rules.md`, 2.5 — messbar in der Probe | 4 |
| Zuschnitt des Kapitels Migration und Installation | `3_9_migration.md`, Kopf | 9 |

Keine Entscheidungen des Entwicklers, sondern technische Wahlen bei der Umsetzung sind seit dem 2026-09-25: die Kodierung des Abbruchwerts (vormals Q-18, Kapitel 3.5.2), die Kostenfunktion der Auswirkungsrechnung (vormals Q-21, Kapitel 3.6.5) und die offenen Punkte der Pfadauflösung (Kapitel 3.7.4). Sie blockieren keinen Schritt als Entscheidung, sondern nur als Arbeit.

Geklärte Punkte stehen in `status.md`: Q-01 bis Q-12, Q-14 bis Q-17, Q-19, Q-20, Q-22, Q-24 bis Q-26, Q-28, Q-31 und Q-32. Gestrichen, weil sie nicht in diese Doku gehören: Q-29 und Q-30.

## 1 Regelteil Marker und Register

Die Abschnitte 11 bis 19 von `rules-core.de.md` fertigstellen: Grammatik, Markerformen, Registerort, Regel für Altes, Nachmarkierung, Robustheit. Der Text liegt seit dem 2026-10-02 im Skill-Ordner — bis zum 2026-10-04 als eigene Datei `rules-register.de.md`, seither im zusammengelegten Regelteil; zu tun bleiben die Befunde, die Kapitel 3.2 dazu nennt, und das Ersetzen der Verweise auf die Entwicklungsdoku. Aufwand: 1 bis 2 Sitzungen. Fehleranfälligkeit gering; die Grammatik ist entschieden.

## 2 Regelteil Planung

`rules-planning.de.md` fertigstellen: Umbauziel, Inhalt geplanter Schritte, Ablageorte, Wiedervorlage; Stand wie in Schritt 1. Hängt an: nichts Offenem mehr; das Bereichsziel ist am 2026-10-02 entschieden (Kapitel 1.7.3, 3.3.2). Aufwand: 1 bis 2 Sitzungen. Fehleranfälligkeit mittel: Der frühere Punkt T2 war inhaltlich strittig.

## 3 Regelteil Skill-Parameter

`rules-startup.de.md` fertigstellen: Erhebung, Skill-Parameterdatei, „Doku wächst an Festlegungen", mehrere Vorhaben je Repository, Erkennung der Projektart. Der Skillstart-Ablauf selbst steht in `SKILL.de.md` (Kapitel 3.10), nicht in diesem Regelteil. Stand wie in Schritt 1; dazu Befund B-12, die fehlende Erhebung. Hängt an: Schritt 1. Aufwand: 1 bis 2 Sitzungen. Fehleranfälligkeit mittel: Zu viele Startfragen machen den Skill lästig.

## 10 Regelteile von Mechanik entlasten und neu schneiden

**Steht vor Schritt 4**, weil er bestimmt, was das Skript ausgeben muss. Drei Arbeiten, die zusammengehören:

**Erstens die Entlastung — am 2026-10-04 ausgeführt.** `rules-core.de.md` ist auf das durchgegangen, was eine Mechanik nacherzählt, die ein Kommando ausführt (Vorgabe 2.6). Entfernt sind die Entscheidungsliste R1–R7, die Formtabelle der Registerzeilen samt Schreibregeln, die vierstufige Suche nach der Registerdatei, die ID-Vergaberegel und die Aufzählung der Felder des Planabschnitts; an ihre Stelle traten Verhaltensregeln für den Umgang mit dem Ergebnis. Gemessen: 2215 Token heraus, 1419 Token Ersatz hinein, netto 802 von 7222 — elf Prozent. Der Fahrplan hatte 2600 veranschlagt und dabei übersehen, dass die Verhaltensregeln selbst Platz brauchen; der Hauptgewinn ist ohnehin nicht der Kontext, sondern dass keine Frage mehr zwei Zuständige hat.

**Die Zielorte,** nachdem die Prüfung ergeben hatte, dass Kapitel 1 und 2 die meisten Vorschriften bereits tragen: Die Entscheidungsliste steht jetzt in Kapitel 1.3.1 — sie legt fest, wann eine Festlegung bindet, und das ist keine Umsetzungseinzelheit. Die Form der Registerzeilen steht in Kapitel 3.6.4 bei `apply`, dem Kommando, das sie schreibt. Die Felder des Planabschnitts standen dort bei `plan-section` schon; die Eigenschaften der ID stehen in Kapitel 1.4 und als Bedingung 2 in Vorgabe 2.2, die Felder des Registers in Kapitel 1.4, das Suchmuster für die Registerdatei in Vorgabe 2.4.

**Abgelehnt: die Trailer-Grammatik der Commit-Notizen.** Der Fahrplan führte sie mit rund 300 Token als Kandidaten. Die Notiz schreibt aber die Instanz selbst in die Commit-Nachricht; es gibt kein Kommando dafür, `notes` liest sie nur aus dem Verlauf. Ohne die Feldliste könnte sie die Zeile nicht bilden — die Mechanik hätte dann keinen anderen Zuständigen, sondern gar keinen. Bei der Feldtabelle in Abschnitt 2 war der Ansatz von 300 Token ebenfalls zu hoch: Herausnehmbar war nur die Reibungsschwelle, deren Zahl allein das Kommando braucht.

**Zweitens der Schnitt — am 2026-10-04 ausgeführt.** `rules-hardness.de.md` und `rules-register.de.md` sind zu `rules-core.de.md` zusammengelegt, zwanzig durchlaufend nummerierte Abschnitte nach Vorgabe 2.16; die Rollentabelle steht zweispaltig als Abschnitt 3, womit B-11 erledigt ist. Die Wurzel lädt einen Regelteil statt zweier. An Token spart das fast nichts — beide wurden ohnehin immer gemeinsam geladen —, wohl aber einen Ladeschritt und drei Verweise, die beim Nutzer ins Leere liefen. Erwogen und verworfen war, die Registergrammatik stattdessen an den Anlass „ein freigegebener Plan wird ausgeführt" zu binden: Das hätte mehr gespart, aber eine Ladebedingung mehr gekostet und die Entlastung aus dem ersten Punkt vorweggenommen, die denselben Text ohnehin verkleinert.

**Offener Rest aus dem Schnitt:** Die Rollentabelle ist zweispaltig übernommen, nur Rolle und Funktion. Die dritte Spalte — was ein Abschnitt der jeweiligen Rolle beschreibt — wird gebraucht, wenn die Instanz dem Entwickler eine Rolle vorschlägt, und gehört deshalb nach `rules-startup.de.md` oder nach `rules-planning.de.md`; welches von beiden, ist noch zu entscheiden (Kapitel 3.3.1).

**Drittens die Wurzel.** Die beiden mechanischen Vorentscheidungen des Ablaufs — Projektart und `mode` — werden ein Kommandoaufruf statt zweier beschriebener Prüfverfahren. Damit sinkt, was ein abgewähltes Projekt zahlt.

Dazu die Adressierung nach Vorgabe 2.16: durchlaufende Nummern in den Zieltexten, benannte Überschriften für Tabellen, auf die verwiesen wird. Hängt an: nichts. Aufwand: 2 bis 3 Sitzungen. Fehleranfälligkeit mittel: Die Grenze zwischen Rechenvorschrift und Verhaltensregel verläuft nicht am Thema.

## 4 Skript Stufe 1

`files/software-design-doc.py` mit `open`, `plan-section`, `apply`, `check`, `impact --hops`, `mentions`, `hardness`, `notes`, `show`, `explain`, `next-id` (Kapitel 3.6.4) — alles außer dem, was Schritt 5 baut; Ausgabevertrag nach Kapitel 3.6; Prüffälle mit Fixture und beschädigten Varianten. Hängt an: Schritt 1 und 2 (für `target:`). Aufwand: 3 bis 4 Sitzungen. Fehleranfälligkeit hoch: Parsing-Ränder (U+00A0, Klammern in Prosa, umbrochenes Layout), Kapitelableitung bei verschobenen Markern. Vor dem ersten Code den Skill `common-code-generation` laden.

**B-14 erledigt (2026-10-03): Die Liste ist nachgeführt, und ein `list` kommt nicht dazu.** Sie stammte aus der Zeit vor dem Schnitt entlang der Anker und nannte mit `list` und `add` zwei Kommandos, die es in Kapitel 3.6.4 nicht gibt, während die beiden Anker `open` und `apply` fehlten — ohne die Stufe 1 gar nicht lauffähig wäre. Zu `add` stand die Antwort ohnehin schon da: Registerzeilen entstehen ausschließlich über `apply` aus einem freigegebenen Plan, in einem Aufruf statt in zehn (Vorgabe 2.7).

Offen war allein, ob ein `list` für die Nachfrage des Entwicklers berechtigt ist. Es ist es nicht: `open` gibt je Festlegung bereits die `ITEM`-Zeile mit ID, Kapitel, Art, Status, Härte und Bezeichnung aus — also genau das, was ein `list` liefern würde —, und der Abgleich, den es nebenbei mitmacht, ist lesend und schadet nicht. Ein eigenes Kommando hätte dieselben Kosten wie ein überflüssiger Skill-Parameter: eine Zeile in jeder Übersicht, ein Verzweigungspfad im Skript, eine weitere Unterscheidung für die Instanz. Geschlossen wurde stattdessen die kleine Lücke, die `list` attraktiv gemacht hätte: `open` liest ohne `--chapter` jetzt den gesamten Doku-Ordner (Kapitel 3.6.4).

## 5 Skript Stufe 2

`lint` auf dem Diff, Fingerabdruck (`fp`, Abgleich in `check`), `supersede` und `retire`, `impact --weighted` mit den drei Kostenfunktionen in `impact.py`, networkx optional. Hängt an: Schritt 4. Die drei Kostenfunktionen werden alle gebaut; welche bleibt, entscheidet die Probe (Kapitel 3.6.5). Aufwand: 2 bis 3 Sitzungen. Fehleranfälligkeit hoch: Fehlalarmquote des Lints, Fingerabdruck-Rauschen.

## 6 Hooks

H1 bis H3 nach Kapitel 3.7: Frontmatter-Einbindung, Pfadauflösung prüfen, Zeitlimits messen, H3 als Angebot des Skillstarts. Hängt an: Schritt 4 und 5 sowie an der offenen Entscheidung, ob H3 gebaut wird (Kapitel 1.7.6); dieser Schritt und das Entscheidungstor der Probe (Kapitel 3.8.5) widersprechen sich darin bisher. Aufwand: 1 Sitzung. Fehleranfälligkeit mittel: Pfadauflösung aus dem Skill-Ordner im Hook-Kontext.

## 7 Skill zusammensetzen

Die Zieltexte liegen seit dem 2026-10-02 als eigene Dateien im Skill-Ordner; dieser Schritt macht aus ihnen ein auslieferbares Ganzes. Zu tun: Frontmatter der `SKILL.de.md` (Name nach Q-32, Hook-Einträge nach Kapitel 3.7), `standard.de.md` aus dem bisherigen Text mit den Anpassungen aus Kapitel 1.11, in jeder Datei die Verweise auf Kapitelnummern und auf Anhang A durch die Zielstruktur ersetzen, die Anrede vereinheitlichen, den Hinweisblock „In Arbeit" entfernen, Datumszeilen setzen, README in beiden Sprachen und die englischen Fassungen aller Regelteile. Auflösung des Abschnitts „Zusammenspiel mit anderen Skills". Hängt an: Schritt 1 bis 6. Aufwand: 2 Sitzungen. Fehleranfälligkeit gering.

## 8 Probe

Fixture, Ablauf und Messung nach Kapitel 3.8; Entscheidung der verbliebenen Verzweigungen (Kostenfunktion, Zitatmarker außerhalb `relate`; der Fingerabdruck ist seit dem 2026-09-25 entschieden, über H3 wird vorher entschieden); zweiter Durchlauf an einer echten Doku empfohlen. Hängt an: Schritt 4 bis 7. Aufwand: 2 bis 3 Sitzungen. Fehleranfälligkeit mittel: Die Fixture ist nicht die Doku des Entwicklers.

## 9 Migration und Installation

Kapitel 3.9: Umzug aus der globalen Anweisungsdatei Passage für Passage, Bereinigung der Projekt-`CLAUDE.md`, Werkzeug-Skills, Baustellenschild, Installation, Verweise im Repository. Hängt an: Schritt 8 bestanden und an der offenen Frage, was von Kapitel 3.9 überhaupt zur Entwicklung gehört (Kopf des Kapitels). Aufwand: 2 bis 3 Sitzungen. Fehleranfälligkeit mittel: Der Umzug berührt globale Anweisungen.

## Summe

Voller Pfad 15 bis 22 Sitzungen. Minimaler Pfad — Schritt 5 auf den Lint beschränkt, H3 weggelassen, Probe eine Sitzung — 11 bis 14. Den Unterschied machen gewichtete Auswirkungsrechnung, Fingerabdruck und die zweite Probenrunde.
