# Sandbox and tool settings: snippets with per-parameter notes

*Last updated: 2026-09-01 · All statements verified against the Claude Code docs (code.claude.com/docs/en/sandboxing, .../settings, .../permissions, .../permission-modes) on 1 September 2026.*

Purpose of this file: ready-to-paste `settings.json` snippets, and beneath them **one line per parameter** (parameter — description), so you need not read through the whole sandbox documentation. `settings.json` is strict JSON and carries **no** comments; that is why the explanations live here as lists next to the blocks.

## Why two areas

The sandbox and the built-in agent tools are two separate enforcement surfaces:

- **Area A – Sandbox (`sandbox.*`)** covers **Bash and every child process it spawns**, OS-enforced (bubblewrap/Seatbelt). A `python script.py` run through Bash is thereby boxed in.
- **Area B – Agent tools (`permissions.*`)** covers **Read, Edit, Write, WebFetch**. These do not run through the sandbox but through the permission system. Without Area B the agent can, for example, read any file outside the project with the Read tool — the sandbox does not prevent that.

The two interlock: `Read` deny rules and `Edit` rules from Area B additionally feed the sandbox's filesystem configuration, and `WebFetch(domain:…)` rules feed its network allowlist. A single entry therefore often takes effect on both surfaces.

All blocks belong in `~/.claude/settings.json` (user settings, applying to every project). For a team, the same content goes instead into server-managed settings (claude.ai console) or, via MDM, into a `managed-settings.json`.

---

## Area A – Sandbox

### Snippet A1 – everyday use (your own project machine)

Closes the read side for secrets, which is open by default; writing and network stay at their defaults (writing only to project + temp, network by prompt/classifier).

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

### Snippet A2 – additionally for unattended runs / untrusted code

Hardened: a hard abort instead of fail-open, no unsandboxed escape, network as a strict allowlist.

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

### Parameters (Area A)

- `sandbox.enabled` — turns the Bash sandbox on; without this `true`, none of the other `sandbox.*` entries take effect.
- `sandbox.failIfUnavailable` — with `true`, Claude Code aborts when the sandbox cannot start (missing bubblewrap/socat, or an unsupported platform) instead of (default) running on unprotected (fail-open).
- `sandbox.allowUnsandboxedCommands` — with `false` ("strict sandbox mode") the `dangerouslyDisableSandbox` escape is ignored entirely; a command must then be sandboxable or be listed in `excludedCommands`. Default `true`.
- `sandbox.autoAllowBashIfSandboxed` — with `true` (default), sandboxable Bash commands run without a prompt; set it to `false` to make every Bash command prompt even under the sandbox.
- `sandbox.filesystem.denyRead` — list of paths that must **not** be read inside the sandbox (OS level, applies to child processes too). Used here for the secret directories; closes the otherwise-open read side.
- `sandbox.filesystem.allowRead` — its counterpart, to re-open individual paths inside a denied region; the more specific path wins (e.g. `denyRead: ["~/"]` plus `allowRead: ["~/projects"]`).
- `sandbox.filesystem.allowWrite` — allows writing outside the default write zone (working directory, `$TMPDIR`), in case a subprocess such as `terraform`/`npm` must write to a fixed location.
- `sandbox.filesystem.denyWrite` — blocks writing to individual paths inside the allowed zone.
- `sandbox.filesystem.disabled` — turns **file** isolation off entirely and keeps only network isolation; set it only for workloads you trust not to escalate their own access (leave off by default).
- `sandbox.network.allowedDomains` — domain allowlist for outbound traffic from the sandbox; empty = no network. Otherwise the first connection to a non-listed domain triggers a prompt/classifier. Keep it as narrow as possible.
- `sandbox.network.strictAllowlist` — with `true`, non-listed hosts are **denied** instead of prompted; takes effect only from user/managed/CLI settings, not from repo files.
- `sandbox.network.deniedDomains` — a blocklist with precedence, to reliably exclude individual hosts even when they would otherwise be allowed.
- `sandbox.network.tlsTerminate` — the proxy terminates TLS itself (required for credential masking with `injectHosts`); advanced, triggers an approval dialog in the team case.
- `sandbox.credentials` — declares secret files/variables to protect from sandboxed commands: `mode: "deny"` blocks them (file read refused, env variable removed), `mode: "mask"` shows the command only a placeholder that the proxy substitutes with the real value only toward the allowed `injectHosts`. A pure `deny` block needs no user approval in the team case, a `mask` block does.

---

## Area B – Agent tools (`permissions.*`)

Covers Read/Edit/Write/WebFetch. The `Read` deny rules here deliberately duplicate the `denyRead` paths from Area A: Area A catches Bash/subprocess access, Area B the agent's Read tool — only both together fully close a secret path.

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

### Parameters (Area B)

- `permissions.disableBypassPermissionsMode` — the value `"disable"` blocks the `--dangerously-skip-permissions` mode; takes effect from any scope, including user settings, and thus serves as self-protection against accidentally disabling all rules.
- `permissions.deny` — list of hard prohibitions, evaluated first and not overridable by any other level. `Read(<path>)` blocks the Read tool (and at the same time feeds the sandbox `denyRead`); `Bash(<cmd> *)` blocks a command (fragile against circumvention — only as defense in depth, not as the sole boundary).
- `permissions.ask` — like `deny`, but prompts instead of blocking; for cases you want to decide individually rather than forbid wholesale.
- `permissions.allow` — pre-approvals without a prompt; takes effect only after the folder is "trusted". Here it carries the `WebFetch(domain:…)` rules.
- `WebFetch(domain:<host>)` — as an `allow` entry: permits the WebFetch tool to reach this host **and** opens it in the sandbox network allowlist. One entry, two effects; replaces raw `curl` over Bash for allowed targets.
- `permissions.additionalDirectories` — additional directories that count as workspace; also extends the sandbox's write zone. Set only when the agent should deliberately work outside the project folder.

---

## One combined block for a solo machine

Area A1 and Area B merged into a single `~/.claude/settings.json` (everyday variant). For unattended operation, add the three extra keys from A2 (`failIfUnavailable`, `allowUnsandboxedCommands`, `network`).

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

## Notes before you adopt this

- **Versions:** `sandbox.filesystem.denyRead` and `sandbox.network.strictAllowlist` require newer Claude Code versions (strictAllowlist from v2.1.219). Check `claude --version`; `claude doctor` reports rejected keys.
- **Path prefix in user settings:** in `~/.claude/settings.json` a `.` path resolves to `~/.claude`, not to the project, and a pattern such as `**/.env` is anchored to the current directory — so it does not apply in every project. That is why `~/` is used throughout for home paths and `//` for filesystem-wide patterns: `//**/.env` matches `.env` anywhere.
- **Deny is absolute:** a user-level `Read` deny cannot be carved out by a project `allow` (deny always wins). If a single project needs read access to, say, a sample `.env`, narrow the user deny.
- **Verify effectiveness:** after entering it, probe empirically (reading outside the project, writing to `/etc`, network to a non-listed host) — only that shows the boundary actually enforced, not the docs. A command that ran past the sandbox carries the prompt title "Bash command (unsandboxed)".
- **No security proof:** these rules lower the probability of misaccess but are a client-side control, not an insurmountable boundary. The hard boundary for high risk remains the structure: sandbox enabled **plus** container/VM with filtered egress.
