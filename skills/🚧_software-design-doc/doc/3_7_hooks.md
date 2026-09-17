## 3.7 Hooks

Stand (2026-09-17): Die drei Hooks sind spezifiziert; die Hook-Dokumentation von Claude Code wurde am selben Tag gegen die hier genutzten Ereignisse, Matcher, Filter, Exit-Codes und JSON-Felder geprüft. Einzelheiten der Pfadauflösung sind offen und am Ende benannt.

### 3.7.1 Zweck

Hooks ersetzen die Erinnerung der Instanz, nicht der Regeltext. Das Repository hat den Nachweis erbracht: Der Hook des Skills `git-branch-model` schloss eine Lücke, die keine Anweisung schloss. Alle drei Hooks sind nur lesend (Vorgabe 2.8); sie prüfen, melden und — genau einer — blockieren. Was sie nicht leisten, ist das Urteil, ob ein Satz eine Festlegung ist; sie erzwingen, dass das Urteil gefällt und aufgeschrieben wird.

### 3.7.2 Die drei Hooks

| | H1 — Lint nach Doku-Edit | H2 — Abgleich vor Commit | H3 — Zustand am Sitzungsstart |
|---|---|---|---|
| Ereignis | `PostToolUse` | `PreToolUse` | `SessionStart` |
| Matcher | `Edit\|Write\|MultiEdit` | `Bash` | `startup\|resume\|compact` |
| Filter | Pfad der Datei liegt im Doku-Ordner (über `if: Edit(<doc_dir>/*)` oder im Skript aus `tool_input.file_path`) | `if: Bash(git commit*)` | — |
| Eingabe | Hook-JSON mit `tool_input.file_path` und `cwd` | Hook-JSON mit `cwd` | Hook-JSON mit `cwd` |
| Kommando | `design-doc.py lint --file <pfad> --changed --json` | `design-doc.py check --json` | `design-doc.py check --summary` |
| Ausgabe | Exit 0; JSON mit `additionalContext`: die Befunde — nicht blockierend | Exit 2 mit Begründung auf stderr bei struktureller Inkonsistenz → blockiert den Commit; sonst Exit 0, Befunde als `additionalContext` | Exit 0; Klartext auf stdout wird Kontext: Zahl Festlegungen, `assumed`, `pending`, unlesbare Zeilen, seit dem letzten Lauf geänderte Definitionssätze |
| Zeitlimit | 20 s | 30 s | 10 s |
| Kosten | ein Skriptlauf je Doku-Edit, Ausgabe wenige Zeilen | ein Lauf je Commit | ein Lauf je Start; fängt menschliche Bearbeitungen zwischen Sitzungen und überlebt die Kompaktierung (Matcher `compact`) |
| Bei `FAILED` des Skripts | Exit 1: nicht blockierend, Meldung als Kontext | Exit 1: nicht blockierend, der Commit läuft; nur Exit 2 blockiert | nicht blockierend |
| Ort | Skill-Frontmatter | Skill-Frontmatter | Projekt-`settings.json` |

Belegt in der Hook-Dokumentation: `PostToolUse` erhält `tool_input` und `tool_output` und honoriert `additionalContext`; `PreToolUse` blockiert bei Exit 2 mit der Begründung aus stderr oder aus `permissionDecisionReason`; `SessionStart` fügt Klartext auf stdout dem Kontext hinzu und kennt die Matcher `startup`, `resume`, `clear`, `compact`, `fork`; das Feld `if` filtert Werkzeugaufrufe in der Syntax der Berechtigungsregeln (`Bash(git *)`, `Edit(*.md)`); Hooks im Frontmatter eines Skills registrieren sich beim Aufruf und gelten für den Rest der Sitzung.

### 3.7.3 Warum H1 und H2 im Skill wohnen und H3 im Projekt

H1 und H2 sind nur sinnvoll, wenn der Skill geladen ist, und sie sollen in jedem Projekt gelten, das ihn führt — ohne Installation je Projekt. Beides leistet das Skill-Frontmatter. H3 muss beim Sitzungsstart laufen, bevor irgendein Skill geladen ist; er kann deshalb nur aus der Projektkonfiguration kommen. Der Skillstart bietet an, ihn einzutragen; er ist optional, weil er nur Projekte betrifft, in denen der Mensch die Doku zwischen Sitzungen bearbeitet.

### 3.7.4 Technisch offen (keine Entscheidung des Entwicklers)

Pfadauflösung: ob `${CLAUDE_SKILL_DIR}` im Kommando eines Frontmatter-Hooks aufgelöst wird oder der Pfad anders zu ermitteln ist; die Doku nennt für Hooks `${CLAUDE_PROJECT_DIR}` und `${CLAUDE_PLUGIN_ROOT}`. Pfadfilter: ob `Edit(<doc_dir>/*)` den Doku-Ordner trifft oder der Filter ins Skript wandert. Zeitlimits nach den ersten Messungen.

### 3.7.5 Entscheidungsgrundlagen

> **[Q-26] Entscheidungsgrundlage — H2 blockiert den Commit oder meldet nur**
> Kontext: H2 blockiert bei struktureller Inkonsistenz (Dublette, Marke ohne Eintrag, `superseded` ohne Ziel). Das ist der einzige blockierende Eingriff des Skills. Eine Blockade ist wirksam, aber im falschen Moment lästig; ohne sie bleibt die Inkonsistenz im Repository.
> Optionen: (a) blockieren bei struktureller Inkonsistenz, melden bei allem anderen; (b) nur melden, nie blockieren; (c) blockieren, aber per Wort des Entwicklers für einen Commit aufhebbar.
> Vorschlag: (a) — (c) ist ohnehin gegeben, weil der Entwickler den Hook im Projekt abschalten kann.
> Gewicht: mittel · Blockiert: Fahrplanschritt 6
> Antwort:

> **[Q-27] Entscheidungsgrundlage — H3 bauen oder bis zur Probe zurückstellen**
> Kontext: H3 (Sitzungsstart) fängt menschliche Bearbeitungen zwischen Sitzungen und überlebt die Kompaktierung. Er ist der einzige Hook, der eine Projektkonfiguration braucht. Ob menschliche Bearbeitungen zwischen Sitzungen vorkommen, weißt Du aus Deiner Praxis.
> Optionen: (a) bauen und am Skillstart anbieten; (b) zurückstellen, bis die Probe zeigt, dass er fehlt; (c) ersetzen durch die Regel „beim Öffnen eines Bereichs läuft `check`" ohne Hook.
> Vorschlag: (a) — die Kosten sind eine Zeile Konfiguration, und der Kompaktierungsfall allein rechtfertigt ihn.
> Gewicht: klein · Blockiert: Fahrplanschritt 6
> Antwort:
