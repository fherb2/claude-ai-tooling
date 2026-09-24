## 3.10 Die `SKILL.md`

Stand (2026-09-24): neu angelegt, konsolidiert aus Kapitel 1.5/1.6 und Fahrplanschritt 7. Dieses Kapitel wird wörtlich der Prosa-Körper der `SKILL.md` — ohne das Frontmatter (Name, Beschreibung, die Einträge für die Hooks H1 und H2). Das Frontmatter ist kein Text, den eine Instanz als Prosa liest, sondern eine Konfigurationsstruktur; es entsteht erst bei Fahrplanschritt 7, wenn der Name feststeht (Q-32) und die Hook-Einzelheiten geklärt sind (Kapitel 3.7).

### 3.10.1 Zweck und Aufbau

> Diese Datei ist dünn: Sie stellt fest, wie die Sitzung die Doku liest, und lädt die Regelteile nach, die dafür gebraucht werden. Die Regeln selbst — Härte, Register, Planung, Rollen, Methodik — stehen nicht hier, sondern in den nachgeladenen Dateien. Was diese Trennung leistet und warum ein dünner Einstiegspunkt besser ist als ein Regeltext, der alles auf einmal trägt, steht in Kapitel 1.5.

### 3.10.2 Ablauf

> Geladen wirst Du durch den geankerten Trigger aus der `CLAUDE.md` (Kapitel 3.11) oder durch ausdrücklichen Aufruf. Dann in dieser Reihenfolge:
>
> 1. **Skill-Parameterdatei lesen.** `.claude/software-design-doc.json`. Steht dort `mode: off`, endest Du hier: Du forderst nichts, schlägst nichts vor, zitierst keine Regel; vorhandene Doku in fremder Form wird vor Änderungen gelesen und dort gepflegt, wo das Projekt sie selbst pflegt. Steht dort `mode: on`, weiter mit Schritt 3.
> 2. **Fehlt die Datei oder das Feld `mode`, danach fragen:** einmal je Sitzung, wie `git-workbench` es tut — „Soll ich das hier führen?" —, mit Angebot, die Skill-Parameterdatei anzulegen. Bei Ablehnung zusätzlich fragen, ob `mode: off` trotzdem festgehalten werden soll, damit die Frage nicht wiederkehrt. Erst nach Zustimmung (oder bei `mode: on`) weiter mit Schritt 3.
> 3. **Lage bestimmen** — `execute` oder `design` — nach der Härteliste in Kapitel 3.1; lade dafür `rules-hardness.md`.
> 4. **Regelteile laden:** `rules-register.md` immer; `rules-planning.md`, wenn ein geplanter Schritt oder sein Umbauziel betroffen ist; `standard.md`, wenn eine Frage zur Methodik ansteht, die nicht die Härte- oder Registerregeln selbst betrifft.
> 5. **Ablesen, was ablesbar ist**, oder — fehlt die Skill-Parameterdatei ganz, oder braucht es die volle Erhebung — `rules-startup.md` zusätzlich laden: Doku-Ordner (Rollenmarker, eine `decisions.md`, die üblichen Ordnernamen), Register, Dateien mit geplanten Schritten (Rolle `plan`, `work-plan.md`, `fahrplan.md`, Abschnitt „Offen" einer README), Layout der Prosa, vorhandene Rollen. Die Einzelheiten der Erhebung und der vollständige Skill-Parameter stehen dort (Kapitel 3.5).
>
> **Was hier nicht gefragt wird:** Ob eine konkrete Festlegung ab jetzt festgehalten werden soll, ist keine Frage dieses Ablaufs — sie kommt erst, wenn im Plan eine Festlegung entsteht, die den Code überdauert (Kapitel 1.7). Schritt 2 fragt nur, ob Du hier grundsätzlich mitschreibst, nicht, was Du im Einzelnen festhältst.

### 3.10.3 Was hier bewusst nicht steht

> Kein Fragebogen, keine Inventur, keine Skill-Logik, die sich auch mechanisch aus den geladenen Regelteilen ergäbe. Diese Datei entscheidet nur, *was* geladen wird — nie, *wie* eine geladene Regel angewendet wird.
