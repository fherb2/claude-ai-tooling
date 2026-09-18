## 3.9 Migration und Installation

Stand (2026-09-17): Vorschlag; jede Passage der Anweisungsdateien wird beim Umzug einzeln freigegeben.

### 3.9.1 Umzug aus der globalen Anweisungsdatei (früher T1)

Abschnitt 2 der globalen `~/.claude/CLAUDE.md` (2.1 Phasen bis 2.6 Fahrplan und Status) ist der Sache nach dieser Skill; sein Inhalt ist der des Vorläufers (Anhang A). Er wandert in den Regelteil `standard.md`, angepasst nach Kapitel 1.9: Segmente als empfohlene Rollen, Phasen je Bereich, Planungsort nach Kapitel 3.4. In der Anweisungsdatei bleiben der geankerte Trigger aus `CLAUDE-snippet.md` und die Abgrenzung der Präambel, wann der Abschnitt überhaupt gilt. Anzupassen ist außerdem 1.9 Kontext-Haushalt: „Detaillierung des Fahrplans vor der Komprimierung" wird zu „Planung an ihrem Ort vertiefen und im Schritt darauf verweisen".

Die Doppelungen in der Projekt-`CLAUDE.md` dieses Repositories — „Wo ein Plan steht", „Fahrplan-Nummerierung", „`work-plan.md`, `status.md` und die Implementierungsdoku sind entwicklungszeitlich" — werden auf das reduziert, was repositoryspezifisch ist. Für jede Fundstelle gilt danach die Probe: Sie nennt den Fahrplan, oder sie beschreibt ihn — beides zugleich darf keine mehr.

### 3.9.2 Die Werkzeug-Skills (Fahrplanschritt 5 des Repositories)

`konzept-segmentierung` und `konsistenzpruefung` dürfen den Fahrplan weiter benutzen, aber nicht mehr definieren; ihre Sätze werden daraufhin durchgesehen, und wo sie eine Eigenschaft des Fahrplans behaupten, wird daraus ein Verweis. Ob beide in dieses Vorhaben überführt und dem Namensschema angeglichen werden, entscheidet der Entwickler; der Abschnitt „Zusammenspiel mit anderen Skills" der bisherigen `SKILL.md` verstößt gegen die Vorgabe, dass kein Skill-Körper auf einen anderen Skill dieses Verzeichnisses verweist, und wird beim Zusammensetzen (Fahrplan, Paket 7) aufgelöst.

### 3.9.3 Aufgelöste Arbeitsdatei (früher T3)

Die Datei `noch-geplant.md` des Skills ist am 2026-09-17 in diese Doku übergegangen: ihre Befunde in Kapitel 1.2, T1 in 3.9.1, T2 in 3.4.3, T3 hier; der Git-LFS-Hinweis aus ihrem Kopf gehört nicht zu diesem Vorhaben und steht bereits als Regel 1 der globalen Anweisungsdatei. Die Datei wurde gelöscht.

### 3.9.4 Installation

1. Baustellenschild vom Ordnernamen entfernen: `skills/software-design-doc/`.
2. Ordner nach `~/.claude/skills/software-design-doc/` kopieren; das Frontmatter der `SKILL.md` trägt H1 und H2.
3. Inhalt der `CLAUDE-snippet.md` unterhalb der Trennlinie in die `CLAUDE.md` des Zielorts übernehmen; die Snippet-Datei bleibt am Zielort liegen.
4. Je Projekt: Skill-Parameterdatei anlegen lassen, wenn gewünscht; H3 anbieten.
5. Verweise im Repository nachziehen: Zeile in `skills/README.md` und `skills/README.en.md`, Fahrplanschritte 5 und 6 des Repositories, `skill-dev-doc.md`, wo der alte Name steht.

### 3.9.5 Entscheidungsgrundlagen

> **[Q-29] Entscheidungsgrundlage — Verbleib der Werkzeug-Skills**
> Kontext: `konzept-segmentierung` und `konsistenzpruefung` sind Werkzeuge innerhalb dieses Standards, liegen nur unter `~/.claude/skills/` und definieren heute Eigenschaften des Fahrplans mit. Der Fahrplanschritt 5 des Repositories stellt die Frage seit August.
> Optionen: (a) in `skills/` dieses Repositories überführen, umbenennen nach dem Namensschema, Fahrplansätze zu Verweisen machen; (b) draußen lassen, nur die Fahrplansätze anpassen; (c) in diesen Skill als nachgeladene Regelteile aufnehmen.
> Vorschlag: (a) — sie gehören zum Produkt und sollten mit ihm versioniert sein; (c) macht diesen Skill schwer.
> Gewicht: mittel · Blockiert: Fahrplanschritt 9
> Antwort:

> **[Q-30] Entscheidungsgrundlage — Reihenfolge der Freigaben beim Umzug**
> Kontext: Abschnitt 2 der globalen Anweisungsdatei umfasst sechs Unterabschnitte; jeder Umzug einer Passage ist eine Änderung an Deinen globalen Anweisungen.
> Optionen: (a) Passage für Passage, je eine Freigabe; (b) Abschnitt 2 als Ganzes in einem Zug, mit vorheriger Gegenüberstellung alt/neu; (c) erst `standard.md` fertigstellen, dann den Abschnitt in einem Zug ersetzen.
> Vorschlag: (c) — die Gegenüberstellung ist dann vollständig, und die globale Datei ist nie in einem Zwischenzustand.
> Gewicht: klein · Blockiert: Fahrplanschritt 9
> Antwort:

> **[Q-31] Entscheidungsgrundlage — Trigger-Anker nach Einführung von `mode: off`**
> Kontext: Der Trigger „bevor du zum ersten Mal einen Lösungsweg vorschlägst oder eine Datei änderst … über eine lokale Korrektur hinaus" lädt den Skill in jedem Projekt. Mit `mode: off` endet er sofort wieder; das kostet einen Ladevorgang je Sitzung in Projekten, die ihn nicht wollen.
> Optionen: (a) Anker unverändert lassen, `mode: off` erledigt den Rest; (b) den Anker in der `CLAUDE.md` des Projekts entfernen, wenn `mode: off` gesetzt wird; (c) Anker nur in die globale Datei, Abwahl über die Projekt-`CLAUDE.md`.
> Vorschlag: (a) — ein Ladevorgang mit sofortigem Ende ist billiger als zwei Stellen, die zusammenpassen müssen.
> Gewicht: klein · Blockiert: Fahrplanschritt 9
> Antwort:
