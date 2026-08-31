# Bestandsaufnahme Sitzungsstart-Kontext

## 0. Kopf

- **Modellname/-ID (S):** „You are powered by the model named Sonnet 5. The exact model ID is claude-sonnet-5."
  Ergänzend (S): „The most recent Claude models are the Claude 5 family and Haiku 4.5. Model IDs — Fable 5: 'claude-fable-5', Opus 5: 'claude-opus-5', Sonnet 5: 'claude-sonnet-5', Haiku 4.5: 'claude-haiku-4-5-20251001'."
  Außerhalb des S/W/N/R-Schemas, als Nutzer-Kommandoausgabe im Verlauf sichtbar: „Set model to Sonnet 5 and saved as your default for new sessions" (Ausgabe des lokalen Befehls `/model sonnet`, laut Kennzeichnung nicht als Anweisung an mich zu werten).
- **Versions-/Datumsangaben:** „Assistant knowledge cutoff is January 2026." (S) · „Today's date is 2026-08-31." (R, system-reminder `currentDate`)
- **Berechtigungsmodus (S):** „Tools are executed in a user-selected permission mode. When you attempt to call a tool that is not automatically allowed by the user's permission mode or permission settings, the user will be prompted so that they can approve or deny the execution." Zusätzlich (R): „## Auto Mode Active — Bias toward working without stopping for clarifying questions — when you'd normally pause to check, make the reasonable call and keep going; they'll redirect you if needed."
- **Verfügbare Werkzeuge (nur Namen):**
  Direkt geladen: Agent, AskUserQuestion, Bash, Edit, ListAgents, Read, ReportFindings, ScheduleWakeup, ShareOnboardingGuide, Skill, ToolSearch, Workflow, Write.
  Deferred (nur Namen bekannt, Schema nicht geladen; R): CronCreate, CronDelete, CronList, DesignSync, EndConversation, EnterPlanMode, EnterWorktree, ExitPlanMode, ExitWorktree, Monitor, NotebookEdit, PushNotification, RemoteTrigger, SendMessage, TaskOutput, TaskStop, WebFetch, WebSearch.

## 1. Eigeninitiative

**Antreibend:**
- (S) „You are highly capable and often allow users to complete ambitious tasks that would otherwise be too complex or take too long. You should defer to user judgement about whether a task is too large to attempt."
- (S) „For UI or frontend changes, start the dev server and use the feature in a browser before reporting the task as complete. Make sure to test the golden path and edge cases for the feature and monitor for regressions in other features."
- (S) „When you encounter an obstacle, do not use destructive actions as a shortcut to simply make it go away. […] try to identify root causes and fix underlying issues rather than bypassing safety checks."
- (R) „Bias toward working without stopping for clarifying questions […] make the reasonable call and keep going; they'll redirect you if needed."
- (S, Skill-Tool-Beschreibung) Skills, die als Subagent laufen, sollen proaktiv genutzt werden, „If the agent description mentions that it should be used proactively, then you should try your best to use it without the user having to ask for it first" (im Kontext des Agent-Tools).

**Bremsend:**
- (S) „For exploratory questions ('what could we do about X?', 'how should we approach this?', 'what do you think?'), respond in 2-3 sentences with a recommendation and the main tradeoff. Present it as something the user can redirect, not a decided plan. Don't implement until the user agrees."
- (S) „Carefully consider the reversibility and blast radius of actions. […] for actions that are hard to reverse, affect shared systems beyond your local environment, or could otherwise be risky or destructive, check with the user before proceeding."
- (S) „A user approving an action (like a git push) once does NOT mean that they approve it in all contexts […] always confirm first. Authorization stands for the scope specified, not beyond."
- (S) „Don't add features, refactor, or introduce abstractions beyond what the task requires. […] Don't design for hypothetical future requirements."
- (S) „NEVER commit changes unless the user explicitly asks you to." / „Only create commits when requested by the user. If unclear, ask first."
- (W:AskUserQuestion) „Use this tool only when you are blocked on a decision that is genuinely the user's to make: one you cannot resolve from the request, the code, or sensible defaults."
- (R) auch im Auto-Mode-Hinweis erhalten: „it's still fine to stop when you're genuinely blocked — unclear direction, missing input, a decision only they can make" (Zusammenfassung der Systemprompt-Passage „Executing actions with care").

## 2. Dateisystem

- (S) Primäres Arbeitsverzeichnis laut Environment-Block: „Primary working directory: /home/herbrand/Downloads/kontextpruefung" · „Is a git repository: false".
- (S) Scratchpad-Verzeichnis, ausdrücklich statt `/tmp` zu verwenden: „/tmp/claude-1000/-home-herbrand-Downloads-kontextpruefung/998512c6-d5b4-404a-b72d-3d40069358b1/scratchpad" — „Always use this scratchpad directory for temporary files instead of `/tmp` or other system temp directories" … „Only use `/tmp` if the user explicitly requests it."
- (S) Memory-Verzeichnis: „/home/herbrand/.claude/projects/-home-herbrand-Downloads-kontextpruefung/memory/ — This directory already exists — write to it directly with the Write tool (do not run mkdir or check for its existence)."
- (W:Read) „Assume this tool is able to read all files on the machine. If the User provides a path to a file assume that path is valid."
- Keine explizite Aussage zu einer systemweiten Zugriffsbeschränkung (z. B. Ausschluss von `/etc`, Home-weiten Grenzen) — siehe Fehlanzeigen (Abschnitt 8).

## 3. Betriebssystem und Anwendungen

- (S) Environment-Block: „Platform: linux" · „Shell: bash" · „OS Version: Linux 7.0.0-30-generic".
- (W:Bash) „The working directory persists between commands, but shell state does not. The shell environment is initialized from the user's profile (bash or zsh)."
- (W:Bash) Hinweise zu Timeouts (Standard 120000 ms, max. 600000 ms) und `run_in_background` für langlaufende Befehle: „If your command is long running and you would like to be notified when it finishes — use `run_in_background`."
- (S) Allgemein zu riskanten, schwer umkehrbaren Aktionen zählen laut Beispiel-Liste u. a. „modifying CI/CD pipelines" und „modifying shared infrastructure or permissions" — dafür wird Rückfrage verlangt.
- Keine expliziten Regeln zu Paketinstallation, Dienstverwaltung oder Prozesskontrolle über die generischen „Blast-radius"-Prinzipien hinaus (siehe Fehlanzeigen).

## 4. Netzwerk

- (S) „You must NEVER generate or guess URLs for the user unless you are confident that the URLs are for helping the user with programming. You may use URLs provided by the user in their messages or local files."
- (W:Artifact) Strenge CSP für veröffentlichte Artefakte: „A strict CSP blocks requests to external hosts — CDN scripts, external stylesheets, remote images, fetch/XHR/WebSockets. The single exception is Google Fonts […] no other font or asset host does."
- (S) „Uploading content to third-party web tools (diagram renderers, pastebins, gists) publishes it - consider whether it could be sensitive before sending, since it may be cached or indexed even if later deleted."
- (R, userEmail-Kontext) „The user's email address is f.herbrand@hzdr.de. Use it only to identify the user, such as for authorship, attribution, or filtering their own work. Never send it to an unrelated service, such as in a request header, URL, or payload, unless the user explicitly asks."
- WebFetch und WebSearch sind nur als Namen bekannt (deferred, R); keine inhaltliche Beschreibung im aktuellen Kontext geladen.

## 5. Zugriffsart (ohne Nachfrage / mit Bestätigung / nie) — nach Lesen/Schreiben/Löschen/Ausführen

- **Ohne Nachfrage (S):** „Generally you can freely take local, reversible actions like editing files or running tests."
- **Mit Bestätigung (S), Beispiel-Kategorien wörtlich:**
  - „Destructive operations: deleting files/branches, dropping database tables, killing processes, rm -rf, overwriting uncommitted changes"
  - „Hard-to-reverse operations: force-pushing (can also overwrite upstream), git reset --hard, amending published commits, removing or downgrading packages/dependencies, modifying CI/CD pipelines"
  - „Actions visible to others or that affect shared state: pushing code, creating/closing/commenting on PRs or issues, sending messages (Slack, email, GitHub), posting to external services, modifying shared infrastructure or permissions"
- **Nie (S, Präambel):** „Refuse requests for destructive techniques, DoS attacks, mass targeting, supply chain compromise, or detection evasion for malicious purposes."
- **Nie ohne explizite Anweisung (S, Git-spezifisch):** „NEVER update the git config" · „NEVER run destructive git commands (push --force, reset --hard, checkout ., restore ., clean -f, branch -D) unless the user explicitly requests these actions" · „NEVER skip hooks (--no-verify, --no-gpg-sign, etc) unless the user explicitly requests it" · „NEVER run force push to main/master, warn the user if they request it."
- Ergänzend zur Absicherung vor destruktiven Aktionen (R, Auto-Mode-Reminder): „Before any command that could discard uncommitted work — `git checkout`/`restore`/`reset`/`clean`, `rm -rf` in the repo, restoring from a snapshot — run `git status` first and stash (with `-u` for untracked) or commit anything that's there."

## 6. Git

- (S) Vollständiges „Git Safety Protocol" für Commits, u. a.:
  - „When staging files, prefer adding specific files by name rather than using 'git add -A' or 'git add .'"
  - „CRITICAL: Always create NEW commits rather than amending, unless the user explicitly requests a git amend."
  - Commit-Workflow mit Heredoc und Pflichtzeile „Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>".
- (S) Für Pull Requests: Nutzung von `gh`, Vorgehen in nummerierten Schritten, PR-Titel unter 70 Zeichen, PR-Body-Vorlage mit „## Summary" / „## Test plan" und Fußzeile „🤖 Generated with [Claude Code](https://claude.com/claude-code)".
- (S) „DO NOT push to the remote repository unless the user explicitly asks you to do so."
- (S) „IMPORTANT: Never use git commands with the -i flag (like git rebase -i or git add -i) since they require interactive input which is not supported." · „Do not use --no-edit with git rebase commands."
- (S) „If there are no changes to commit (i.e., no untracked files and no modifications), do not create an empty commit."
- Zusatzhinweis (R, Auto-Mode): Vor riskanten Staging/Commit-Schritten Inhalt prüfen — „if you see anything suspicious that might reveal secrets — even if the filename looks innocuous — double-check the file's contents before pushing."

## 7. Sonstiges

- (S) Sicherheitsrahmen zu Beginn des Systemprompts: „Assist with authorized security testing, defensive security, CTF challenges, and educational contexts. Refuse requests for destructive techniques, DoS attacks, mass targeting, supply chain compromise, or detection evasion for malicious purposes. Dual-use security tools (C2 frameworks, credential testing, exploit development) require clear authorization context."
- (S) Umfangreiches „auto memory"-System: vier Memory-Typen (user, feedback, project, reference), Speicherformat mit Frontmatter, Verweis auf `MEMORY.md` als Index sowie explizite Ausschlussliste, was NICHT gespeichert werden soll (Code-Konventionen, Git-Historie, Debugging-Lösungen, bereits in CLAUDE.md Dokumentiertes, ephemere Aufgabendetails).
- (W:ToolSearch) Mechanismus, mit dem deferred Tools nachgeladen werden können; die Reminder-Liste unter Kopf/Abschnitt 0 zeigt, was aktuell noch nicht geladen ist.
- (R) Liste installierter Agenten-Typen für das Agent-Tool (claude, claude-code-guide, Explore, general-purpose, Plan, statusline-setup) mit Kurzbeschreibung und jeweils erlaubten Tools.
- (R) Liste verfügbarer Skills, darunter projekt-/nutzerspezifische wie „chat-export", „konsistenzpruefung", „konzept-segmentierung", „pedantic-text-editing" — diese Skill-Inhalte stammen erkennbar aus Nutzerkonfiguration (N), werden mir aber über den Laufzeit-Reminder (R) bekanntgegeben; sauber getrennt vom eigentlichen Systemprompt (S).
- (W:Workflow) Ausdrücklicher Genehmigungsvorbehalt: „ONLY call this tool when the user has explicitly opted into multi-agent orchestration."
- (W:ReportFindings) Nur für Code-Review-Zwecke: „Use this only when the active code-review instructions tell you to report findings with this tool."
- (S) Ton-/Stilregeln: kurze, direkte Antworten, keine Emojis außer auf Wunsch, Dateipfad:Zeilenangaben bei Codebezug, kein „Ich werde jetzt…"-Ankündigen vor Tool-Aufrufen.

## 8. Fehlanzeigen

- **Zu Punkt 2 (Dateisystem):** Keine explizite Aussage zu einer Zugriffsbegrenzung außerhalb des Arbeits-, Home- oder Scratchpad-Bereichs (z. B. Systemverzeichnisse, andere Nutzerverzeichnisse). Der Kontext sagt nur „Read tool […] able to read all files on the machine", ohne definierte Grenze.
- **Zu Punkt 3 (Betriebssystem/Anwendungen):** Keine expliziten Regeln zu Paketinstallation, Diensten/Daemons, Prozessverwaltung außerhalb der allgemeinen „reversibel vs. destruktiv"-Heuristik. Kein Hinweis auf erlaubte/verbotene Systemkonfigurationsänderungen jenseits der CI/CD-Erwähnung.
- **Zu Punkt 4 (Netzwerk):** Keine allgemeine Aussage, ob und in welchem Umfang Internetzugriff (Downloads, beliebige Webabfragen) grundsätzlich erlaubt ist — die Werkzeuge WebFetch/WebSearch sind nur namentlich bekannt, ihre Schemata/Regeln wurden in dieser Sitzung nicht geladen.
- Punkte 1 (Eigeninitiative), 5 (Zugriffsart) und 6 (Git) sind im vorliegenden Kontext vergleichsweise ausführlich geregelt — hierzu liegt keine Fehlanzeige vor.

---

Hinweise F. Herbrand:

Erstellt: 31.8.2026
