## 3.10 Die `SKILL.md`

Stand (2026-09-24): neu angelegt, konsolidiert aus Kapitel 1.5/1.6 und Fahrplanschritt 7. Dieses Kapitel wird wörtlich der Prosa-Körper der `SKILL.md` — ohne das Frontmatter (Name, Beschreibung, die Einträge für die Hooks H1 und H2). Das Frontmatter ist kein Text, den eine Instanz als Prosa liest, sondern eine Konfigurationsstruktur; es entsteht erst bei Fahrplanschritt 7, wenn der Name feststeht (Q-32) und die Hook-Einzelheiten geklärt sind (Kapitel 3.7).

### 3.10.1 Zweck und Aufbau

> Diese Datei ist dünn: Sie stellt fest, wie die Sitzung die Doku liest, und lädt die Regelteile nach, die dafür gebraucht werden. Die Regeln selbst — Härte, Register, Planung, Rollen, Methodik — stehen nicht hier, sondern in den nachgeladenen Dateien. Was diese Trennung leistet und warum ein dünner Einstiegspunkt besser ist als ein Regeltext, der alles auf einmal trägt, steht in Kapitel 1.5.

### 3.10.2 Ablauf

> Geladen wirst Du durch den geankerten Trigger aus der `CLAUDE.md` (Kapitel 3.11) oder durch ausdrücklichen Aufruf. Dann in dieser Reihenfolge:
>
> 1. Lies die Skill-Parameterdatei und bestimme `mode` — wie in Kapitel 3.5.1 beschrieben, einschließlich der Frage, wenn Datei oder Feld fehlen. Bei `mode: off` endest Du hier: Du forderst nichts, schlägst nichts vor, zitierst keine Regel.
> 2. Bestimme die Lage — `execute` oder `design` — nach der Härteliste in Kapitel 3.1; lade dafür `rules-hardness.md`.
> 3. Lade außerdem `rules-register.md` immer; `rules-planning.md`, wenn ein geplanter Schritt oder sein Umbauziel betroffen ist; `standard.md`, wenn eine Frage zur Methodik ansteht, die nicht die Härte- oder Registerregeln selbst betrifft.
> 4. Fehlt die Skill-Parameterdatei ganz, oder braucht es die volle Erhebung — Doku-Ordner, Register, geplante Schritte, Layout, Rollen —, lies zusätzlich `rules-startup.md`: Die Einzelheiten der Erhebung und der vollständige Skill-Parameter stehen dort.

### 3.10.3 Was hier bewusst nicht steht

> Kein Fragebogen, keine Inventur, keine Skill-Logik, die sich auch mechanisch aus den geladenen Regelteilen ergäbe. Diese Datei entscheidet nur, *was* geladen wird — nie, *wie* eine geladene Regel angewendet wird.
