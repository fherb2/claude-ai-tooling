# Fahrplan des Vorhabens `software-design-doc`

Die anstehenden Schritte. Erledigte Schritte fliegen raus; die Nummern der übrigen werden dabei nicht neu vergeben, neue Schritte zählen hoch. Die Reihenfolge der Schritte im Dokument ist maßgeblich, wo Abhängigkeiten bestehen; sie stehen bei jedem Schritt.

Dieser Fahrplan folgt dem bisherigen Schema (Kapitel 2.14 der Vorgaben). Sitzungsschätzungen sind grob; eine Sitzung ist ein zusammenhängender Arbeitsblock mit Freigaben. Vor Schritt 1 sind die Punkte unter „Klärungsbedarf" zu entscheiden oder bewusst offen zu lassen.

## Entscheidungsgrundlagen — Leseplan

Die offenen Punkte stehen als Blöcke `[Q-nn]` dort in der Doku, wo ihr Kontext steht: Kontext, Optionen, Vorschlag, Gewicht, blockierter Schritt und eine leere Zeile **Antwort:** für den Entwickler. Vorgehen: Der Entwickler geht die Dateien in Leseordnung durch, schreibt seine Antwort und weitere Gesichtspunkte unter **Antwort:** oder als neuen Block mit der nächsten freien Nummer; die Instanz liest die Antworten und führt die Restklärung im Gespräch. Ein geklärter Block wird durch den Entscheidungstext im Kapitel ersetzt und in `status.md` vermerkt; seine Nummer wird nicht neu vergeben.

| Q | Thema | Ort | Gewicht | Blockiert |
|---|---|---|---|---|
| Q-02 | Ereigniszeile `upheld` | `3_1_hardness.md`, Anfang | klein | 1 |
| Q-03 | Marker vor oder nach Satzzeichen | `3_2_register_marks.md`, 3.2.10 | klein | 1 |
| Q-04 | Fingerabdruck: ob und wie | 3.2.10 | mittel | 5 |
| Q-05 | Suchschlüssel | 3.2.10 | mittel | 1 |
| Q-06 | Zitatmarker außerhalb `relate` | 3.2.10 | klein | — |
| Q-07 | Rückfalloption Wortlaut-Anker | 3.2.10 | klein | 3 |
| Q-12 | Inhalt geplanter Schritte, Ablageorte (früher T2) | `3_4_planned_steps.md`, 3.4.4 | groß | 2 |
| Q-13 | Kapitelziel über Dateipfad | 3.4.4 | mittel | 2 |
| Q-14 | Kennungen für Schritte | 3.4.4 | klein | 2 |
| Q-15 | Wann bei fehlender Doku gefragt wird | `3_5_startup_parameters.md`, 3.5.5 | mittel | 3 |
| Q-16 | Standardwert von `mode` | 3.5.5 | mittel | 3 |
| Q-17 | `layout` als Skill-Parameter | 3.5.5 | klein | 3 |
| Q-18 | `impact_cutoff` ein oder zwei Felder | 3.5.5 | klein | 3 |
| Q-19 | Repositories mit mehreren Vorhaben | 3.5.5 | mittel | 3 |
| Q-20 | Graphenmodell (gesondert) | `3_6_script.md`, 3.6.9 | groß | 5 |
| Q-21 | Kostenfunktion | 3.6.9 | klein | 5 |
| Q-22 | Name `impact` | 3.6.9 | klein | 4 |
| Q-23 | Standardausgabe Zeilen oder JSON | 3.6.9 | klein | 4 |
| Q-24 | Dateiname des Skripts | 3.6.9 | klein | 4 |
| Q-26 | H2 blockiert oder meldet | `3_7_hooks.md`, 3.7.5 | mittel | 6 |
| Q-27 | H3 bauen oder zurückstellen | 3.7.5 | klein | 6 |
| Q-28 | Messgrößen und Schwellen der Probe | `3_8_probe.md`, vor 3.8.5 | mittel | 8 |
| Q-29 | Verbleib der Werkzeug-Skills | `3_9_migration.md`, 3.9.5 | mittel | 9 |
| Q-30 | Reihenfolge der Freigaben beim Umzug | 3.9.5 | klein | 9 |
| Q-31 | Trigger-Anker nach `mode: off` | 3.9.5 | klein | 9 |

Geklärte Blöcke werden aus dieser Tabelle entfernt und in `status.md` vermerkt; bisher sind es Q-01, Q-08 bis Q-11, Q-25 und Q-32. Vor Schritt 1 zu klären: Q-02, Q-03, Q-05. Vor Schritt 2: Q-12 bis Q-14. Vor Schritt 3: Q-07, Q-15 bis Q-19. Die übrigen blockieren spätere Schritte.

## 1 Regelteil Marker und Register

Kapitel 3.2 zum Regelteil `rules-register.md` ausformulieren: Grammatik, Markerformen, Registerort, Regel für Altes, Nachmarkierung, Robustheit. Ergebnis: Entwurf im Chat, danach Datei im Skill-Ordner. Hängt an: Q-02, Q-03, Q-05. Aufwand: 1 bis 2 Sitzungen. Fehleranfälligkeit gering; die Grammatik ist entschieden.

## 2 Regelteil Planung

Kapitel 3.4 zum Regelteil `rules-planning.md`: Umbauziel, Inhalt geplanter Schritte, Ablageorte, Wiedervorlage. Hängt an: Q-12 bis Q-14. Aufwand: 1 bis 2 Sitzungen. Fehleranfälligkeit mittel: Der frühere Punkt T2 war inhaltlich strittig.

## 3 Regelteil Skillstart

Kapitel 3.5 zum Regelteil `rules-startup.md`: Erhebung, Fragen, Skill-Parameterdatei, `mode: off`, „Doku wächst an Festlegungen". Hängt an: Schritt 1; Q-07, Q-15 bis Q-19. Aufwand: 1 bis 2 Sitzungen. Fehleranfälligkeit mittel: Zu viele Startfragen machen den Skill lästig.

## 4 Skript Stufe 1

`files/design-doc.py` mit `list`, `show`, `next-id`, `add`, `check`, `mentions`, `hardness`, `impact --hops`, `plan-section`, `explain`; Ausgabevertrag nach Kapitel 3.6; Prüffälle mit Fixture und beschädigten Varianten. Hängt an: Schritt 1 und 2 (für `target:`). Aufwand: 3 bis 4 Sitzungen. Fehleranfälligkeit hoch: Parsing-Ränder (U+00A0, Klammern in Prosa, umbrochenes Layout), Kapitelableitung bei verschobenen Markern. Vor dem ersten Code den Skill `common-code-generation` laden.

## 5 Skript Stufe 2

`lint` auf dem Diff, Fingerabdruck (`fp`, Abgleich in `check`), `supersede` und `retire`, `impact --weighted` mit den drei Kostenfunktionen in `impact.py`, networkx optional. Hängt an: Schritt 4; Q-04, Q-20, Q-21. Aufwand: 2 bis 3 Sitzungen. Fehleranfälligkeit hoch: Fehlalarmquote des Lints, Fingerabdruck-Rauschen.

## 6 Hooks

H1 bis H3 nach Kapitel 3.7: Frontmatter-Einbindung, Pfadauflösung prüfen, Zeitlimits messen, H3 als Angebot des Skillstarts. Hängt an: Schritt 4 und 5. Aufwand: 1 Sitzung. Fehleranfälligkeit mittel: Pfadauflösung aus dem Skill-Ordner im Hook-Kontext.

## 7 Skill zusammensetzen

Dünne `SKILL.md` (Lage, Skill-Parameter, Nachladen, Frontmatter-Hooks), `standard.md` aus dem bisherigen Text mit den Anpassungen aus Kapitel 1.11, Regelteile aus Schritt 1 bis 3, `rules-hardness.md` aus Kapitel 3.1, `CLAUDE-snippet.md` mit dem geankerten Trigger, README in beiden Sprachen, Datumszeilen. Auflösung des Abschnitts „Zusammenspiel mit anderen Skills". Hängt an: Schritt 1 bis 6. Aufwand: 2 Sitzungen. Fehleranfälligkeit gering.

## 8 Probe

Fixture, Ablauf und Messung nach Kapitel 3.8; Entscheidung der Verzweigungen (Kostenfunktion, Fingerabdruck, H3, Zitatmarker außerhalb `relate`); zweiter Durchlauf an einer echten Doku empfohlen. Hängt an: Schritt 4 bis 7; Q-28. Aufwand: 2 bis 3 Sitzungen. Fehleranfälligkeit mittel: Die Fixture ist nicht die Doku des Entwicklers.

## 9 Migration und Installation

Kapitel 3.9: Umzug aus der globalen Anweisungsdatei Passage für Passage, Bereinigung der Projekt-`CLAUDE.md`, Werkzeug-Skills, Baustellenschild, Installation, Verweise im Repository. Hängt an: Schritt 8 bestanden; Q-29 bis Q-31 (Q-32 geklärt, siehe status.md). Aufwand: 2 bis 3 Sitzungen. Fehleranfälligkeit mittel: Der Umzug berührt globale Anweisungen.

## Summe

Voller Pfad 15 bis 22 Sitzungen. Minimaler Pfad — Schritt 5 auf den Lint beschränkt, H3 weggelassen, Probe eine Sitzung — 11 bis 14. Den Unterschied machen gewichtete Auswirkungsrechnung, Fingerabdruck und die zweite Probenrunde.
