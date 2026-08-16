# parallel-sessions — Zusammenarbeit mehrerer Claude-Instanzen in einem Repository

Zwei Schritte in fester Reihenfolge: erst die Schreibhoheit für Git klären (und bis zur Antwort keine schreibenden Kommandos ausführen), dann das Worktree-Modell als saubere Trennung anbieten und beide Einrichtungswege erklären.

**Status:** Anweisungen vollständig, Frontmatter gesetzt, stiller Trigger vorhanden. In der Gesamt-README beschrieben.

**Trigger gemessen** (14. August 2026, nicht-interaktiv nach Kapitel 4.2 der Vorgaben): Mit der jetzigen Description feuert er auf Sonnet im ersten Turn — sowohl in dieser Fassung als auch in einer reinen Überwachungsfassung ohne Anker, geprüft mit sechszeiliger und mit vollständiger realer `CLAUDE.md`, mit und ohne konkurrierende Handlungsanweisung im selben Prompt. Der Anker bleibt trotzdem, weil die Überwachungsfassung allein keine eigene Tragfähigkeit hat (Vorgaben, Kapitel 2, Punkt 4).

**Grundlage der Worktree-Beschreibung** (Beobachtung an der Werkzeugbeschreibung von `EnterWorktree`, 14. August 2026): Das Werkzeug legt den Worktree unter `.claude/worktrees/` an und erzeugt dabei **immer einen neuen Branch**, nie den bereits ausgecheckten. Basis ist standardmäßig `origin/<default-branch>`; die Einstellung `worktree.baseRef` mit dem Wert `head` zweigt stattdessen vom aktuellen lokalen HEAD ab. Ein Branch kann ohnehin nie in zwei Worktrees gleichzeitig ausgecheckt sein — das erzwingt Git.

**Offen:** derzeit nichts. Die Erprobung am Zielort findet statt, wenn der Skill dort gebraucht wird.

**Bewusst offen gelassen.** Beides sind Festlegungen des jeweiligen Projekts und gehören in dessen `CLAUDE.md`, nicht in den Skill. Er benennt den Konflikt und überlässt die Entscheidung dem Nutzer:

- **Branch-Benennung im Worktree-Modus.** Arbeitet ein Projekt mit einem festen Branch-Namen für Claudes Arbeitsstand (`claude-workbench`), kollidiert das mit mehreren gleichzeitigen Worktrees: Sie brauchen mehrere Namen. Denkbare Wege sind ein festes Schema mit Zusatz (`claude-workbench-<aufgabe>`), die freie Vergabe durch das Werkzeug oder der Verzicht auf den festen Namen im Worktree-Fall. Hinzu kommt, dass die Werkbank per Konvention vom **Hauptpfad** abgeleitet wird, das Werkzeug aber standardmäßig vom Default-Branch — `worktree.baseRef` oder ein manuelles `git worktree add` wären die Auswege.
- **Projekteigene Zustandsdateien mit Branch-Bezug.** Wo eine versionierte Datei den Namen der Werkbank festhält (etwa `arbeitsdaten.json`), trägt jeder Branch seine eigene Fassung — ein gemeinsamer Zustand entsteht also nicht. Offen ist, ob ein abweichender Werkbank-Name beim Zusammenführen in den Hauptpfad mitwandern soll oder dort ausgenommen wird, und ob die Datei ein eigenes Feld für den aktuellen Worktree-Namen braucht.
