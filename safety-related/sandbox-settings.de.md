# Sandbox- und Werkzeug-Settings: Snippets mit Parameterbeschreibung

*Stand: 2026-09-01 · Alle Angaben gegen die Claude-Code-Doku (code.claude.com/docs/en/sandboxing, .../settings, .../permissions, .../permission-modes) am 1. September 2026 geprüft.*

**Geltungsbereich:** Linux und macOS; unter Windows nur über WSL2 — nativ läuft die Sandbox dort nicht, und Pfade würden anders geschrieben (`//c/**/.env` statt `//**/.env`). Einzige dokumentierte macOS-Abweichung: Beim Credential-*Masking* blockt macOS die Datei, statt den Wert zu ersetzen; die reinen `deny`-Regeln hier sind davon nicht betroffen.

Ziel dieser Datei: fertige `settings.json`-Snippets zum Übernehmen, und darunter je Parameter **eine Zeile** (Parameter — Beschreibung), damit man die Sandbox-Doku nicht querlesen muss. `settings.json` ist striktes JSON und trägt **keine** Kommentare; deshalb stehen die Erklärungen hier als Listen neben den Blöcken.

## Wer was sichert

Bevor man Regeln schreibt, lohnt die Frage, was überhaupt noch offen ist. Drei Schichten — und nur die dritte braucht eine Regel:

- **Schreibzugriffe: der Sandbox-Default.** Die Schreibseite ist eine Allowlist — erlaubt sind nur Arbeitsverzeichnis, Session-Temp und ausdrücklich hinzugefügte Verzeichnisse; **alles andere ist gesperrt**, ohne dass es jemand aufzählen müsste. `/etc`, `/usr`, fremde Projekte, die Home-Wurzel: zu.
- **Fremde Daten: das Betriebssystem.** Claude Code läuft mit den Rechten des Nutzers, nicht mehr. Root-eigene Dateien und fremde Home-Verzeichnisse sind schon durch die Dateirechte unerreichbar; eine Regel fügt dort nichts hinzu.
- **Die eigenen Daten beim Lesen: hier, und nur hier, braucht es eine Regel.** Der Lese-Default der Sandbox ist offen (bis auf wenige Engine-Pfade) — und im Home liegen praktisch alle Geheimnisse.

## Warum eine Sperrliste hier nicht trägt

Naheliegend wäre, die bekannten Geheimnis-Pfade aufzuzählen: `~/.ssh`, `~/.aws` und so weiter. Das trägt nicht. Thunderbird hält Mailkonten samt Passwörtern, Browserprofile halten Sitzungs-Cookies, dazu kommen Passwortmanager, Wallets, VPN-Konfigurationen, Credential-Stores von Editoren, `~/.config/<beliebig>` — und morgen wird Software installiert, die heute niemand auf dem Zettel hat. Eine solche Liste ist **schon beim Schreiben unvollständig** und veraltet mit jeder Installation.

Tragfähig ist die **Umkehrung**: das Home sperren und freigeben, was die Arbeit braucht. Aus „jedes Geheimnis aufzählen" (unbegrenzt, veraltend) wird „aufzählen, was gebraucht wird" (klein, stabil) — und ein Fehler dabei **fällt auf**, weil ein Kommando scheitert, statt still zu lecken.

Die Systempfade bleiben dabei offen, und das ist richtig: `/usr`, `/lib`, Zertifikate und Locale werden von jedem Kommando gebraucht und enthalten keine Nutzergeheimnisse.

## Die zwei Wirkungsflächen

Sandbox und Agent-Werkzeuge sind getrennt, und beide brauchen eine Regel:

- **Bereich A – Sandbox (`sandbox.*`)** deckt **Bash und alle davon gestarteten Kindprozesse** ab, OS-durchgesetzt (bubblewrap/Seatbelt). Ein `python script.py` über Bash ist damit eingehaust.
- **Bereich B – Agent-Werkzeuge (`permissions.*`)** deckt **Read, Edit, Write, WebFetch** ab. Diese laufen nicht durch die Sandbox, sondern über das Berechtigungssystem.

Die beiden greifen ineinander: `Read`-Deny- und `Edit`-Regeln aus Bereich B fließen zusätzlich in die Dateikonfiguration der Sandbox ein, und `WebFetch(domain:…)`-Regeln in deren Netz-Allowlist. Eine Angabe wirkt dadurch oft auf beiden Flächen.

Alle Blöcke gehören in `~/.claude/settings.json` (User-Settings, gelten für alle Projekte). Für ein Team gehören dieselben Inhalte stattdessen in server-managed settings (claude.ai-Konsole) bzw. per MDM in eine `managed-settings.json`.

---

## Bereich A – Sandbox

### Snippet A1 – die empfohlene Grundform: Home zu, Arbeit auf

```json
{
  "sandbox": {
    "enabled": true,
    "filesystem": {
      "denyRead": ["~/"],
      "allowRead": ["~/git"]
    }
  }
}
```

`~/git` durch den Ort ersetzen, an dem die eigenen Projekte liegen. Der speziellere Pfad gewinnt, deshalb genügt das eine Paar: Das Home ist gesperrt, der Arbeitsbereich wieder offen, alles Übrige im Home — Thunderbird, Browserprofile, Passwortmanager, was auch immer noch dazukommt — bleibt zu, ohne je aufgezählt worden zu sein.

**Einlaufphase einplanen.** Manches im Home wird legitim gelesen: `~/.gitconfig`, Paket-Caches, Toolchains wie `~/.cargo`, `~/.rustup`, `~/.nvm`, `~/.pyenv`. Die sperrt die Umkehrung mit, und Kommandos scheitern, bis der Pfad in `allowRead` steht. Das ist gewollt sichtbar: laufen lassen, den gescheiterten Pfad ablesen, ergänzen. Welche Pfade nötig sind, hängt vom eigenen Werkzeugkasten ab.

**Ankerregel beachten.** In User-Settings löst `.` auf `~/.claude` auf, nicht aufs Projekt — deshalb oben ein `~/`-Pfad statt `.`. Wer stattdessen projektweise freigeben will, legt das `allowRead` in die **Projekt**-`.claude/settings.json`; nur dort zeigt `.` auf die Projektwurzel.

### Snippet A2 – Minimalvariante, wenn nicht umgekehrt werden soll

Sperrt nur die bekanntesten Geheimnis-Pfade. **Schwächer als A1**, weil sie alles übersieht, was nicht auf der Liste steht — als Einstieg brauchbar, nicht als Ziel.

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
        "~/.config",
        "~/.local/share",
        "~/.mozilla",
        "~/.thunderbird",
        "~/.netrc",
        "~/.npmrc",
        "~/.pypirc",
        "~/.git-credentials",
        "~/.password-store"
      ]
    }
  }
}
```

### Snippet A3 – zusätzlich für unbeaufsichtigten Lauf / fremden Code

Verschärft: harter Abbruch statt fail-open, kein Unsandboxed-Ausweg, Netz als strikte Allowlist.

```json
{
  "sandbox": {
    "enabled": true,
    "failIfUnavailable": true,
    "allowUnsandboxedCommands": false,
    "filesystem": {
      "denyRead": ["~/"],
      "allowRead": ["~/git"]
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
- `sandbox.filesystem.denyRead` — Pfade, die innerhalb der Sandbox **nicht** gelesen werden dürfen (OS-Ebene, gilt auch für Subprozesse). In der Grundform steht hier das ganze Home.
- `sandbox.filesystem.allowRead` — gibt einzelne Pfade innerhalb eines gesperrten Bereichs wieder frei; **der speziellere Pfad gewinnt**. Das ist der Schlüssel zur Umkehrung.
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

Deckt Read/Edit/Write/WebFetch ab. Zwei Dinge sind hier anders als in Bereich A:

**Es gibt schon eine Grenze.** Für lesende Werkzeuge ist laut Doku keine Zustimmung nötig „within the working directory and additional directories" — außerhalb also **schon**. Im Manual-Modus fragt Claude dort nach; im Auto-Modus entscheidet an dieser Grenze der Klassifikator statt des Nutzers.

**Die Umkehrung funktioniert hier nicht.** Bei `permissions` gewinnt `deny` immer und lässt sich durch kein `allow` wieder aufmachen. Ein `Read(~/**)`-Deny wäre deshalb nicht projektweise ausnehmbar. Was bleibt, ist eine gezielte Sperre der wertvollsten Pfade — bewusst unvollständig, als Ergänzung zur Arbeitsverzeichnis-Grenze, nicht als deren Ersatz.

### Snippet B1

```json
{
  "permissions": {
    "disableBypassPermissionsMode": "disable",
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

### Parameter (Bereich B)

- `permissions.disableBypassPermissionsMode` — Wert `"disable"` sperrt den Modus `--dangerously-skip-permissions`; wirkt aus jedem Scope, auch aus User-Settings, und taugt so als Selbstschutz gegen ein versehentliches Aushebeln aller Regeln.
- `permissions.deny` — Liste harter Verbote, zuerst ausgewertet und durch keine andere Ebene aufhebbar. `Read(<pfad>)` sperrt das Read-Werkzeug (und speist zugleich die Sandbox-`denyRead`); `Bash(<cmd> *)` sperrt ein Kommando (fragil gegen Umgehung — nur als Defense-in-depth, nicht als alleinige Grenze).
- `permissions.ask` — wie `deny`, aber statt zu blocken wird nachgefragt. Besonders nützlich als `Bash(dangerouslyDisableSandbox:true)`: Dann bleibt der Auto-Modus überall erhalten, und nur das eine Ereignis „raus aus der Sandbox" wird dem Nutzer vorgelegt.
- `permissions.allow` — Vorab-Freigaben ohne Rückfrage; greift erst, nachdem der Ordner „getrusted" ist. Hier trägt es die `WebFetch(domain:…)`-Regeln.
- `WebFetch(domain:<host>)` — als `allow`-Eintrag: erlaubt dem WebFetch-Werkzeug diesen Host **und** öffnet ihn in der Sandbox-Netz-Allowlist. Eine Angabe, zwei Wirkungen; ersetzt für erlaubte Ziele das Roh-`curl` über Bash.
- `permissions.additionalDirectories` — zusätzliche Verzeichnisse, die als Arbeitsbereich gelten; erweitert zugleich die Schreibzone der Sandbox. Nur setzen, wenn der Agent bewusst außerhalb des Projektordners arbeiten soll.

---

## Komplettblock für einen Solo-Rechner

Grundform A1 und Bereich B zusammengeführt zu einer `~/.claude/settings.json`. Für unbeaufsichtigten Betrieb die drei Zusatzschlüssel aus A3 (`failIfUnavailable`, `allowUnsandboxedCommands`, `network`) ergänzen.

```json
{
  "sandbox": {
    "enabled": true,
    "filesystem": {
      "denyRead": ["~/"],
      "allowRead": ["~/git"]
    }
  },
  "permissions": {
    "disableBypassPermissionsMode": "disable",
    "ask": [
      "Bash(dangerouslyDisableSandbox:true)"
    ],
    "deny": [
      "Read(~/.ssh/**)", "Read(~/.aws/**)", "Read(~/.gnupg/**)",
      "Read(~/.netrc)", "Read(~/.npmrc)", "Read(~/.git-credentials)",
      "Read(~/.password-store/**)", "Read(//**/.env)", "Read(//**/.env.*)"
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

- **Die Netzlisten addieren sich.** Die wirksame Allowlist der Sandbox ist `sandbox.network.allowedDomains` **plus** die Domains aus den `WebFetch(domain:…)`-Allow-Regeln. Eine Domain kann deshalb in beiden Blöcken stehen — das ist gewollt, damit jeder Block für sich kopierbar bleibt, und schadet nicht. Umgekehrt heißt es: Wer eine Domain für WebFetch freigibt, öffnet sie auch für Bash.
- **Versionen:** `sandbox.filesystem.denyRead`/`allowRead` und `sandbox.network.strictAllowlist` brauchen neuere Claude-Code-Versionen (strictAllowlist ab v2.1.219). `claude --version` prüfen; abgelehnte Schlüssel meldet `claude doctor`.
- **Pfad-Prefix in User-Settings:** In `~/.claude/settings.json` löst ein `.`-Pfad auf `~/.claude` auf, nicht aufs Projekt, und ein Muster wie `**/.env` ist an das aktuelle Verzeichnis gebunden — es greift damit nicht in jedem Projekt. Deshalb hier durchgängig `~/` für Home-Pfade und `//` für dateisystemweite Muster: `//**/.env` matcht `.env` überall.
- **Deny ist absolut:** Eine User-`Read`-Deny lässt sich nicht per Projekt-`allow` ausnehmen (deny gewinnt immer). Braucht ein einzelnes Projekt Lesezugriff auf z. B. eine Beispiel-`.env`, die User-Deny enger fassen. In der Sandbox ist das anders — dort ist `allowRead` innerhalb von `denyRead` genau der vorgesehene Weg.
- **Wirksamkeit prüfen:** Nach dem Eintragen empirisch abtasten (Lesen im Home außerhalb des Arbeitsbereichs, Schreiben in `/etc`, Netz zu nicht gelistetem Host) — nur das zeigt die real durchgesetzte Grenze, nicht die Doku. Ein Kommando, das an der Sandbox vorbeilief, trägt den Prompt-Titel „Bash command (unsandboxed)".
- **Kein Sicherheitsbeweis:** Diese Regeln senken die Wahrscheinlichkeit von Fehlzugriffen, sind aber eine client-seitige Steuerung, keine unüberwindbare Grenze. Die harte Grenze für hohe Risiken bleibt die Struktur: Sandbox aktiviert **plus** Container/VM mit gefiltertem Egress.
