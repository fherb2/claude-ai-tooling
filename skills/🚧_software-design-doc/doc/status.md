# Status des Vorhabens `software-design-doc`

Ausschließlich abgearbeitete Fahrplaneinträge und geklärte Entscheidungsgrundlagen in der Reihenfolge des Abschlusses. Keine Entscheidungen im Wortlaut — die gehören sofort in das zuständige Kapitel; hier steht nur, dass und wann sie gefallen sind.

Noch kein Fahrplanschritt abgeschlossen. Die Doku wurde am 2026-09-17 angelegt; Arbeitspunkt 1 (Kapitel 3.1) ist am selben Tag final geworden.

## Geklärte Entscheidungsgrundlagen

Die Nummern werden nicht neu vergeben.

| Q | Thema | Geklärt am | Ergebnis steht in |
|---|---|---|---|
| Q-01 | Wortlaut der Vorgaben 2.5 bis 2.7 | 2026-09-19 | Kapitel 2.5 bis 2.7 — Wortlaut bestätigt und vom Entwickler um die Begründungen zum Ausgabevertrag und zum Bündeln von Skriptaufrufen erweitert |
| Q-32 | Name nach Abschluss der Regelteile prüfen | 2026-09-18 | Kapitel 1.1 und Fahrplanschritt 9 — beim Zusammensetzen wird geprüft, ob die softwarespezifischen Teile in einem eigenen Regelteil isoliert sind; wenn ja, Umbenennung in `solution-design-doc` vor der Installation |
| Q-08 | Umfang des Rollensatzes | 2026-09-20 | Kapitel 1.3.3 — alle zwölf arc42-Rollen plus fünf Rollen der Projektarbeit |
| Q-09 | Rolle `decisions` neben dem Register | 2026-09-20 | Kapitel 1.3.3 — Rolle bleibt; das Register hält Attribute, ein `decisions`-Abschnitt hält Begründungen kapitelübergreifender Entscheidungen in Prosa |
| Q-10 | Namen der Funktionen | 2026-09-20 | Kapitel 1.3.3 — `define`, `relate`, `global`, `nonbinding`, `plan`, `register` bleiben |
| Q-11 | Position des Rollenmarkers | 2026-09-20 | Kapitel 3.3.1 — am Ende der Überschrift |
| Q-25 | networkx optional oder Voraussetzung | 2026-09-20 | gegenstandslos — mit dem Skill-Parameter `impact_lib` bereits entschieden: optional, nie Voraussetzung, bewusste Wahl des Entwicklers; Ergebnis in Kapitel 1.7.4 und 3.6.1 |
