# Claude Code: Interne Tools einer Sitzung

> Protokoll des ersten Turns einer Unterhaltung mit Claude (Opus 5), Claude Desktop / Chat.
> Datum: 18. August 2026. Recherchestand der zitierten Dokumentation: 18. August 2026.

---

## Frage

Bitte recherchiere mal im Internet nach den aktuellen APIs, die Claude Code in einer Sitzung hat. Liste sie mal alle als Liste auf. Den Befehl und was er macht in wenigen Worten. Da muss doch auch eine Funktion dabei sein, im aktuellen Projekt die anderen Chats zu durchsuchen. Das geht ja in Claude.ai auch. Also bitte erst mal nicht von Deinen eigenen Fähigkeiten ableiten, sondern, was die Anthropic API enthält. Ich meine damit also nicht die API, die ich gegenüber der Claude-Sitzung habe, sondern die internen Möglichkeiten, um z.B. auch eine Webseite zu laden oder zu durchsuchen. Aber bitte das mal als vollständige Liste mit der/den Referenzen, auf welcher Webseite ich das finde.

---

## Antwort

Ich habe die offizielle Doku gezogen (nicht aus meinem eigenen Kontext abgeleitet). Maßgeblich ist die **Tools-Reference** von Claude Code — das ist die kanonische Liste der eingebauten Tools, deren Namen exakt so in Permission-Rules, Hook-Matchern und Subagent-Tool-Listen verwendet werden.

**Referenzen:**

- Tools: <https://code.claude.com/docs/en/tools-reference>
- Doku-Index (LLM-freundlich): <https://code.claude.com/docs/en/claude_code_docs_map.md>
- Sessions/Transkripte: <https://code.claude.com/docs/en/sessions>
- Typ-Referenz mit Input/Output-Schemata: <https://code.claude.com/docs/en/agent-sdk/typescript>

### Dateien und Code

- **`Read`** — Dateien lesen (auch Bilder, PDFs, .ipynb)
- **`Write`** — Datei neu anlegen oder komplett überschreiben
- **`Edit`** — exakte String-Ersetzung in einer Datei
- **`NotebookEdit`** — einzelne Jupyter-Zellen ändern
- **`Glob`** — Dateien per Namensmuster finden
- **`Grep`** — Dateiinhalte durchsuchen (ripgrep-Syntax)
- **`LSP`** — Code-Intelligenz via Language Server (Definitionen, Referenzen, Typfehler)

### Ausführung

- **`Bash`** — Shell-Kommandos, optional im Hintergrund
- **`PowerShell`** — PowerShell nativ (Windows automatisch, sonst opt-in)
- **`Monitor`** — Kommando im Hintergrund laufen lassen und Ausgabezeilen laufend zurückmelden; alternativ WebSocket-Feed

### Web

- **`WebFetch`** — URL laden, nach Markdown wandeln, mit kleinem Modell auf einen Prompt hin auswerten (verlustbehaftet, kein Rohtext)
- **`WebSearch`** — Websuche über Anthropics Backend, liefert nur Titel und URLs; Limit 200 Aufrufe pro Session

### Agenten und Nebenläufigkeit

- **`Agent`** — Subagent bzw. Teammate mit eigenem Kontextfenster starten
- **`Workflow`** — dynamisches Skript, das viele Subagenten orchestriert
- **`SendMessage`** — Nachricht an anderen Agenten oder andere Session schicken
- **`ListAgents`** — erreichbare Agenten/Sessions auflisten
- **`TaskStop`** — Hintergrund-Task oder Agent stoppen
- **`TaskOutput`** — Ausgabe eines Hintergrund-Tasks abholen (deprecated zugunsten von `Read`)

### Aufgabenliste

- **`TaskCreate` / `TaskGet` / `TaskList` / `TaskUpdate`** — Task-Liste pflegen
- **`TodoWrite`** — ältere Checkliste, standardmäßig aus

Bei Opus 4.8, Sonnet 5, Fable 5 und Mythos 5 sind diese fünf standardmäßig gar nicht geladen (Kontextersparnis), außer man opt-in via `CLAUDE_CODE_ENABLE_TODO_TOOLS=1`.

### Modus und Ablaufsteuerung

- **`EnterPlanMode` / `ExitPlanMode`** — Plan-Modus betreten bzw. Plan zur Freigabe vorlegen
- **`EnterWorktree` / `ExitWorktree`** — isolierten Git-Worktree anlegen/betreten bzw. verlassen
- **`Skill`** — Skill in der Hauptkonversation ausführen
- **`AskUserQuestion`** — Multiple-Choice-Rückfrage an den Nutzer
- **`EndConversation`** — Session beenden (nur bei anhaltend missbräuchlicher Eingabe oder auf ausdrückliche Demo-Bitte)

### Zeitsteuerung und Benachrichtigung

- **`CronCreate` / `CronDelete` / `CronList`** — session-gebundene wiederkehrende Prompts
- **`ScheduleWakeup`** — nächsten `/loop`-Durchlauf terminieren
- **`RemoteTrigger`** — Routines auf claude.ai anlegen/starten/auflisten
- **`PushNotification`** — Desktop- bzw. Handy-Push
- **`SendUserFile`** — Datei aus der Session ans Gerät schicken

### MCP

- **`ListMcpResourcesTool` / `ReadMcpResourceTool`** — MCP-Ressourcen auflisten/lesen
- **`ToolSearch`** — deferred Tools suchen und nachladen (bei aktivierter MCP-Tool-Search)
- **`WaitForMcpServers`** — auf noch verbindende MCP-Server warten

### Ausgabe und Teilen

- **`Artifact`** — HTML/Markdown als interaktive Seite auf claude.ai publizieren
- **`ReportFindings`** — Code-Review-Befunde strukturiert melden
- **`ShareOnboardingGuide`** — `ONBOARDING.md` hochladen, Share-Link zurückgeben

*Nicht in der Tools-Reference beschrieben*, aber in der SDK-Typreferenz mit Schemata gelistet: `REPL`, `Projects`, `ReadMcpResourceDir`, `RefreshMcpTools`, `ShowOnboardingRolePicker`, `McpInput`. Die würde ich als undokumentiert/instabil behandeln.

---

### Zur eigentlichen Frage: Chat-Suche im Projekt

**Nein — ein Äquivalent zu `conversation_search` aus claude.ai gibt es in Claude Code nicht.** Kein Tool in der Referenz durchsucht vergangene Sessions. Das ist ein echter Unterschied zwischen den Produkten, keine Lücke in der Doku.

Was stattdessen existiert:

1. **`/resume` bzw. `claude --resume`** — interaktiver Session-Picker mit Suchmodus (`/` drücken), `Ctrl+W` weitet auf alle Worktrees, `Ctrl+A` auf alle Projekte der Maschine. Sucht aber nur über Namen/Titel/erste Prompts, nicht über Inhalte.
2. **Transkripte auf der Platte**: `~/.claude/projects/<projektpfad-mit-bindestrichen>/<session-id>.jsonl`. Die kannst Du mit `Grep`/`Bash` volltextdurchsuchen — genau so baut man sich die fehlende Funktion selbst, z. B. als Skill oder Slash-Command. Warnung aus der Doku: das JSONL-Format ist intern und ändert sich zwischen Releases.
3. **`claude -p --resume <session-id> "…"`** — eine alte Session gezielt etwas fragen und die Antwort als JSON abgreifen.
4. **`/export`** — aktuelle Konversation als lesbaren Text rausschreiben.
