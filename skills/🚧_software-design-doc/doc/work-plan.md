# Fahrplan des Vorhabens `software-design-doc`

Die anstehenden Schritte. Erledigte Schritte fliegen raus; die Nummern der übrigen werden dabei nicht neu vergeben, neue Schritte zählen hoch. Die Reihenfolge der Schritte im Dokument ist maßgeblich, wo Abhängigkeiten bestehen; sie stehen bei jedem Schritt.

Dieser Fahrplan folgt dem bisherigen Schema (Kapitel 2.14 der Vorgaben). Sitzungsschätzungen sind grob; eine Sitzung ist ein zusammenhängender Arbeitsblock mit Freigaben. Vor Schritt 1 sind die Punkte unter „Klärungsbedarf" zu entscheiden oder bewusst offen zu lassen.

## Offene Entscheidungen

**Es gibt keine `[Q-nn]`-Blöcke mehr** (umgestellt am 2026-09-25). Bis dahin standen offene Punkte als eigene Blöcke am Ende der Kapitel von Segment 3 — mit Kontext, Optionen, Vorschlag und einer leeren Zeile **Antwort:**. Das erwies sich als falscher Ort: Segment 3 trägt die Umsetzungsbeschreibung, und eine dort auftauchende Frage bedeutet fast immer, dass etwas Funktionales oder eine Vorgabe noch nicht entschieden ist. Alle verbliebenen Punkte sind deshalb an die Stelle gewandert, an der die Entscheidung hingehört, und dort so in den Text eingearbeitet, dass sich die Frage aus dem Gedankengang selbst ergibt (Festlegung des Entwicklers vom 2026-09-25).

Vorgehen seitdem: Der Entwickler geht die Kapitel in Leseordnung durch und antwortet dort, wo die Frage steht. Eine beantwortete Entscheidung wird zum Entscheidungstext an derselben Stelle und in `status.md` vermerkt; die Nummern der früheren Blöcke werden nicht neu vergeben.

| Offener Punkt | Wo er steht | Blockiert |
|---|---|---|
| Wie ein Schritt einen ganzen Bereich als Umbauziel benennt (vormals Q-13) | `1_overview.md`, 1.7.3 — Folge für die Vorgaben in `2_rules.md`, 2.3 | 2 |
| Ob der Zustandsbericht am Sitzungsstart gebaut wird (vormals Q-27) | `1_overview.md`, 1.7.6 — Bauweise in `3_7_hooks.md` | 6 |
| Welche Ausgabeform der Standard ist (vormals Q-23) | `2_rules.md`, 2.5 — messbar in der Probe | 4 |
| Zuschnitt des Kapitels Migration und Installation | `3_9_migration.md`, Kopf | 9 |

Keine Entscheidungen des Entwicklers, sondern technische Wahlen bei der Umsetzung sind seit dem 2026-09-25: die Kodierung des Abbruchwerts (vormals Q-18, Kapitel 3.5.2), die Kostenfunktion der Auswirkungsrechnung (vormals Q-21, Kapitel 3.6.5) und die offenen Punkte der Pfadauflösung (Kapitel 3.7.4). Sie blockieren keinen Schritt als Entscheidung, sondern nur als Arbeit.

Geklärte Punkte stehen in `status.md`: Q-01 bis Q-12, Q-14 bis Q-17, Q-19, Q-20, Q-22, Q-24 bis Q-26, Q-28, Q-31 und Q-32. Gestrichen, weil sie nicht in diese Doku gehören: Q-29 und Q-30.

## 1 Regelteil Marker und Register

Kapitel 3.2 zum Regelteil `rules-register.md` ausformulieren: Grammatik, Markerformen, Registerort, Regel für Altes, Nachmarkierung, Robustheit. Ergebnis: Entwurf im Chat, danach Datei im Skill-Ordner. Aufwand: 1 bis 2 Sitzungen. Fehleranfälligkeit gering; die Grammatik ist entschieden.

## 2 Regelteil Planung

Kapitel 3.4 zum Regelteil `rules-planning.md`: Umbauziel, Inhalt geplanter Schritte, Ablageorte, Wiedervorlage. Hängt an: der offenen Entscheidung über das Bereichsziel (Kapitel 1.7.3 und Vorgabe 2.3). Aufwand: 1 bis 2 Sitzungen. Fehleranfälligkeit mittel: Der frühere Punkt T2 war inhaltlich strittig.

## 3 Regelteil Skill-Parameter

Kapitel 3.5 zum Regelteil `rules-startup.md`: Erhebung, Skill-Parameterdatei, „Doku wächst an Festlegungen", mehrere Vorhaben je Repository. Die Mode-Frage und der Skillstart-Ablauf selbst sind Teil der `SKILL.md` (Kapitel 3.10), nicht dieses Regelteils. Hängt an: Schritt 1. Aufwand: 1 bis 2 Sitzungen. Fehleranfälligkeit mittel: Zu viele Startfragen machen den Skill lästig.

## 4 Skript Stufe 1

`files/software-design-doc.py` mit `list`, `show`, `next-id`, `add`, `check`, `mentions`, `hardness`, `impact --hops`, `plan-section`, `explain`; Ausgabevertrag nach Kapitel 3.6; Prüffälle mit Fixture und beschädigten Varianten. Hängt an: Schritt 1 und 2 (für `target:`). Aufwand: 3 bis 4 Sitzungen. Fehleranfälligkeit hoch: Parsing-Ränder (U+00A0, Klammern in Prosa, umbrochenes Layout), Kapitelableitung bei verschobenen Markern. Vor dem ersten Code den Skill `common-code-generation` laden.

## 5 Skript Stufe 2

`lint` auf dem Diff, Fingerabdruck (`fp`, Abgleich in `check`), `supersede` und `retire`, `impact --weighted` mit den drei Kostenfunktionen in `impact.py`, networkx optional. Hängt an: Schritt 4. Die drei Kostenfunktionen werden alle gebaut; welche bleibt, entscheidet die Probe (Kapitel 3.6.5). Aufwand: 2 bis 3 Sitzungen. Fehleranfälligkeit hoch: Fehlalarmquote des Lints, Fingerabdruck-Rauschen.

## 6 Hooks

H1 bis H3 nach Kapitel 3.7: Frontmatter-Einbindung, Pfadauflösung prüfen, Zeitlimits messen, H3 als Angebot des Skillstarts. Hängt an: Schritt 4 und 5 sowie an der offenen Entscheidung, ob H3 gebaut wird (Kapitel 1.7.6); dieser Schritt und das Entscheidungstor der Probe (Kapitel 3.8.5) widersprechen sich darin bisher. Aufwand: 1 Sitzung. Fehleranfälligkeit mittel: Pfadauflösung aus dem Skill-Ordner im Hook-Kontext.

## 7 Skill zusammensetzen

Dünne `SKILL.md` aus Kapitel 3.10 (Lage, Skill-Parameter, Nachladen) plus Frontmatter (Name nach Q-32, Hook-Einträge nach Kapitel 3.7), `standard.md` aus dem bisherigen Text mit den Anpassungen aus Kapitel 1.11, Regelteile aus Schritt 1 bis 3, `rules-hardness.md` aus Kapitel 3.1, `CLAUDE-snippet.md` aus Kapitel 3.11, README in beiden Sprachen, Datumszeilen. Auflösung des Abschnitts „Zusammenspiel mit anderen Skills". Hängt an: Schritt 1 bis 6. Aufwand: 2 Sitzungen. Fehleranfälligkeit gering.

## 8 Probe

Fixture, Ablauf und Messung nach Kapitel 3.8; Entscheidung der Verzweigungen (Kostenfunktion, Fingerabdruck, H3, Zitatmarker außerhalb `relate`); zweiter Durchlauf an einer echten Doku empfohlen. Hängt an: Schritt 4 bis 7. Aufwand: 2 bis 3 Sitzungen. Fehleranfälligkeit mittel: Die Fixture ist nicht die Doku des Entwicklers.

## 9 Migration und Installation

Kapitel 3.9: Umzug aus der globalen Anweisungsdatei Passage für Passage, Bereinigung der Projekt-`CLAUDE.md`, Werkzeug-Skills, Baustellenschild, Installation, Verweise im Repository. Hängt an: Schritt 8 bestanden und an der offenen Frage, was von Kapitel 3.9 überhaupt zur Entwicklung gehört (Kopf des Kapitels). Aufwand: 2 bis 3 Sitzungen. Fehleranfälligkeit mittel: Der Umzug berührt globale Anweisungen.

## Summe

Voller Pfad 15 bis 22 Sitzungen. Minimaler Pfad — Schritt 5 auf den Lint beschränkt, H3 weggelassen, Probe eine Sitzung — 11 bis 14. Den Unterschied machen gewichtete Auswirkungsrechnung, Fingerabdruck und die zweite Probenrunde.
