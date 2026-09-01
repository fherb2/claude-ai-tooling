# Sandbox- und Werkzeug-Settings: Snippets mit Parameterbeschreibung

*Stand: 2026-09-01 · Alle Angaben gegen die Claude-Code-Doku (code.claude.com/docs/en/sandboxing, .../settings, .../permissions, .../permission-modes) am 1. September 2026 geprüft.*

**Geltungsbereich:** Linux und macOS; unter Windows nur über WSL2 — nativ läuft die Sandbox dort nicht, und Pfade würden anders geschrieben (`//c/**/.env` statt `//**/.env`). Einzige dokumentierte macOS-Abweichung: Beim Credential-*Masking* blockt macOS die Datei, statt den Wert zu ersetzen; reine `deny`-Regeln sind davon nicht betroffen.

Ziel dieser Datei: fertige `settings.json`-Snippets zum Übernehmen, und darunter je Parameter **eine Zeile** (Parameter — Beschreibung), damit man die Sandbox-Doku nicht querlesen muss. `settings.json` ist striktes JSON und trägt **keine** Kommentare; deshalb stehen die Erklärungen hier als Listen neben den Blöcken.

**Herkunft der Blöcke ist jeweils angegeben:** *[Doku]* = wörtlich aus Anthropics Beispielen, *[NVIDIA]* = aus der Hersteller-Referenzkonfiguration für Container, *[angepasst]* = daraus abgeleitet, *[ungetestet]* = hier nicht erprobt. Quellen am Ende.

## Wer was sichert

Bevor man Regeln schreibt, lohnt die Frage, was überhaupt noch offen ist. Vier Schichten — und nur die letzten beiden brauchen eine Regel:

- **Schreibzugriffe: der Sandbox-Default.** Die Schreibseite ist eine Allowlist — erlaubt sind nur Arbeitsverzeichnis, Session-Temp und ausdrücklich hinzugefügte Verzeichnisse; **alles andere ist gesperrt**, ohne dass es jemand aufzählen müsste. `/etc`, `/usr`, fremde Projekte: zu.
- **Fremde Daten: das Betriebssystem.** Claude Code läuft mit den Rechten des Nutzers, nicht mehr. Root-eigene Dateien und fremde Home-Verzeichnisse sind schon durch die Dateirechte unerreichbar.
- **Eigene Geheimnisse: `sandbox.credentials`.** Dafür gibt es einen eigenen Mechanismus — und nur er erreicht auch **Umgebungsvariablen**. Ein Token in `GITHUB_TOKEN` wird von keiner Pfadliste erfasst.
- **Selbst-Rechteausweitung: Schreibschutz der eigenen Konfiguration.** Wer die `settings.json` oder einen Hook schreiben kann, erweitert sich selbst die Rechte für den nächsten Lauf.

## Die zwei Wirkungsflächen

Sandbox und Agent-Werkzeuge sind getrennt, und beide brauchen eine Regel:

- **Bereich A – Sandbox (`sandbox.*`)** deckt **Bash und alle davon gestarteten Kindprozesse** ab, OS-durchgesetzt (bubblewrap/Seatbelt). Ein `python script.py` über Bash ist damit eingehaust.
- **Bereich B – Agent-Werkzeuge (`permissions.*`)** deckt **Read, Edit, Write, WebFetch** ab. Diese laufen nicht durch die Sandbox, sondern über das Berechtigungssystem. Die NVIDIA-Referenz formuliert es knapp: „Deny rules on Read and Edit only block Claude's built-in file tools" — OS-Durchsetzung braucht zusätzlich die Sandbox-Regeln.

Die beiden greifen ineinander: `Read`-Deny- und `Edit`-Regeln aus Bereich B fließen zusätzlich in die Dateikonfiguration der Sandbox ein, und `WebFetch(domain:…)`-Regeln in deren Netz-Allowlist.

---

## Bereich A – Sandbox

### A1 – Geheimnisse schützen *[Doku]*

Der vorgesehene Weg, wörtlich aus der Sandbox-Doku. Erfasst Dateien **und** Umgebungsvariablen:

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

Die Listen sind um die eigenen Fälle zu ergänzen — `~/.gnupg`, `~/.netrc`, `~/.npmrc`, `~/.git-credentials`, `~/.password-store`, und bei den Variablen alles, was im eigenen Environment an Tokens steht.

### A2 – Selbst-Rechteausweitung verhindern *[NVIDIA]*

Claude Code schützt einige Pfade schon selbst; die Hersteller-Referenz setzt sie zusätzlich explizit:

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

Dazu, wenn das Netz eng geführt werden soll *[angepasst, Domains nach Trail of Bits]*:

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

### A4 – Home-Umkehrung *[Doku] [bei uns gescheitert]*

Die Doku beschreibt, wie sich das ganze Home sperren und nur die Arbeit freigeben lässt — das wäre der einzige Weg, der auch Thunderbird, Browserprofile und künftig installierte Software erfasst, ohne sie aufzuzählen:

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

**Gehört laut Doku in die Projekt-`.claude/settings.json`**, weil `.` nur dort auf die Projektwurzel zeigt; in User-Settings löst `.` auf `~/.claude` auf, und die Projektdateien blieben gesperrt.

**Testvermerk (1. September 2026):** Eine Variante dieser Konfiguration in den **User**-Settings, mit dem Projekt-*Elternordner* statt `.` im `allowRead`, hat hier die Sandbox unbrauchbar gemacht: Schon der Aufbau bricht ab mit `bwrap: Can't create file at <projekt>/.mcp.json: Read-only file system` — bubblewrap kann die Maskierung der geschützten Pfade im Projekt nicht mehr anlegen, und damit scheitert jedes Bash-Kommando. Die **dokumentierte** Form (Projekt-Settings, `allowRead: ["."]`) ist hier **nicht erprobt**. Vor dem Einsatz also erst in einer Wegwerf-Sitzung probieren. Bemerkenswert als Einordnung: Die einzige uns bekannte, real laufende Herstellerkonfiguration (NVIDIA) verzichtet auf die Umkehrung und schützt stattdessen gezielt Credentials.

### Parameter (Bereich A)

- `sandbox.enabled` — schaltet die Bash-Sandbox ein; ohne dieses `true` greift keine der übrigen `sandbox.*`-Angaben.
- `sandbox.credentials.files` — Geheimnis-Dateien: `mode: "deny"` verweigert den Read innerhalb der Sandbox; `mode: "mask"` zeigt einen Platzhalter, den der Proxy nur Richtung erlaubter `injectHosts` ersetzt (braucht `network.tlsTerminate`).
- `sandbox.credentials.envVars` — dasselbe für Umgebungsvariablen; `deny` entfernt sie vor jedem sandboxed Kommando. **Der einzige Weg, Token im Environment zu erwischen.**
- `sandbox.filesystem.denyRead` — Pfade, die innerhalb der Sandbox nicht gelesen werden dürfen (OS-Ebene, gilt auch für Subprozesse).
- `sandbox.filesystem.allowRead` — gibt einzelne Pfade innerhalb eines gesperrten Bereichs wieder frei; der speziellere Pfad gewinnt. Grundlage der Umkehrung in A4.
- `sandbox.filesystem.denyWrite` — sperrt Schreiben in einzelnen Pfaden innerhalb der erlaubten Zone; in A2 gegen Selbst-Rechteausweitung.
- `sandbox.filesystem.allowWrite` — erlaubt Schreiben außerhalb der Default-Schreibzone, falls ein Subprozess an einen festen Ort schreiben muss (Doku-Beispiel: `["~/.kube", "/tmp/build"]`).
- `sandbox.filesystem.disabled` — schaltet die Datei-Isolation ganz ab und behält nur die Netz-Isolation; nur für Workloads setzen, denen man Selbst-Rechteausweitung nicht zutraut.
- `sandbox.failIfUnavailable` — bei `true` Abbruch, wenn die Sandbox nicht starten kann, statt (Default) ungeschützt weiterzulaufen (fail-open).
- `sandbox.allowUnsandboxedCommands` — bei `false` („Strict sandbox mode") wird `dangerouslyDisableSandbox` komplett ignoriert.
- `sandbox.autoAllowBashIfSandboxed` — Default `true`: sandboxbare Kommandos laufen ohne Prompt. Die NVIDIA-Referenz setzt bewusst `false`, will also trotz Sandbox gefragt werden.
- `sandbox.excludedCommands` — Kommandos, die außerhalb der Sandbox laufen dürfen (z. B. `docker`, das drinnen nicht funktioniert).
- `sandbox.enableWeakerNestedSandbox` — nötig **innerhalb von Containern**: bubblewrap läuft dort in reduziertem Modus und kann kein frisches `/proc` mounten. Schwächt die Isolation; außerhalb von Containern nicht setzen.
- `sandbox.network.allowedDomains` — Domain-Allowlist für ausgehenden Verkehr; leer = kein Netz. So eng wie möglich halten.
- `sandbox.network.strictAllowlist` — nicht gelistete Hosts werden **abgewiesen** statt nachgefragt; wirkt nur aus User-/Managed-/CLI-Settings.
- `sandbox.network.deniedDomains` — Blocklist mit Vorrang.
- `sandbox.network.tlsTerminate` — der Proxy terminiert TLS selbst; Voraussetzung für Credential-Masking.

---

## Bereich B – Agent-Werkzeuge (`permissions.*`)

Zwei Dinge sind hier anders als in Bereich A:

**Es gibt schon eine Grenze.** Für lesende Werkzeuge ist laut Doku keine Zustimmung nötig „within the working directory and additional directories" — außerhalb also **schon**. Im Manual-Modus fragt Claude dort nach; im Auto-Modus entscheidet an dieser Grenze der Klassifikator statt des Nutzers.

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

Die `ask`-Regel ist der wirksamste einzelne Eintrag: Der Auto-Modus bleibt überall erhalten, und nur das eine Ereignis „raus aus der Sandbox" wird dem Nutzer zwingend vorgelegt — durchgesetzt vom Client, nicht vom Modell.

### B2 – Umgebungsverändernde Kommandos sperren *[NVIDIA]*

```json
{
  "permissions": {
    "deny": [
      "Bash(sudo *)",
      "Bash(pip install *)",
      "Bash(pip3 install *)",
      "Bash(python -m pip install *)",
      "Bash(python3 -m pip install *)",
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

Verhindert, dass sich der Agent die Umgebung selbst umbaut. **Vorbehalt:** Bash-Deny-Regeln sind gegen gezielte Umgehung fragil (Variablen, Interpreter-Wrapping) — Defense-in-depth, keine Grenze.

### Parameter (Bereich B)

- `permissions.disableBypassPermissionsMode` — Wert `"disable"` sperrt `--dangerously-skip-permissions`; wirkt aus jedem Scope, auch aus User-Settings, taugt also als Selbstschutz.
- `permissions.deny` — harte Verbote, zuerst ausgewertet, durch keine andere Ebene aufhebbar. `Read(<pfad>)` sperrt das Read-Werkzeug und speist zugleich die Sandbox-`denyRead`.
- `permissions.ask` — wie `deny`, aber es wird gefragt. Als `Bash(dangerouslyDisableSandbox:true)` die gezielte Ebenenfrage am Sandbox-Ausstieg.
- `permissions.allow` — Vorab-Freigaben; greifen erst, nachdem der Ordner „getrusted" ist.
- `WebFetch(domain:<host>)` — erlaubt dem WebFetch-Werkzeug diesen Host **und** öffnet ihn in der Sandbox-Netz-Allowlist.
- `permissions.additionalDirectories` — zusätzliche Arbeitsverzeichnisse; erweitert zugleich die Schreibzone der Sandbox.

---

## Hinweise vor dem Übernehmen

- **Erst in einer Wegwerf-Sitzung probieren.** Eine fehlerhafte Sandbox-Dateikonfiguration kann den Sandbox-**Aufbau** zum Scheitern bringen, nicht nur einzelne Kommandos — dann läuft gar kein Bash mehr (bei uns geschehen, siehe A4).
- **Die Netzlisten addieren sich.** Die wirksame Allowlist ist `sandbox.network.allowedDomains` **plus** die Domains der `WebFetch(domain:…)`-Allow-Regeln. Wer eine Domain für WebFetch freigibt, öffnet sie auch für Bash.
- **DNS bleibt ein Exfiltrationskanal**, auch mit Domain-Allowlist — ausdrücklich so von Trail of Bits benannt. Eine Egress-Allowlist ist wirksam, aber nicht dicht.
- **VS Code als Sonderfall:** Trail of Bits warnt, dass „Reopen in Container" eine RPC-Brücke öffnet, über die Code aus dem Container **Kommandos auf dem Host** ausführen kann, und empfiehlt für nicht vertrauenswürdigen Code das Terminal statt VS Code.
- **Pfad-Prefix in User-Settings:** `.` löst dort auf `~/.claude` auf, nicht aufs Projekt, und `**/.env` ist an das aktuelle Verzeichnis gebunden. Deshalb `~/` für Home-Pfade und `//` für dateisystemweite Muster: `//**/.env` matcht `.env` überall.
- **Deny ist absolut:** Eine User-`Read`-Deny lässt sich nicht per Projekt-`allow` ausnehmen. In der Sandbox ist das anders — dort ist `allowRead` innerhalb von `denyRead` der vorgesehene Weg.
- **Versionen:** `strictAllowlist` ab v2.1.219; `claude --version` prüfen, `claude doctor` meldet abgelehnte Schlüssel.
- **Wirksamkeit prüfen:** Nach dem Eintragen empirisch abtasten — nur das zeigt die real durchgesetzte Grenze, nicht die Doku. Ein Kommando, das an der Sandbox vorbeilief, trägt den Prompt-Titel „Bash command (unsandboxed)".
- **Kein Sicherheitsbeweis:** Diese Regeln senken die Wahrscheinlichkeit von Fehlzugriffen, sind aber eine client-seitige Steuerung. Die harte Grenze für hohe Risiken bleibt die Struktur: Sandbox **plus** Container/VM mit gefiltertem Egress — wobei auch dort In-Container-Credentials ungeschützt bleiben.

## Quellen

- Claude-Code-Doku: [Sandboxing](https://code.claude.com/docs/en/sandboxing) · [Permissions](https://code.claude.com/docs/en/permissions) · [Settings](https://code.claude.com/docs/en/settings) · [Settings-Referenz](https://code.claude.com/docs/en/settings-reference)
- NVIDIA AI Workbench, [Configure Claude Code Sandboxing in a Project Container](https://docs.nvidia.com/ai-workbench/user-guide/latest/quickstart/quickstart-claude-sandbox.html)
- Trail of Bits, [claude-code-devcontainer](https://github.com/trailofbits/claude-code-devcontainer)
