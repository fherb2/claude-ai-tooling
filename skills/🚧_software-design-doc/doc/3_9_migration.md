## 3.9 Migration und Installation

Stand (2026-09-25): Vorschlag; jede Passage der Anweisungsdateien wird beim Umzug einzeln freigegeben.

**Zum Zuschnitt dieses Kapitels steht eine Frage offen.** Am 2026-09-25 wurden zwei Entscheidungsgrundlagen hier gestrichen, weil sie nicht zur Entwicklung des Skills gehören: die Reihenfolge der Freigaben beim Umzug (vormals Q-30) — das Anpassen der eigenen Installation ist Sache des Entwicklers und kein Bestandteil des Produkts —, und der künftige Ort der beiden Werkzeug-Skills (vormals Q-29), der die Organisation des Repositories betrifft und in dessen eigenen Fahrplan gehört. Damit stellt sich dieselbe Frage für das Kapitel als Ganzes: Was hier steht, hat keine Quelle in Kapitel 1 und beschreibt überwiegend Handlungen am System des Entwicklers statt einer Einheit des Skills. Zur Entwicklung gehört unbestritten, dass der Inhalt von Abschnitt 2 der globalen Anweisungsdatei die Quelle des Regelteils `standard` ist (Fahrplanschritt 7); der Rest — insbesondere die Gegenüberstellung unten, welche Anweisungen entfallen und welche bleiben — ist getane Arbeit, die eher in einen Anhang gehört. Entschieden ist das nicht, und es hat bis Fahrplanschritt 9 Zeit.

### 3.9.1 Umzug aus der globalen Anweisungsdatei (früher T1)

Abschnitt 2 der globalen `~/.claude/CLAUDE.md` (2.1 Phasen bis 2.6 Fahrplan und Status) ist der Sache nach dieser Skill; sein Inhalt ist der des Vorläufers (Anhang A). Er wandert in den Regelteil `standard.md`, angepasst nach Kapitel 1.11: Segmente als empfohlene Rollen, Phasen je Bereich, Planungsort nach Kapitel 3.4. In der Anweisungsdatei bleiben der geankerte Trigger aus `CLAUDE-snippet.md` und die Abgrenzung der Präambel, wann der Abschnitt überhaupt gilt. Anzupassen ist außerdem 1.9 Kontext-Haushalt: „Detaillierung des Fahrplans vor der Komprimierung" wird zu „Planung an ihrem Ort vertiefen und im Schritt darauf verweisen".

Die Doppelungen in der Projekt-`CLAUDE.md` dieses Repositories — „Wo ein Plan steht", „Fahrplan-Nummerierung", „`work-plan.md`, `status.md` und die Implementierungsdoku sind entwicklungszeitlich" — werden auf das reduziert, was repositoryspezifisch ist. Für jede Fundstelle gilt danach die Probe: Sie nennt den Fahrplan, oder sie beschreibt ihn — beides zugleich darf keine mehr.

**Was der Skill ersetzt und was bleibt.** Geprüft am 2026-09-19 gegen den Wortlaut beider Anweisungsdateien. Der Skill wird nicht gegen die bisherigen Regeln getestet; geprüft wird, welche von ihnen mit seinem Einbau entfallen können.

| Fundstelle | Was mit ihr geschieht |
|---|---|
| global, Abschnitt „Planung" (Ablageort erfragen: Chat, File im Projekt, `~/.claude`) | **bleibt unverändert.** Sie trägt den Vorbehalt „und der Ablageort der Planung nicht klar geregelt ist" und schaltet sich damit selbst ab, sobald der Skill ihn regelt. Für Vorhaben ohne Quellcode bleibt sie nötig. |
| global §1.3 Plan vor Ausführung, §1.4 Abweichung heißt anhalten, §1.5 Rückfragen | **bleiben.** Sie regeln, *ob* und *wie vollständig* geplant wird, nicht *wo*. |
| global §1.9 Kontext-Haushalt | **muss geändert werden**, nicht nur entfallen: „Detaillierung des Fahrplans" widerspricht dem Skill unmittelbar. |
| global §2.1 bis §2.6 | **entfallen** vollständig; ihr Inhalt wird zum Regelteil `standard.md`. |
| Projekt, „Wo ein Plan steht" (zwei Orte, keine eigenen Plan-Dateien) | **entfällt.** Der Skill kennt mehr Ablageorte; die Regel wäre danach falsch. |
| Projekt, „Fahrplan-Nummerierung" | **entfällt** als Doppelung; der Skill sagt dasselbe (Kapitel 3.4.1). |
| Projekt, „entwicklungszeitliche Dateien" | überwiegend **Doppelung** zu „Doku wächst an Festlegungen"; der repositoryspezifische Rest bleibt. |
| Projekt, „Pläne aus dem Planmodus" (`~/.claude/plans/`) | **bleibt.** Anderer Gegenstand: der Planmodus von Claude Code. |
| Projekt, Dateiname `work-plan.md` statt `fahrplan.md` | **bleibt.** Repositoryspezifische Festlegung. |

Ein früher notiertes §1.7 („Der Commit-Body benennt den Fahrplanpunkt") existiert nicht mehr; Abschnitt 1 der globalen Datei springt von 1.6 auf 1.8.

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
