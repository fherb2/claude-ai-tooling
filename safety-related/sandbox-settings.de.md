# Sandbox- und Werkzeug-Settings: Snippets mit Parameterbeschreibung

*Stand: 2026-09-01 · Alle Angaben gegen die Claude-Code-Doku (code.claude.com/docs/en/sandboxing, .../settings, .../permissions, .../permission-modes) am 1. September 2026 geprüft.*

Ziel dieser Datei: fertige `settings.json`-Snippets zum Übernehmen, und darunter je Parameter **eine Zeile** (Parameter — Beschreibung), damit man die Sandbox-Doku nicht querlesen muss. `settings.json` ist striktes JSON und trägt **keine** Kommentare; deshalb stehen die Erklärungen hier als Listen neben den Blöcken.

## Warum zwei Bereiche

Die Sandbox und die eingebauten Agent-Werkzeuge sind zwei getrennte Wirkungsflächen:

- **Bereich A – Sandbox (`sandbox.*`)** deckt **Bash und alle davon gestarteten Kindprozesse** ab, OS-durchgesetzt (bubblewrap/Seatbelt). Ein `python script.py` über Bash ist damit eingehaust.
- **Bereich B – Agent-Werkzeuge (`permissions.*`)** deckt **Read, Edit, Write, WebFetch** ab. Diese laufen nicht durch die Sandbox, sondern über das Berechtigungssystem. Ohne Bereich B kann der Agent z. B. per Read-Werkzeug jede Datei außerhalb des Projekts lesen — die Sandbox verhindert das nicht.

Die beiden greifen ineinander: `Read`-Deny- und `Edit`-Regeln aus Bereich B fließen zusätzlich in die Dateikonfiguration der Sandbox ein, und `WebFetch(domain:…)`-Regeln in deren Netz-Allowlist. Eine Angabe wirkt dadurch oft auf beiden Flächen.

Alle Blöcke gehören in `~/.claude/settings.json` (User-Settings, gelten für alle Projekte). Für ein Team gehören dieselben Inhalte stattdessen in server-managed settings (claude.ai-Konsole) bzw. per MDM in eine `managed-settings.json`.

---

## Bereich A – Sandbox

### Snippet A1 – Alltag (eigener Projektrechner)

Schließt die per Default offene **Leseseite** für Geheimnisse; Schreiben und Netz bleiben wie im Default (Schreiben nur Projekt+Temp, Netz per Prompt/Klassifikator).

```json
{
  "sandbox": {
    "enabled": true,
    "filesystem": {
      "denyRead": [
        "~/.ssh",
        "~/.aws",
        "~/.gnupg",
        "~/.kube",
        "~/.config/gcloud",
        "~/.docker/config.json",
        "~/.netrc",
        "~/.git-credentials"
      ]
    }
  }
}
```

### Snippet A2 – zusätzlich für unbeaufsichtigten Lauf / fremden Code

Verschärft: harter Abbruch statt fail-open, kein Unsandboxed-Ausweg, Netz als strikte Allowlist.

```json
{
  "sandbox": {
    "enabled": true,
    "failIfUnavailable": true,
    "allowUnsandboxedCommands": false,
    "filesystem": {
      "denyRead": [
        "~/.ssh", "~/.aws", "~/.gnupg", "~/.kube",
        "~/.config/gcloud", "~/.docker/config.json",
        "~/.netrc", "~/.git-credentials"
      ]
    },
    "network": {
      "strictAllowlist": true,
      "allowedDomains": [
        "registry.npmjs.org", "*.npmjs.org",
        "github.com", "*.githubusercontent.com",
        "pypi.org", "files.pythonhosted.org"
      ]
    }
  }
}
```

### Parameter (Bereich A)

- `sandbox.enabled` — schaltet die Bash-Sandbox ein; ohne dieses `true` greift keine der übrigen `sandbox.*`-Angaben.
- `sandbox.failIfUnavailable` — bei `true` bricht Claude Code ab, wenn die Sandbox mangels bubblewrap/socat oder auf unsupported Plattform nicht starten kann, statt (Default) ungeschützt weiterzulaufen (fail-open).
- `sandbox.allowUnsandboxedCommands` — bei `false` („Strict sandbox mode") wird der Ausweg `dangerouslyDisableSandbox` komplett ignoriert; ein Kommando muss dann sandboxbar sein oder in `excludedCommands` stehen. Default `true`.
- `sandbox.autoAllowBashIfSandboxed` — bei `true` (Default) laufen sandboxbare Bash-Kommandos ohne Rückfrage; auf `false` setzen, wenn trotz Sandbox jedes Bash-Kommando einen Prompt bekommen soll.
- `sandbox.filesystem.denyRead` — Liste von Pfaden, die innerhalb der Sandbox **nicht** gelesen werden dürfen (OS-Ebene, gilt auch für Subprozesse). Hier für die Geheimnis-Verzeichnisse; schließt die sonst offene Leseseite.
- `sandbox.filesystem.allowRead` — Gegenstück, um innerhalb eines gesperrten Bereichs einzelne Pfade wieder freizugeben; der speziellere Pfad gewinnt (z. B. `denyRead: ["~/"]` plus `allowRead: ["~/projects"]`).
- `sandbox.filesystem.allowWrite` — erlaubt Schreiben außerhalb der Default-Schreibzone (Arbeitsverzeichnis, `$TMPDIR`), falls ein Subprozess wie `terraform`/`npm` an einen festen Ort schreiben muss.
- `sandbox.filesystem.denyWrite` — sperrt Schreiben in einzelnen Pfaden innerhalb der erlaubten Zone.
- `sandbox.filesystem.disabled` — schaltet die **Datei**-Isolation ganz ab und behält nur die Netz-Isolation; nur für Workloads setzen, denen man Selbst-Rechteausweitung nicht zutraut (Default aus lassen).
- `sandbox.network.allowedDomains` — Domain-Allowlist für ausgehenden Verkehr aus der Sandbox; leer = kein Netz. Erste Verbindung zu einer nicht gelisteten Domain löst sonst Prompt/Klassifikator aus. So eng wie möglich halten.
- `sandbox.network.strictAllowlist` — bei `true` werden nicht gelistete Hosts **abgewiesen** statt nachgefragt; wirkt nur aus User-/Managed-/CLI-Settings, nicht aus Repo-Dateien.
- `sandbox.network.deniedDomains` — Blocklist mit Vorrang, um einzelne Hosts sicher auszuschließen, auch wenn sie sonst zugelassen wären.
- `sandbox.network.tlsTerminate` — der Proxy terminiert TLS selbst (nötig für Credential-Masking mit `injectHosts`); fortgeschritten, löst im Team-Fall einen Freigabedialog aus.
- `sandbox.credentials` — deklariert Geheimnis-Dateien/-Variablen zum Schutz vor sandboxed Kommandos: `mode: "deny"` sperrt sie (Datei-Read verweigert, Env-Variable entfernt), `mode: "mask"` zeigt dem Kommando nur einen Platzhalter, den der Proxy erst Richtung erlaubter `injectHosts` durch den echten Wert ersetzt. Ein reiner `deny`-Block braucht im Team-Fall keine Nutzerfreigabe, ein `mask`-Block schon.

---

## Bereich B – Agent-Werkzeuge (`permissions.*`)

Deckt Read/Edit/Write/WebFetch ab. Die `Read`-Deny-Regeln hier verdoppeln bewusst die `denyRead`-Pfade aus Bereich A: Bereich A fängt den Bash-/Subprozess-Zugriff, Bereich B das Read-Werkzeug des Agenten — erst beide zusammen schließen einen Geheimnis-Pfad vollständig.

### Snippet B1

```json
{
  "permissions": {
    "disableBypassPermissionsMode": "disable",
    "deny": [
      "Read(~/.ssh/**)",
      "Read(~/.aws/**)",
      "Read(~/.gnupg/**)",
      "Read(~/.kube/**)",
      "Read(~/.config/gcloud/**)",
      "Read(~/.docker/config.json)",
      "Read(~/.netrc)",
      "Read(~/.git-credentials)",
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

### Parameter (Bereich B)

- `permissions.disableBypassPermissionsMode` — Wert `"disable"` sperrt den Modus `--dangerously-skip-permissions`; wirkt aus jedem Scope, auch aus User-Settings, und taugt so als Selbstschutz gegen ein versehentliches Aushebeln aller Regeln.
- `permissions.deny` — Liste harter Verbote, zuerst ausgewertet und durch keine andere Ebene aufhebbar. `Read(<pfad>)` sperrt das Read-Werkzeug (und speist zugleich die Sandbox-`denyRead`); `Bash(<cmd> *)` sperrt ein Kommando (fragil gegen Umgehung — nur als Defense-in-depth, nicht als alleinige Grenze).
- `permissions.ask` — wie `deny`, aber statt zu blocken wird nachgefragt; für Fälle, die man einzeln entscheiden will statt pauschal zu verbieten.
- `permissions.allow` — Vorab-Freigaben ohne Rückfrage; greift erst, nachdem der Ordner „getrusted" ist. Hier trägt es die `WebFetch(domain:…)`-Regeln.
- `WebFetch(domain:<host>)` — als `allow`-Eintrag: erlaubt dem WebFetch-Werkzeug diesen Host **und** öffnet ihn in der Sandbox-Netz-Allowlist. Eine Angabe, zwei Wirkungen; ersetzt für erlaubte Ziele das Roh-`curl` über Bash.
- `permissions.additionalDirectories` — zusätzliche Verzeichnisse, die als Arbeitsbereich gelten; erweitert zugleich die Schreibzone der Sandbox. Nur setzen, wenn der Agent bewusst außerhalb des Projektordners arbeiten soll.

---

## Komplettblock für einen Solo-Rechner

Bereich A1 und Bereich B zusammengeführt zu einer `~/.claude/settings.json` (Alltagsvariante). Für unbeaufsichtigten Betrieb die drei Zusatzschlüssel aus A2 (`failIfUnavailable`, `allowUnsandboxedCommands`, `network`) ergänzen.

```json
{
  "sandbox": {
    "enabled": true,
    "filesystem": {
      "denyRead": [
        "~/.ssh", "~/.aws", "~/.gnupg", "~/.kube",
        "~/.config/gcloud", "~/.docker/config.json",
        "~/.netrc", "~/.git-credentials"
      ]
    }
  },
  "permissions": {
    "disableBypassPermissionsMode": "disable",
    "deny": [
      "Read(~/.ssh/**)", "Read(~/.aws/**)", "Read(~/.gnupg/**)",
      "Read(~/.kube/**)", "Read(~/.config/gcloud/**)",
      "Read(~/.docker/config.json)", "Read(~/.netrc)",
      "Read(~/.git-credentials)", "Read(//**/.env)", "Read(//**/.env.*)"
    ],
    "allow": [
      "WebFetch(domain:github.com)",
      "WebFetch(domain:docs.claude.com)"
    ]
  }
}
```

---

## Hinweise vor dem Übernehmen

- **Versionen:** `sandbox.filesystem.denyRead` und `sandbox.network.strictAllowlist` brauchen neuere Claude-Code-Versionen (strictAllowlist ab v2.1.219). `claude --version` prüfen; abgelehnte Schlüssel meldet `claude doctor`.
- **Pfad-Prefix in User-Settings:** In `~/.claude/settings.json` löst ein `.`-Pfad auf `~/.claude` auf, nicht aufs Projekt, und ein Muster wie `**/.env` ist an das aktuelle Verzeichnis gebunden — es greift damit nicht in jedem Projekt. Deshalb hier durchgängig `~/` für Home-Pfade und `//` für dateisystemweite Muster: `//**/.env` matcht `.env` überall.
- **Deny ist absolut:** Eine User-`Read`-Deny lässt sich nicht per Projekt-`allow` ausnehmen (deny gewinnt immer). Braucht ein einzelnes Projekt Lesezugriff auf z. B. eine Beispiel-`.env`, die User-Deny enger fassen.
- **Wirksamkeit prüfen:** Nach dem Eintragen empirisch abtasten (Lesen außerhalb des Projekts, Schreiben in `/etc`, Netz zu nicht gelistetem Host) — nur das zeigt die real durchgesetzte Grenze, nicht die Doku. Ein Kommando, das an der Sandbox vorbeilief, trägt den Prompt-Titel „Bash command (unsandboxed)".
- **Kein Sicherheitsbeweis:** Diese Regeln senken die Wahrscheinlichkeit von Fehlzugriffen, sind aber eine client-seitige Steuerung, keine unüberwindbare Grenze. Die harte Grenze für hohe Risiken bleibt die Struktur: Sandbox aktiviert **plus** Container/VM mit gefiltertem Egress.
