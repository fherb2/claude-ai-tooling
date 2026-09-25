## 3.7 Hooks

Stand (2026-09-25): Die drei Hooks sind spezifiziert; die Hook-Dokumentation von Claude Code wurde am 2026-09-17 gegen die hier genutzten Ereignisse, Matcher, Filter, Exit-Codes und JSON-Felder geprüft. Einzelheiten der Pfadauflösung sind offen und am Ende benannt.

**Ob H3 überhaupt gebaut wird, ist hier nicht zu entscheiden** (seit 2026-09-25, vormals Q-27). Er ist der einzige Hook, der je Projekt eingerichtet werden muss, und damit eine Ausnahme von einer Zusage, die Kapitel 1.3.5 gibt; die Entscheidungsgrundlage steht deshalb bei der Leistung, die er erbringt (Kapitel 1.7.6). Solange sie aussteht, beschreibt dieses Kapitel ihn vollständig, ohne seinen Bestand zu behaupten — und der Fahrplan enthält an zwei Stellen Widersprüchliches: Schritt 6 baut ihn, das Entscheidungstor der Probe führt ihn unter dem, was erst danach entschieden wird (Kapitel 3.8.5). Das wird mit der Antwort aufgelöst, nicht vorher.

### 3.7.1 Gegenstand

**Warum die Einhaltung an Hooks hängt und nicht am Regeltext, steht in Kapitel 1.3.5.** Hier steht, welche drei es gibt und wie sie gebaut sind. Zwei Eigenschaften gelten für alle: Sie sind nur lesend (Vorgabe 2.8) — sie prüfen, melden, und genau einer blockiert. Und sie fällen kein Urteil darüber, ob ein Satz eine Festlegung ist; sie erzwingen nur, dass das Urteil gefällt und aufgeschrieben wird.

Der Nachweis, dass ein Hook trägt, wo eine Anweisung nicht trägt, liegt in diesem Repository vor: Der Hook des Skills `git-branch-model` schloss eine Lücke, die keine Formulierung schloss.

### 3.7.2 Die drei Hooks

| | H1 — Lint nach Doku-Edit | H2 — Abgleich vor Commit | H3 — Zustand am Sitzungsstart |
|---|---|---|---|
| Ereignis | `PostToolUse` | `PreToolUse` | `SessionStart` |
| Matcher | `Edit\|Write\|MultiEdit` | `Bash` | `startup\|resume\|compact` |
| Filter | Pfad der Datei liegt im Doku-Ordner (über `if: Edit(<doc_dir>/*)` oder im Skript aus `tool_input.file_path`) | `if: Bash(git commit*)` | — |
| Eingabe | Hook-JSON mit `tool_input.file_path` und `cwd` | Hook-JSON mit `cwd` | Hook-JSON mit `cwd` |
| Kommando | `software-design-doc.py lint --file <pfad> --changed --json` | `software-design-doc.py check --json` | `software-design-doc.py check --summary` |
| Ausgabe | Exit 0; JSON mit `additionalContext`: die Befunde — nicht blockierend | Exit 2 mit Begründung auf stderr bei struktureller Inkonsistenz → blockiert den Commit, es sei denn, der Entwickler hat die Blockade für diesen einen Commit ausdrücklich aufgehoben (entschieden am 2026-09-24, vormals Q-26); sonst Exit 0, Befunde als `additionalContext` | Exit 0; Klartext auf stdout wird Kontext: Zahl Festlegungen, `assumed`, `pending`, unlesbare Zeilen, seit dem letzten Lauf geänderte Definitionssätze |
| Zeitlimit | 20 s | 30 s | 10 s |
| Kosten | ein Skriptlauf je Doku-Edit, Ausgabe wenige Zeilen | ein Lauf je Commit | ein Lauf je Start; fängt menschliche Bearbeitungen zwischen Sitzungen und überlebt die Kompaktierung (Matcher `compact`) |
| Bei `FAILED` des Skripts | Exit 1: nicht blockierend, Meldung als Kontext | Exit 1: nicht blockierend, der Commit läuft; nur Exit 2 blockiert | nicht blockierend |
| Ort | Skill-Frontmatter | Skill-Frontmatter | Projekt-`settings.json` |

Belegt in der Hook-Dokumentation: `PostToolUse` erhält `tool_input` und `tool_output` und honoriert `additionalContext`; `PreToolUse` blockiert bei Exit 2 mit der Begründung aus stderr oder aus `permissionDecisionReason`; `SessionStart` fügt Klartext auf stdout dem Kontext hinzu und kennt die Matcher `startup`, `resume`, `clear`, `compact`, `fork`; das Feld `if` filtert Werkzeugaufrufe in der Syntax der Berechtigungsregeln (`Bash(git *)`, `Edit(*.md)`); Hooks im Frontmatter eines Skills registrieren sich beim Aufruf und gelten für den Rest der Sitzung.

### 3.7.3 Warum H1 und H2 im Skill wohnen und H3 im Projekt

H1 und H2 sind nur sinnvoll, wenn der Skill geladen ist, und sie sollen in jedem Projekt gelten, das ihn führt — ohne Installation je Projekt. Beides leistet das Skill-Frontmatter. H3 muss beim Sitzungsstart laufen, bevor irgendein Skill geladen ist; er kann deshalb nur aus der Projektkonfiguration kommen. Der Skillstart bietet an, ihn einzutragen; er ist optional, weil er nur Projekte betrifft, in denen der Mensch die Doku zwischen Sitzungen bearbeitet.

### 3.7.4 Technisch offen (keine Entscheidung des Entwicklers)

Pfadauflösung: ob `${CLAUDE_SKILL_DIR}` im Kommando eines Frontmatter-Hooks aufgelöst wird oder der Pfad anders zu ermitteln ist; die Doku nennt für Hooks `${CLAUDE_PROJECT_DIR}` und `${CLAUDE_PLUGIN_ROOT}`. Pfadfilter: ob `Edit(<doc_dir>/*)` den Doku-Ordner trifft oder der Filter ins Skript wandert. Zeitlimits nach den ersten Messungen. Aufhebung der H2-Blockade (Kapitel 1.3.5, entschieden am 2026-09-24): wie der Entwickler das Wort dafür je Commit ausspricht — Script-Argument, Umgebungsvariable oder eine Zeile in der Commit-Message.
