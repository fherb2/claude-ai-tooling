# Sandbox- und Werkzeug-Settings: Snippets mit Parameterbeschreibung

*Stand: 2026-09-01 · Angaben gegen die Claude-Code-Doku, eine Hersteller-Referenzkonfiguration, das Bedrohungsmodell von Trail of Bits und vier Bug-Reports im Claude-Code-Repository geprüft. Quellen am Ende.*

**Geltungsbereich:** Linux und macOS; unter Windows nur über WSL2 — nativ läuft die Sandbox dort nicht, und Pfade würden anders geschrieben (`//c/**/.env` statt `//**/.env`).

**Herkunft jedes Blocks ist angegeben:** *[Doku]* = aus Anthropics Beispielen, *[NVIDIA]* = aus der Hersteller-Referenz für Container, *[angepasst]* = daraus abgeleitet.

## Das Wichtigste zuerst

Wer nur eine Aussage mitnimmt, dann diese: **Gegenüber dem eigenen System schützt verlässlich nur eine Grenze außerhalb von Claude Code** — Container, VM oder ein eingehauster Nutzer. Die Einstellungen in dieser Datei sind **Steuerung**, nicht Systemschutz: Sie bremsen den alltäglichen Übereifer und stellen im Auto-Modus die eine Frage, auf die es ankommt.

Konkret für heute:

- **Was zuverlässig arbeitet:** die Berechtigungsebene (`permissions.*`) — Read-Sperren, Bypass-Sperre, die `ask`-Regel am Sandbox-Ausstieg. Sie hängt nicht an bubblewrap.
- **Was mit Vorbehalt arbeitet:** die Sandbox-Dateiebene. `denyRead` ist dokumentiert, aber nachweislich nicht immer durchgesetzt, und die Doku-Empfehlung zum Sperren des Homes ist ein bekannter, ungefixter Bug.
- **Was heute abrät:** die Sandbox dauerhaft einzuschalten, während man mit **git-Worktrees** arbeitet — dann scheitern alle git-Kommandos.

## Wer was sichert

Vier Schichten, und nur die letzten beiden brauchen eine Regel von Dir:

- **Schreibzugriffe: der Sandbox-Default.** Die Schreibseite ist eine Allowlist — erlaubt sind nur Arbeitsverzeichnis, Session-Temp und hinzugefügte Verzeichnisse; alles andere ist gesperrt, ohne Aufzählung. `/etc`, `/usr`, fremde Projekte: zu.
- **Fremde Daten: das Betriebssystem.** Claude Code läuft mit den Rechten des Nutzers. Root-eigene Dateien und fremde Home-Verzeichnisse sind schon durch die Dateirechte unerreichbar.
- **Eigene Geheimnisse: `sandbox.credentials`.** Dafür gibt es einen eigenen Mechanismus — und nur er erreicht auch **Umgebungsvariablen**. Ein Token in `GITHUB_TOKEN` wird von keiner Pfadliste erfasst.
- **Selbst-Rechteausweitung: Schreibschutz der eigenen Konfiguration.** Wer die `settings.json` oder einen Hook schreiben kann, erweitert sich selbst die Rechte für den nächsten Lauf.

Wichtig für die Einordnung: **Was die Sandbox überhaupt umfasst**, sagt die Doku kategorisch — „The sandbox isolates Bash subprocesses. Other tools operate under different boundaries." Memory schreiben, Sitzungsprotokolle führen, Skills laden sind Operationen der Engine, keine Bash-Kindprozesse; `sandbox.denyRead` erreicht sie nicht und schränkt Claude dort auch nicht ein.

## Der Stand der Sandbox heute: vier belegte Einschränkungen

Diese vier stammen aus Bug-Reports im Claude-Code-Repository und sind der Grund, warum die Empfehlungen unten so ausfallen, wie sie ausfallen.

**1. Die Doku-Empfehlung zum Sperren des Homes ist defekt.** [Issue #40941](https://github.com/anthropics/claude-code/issues/40941) meldet exakt das Beispiel aus der Doku (`denyRead: ["~/"]` plus `allowRead: ["."]`): falsches Arbeitsverzeichnis, Shell-Resets, `ls` und `git status` scheitern. Der Melder: „The offending line is `"denyRead": ["~/"]`. Removing this line consistently fixes the problem." Labels `bug`, `has repro` — **closed as not planned** (30. März 2026).

**2. Ein fehlerhafter Dateibereich kann die Sandbox am Start hindern.** [Issue #50781](https://github.com/anthropics/claude-code/issues/50781): `bwrap: Can't create file at …: Read-only file system`, und damit scheitert **jedes** Bash-Kommando. Ursache: Die Sandbox markiert Pfade per `denyWithinAllow` als read-only, und bwraps eigene Initialisierung will genau dort schreiben — „The sandbox cannot bootstrap itself." Besonders zu wissen: **`dangerouslyDisableSandbox` hilft dann nicht**, „because bwrap runs before this flag takes effect". Closed as not planned (19. April 2026).

**3. `denyRead` wird nicht zuverlässig durchgesetzt.** [Issue #61208](https://github.com/anthropics/claude-code/issues/61208), Titel „Security: denyRead in sandbox not working": Mit `denyRead: ["//**"]` und einer engen `allowRead`-Liste konnte weiterhin überall gelesen werden; die Varianten `["/"]` und `["~/"]` ebenso wirkungslos. Labels `area:security`, `bug` — **closed as not planned** (21. Mai 2026). Praktische Folge: **Kein `denyRead`-Eintrag gilt als wirksam, bevor Du ihn selbst abgetastet hast.**

**4. Sandbox und git-Worktrees vertragen sich nicht.** [Issue #80278](https://github.com/anthropics/claude-code/issues/80278) — **offen und von Maintainern reproduziert** (22. Juli 2026): Die Sandbox maskiert `.git/config.worktree` mit einem lese-verweigerten `/dev/null`-Bind-Mount, worauf **alle** git-Kommandos scheitern, auch `git status`. Ausgelöst wird `extensions.worktreeConfig=true` automatisch von `git worktree` und `git sparse-checkout`. Die Workarounds sind alle unschön: `excludedCommands: ["git *"]` (nimmt ganze Shell-Aufrufe aus der Sandbox), `allowUnsandboxedCommands: true` oder Dateisystem-Isolation ganz aus.

---

## Bereich A – Sandbox

### A1 – Geheimnisse schützen *[Doku]* — die heute praktikable Form

Der vorgesehene Weg, aus der Sandbox-Doku. Erfasst Dateien **und** Umgebungsvariablen:

```json
{
  "sandbox": {
    "enabled": true,
    "credentials": {
      "files": [
        { "path": "~/.aws/credentials", "mode": "deny" },
        { "path": "~/.ssh", "mode": "deny" }
      ],
      "envVars": [
        { "name": "GITHUB_TOKEN", "mode": "deny" },
        { "name": "NPM_TOKEN", "mode": "deny" }
      ]
    }
  }
}
```

Beide Listen sind um Deine eigenen Fälle zu ergänzen — was dazugehört, steht unten unter „Was Du selbst festlegen musst".

### A2 – Selbst-Rechteausweitung verhindern *[NVIDIA]*

Claude Code schützt einige Pfade selbst; die Hersteller-Referenz setzt sie zusätzlich explizit:

```json
{
  "sandbox": {
    "enabled": true,
    "filesystem": {
      "denyWrite": [
        "~/.claude/settings.json",
        "~/.claude/hooks",
        "~/.claude.json",
        "~/.claude/credentials.json"
      ],
      "denyRead": [
        "~/.claude.json",
        "~/.claude/credentials.json"
      ]
    }
  }
}
```

### A3 – Härtung für unbeaufsichtigten Lauf *[Doku]*

```json
{
  "sandbox": {
    "enabled": true,
    "failIfUnavailable": true,
    "allowUnsandboxedCommands": false
  }
}
```

Und wenn das Netz eng geführt werden soll *[angepasst, Domains nach Trail of Bits]*:

```json
{
  "sandbox": {
    "network": {
      "strictAllowlist": true,
      "allowedDomains": [
        "api.anthropic.com",
        "github.com", "raw.githubusercontent.com",
        "registry.npmjs.org",
        "pypi.org", "files.pythonhosted.org"
      ]
    }
  }
}
```

### A4 – Home-Umkehrung *[Doku] — derzeit defekt, nicht verwenden*

Die Doku beschreibt, wie sich das ganze Home sperren und nur die Arbeit freigeben ließe. Das wäre der einzige Weg, der auch Thunderbird, Browserprofile und künftig installierte Software erfasst, **ohne sie aufzuzählen** — und genau deshalb wäre er der bessere:

```json
{
  "sandbox": {
    "enabled": true,
    "filesystem": {
      "denyRead": ["~/"],
      "allowRead": ["."]
    }
  }
}
```

Laut Doku gehört das in die Projekt-`.claude/settings.json`, weil `.` nur dort auf die Projektwurzel zeigt. Für mehrere Projekte ließe es sich aufteilen — `enabled` und `denyRead` in die User-Settings, `allowRead: ["."]` je Projekt —, denn „when you define the same filesystem array in multiple settings scopes, Claude Code merges them, combining paths from every scope".

**Trotzdem: nicht verwenden.** Genau diese Konfiguration ist als Bug gemeldet (#40941, oben), und ein eigener Versuch am 1. September 2026 hat sie bestätigt: Der Sandbox-Aufbau brach ab mit `bwrap: Can't create file at <projekt>/.mcp.json: Read-only file system`, danach lief kein einziges Bash-Kommando mehr. Der Block steht hier, damit man ihn wiedererkennt — nicht zum Übernehmen.

### Parameter (Bereich A)

- `sandbox.enabled` — schaltet die Bash-Sandbox ein. Für alle Projekte gehört sie laut Doku in die User-Settings.
- `sandbox.credentials.files` — Geheimnis-Dateien: `mode: "deny"` verweigert den Read innerhalb der Sandbox; `mode: "mask"` zeigt einen Platzhalter, den der Proxy nur Richtung erlaubter `injectHosts` ersetzt (braucht `network.tlsTerminate`).
- `sandbox.credentials.envVars` — dasselbe für Umgebungsvariablen; `deny` entfernt sie vor jedem sandboxed Kommando. **Der einzige Weg, Token im Environment zu erwischen.**
- `sandbox.filesystem.denyRead` — Pfade, die sandboxed Kommandos nicht lesen dürfen (OS-Ebene, gilt auch für Subprozesse). **Wirksamkeit einzeln prüfen, siehe Einschränkung 3.**
- `sandbox.filesystem.allowRead` — gibt Pfade innerhalb eines gesperrten Bereichs wieder frei; der speziellere Pfad gewinnt.
- `sandbox.filesystem.denyWrite` — sperrt Schreiben in einzelnen Pfaden innerhalb der erlaubten Zone; in A2 gegen Selbst-Rechteausweitung.
- `sandbox.filesystem.allowWrite` — erlaubt Schreiben außerhalb der Default-Schreibzone (Doku-Beispiel: `["~/.kube", "/tmp/build"]`).
- `sandbox.filesystem.disabled` — schaltet die Datei-Isolation ganz ab, behält nur die Netz-Isolation. Einer der Workarounds für Einschränkung 4 — mit dem entsprechenden Verlust.
- `sandbox.failIfUnavailable` — bei `true` Abbruch, statt (Default) ungeschützt weiterzulaufen (fail-open).
- `sandbox.allowUnsandboxedCommands` — bei `false` („Strict sandbox mode") wird `dangerouslyDisableSandbox` ignoriert. Achtung: Gegen einen gescheiterten Sandbox-**Aufbau** (Einschränkung 2) hilft der Ausweg ohnehin nicht.
- `sandbox.autoAllowBashIfSandboxed` — Default `true`: sandboxbare Kommandos laufen ohne Prompt. Die NVIDIA-Referenz setzt bewusst `false`.
- `sandbox.excludedCommands` — Kommandos, die außerhalb der Sandbox laufen dürfen. Einer der Workarounds für Einschränkung 4 (`["git *"]`) — nimmt dann aber ganze Shell-Aufrufe heraus.
- `sandbox.enableWeakerNestedSandbox` — nötig **innerhalb von Containern**: bubblewrap läuft dort reduziert und kann kein frisches `/proc` mounten. Schwächt die Isolation; außerhalb von Containern nicht setzen.
- `sandbox.network.allowedDomains` / `strictAllowlist` / `deniedDomains` / `tlsTerminate` — Domain-Allowlist, hartes Abweisen statt Nachfragen, Blocklist mit Vorrang, TLS-Terminierung als Voraussetzung fürs Masking.

---

## Bereich B – Agent-Werkzeuge (`permissions.*`)

**Diese Ebene funktioniert.** Sie hängt nicht an bubblewrap und ist von den vier Einschränkungen oben nicht betroffen. Zwei Eigenheiten:

**Es gibt schon eine Grenze.** Für lesende Werkzeuge ist laut Doku keine Zustimmung nötig „within the working directory and additional directories" — außerhalb also schon. Im Manual-Modus fragt Claude dort; im Auto-Modus entscheidet der Klassifikator.

**Die Umkehrung funktioniert hier nicht.** Bei `permissions` gewinnt `deny` immer und lässt sich durch kein `allow` wieder aufmachen.

### B1 – Geheimnisse, Bypass-Sperre, Ebenenfrage *[angepasst]*

```json
{
  "permissions": {
    "disableBypassPermissionsMode": "disable",
    "ask": [
      "Bash(dangerouslyDisableSandbox:true)"
    ],
    "deny": [
      "Read(~/.ssh/**)",
      "Read(~/.aws/**)",
      "Read(~/.gnupg/**)",
      "Read(~/.netrc)",
      "Read(~/.npmrc)",
      "Read(~/.git-credentials)",
      "Read(~/.password-store/**)",
      "Read(//**/.env)",
      "Read(//**/.env.*)"
    ],
    "allow": [
      "WebFetch(domain:github.com)",
      "WebFetch(domain:docs.claude.com)"
    ]
  }
}
```

Die `ask`-Regel ist der wirksamste einzelne Eintrag: Der Auto-Modus bleibt überall erhalten, und nur das eine Ereignis „raus aus der Sandbox" wird Dir zwingend vorgelegt — durchgesetzt vom Client, nicht vom Modell.

### B2 – Umgebungsverändernde Kommandos sperren *[NVIDIA]*

```json
{
  "permissions": {
    "deny": [
      "Bash(sudo *)",
      "Bash(pip install *)",
      "Bash(pip3 install *)",
      "Bash(docker *)",
      "Bash(podman *)"
    ],
    "ask": [
      "Bash(git add *)",
      "Bash(git commit *)"
    ]
  }
}
```

**Vorbehalt:** Bash-Deny-Regeln sind gegen gezielte Umgehung fragil (Variablen, Interpreter-Wrapping) — Defense-in-depth, keine Grenze.

### Parameter (Bereich B)

- `permissions.disableBypassPermissionsMode` — `"disable"` sperrt `--dangerously-skip-permissions`; wirkt aus jedem Scope, auch aus User-Settings.
- `permissions.deny` — harte Verbote, zuerst ausgewertet, durch keine Ebene aufhebbar. `Read(<pfad>)` sperrt das Read-Werkzeug und speist zugleich die Sandbox-`denyRead`.
- `permissions.ask` — wie `deny`, aber es wird gefragt. Als `Bash(dangerouslyDisableSandbox:true)` die gezielte Ebenenfrage am Sandbox-Ausstieg.
- `permissions.allow` — Vorab-Freigaben; greifen erst, nachdem der Ordner „getrusted" ist.
- `WebFetch(domain:<host>)` — erlaubt dem WebFetch-Werkzeug diesen Host **und** öffnet ihn in der Sandbox-Netz-Allowlist.
- `permissions.additionalDirectories` — zusätzliche Arbeitsverzeichnisse; erweitert zugleich die Schreibzone der Sandbox.

---

## Was Du selbst festlegen musst

Weil die Umkehrung ausfällt, bleibt nur die Aufzählung — und deren Preis trägst Du, dauerhaft:

**Eine Inventur Deiner Geheimnisse.** Niemand kann sie für Dich machen, sie hängt an Deiner installierten Software. Durchzugehen wären mindestens: Schlüssel (`~/.ssh`, `~/.gnupg`); Cloud-CLIs (`~/.aws`, `~/.config/gcloud`, `~/.azure`, `~/.kube`, `~/.docker/config.json`); Paketquellen (`~/.npmrc`, `~/.pypirc`, `~/.cargo/credentials.toml`, `~/.m2/settings.xml`); Git (`~/.netrc`, `~/.git-credentials`); Passwortverwaltung (`~/.password-store`, `~/.local/share/keyrings`, KeePass-Dateien — die liegen irgendwo); Mail (`~/.thunderbird`, Evolution); Browser (`~/.mozilla`, `~/.config/google-chrome`, Chromium, Brave); Messenger; VPN-Konfigurationen; Editor-Credential-Stores (JetBrains, VS Code); Backup-Werkzeuge (restic-, borg-Passwörter); und die Shell-History, in der Tokens landen.

**Eine zweite Inventur im Environment.** Tokens in Umgebungsvariablen erwischt keine Pfadliste — nur `sandbox.credentials.envVars`. Was bei Dir gesetzt ist, weißt nur Du.

**Pflege auf beiden Flächen.** Jeder Pfad braucht einen Eintrag für das Read-Werkzeug und einen für die Sandbox. Teilweise automatisch, weil Read-Denys in die Sandbox einfließen — aber nur teilweise.

**Fortschreibung ohne Auslöser.** Jede neu installierte Anwendung kann eine neue Geheimnisablage mitbringen, und nichts erinnert Dich daran. Das ist die strukturelle Schwäche der Aufzählung: Sie verschwindet nicht, sie wandert nur von der Maschine zu Dir.

**Empirische Nachkontrolle.** Wegen Einschränkung 3 gilt kein Eintrag als wirksam, bevor Du ihn abgetastet hast: Lesen versuchen, Ergebnis ansehen.

**Und akzeptieren, was nicht abdeckbar ist:** vergessene Orte, Shell-History, Reste in `/tmp`, alles was ein laufender Prozess im Speicher hält.

## Was nur Container oder VM leisten

Alles oben ist **client-seitige Steuerung**. Gegenüber dem eigenen System schützt verlässlich nur eine Grenze, die außerhalb von Claude Code liegt. Das ist nicht eine Meinung, sondern die Übereinstimmung aller geprüften Quellen: Anthropic empfiehlt für den Bypass-Modus „only … in isolated environments like containers, VMs"; Anthropic betreibt sein eigenes Cowork-Produkt mit Claude in einer VM; ein systematischer macOS-Vergleich kam zum Schluss „the VM boundary is the security boundary"; und Trail of Bits' gesamter Ansatz ist ein Container.

**Aber auch das nicht grenzenlos:**

- Ein Container schützt **den Host**, nicht seinen **Inhalt**. Trail of Bits sagt ausdrücklich, dass In-Container-Credentials nicht isoliert sind — „Claude, GitHub, and other tokens provided to container are simply accessible inside it". Das gemountete Projektverzeichnis ist echt und beschreibbar.
- **DNS bleibt ein Exfiltrationskanal**, auch mit Domain-Allowlist.
- **VS Code schwächt die Grenze:** Trail of Bits warnt, dass „Reopen in Container" eine RPC-Brücke öffnet, über die Code aus dem Container **Kommandos auf dem Host** ausführen kann, und empfiehlt für nicht vertrauenswürdigen Code das Terminal statt VS Code.

Die vernünftige Aufteilung ist deshalb: **Container/VM als Grenze für das, was es wert ist** — unbeaufsichtigte Läufe, fremder Code, Firmen- und OT-Rechner. **Die Einstellungen als Steuerung darin** — sie bremsen den alltäglichen Übereifer und stellen die eine Frage, die zählt.

## Hinweise vor dem Übernehmen

- **Erst in einer Wegwerf-Sitzung probieren.** Eine fehlerhafte Sandbox-Dateikonfiguration kann den Sandbox-**Aufbau** zum Scheitern bringen — dann läuft gar kein Bash mehr, und der Notausstieg greift nicht (Einschränkung 2).
- **Mit git-Worktrees: Sandbox besser aus**, bis #80278 behoben ist.
- **Die Netzlisten addieren sich.** Wirksam ist `allowedDomains` **plus** die Domains der `WebFetch(domain:…)`-Regeln. Wer eine Domain für WebFetch freigibt, öffnet sie auch für Bash.
- **Pfad-Prefix in User-Settings:** `.` löst dort auf `~/.claude` auf, nicht aufs Projekt, und `**/.env` ist an das aktuelle Verzeichnis gebunden. Deshalb `~/` für Home-Pfade und `//` für dateisystemweite Muster: `//**/.env` matcht `.env` überall.
- **Deny ist absolut:** Eine User-`Read`-Deny lässt sich nicht per Projekt-`allow` ausnehmen. In der Sandbox ist das anders — dort ist `allowRead` innerhalb von `denyRead` der vorgesehene Weg.
- **Änderungen wirken sofort:** „When you edit these filesystem lists during a session, Claude Code applies the change to the running session" — für einen Test braucht es keine neue Sitzung.
- **Kein Sicherheitsbeweis.** Diese Regeln senken die Wahrscheinlichkeit von Fehlzugriffen. Mehr behaupten sie nicht.

## Quellen

**Claude-Code-Doku:** [Sandboxing](https://code.claude.com/docs/en/sandboxing) · [Permissions](https://code.claude.com/docs/en/permissions) · [Settings](https://code.claude.com/docs/en/settings) · [Settings-Referenz](https://code.claude.com/docs/en/settings-reference)

**Referenzkonfigurationen:** NVIDIA AI Workbench, [Configure Claude Code Sandboxing in a Project Container](https://docs.nvidia.com/ai-workbench/user-guide/latest/quickstart/quickstart-claude-sandbox.html) · Trail of Bits, [claude-code-devcontainer](https://github.com/trailofbits/claude-code-devcontainer)

**Bug-Reports:** [#40941](https://github.com/anthropics/claude-code/issues/40941) Doku-Empfehlung bricht das Arbeitsverzeichnis · [#50781](https://github.com/anthropics/claude-code/issues/50781) bwrap kann sich nicht bootstrappen · [#61208](https://github.com/anthropics/claude-code/issues/61208) `denyRead` nicht durchgesetzt · [#80278](https://github.com/anthropics/claude-code/issues/80278) git-Worktrees brechen (offen)
