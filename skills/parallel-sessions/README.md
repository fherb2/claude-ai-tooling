# parallel-sessions — Zusammenarbeit mehrerer Claude-Instanzen in einem Repository

**✅ Fertig und nutzbar.** Anweisungen vollständig, Frontmatter gesetzt, stiller Trigger vorhanden und gemessen.

**Klärt die Zusammenarbeit, wenn mehrere Claude-Code-Instanzen gleichzeitig im selben Repository arbeiten.** Zwei gleichzeitig laufende Instanzen teilen sich einen einzigen Arbeitsbaum und einen einzigen ausgecheckten Branch: Was die eine committet, nimmt ungefragt mit, was die andere gerade geändert hat. Das Tückische daran ist nicht der Konflikt — den würde Git melden —, sondern das lautlose Mitwandern.

Der Skill geht deshalb in zwei Schritten vor, in fester Reihenfolge. Erst wird geklärt, **welche Instanz eigenständig schreibende Git-Kommandos ausführen darf**; bis zur Antwort führt die fragende Instanz keines davon aus. Danach wird das **Worktree-Modell** als saubere Trennung angeboten — kurz und ohne Drängen, denn es ist eine Änderung der Arbeitsweise, keine technische Notwendigkeit.

## Installation

1. **Zielort wählen.** Der Skill gilt entweder für alle Projekte des Nutzers oder nur für eines:

   | Ort         | Pfad                                    | Gilt für                  |
   | ----------- | --------------------------------------- | ------------------------- |
   | Persönlich  | `~/.claude/skills/parallel-sessions/`   | alle Projekte des Nutzers |
   | Projekt     | `.claude/skills/parallel-sessions/`     | nur dieses Projekt        |

2. **Ordner `parallel-sessions/` unter seinem unveränderten Namen kopieren.** Er enthält `SKILL.md`, `CLAUDE-snippet.md` und diese `README.md`. Ein Sprachkürzel trägt bisher keine der Dateien, weil es nur die deutsche Fassung gibt; die `SKILL.md` heißt also schon so, wie Claude Code sie erwartet.

3. **Stillen Trigger übernehmen.** Der Inhalt der `CLAUDE-snippet.md` **unterhalb der Trennlinie** kommt in die `CLAUDE.md` des Zielorts, danach wird die Snippet-Datei dort gelöscht. Ohne diesen Schritt bemerkt der Skill die Situation nicht: Niemand sagt von sich aus „hier arbeitet gerade eine zweite Instanz".

## Details

**Schritt 1 im Einzelnen.** Gefragt wird nach der Hoheit über `commit`, `add`, `push`, `checkout`, `restore`, `reset` und `merge`; lesende Kommandos wie `status`, `diff`, `log` und `fetch` bleiben durchgehend erlaubt. Der Nutzer muss das **jeder** Instanz einzeln sagen — eine Instanz kann nicht wissen, was er einer anderen mitgeteilt hat. Ist die Hoheit einmal erteilt, wird nicht bei jedem Commit erneut gefragt.

**Schritt 2 im Einzelnen.** Ein Worktree ist ein zweiter Arbeitsbaum desselben Repositorys in einem eigenen Verzeichnis, mit eigenem ausgechecktem Branch, aber gemeinsamer Historie. Derselbe Branch lässt sich nie in zwei Worktrees gleichzeitig auschecken — das erzwingt Git von sich aus und ist genau die gewünschte Trennung. Der Skill erklärt beide Einrichtungswege und ihren Unterschied:

- **`EnterWorktree`** legt den Worktree unter `.claude/worktrees/` an und erzeugt dabei **immer einen neuen Branch**, nie den bereits ausgecheckten. Basis ist standardmäßig `origin/<default-branch>`; die Einstellung `worktree.baseRef` mit dem Wert `head` zweigt stattdessen vom aktuellen lokalen HEAD ab.
- **`git worktree add <pfad> -b <branch> <basis>`** von Hand ist der flexiblere Weg, weil Ort und Basis frei bestimmt werden.

(Beobachtung an der Werkzeugbeschreibung von `EnterWorktree`, 14. August 2026.)

**Trigger gemessen** (14. August 2026, nicht-interaktiv): Mit der jetzigen Description feuert er auf Sonnet im ersten Turn — sowohl in dieser Fassung als auch in einer reinen Überwachungsfassung ohne Anker, geprüft mit sechszeiliger und mit vollständiger realer `CLAUDE.md`, mit und ohne konkurrierende Handlungsanweisung im selben Prompt. Der Anker bleibt trotzdem, weil die Überwachungsfassung allein keine eigene Tragfähigkeit hat (Vorgaben, Kapitel 2, Punkt 4).

**Erweitern.** Wer den Skill um ein eigenes Branch-Namensschema ergänzt, sollte es in der `CLAUDE.md` des Projekts verankern und hier nur darauf verweisen — sonst gilt das Schema plötzlich für alle Projekte.

## Stand und Offenes

**Status:** Anweisungen vollständig, Frontmatter gesetzt, stiller Trigger vorhanden und gemessen. Die Erprobung am Zielort findet statt, wenn der Skill dort gebraucht wird.

**Offen:** derzeit nichts.

**Bewusst offen gelassen.** Beides sind Festlegungen des jeweiligen Projekts und gehören in dessen `CLAUDE.md`, nicht in den Skill. Er benennt den Konflikt und überlässt die Entscheidung dem Nutzer:

- **Branch-Benennung im Worktree-Modus.** Arbeitet ein Projekt mit einem festen Branch-Namen für Claudes Arbeitsstand (`claude-workbench`), kollidiert das mit mehreren gleichzeitigen Worktrees: Sie brauchen mehrere Namen. Denkbare Wege sind ein festes Schema mit Zusatz (`claude-workbench-<aufgabe>`), die freie Vergabe durch das Werkzeug oder der Verzicht auf den festen Namen im Worktree-Fall. Hinzu kommt, dass die Werkbank per Konvention vom **Hauptpfad** abgeleitet wird, das Werkzeug aber standardmäßig vom Default-Branch — `worktree.baseRef` oder ein manuelles `git worktree add` wären die Auswege.
- **Projekteigene Zustandsdateien mit Branch-Bezug.** Wo eine versionierte Datei den Namen der Werkbank festhält (etwa `arbeitsdaten.json`), trägt jeder Branch seine eigene Fassung — ein gemeinsamer Zustand entsteht also nicht. Offen ist, ob ein abweichender Werkbank-Name beim Zusammenführen in den Hauptpfad mitwandern soll oder dort ausgenommen wird, und ob die Datei ein eigenes Feld für den aktuellen Worktree-Namen braucht.
