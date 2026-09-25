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
| Q-11 | Position des Rollenmarkers | 2026-09-20 | Kapitel 3.3.1 — am Ende der Überschrift; am 2026-09-21 auf Vorschlag des Entwicklers erweitert: ein Rollenwechsel ist auch am Ende eines Absatzes möglich (Kapitel 1.3.3). Ebenfalls am 2026-09-21 bestätigt: die Grenze nach unten — feiner als der Absatz wird nicht gewechselt, ein Definitionsmarker am Satz geht der Rolle vor |
| Q-03 | Platzierung des Markers im Satz | 2026-09-21 | Kapitel 3.2.2 — vor dem Satzzeichen |
| Q-07 | Rückfalloption ohne Marker (Wortlaut-Anker) | 2026-09-21 | Kapitel 1.3.3 und 3.2.9 — zurückgestellt, im Regeltext als Möglichkeit genannt. Vom Entwickler ergänzt: Der Markereinbau wird immer mit Begründung vorgeschlagen, der Entwickler kann ihn abwählen; was eine Abwahl bedeutet, steht in 1.3.3 |
| Q-25 | networkx optional oder Voraussetzung | 2026-09-20 | gegenstandslos — mit dem Skill-Parameter `impact_lib` bereits entschieden: optional, nie Voraussetzung, bewusste Wahl des Entwicklers; Ergebnis in Kapitel 1.7.4 und 3.6.1 |
| Q-15 | Wann bei fehlender Doku gefragt wird | 2026-09-24 | Kapitel 1.7 und 3.5.3 — (a): erst fragen, wenn im Plan eine Festlegung entsteht, die den Code überdauert |
| Q-19 | Repositories mit mehreren Vorhaben | 2026-09-24 | Kapitel 3.5.4 — (a): keine zweite Skill-Parameterdatei je Vorhaben, die `[register: pfad]`-Zeile im Dokument reicht |
| Q-02 | Umbenennung der Ereigniszeile in `upheld` | 2026-09-24 | Kapitel 3.1.1 — (a): `upheld` bestätigt |
| Q-26 | H2 blockiert den Commit oder meldet nur | 2026-09-24 | Kapitel 1.3.5 und 3.7 — (a) mit (c), vom Entwickler kombiniert: H2 blockiert bei struktureller Inkonsistenz, der Entwickler kann das für einen einzelnen Commit ausdrücklich aufheben statt den Hook ganz abzuschalten; wie er das Wort dafür ausspricht, ist als technische Einzelheit in 3.7.4 offen |
| Q-05 | Suchschlüssel | 2026-09-24 | Kapitel 1.7.4 — (a): die Instanz wählt sie beim Anlegen, sichtbar im Planabschnitt; Pflege nur bei Reibung oder verfehlten Erwähnungen |
| Q-31 | Trigger-Anker nach `mode: off` | 2026-09-24 | Kapitel 1.7.7 — (a): Anker bleibt unverändert |
| Q-04 | Fingerabdruck: ob und wie | 2026-09-24 | Kapitel 1.7.6 und 3.6.7 — (a), vom Entwickler ergänzt: vor der Meldung prüft das Skript mechanisch die Edit-Distanz; unterhalb einer noch offenen Schwelle nur stille Neuberechnung statt Meldung |
| Q-16 | Standardwert von `mode` | 2026-09-24 | Kapitel 1.7.7 und 3.10.2/3.5.2 — (b): einmal je Sitzung fragen (wie `git-workbench`), Standard in der Tabelle jetzt „erfragt"; vom Entwickler ergänzt: bei Ablehnung zusätzlich fragen, ob `mode: off` festgehalten werden soll |
| Q-12 | Inhalt geplanter Schritte, Ablageorte einer Planung | 2026-09-24 | Kapitel 1.7.3 und 3.4.3 — alle vier Punkte übernommen, nach Rückfrage des Entwicklers selbständig verständlich neu formuliert |
| Q-06 | Zitatmarker außerhalb der Funktion `relate` | 2026-09-24 | Kapitel 1.7.4 — (a): optional, die Probe entscheidet |
| Q-20 | Das Graphenmodell | 2026-09-24 | Kapitel 1.7.4 und 3.6.5 — mechanische Nähe (Absatz/Abschnitt/Nachbarabschnitt/Kapitel); „hängt inhaltlich zusammen" bleibt der Instanz vorbehalten, nachgelagert je Kandidat der Vorauswahl, nicht als eigene Berechnung im Graphen |
| Q-28 | Messgrößen und Schwellen der Probe | 2026-09-24 | Kapitel 1.9 und 3.8.4 — Tabelle übernommen wie vorgeschlagen |
| Q-22 | Name `impact` | 2026-09-25 | Kapitel 3.6 — (a): `impact` folgt der durchgehenden Begriffswahl „Auswirkung" in Kapitel 1.7.4; `neighborhood` und `reach` benennen den Graphen statt der Aufgabe |
| Q-14 | Kennungen für geplante Schritte | 2026-09-25 | Kapitel 3.4.1 — (a): keine eigenen Kennungen; Nummer und Datei im Freitext genügen, weil die Nummer stabil ist und erledigte Schritte über die Statusdatei auffindbar bleiben |
| Q-24 | Dateiname des Skripts | 2026-09-25 | Kapitel 3.6.1 — (b), vom Entwickler gewählt: `software-design-doc.py`, also der Name des Skills; folgt aus Q-32 eine Umbenennung, wandert der Skriptname mit |
| Q-17 | `layout` als Skill-Parameter | 2026-09-25 | Kapitel 1.4 und 3.5.2 — (b), vom Entwickler entschieden: kein Skill-Parameter. Die Unterscheidung ist am Text eindeutig, denn halbe Sätze sind kein Absatz; nur bei fehlender Doku oder echter Uneindeutigkeit wird einmal gefragt |

## Umgestellt: keine Entscheidungsblöcke in Segment 3

Am 2026-09-25 hat der Entwickler festgestellt, dass Segment 3 die Umsetzungsbeschreibung trägt und dort eigentlich keine Fragen mehr auftauchen dürfen: Eine Frage bedeutet, dass etwas Funktionales oder eine Vorgabe noch nicht entschieden ist. Die `[Q-nn]`-Blöcke wurden daraufhin aufgelöst. Die verbliebenen Punkte stehen jetzt an der Stelle, an der die Entscheidung hingehört, und sind dort so in den Text eingearbeitet, dass sich die Frage aus dem Gedankengang selbst ergibt — das Bereichsziel eines geplanten Schritts in Kapitel 1.7.3 und Vorgabe 2.3 (vormals Q-13), der Zustandsbericht am Sitzungsstart in Kapitel 1.7.6 (vormals Q-27), die Ausgabeform in Vorgabe 2.5 (vormals Q-23). Zwei Punkte waren keine Entscheidungen des Entwicklers, sondern technische Wahlen bei der Umsetzung und stehen als solche im laufenden Text (vormals Q-18 und Q-21). Zwei weitere wurden gestrichen, weil sie nicht zur Entwicklung des Skills gehören: die Reihenfolge der Freigaben beim Umzug, der die Installation des Entwicklers betrifft (vormals Q-30), und der künftige Ort der beiden Werkzeug-Skills, der zur Organisation des Repositories gehört (vormals Q-29). Der Zuschnitt von Kapitel 3.9 ist dadurch selbst zur offenen Frage geworden.

Im selben Zug wurde der Prüfvermerk des Entwicklers in Kapitel 1.7.4 aufgelöst: Die Bibliothek heißt `networkx` und wird jetzt dort beim Namen genannt, wo der Entwickler über ihre Installation entscheiden soll.
