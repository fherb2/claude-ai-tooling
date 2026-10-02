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

`rules-register.de.md` fertigstellen: Grammatik, Markerformen, Registerort, Regel für Altes, Nachmarkierung, Robustheit. Die Datei liegt seit dem 2026-10-02 im Skill-Ordner und trägt den Text bereits; zu tun bleiben die Befunde, die Kapitel 3.2 dazu nennt, und das Ersetzen der Verweise auf die Entwicklungsdoku. Aufwand: 1 bis 2 Sitzungen. Fehleranfälligkeit gering; die Grammatik ist entschieden.

## 2 Regelteil Planung

`rules-planning.de.md` fertigstellen: Umbauziel, Inhalt geplanter Schritte, Ablageorte, Wiedervorlage; Stand wie in Schritt 1. Hängt an: nichts Offenem mehr; das Bereichsziel ist am 2026-10-02 entschieden (Kapitel 1.7.3, 3.3.2). Aufwand: 1 bis 2 Sitzungen. Fehleranfälligkeit mittel: Der frühere Punkt T2 war inhaltlich strittig.

## 3 Regelteil Skill-Parameter

`rules-startup.de.md` fertigstellen: Erhebung, Skill-Parameterdatei, „Doku wächst an Festlegungen", mehrere Vorhaben je Repository, Erkennung der Projektart. Der Skillstart-Ablauf selbst steht in `SKILL.de.md` (Kapitel 3.10), nicht in diesem Regelteil. Stand wie in Schritt 1; dazu Befund B-12, die fehlende Erhebung. Hängt an: Schritt 1. Aufwand: 1 bis 2 Sitzungen. Fehleranfälligkeit mittel: Zu viele Startfragen machen den Skill lästig.

## 10 Regelteile von Mechanik entlasten und neu schneiden

**Steht vor Schritt 4**, weil er bestimmt, was das Skript ausgeben muss. Drei Arbeiten, die zusammengehören:

**Erstens die Entlastung.** Jeden Regelteil daraufhin durchgehen, ob er eine Mechanik nacherzählt, die ein Kommando ausführt (Vorgabe 2.6). Wo ja, tritt an die Stelle der Beschreibung ein Satz darüber, was die Ausgabe des Kommandos sagt — und die Rechenvorschrift wandert in die Doku, wo sie als Spezifikation gebraucht wird. Erkannte Kandidaten mit geschätztem Umfang: die Entscheidungsliste R1–R7 (728 Token), die Registergrammatik (667), die Trailer-Grammatik der Commit-Notizen (rund 300 von 538), Teile der Feldtabelle (rund 300 von 787), der Aufbau des Planabschnitts (rund 300 von 637), Registerort und ID-Vergabe (rund 350). Zusammen etwa 2 600 von 7 900 Token der beiden heute immer geladenen Teile. Die Abgrenzung ist im Einzelfall zu prüfen und nicht am Thema abzulesen: Was rechnet, gehört ins Skript; was Verhalten regelt, bleibt.

**Zweitens der Schnitt.** `rules-hardness.de.md` und `rules-register.de.md` werden heute beide immer und gemeinsam geladen — die Trennung spart nichts (Vorgabe 2.15). Zu entscheiden: zusammenlegen, oder die Registergrammatik an den Anlass „ein freigegebener Plan wird ausgeführt" binden. Das zweite spart mehr und hängt daran, ob der Anlass trennscharf bleibt.

**Drittens die Wurzel.** Die beiden mechanischen Vorentscheidungen des Ablaufs — Projektart und `mode` — werden ein Kommandoaufruf statt zweier beschriebener Prüfverfahren. Damit sinkt, was ein abgewähltes Projekt zahlt.

Dazu die Adressierung nach Vorgabe 2.16: durchlaufende Nummern in den Zieltexten, benannte Überschriften für Tabellen, auf die verwiesen wird. Hängt an: nichts. Aufwand: 2 bis 3 Sitzungen. Fehleranfälligkeit mittel: Die Grenze zwischen Rechenvorschrift und Verhaltensregel verläuft nicht am Thema.

## 4 Skript Stufe 1

`files/software-design-doc.py` mit `list`, `show`, `next-id`, `add`, `check`, `mentions`, `hardness`, `impact --hops`, `plan-section`, `explain`, `notes` (Kapitel 3.6.4); Ausgabevertrag nach Kapitel 3.6; Prüffälle mit Fixture und beschädigten Varianten. Hängt an: Schritt 1 und 2 (für `target:`). Aufwand: 3 bis 4 Sitzungen. Fehleranfälligkeit hoch: Parsing-Ränder (U+00A0, Klammern in Prosa, umbrochenes Layout), Kapitelableitung bei verschobenen Markern. Vor dem ersten Code den Skill `common-code-generation` laden.

**Befund B-14 (2026-09-25): Die Kommandoliste dieses Schritts passt nicht zur Spezifikation.** Sie nennt `list` und `add`; beide gibt es in Kapitel 3.6.4 nicht, und für `add` steht dort ausdrücklich, dass es keines gibt — Registerzeilen entstehen ausschließlich über `apply` aus einem freigegebenen Plan, in einem Aufruf statt in zehn, weil jeder Skriptaufruf die Instanz Geld kostet (Vorgabe 2.7). Umgekehrt fehlen hier die beiden Ankerkommandos `open` (Bereich öffnen) und `apply` (Plan ausführen). Die Liste stammt aus der Zeit vor dem Schnitt entlang der Anker (Kapitel 1.3.6) und wurde beim Umbau nicht nachgezogen. Vermutlich ist schlicht diese Liste nachzuführen — aber das ist zu prüfen und nicht vorauszusetzen: Ein `list` für die Nachfrage des Entwicklers wäre denkbar, auch wenn es im Ablauf nicht vorkommt.

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
