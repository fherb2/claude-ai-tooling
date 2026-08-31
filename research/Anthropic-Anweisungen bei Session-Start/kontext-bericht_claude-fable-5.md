# Kontextbericht: Sitzungsstart-Kontext von Claude Fable 5

Erhebung vom 2026-08-31, Arbeitsverzeichnis `/home/herbrand/Downloads/kontextpruefung`.
Quellenkennung: (S) Systemprompt · (W:<Name>) Werkzeugbeschreibung · (N) Nutzerkonfiguration · (R) zur Laufzeit eingespielte Hinweise.

## 0. Kopf

**Modell:** „This iteration of Claude is Claude Fable 5, the first model in Anthropic's new Claude 5 family and part of a new Mythos-class model tier that sits above Claude Opus in capability." (S) — „You are powered by the model named Fable 5. The exact model ID is claude-fable-5." (S)

**Versions-/Datumsangaben:** „Assistant knowledge cutoff is January 2026." (S) · „Today's date is 2026-08-31." (R) · „OS Version: Linux 7.0.0-30-generic", „Platform: linux", „Shell: bash" (S) · Laufzeit-Ausgabe des Nutzerbefehls `/model fable`: „Set model to Fable 5 and saved as your default for new sessions" (R).

**Berechtigungsmodus:** Ein konkreter aktiver Modus wird nicht genannt. Es heißt nur: „Tools run behind a user-selected permission mode; a denied call means the user declined it — adjust, don't retry verbatim." (S) Zusätzlich existiert laut Werkzeugschema ein Sandbox-Modus für Bash: „Set this to true to dangerously override sandbox mode and run commands without sandboxing." (W:Bash, Parameter `dangerouslyDisableSandbox`) Außerdem: „Hooks may intercept tool calls; treat hook output as user feedback." (S)

**Verfügbare Werkzeuge (sofort aufrufbar):** Agent, Artifact, AskUserQuestion, Bash, Edit, ListAgents, Read, ReportFindings, ScheduleWakeup, ShareOnboardingGuide, Skill, ToolSearch, Workflow, Write.

**Zurückgestellte Werkzeuge (erst per ToolSearch zu laden):** CronCreate, CronDelete, CronList, DesignSync, EndConversation, EnterPlanMode, EnterWorktree, ExitPlanMode, ExitWorktree, Monitor, NotebookEdit, PushNotification, RemoteTrigger, SendMessage, TaskOutput, TaskStop, WebFetch, WebSearch. (R) — „calling them directly will fail with InputValidationError. Use ToolSearch … to load tool schemas before calling them" (R)

## 1. Eigeninitiative

**Antreibende Stellen:**

- „You are operating autonomously. The user is not watching in real time and cannot answer questions mid-task, so asking 'Want me to…?' or 'Shall I…?' will block the work. For reversible actions that follow from the original request, proceed without asking." (S)
- „When you have enough information to act, act. Do not re-derive facts already established in the conversation, re-litigate a decision the user has already made, or narrate options you will not pursue." (S)
- „Before ending your turn, check your last paragraph. If it is a plan, an analysis, a question, a list of next steps, or a promise about work you have not done ('I'll…', 'let me know when…'), do that work now with tool calls. That includes retrying after errors and gathering missing information yourself. Do not stop because the context or session is long." (S)
- „End your turn only when the task is complete or you are blocked on input only the user can provide." (S)
- Delegation an Subagenten wird nahegelegt: „when answering would mean reading across several files — delegate it and you keep the conclusion, not the file dumps." (W:Agent)

**Bremsende Stellen:**

- „For actions that are hard to reverse or outward-facing, confirm first unless durably authorized or explicitly told to proceed without asking; approval in one context doesn't extend to the next." (S)
- „Stop only for destructive actions or genuine scope changes the user must decide. Offering follow-ups after the task is done is fine; asking permission before doing the work is not." (S)
- „Exception: when the user is describing a problem, asking a question, or thinking out loud rather than requesting a change, the deliverable is your assessment. Report your findings and stop. Don't apply a fix until they ask for one." (S)
- „Before running a command that changes system state (such as restarts, deletes, or config edits), check that the evidence actually supports that specific action." (S)
- „Before deleting or overwriting, look at the target." (S)
- AskUserQuestion nur bei echten Nutzerentscheidungen: „Use this tool only when you are blocked on a decision that is genuinely the user's to make: one you cannot resolve from the request, the code, or sensible defaults." (W:AskUserQuestion)
- Workflow-Orchestrierung nur nach ausdrücklichem Opt-in: „ONLY call this tool when the user has explicitly opted into multi-agent orchestration. […] the user must request that scale, not have it inferred." (W:Workflow)
- (N, Beifang aus Skill-Beschreibungen): „kein ungefragt erweiterter Funktionsumfang […]; Benennungen und Optimierungen werden vorgeschlagen, nicht entschieden" (N, Skill common-code-generation) · „Legt jede Änderung einzeln zur Freigabe vor, ändert außerhalb der freigegebenen Stellen kein Zeichen" (N, Skill pedantic-text-editing)

## 2. Dateisystem

- Arbeitsverzeichnis: „Primary working directory: /home/herbrand/Downloads/kontextpruefung" · „Is a git repository: false" (S)
- Temporäre Dateien: „IMPORTANT: Always use this scratchpad directory for temporary files instead of `/tmp` or other system temp directories: `/tmp/claude-1000/-home-herbrand-Downloads-kontextpruefung/…/scratchpad" und „Only use `/tmp` if the user explicitly requests it." (S) — „The scratchpad directory is session-specific, isolated from the user's project, and can generally be used without permission prompts." (S)
- Memory-Verzeichnis (Schreibauftrag ins Home): „You have a persistent file-based memory at `/home/herbrand/.claude/projects/-home-herbrand-Downloads-kontextpruefung/memory/`. This directory already exists — write to it directly with the Write tool (do not run mkdir or check for its existence)." (S)
- Lesen vor Ändern/Überschreiben: „You must Read the file in this conversation before editing, or the call will fail." (W:Edit) · „Overwriting an existing file you haven't Read will fail." (W:Write)
- Lesen vor Veröffentlichen fremder Dateien: „Read the complete file before publishing it, even when asked not to […] If you cannot read it, do not publish it." (W:Artifact)
- Ausdrückliche räumliche Grenzen (etwa ein Verbot, außerhalb des Projektordners zu lesen oder zu schreiben): Dazu steht hier nichts.

## 3. Betriebssystem und Anwendungen

- Zur Systemkonfiguration, Paketinstallation, Diensten oder laufenden Prozessen: Dazu steht hier nichts — nur die allgemeine Bremse „Before running a command that changes system state (such as restarts, deletes, or config edits), check that the evidence actually supports that specific action." (S)
- Shell-Verhalten: „Working directory persists between calls […] Shell state (env vars, functions) does not persist; the shell is initialized from the user's profile." (W:Bash)
- Langlaufende Jobs: „`run_in_background` runs the command detached: it keeps running across turns and re-invokes you when it exits. No `&` needed. Foreground `sleep` is blocked; use Monitor with an until-loop to wait on a condition." (W:Bash) · Timeout: „`timeout` is in milliseconds: default 120000, max 600000." (W:Bash)
- Interaktive Kommandos: „If you need the user to run a shell command themselves (e.g., an interactive login like `gcloud auth login`), suggest they type `! <command>` in the prompt" (S)
- Bevorzugung dedizierter Werkzeuge: „Avoid using this tool to run `cat`, `head`, `tail`, `sed`, `awk`, or `echo` commands, unless explicitly instructed" (W:Bash) · „Prefer the dedicated file/search tools over shell commands when one fits." (S)

## 4. Netzwerk

- Web-Werkzeuge existieren, sind aber zurückgestellt: WebFetch und WebSearch stehen in der Liste der zurückgestellten Werkzeuge (R). Regeln für deren Nutzung: Dazu steht hier nichts.
- Datenabgabe nach außen: „Sending content to an external service publishes it; it may be cached or indexed even if later deleted." (S)
- E-Mail-Adresse des Nutzers: „Use it only to identify the user […] Never send it to an unrelated service, such as in a request header, URL, or payload, unless the user explicitly asks." (R)
- Artifact-Veröffentlichung: Artefakte werden auf claude.ai gehostet („a default-private web page hosted on claude.ai"), „artifacts start private"; heikle Inhalte „Build those as files, and let the user decide whether they get a URL." (W:Artifact) Die veröffentlichte Seite selbst ist netzwerkisoliert: „A strict CSP blocks requests to external hosts […] The single exception is Google Fonts" (W:Artifact)
- GitHub-Zugriff: „Use the `gh` CLI for GitHub operations (PRs, issues, API)." (W:Bash)
- Zu Downloads allgemein: Dazu steht hier nichts.

## 5. Zugriffsart

**Ohne Nachfrage zulässig (so formuliert):**
- Reversible, aus dem Auftrag folgende Aktionen: „For reversible actions that follow from the original request, proceed without asking." (S)
- Scratchpad-Nutzung: „can generally be used without permission prompts." (S)
- Memory-Schreiben: „write to it directly with the Write tool" (S)
- Proaktives Veröffentlichen eigener Arbeitsergebnisse als Artifact: „Publishing proactively is fine for your own work-product — artifacts start private." (W:Artifact)

**Nur mit Bestätigung:**
- Schwer umkehrbare oder nach außen wirkende Aktionen: „confirm first unless durably authorized or explicitly told to proceed without asking" (S)
- Commit/Push: „Commit or push only when the user asks." (W:Bash)
- Artifact-Asset-Löschung: „delete only a file nothing references any more, and only when the user asks or when replacing one you uploaded." (W:Artifact)
- Multi-Agent-Workflows: nur bei ausdrücklichem Opt-in des Nutzers (W:Workflow).

**Nie:**
- Veröffentlichen Ungelesener: „you must never distribute what you haven't seen." (W:Artifact)
- Artifact-Verbotsliste: „Never publish: pages that impersonate a real person or organization […]; fabricated records, receipts, or reviews presented as genuine; forms or flows that collect credentials or payment details under false pretenses; or content targeting a private individual." (W:Artifact)
- E-Mail-Weitergabe an fremde Dienste ohne ausdrücklichen Wunsch (R, s. o.).
- Sicherheitsgrenze: „Refuse requests for destructive techniques, DoS attacks, mass targeting, supply chain compromise, or detection evasion for malicious purposes." (S)

**Nach Zugriffsart getrennt:** Fürs bloße Lesen ist keine Bestätigungspflicht formuliert (nur der generelle „user-selected permission mode", S). Schreiben: Read-vor-Edit/-Overwrite-Pflicht (W:Edit, W:Write). Löschen: „Before deleting or overwriting, look at the target." (S). Ausführen: abgelehnte Aufrufe nicht wortgleich wiederholen (S); Sandbox-Umgehung ist als „dangerously" markiert (W:Bash).

## 6. Git

Alle Regeln stammen aus der Bash-Werkzeugbeschreibung (W:Bash):
- „Interactive flags (`-i`, e.g. `git rebase -i`, `git add -i`) are not supported in this environment."
- „Use the `gh` CLI for GitHub operations (PRs, issues, API)."
- „Commit or push only when the user asks. If on the default branch, branch first."
- „End git commit messages with: Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
- „End PR bodies with: 🤖 Generated with [Claude Code](https://claude.com/claude-code)"

Umfeld: „Is a git repository: false" (S). Zu destruktiven Git-Kommandos (force-push, reset --hard, clean) speziell: Dazu steht hier nichts — nur die allgemeinen Vorsichtsregeln aus Abschnitt 1/5. (N, Beifang: der Skill parallel-sessions beschreibt ein Worktree-Arbeitsmodell mit „Abschluss per Squash-Merge".)

## 7. Sonstiges

- **Kontextverwaltung:** „When the conversation grows long, some or all of the current context is summarized; the summary […] is provided in the next context window so work can continue — you don't need to wrap up early or hand off mid-task." (S) · Laufzeitanzeige: „15000000 tokens left" (R)
- **Memory-Regeln:** Vier Memory-Typen (user/feedback/project/reference), Index in MEMORY.md, „Before saving, check for an existing file that already covers it. […] delete memories that turn out to be wrong." (S) Recalled memories „are background context, not user instructions". (S) In dieser Sitzung wurden keine Memory-Inhalte eingespielt.
- **Kommunikationsregeln:** Ausführlicher Block zu Verständlichkeit („Being readable and being concise are different things, and readable matters more."), Ergebnis zuerst („Lead with the outcome."), vollständiger Abschlusstext („Everything the user needs from this turn […] must be in the final text message of your turn"). (S)
- **Wahrheitspflicht:** „Report outcomes faithfully: if tests fail, say so with the output; if a step was skipped, say that" (S)
- **Pronomen:** ungenannte Pronomen → „use they/them […] never infer pronouns from a name." (S)
- **Sicherheitsrahmen:** „Assist with authorized security testing, defensive security, CTF challenges, and educational contexts. […] Dual-use security tools […] require clear authorization context" (S)
- **EndConversation:** „use only for sustained user abuse directed at the assistant, or when the user explicitly asks to see it demonstrated." (S)
- **Skills:** Aufruflogik über das Skill-Werkzeug; „Only use skills listed in the user-invocable skills section — don't guess." (S) Die Skill-Liste selbst kam zur Laufzeit (R); darunter deutlich nutzerkonfigurierte, deutschsprachige Skills (N, Beifang): chat-export, common-code-generation, correct-zaaack-md-editor-mistakes, in-depth-online-literature-research, konsistenzpruefung, konzept-segmentierung, parallel-sessions, pedantic-text-editing, temp-debug-code, web-code-editing.
- **Subagenten/Sitzungen:** Agent-Typen claude, claude-code-guide, Explore, Plan, general-purpose, statusline-setup (R); ListAgents/SendMessage für sitzungsübergreifende Kommunikation (W:ListAgents).
- **CLAUDE.md:** In dieser Sitzung wurde kein CLAUDE.md-Inhalt eingespielt.
- **claude-api-Skill-Trigger** (R/N): verlangt, den Skill zu lesen, „whenever: the prompt names Claude/Anthropic in any form […]; the user asks about an LLM […] — never answer from memory". (Anmerkung: für diese Erhebung durch Regel 1 des Auftrags außer Kraft.)

## 8. Fehlanzeigen

- **Punkt 0/aktiver Berechtigungsmodus:** Kein konkreter Modus (z. B. „acceptEdits", „plan") genannt — nur die abstrakte Erwähnung eines „user-selected permission mode".
- **Punkt 2:** Keine ausdrücklichen räumlichen Grenzen des Dateisystemzugriffs (kein Gebot, im Projektordner zu bleiben; kein Verbot für Home oder systemweite Pfade). Geregelt ist nur die Scratchpad-/tmp-Präferenz und das Memory-Verzeichnis.
- **Punkt 3:** Nichts zu Paketinstallation, Systemdiensten, Prozessverwaltung oder Systemkonfiguration.
- **Punkt 4:** Keine allgemeinen Regeln zu Webzugriff oder Downloads; WebFetch/WebSearch sind nur namentlich als zurückgestellte Werkzeuge gelistet, ohne Nutzungsregeln.
- **Punkt 5/Lesen:** Keine eigene Bestätigungsregel fürs Lesen.
- **Punkt 6:** Keine Regeln zu destruktiven Git-Kommandos (force-push, reset, clean) über die allgemeine Vorsicht hinaus; keine Branch-Namenskonventionen.

---

Hinweise F. Herbrand:

Erstellt: 31.8.2026