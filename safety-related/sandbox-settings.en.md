# Sandbox and tool settings: snippets with per-parameter notes

*Last updated: 2026-09-01 · All statements verified against the Claude Code docs (code.claude.com/docs/en/sandboxing, .../settings, .../permissions, .../permission-modes) on 1 September 2026.*

**Scope:** Linux and macOS; on Windows only through WSL2 — the sandbox does not run natively there, and paths would be written differently (`//c/**/.env` instead of `//**/.env`). The one documented macOS deviation concerns credential *masking*: there macOS blocks the file instead of substituting the value; the plain `deny` rules used here are unaffected.

Purpose of this file: ready-to-paste `settings.json` snippets, and beneath them **one line per parameter** (parameter — description), so you need not read through the whole sandbox documentation. `settings.json` is strict JSON and carries **no** comments; that is why the explanations live here as lists next to the blocks.

## What secures what

Before writing rules, it is worth asking what is actually still open. Three layers — and only the third needs a rule:

- **Writing: the sandbox default.** The write side is an allowlist — only the working directory, the session temp directory and explicitly added directories are permitted; **everything else is blocked**, without anyone having to enumerate it. `/etc`, `/usr`, other projects, the home root: closed.
- **Other people's data: the operating system.** Claude Code runs with the user's rights, no more. Root-owned files and other users' home directories are already out of reach through the file permissions; a rule adds nothing there.
- **Your own data when read: here, and only here, a rule is needed.** The sandbox's read default is open (apart from a few engine paths) — and practically all secrets live in the home directory.

## Why a deny list does not carry here

The obvious move would be to enumerate the known secret paths: `~/.ssh`, `~/.aws` and so on. That does not carry. Thunderbird holds mail accounts along with their passwords, browser profiles hold session cookies, and then there are password managers, wallets, VPN configurations, editors' credential stores, `~/.config/<anything>` — and tomorrow software gets installed that nobody has on their list today. Such a list is **already incomplete as it is written**, and it goes stale with every installation.

What does carry is the **inversion**: block the home directory and release what the work needs. "Enumerate every secret" (unbounded, going stale) becomes "enumerate what is needed" (small, stable) — and a mistake there **shows**, because a command fails instead of leaking silently.

System paths stay open in this, and rightly so: `/usr`, `/lib`, certificates and locale data are needed by every command and hold no user secrets.

## The two enforcement surfaces

The sandbox and the agent tools are separate, and both need a rule:

- **Area A – Sandbox (`sandbox.*`)** covers **Bash and every child process it spawns**, OS-enforced (bubblewrap/Seatbelt). A `python script.py` run through Bash is thereby boxed in.
- **Area B – Agent tools (`permissions.*`)** covers **Read, Edit, Write, WebFetch**. These do not run through the sandbox but through the permission system.

The two interlock: `Read` deny rules and `Edit` rules from Area B additionally feed the sandbox's filesystem configuration, and `WebFetch(domain:…)` rules feed its network allowlist. A single entry therefore often takes effect on both surfaces.

All blocks belong in `~/.claude/settings.json` (user settings, applying to every project). For a team, the same content goes instead into server-managed settings (claude.ai console) or, via MDM, into a `managed-settings.json`.

---

## Area A – Sandbox

### Snippet A1 – the recommended base form: home closed, work open

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

Replace `~/git` with wherever your own projects live. The more specific path wins, so this one pair is enough: the home directory is blocked, the work area open again, and everything else in the home — Thunderbird, browser profiles, password managers, whatever else arrives later — stays closed without ever having been enumerated.

**Plan for a run-in phase.** Some things in the home are read legitimately: `~/.gitconfig`, package caches, toolchains such as `~/.cargo`, `~/.rustup`, `~/.nvm`, `~/.pyenv`. The inversion blocks those too, and commands fail until the path is listed in `allowRead`. That visibility is the point: run it, read off the failing path, add it. Which paths you need depends on your own toolbox.

**Mind the anchor rule.** In user settings a `.` path resolves to `~/.claude`, not to the project — hence the `~/` path above rather than `.`. If you would rather release per project, put the `allowRead` into the **project's** `.claude/settings.json`; only there does `.` point at the project root.

### Snippet A2 – minimal variant, if you do not want to invert

Blocks only the best-known secret paths. **Weaker than A1**, because it misses everything not on the list — usable as a start, not as a destination.

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

### Snippet A3 – additionally for unattended runs / untrusted code

Hardened: a hard abort instead of fail-open, no unsandboxed escape, network as a strict allowlist.

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

### Parameters (Area A)

- `sandbox.enabled` — turns the Bash sandbox on; without this `true`, none of the other `sandbox.*` entries take effect.
- `sandbox.failIfUnavailable` — with `true`, Claude Code aborts when the sandbox cannot start (missing bubblewrap/socat, or an unsupported platform) instead of (default) running on unprotected (fail-open).
- `sandbox.allowUnsandboxedCommands` — with `false` ("strict sandbox mode") the `dangerouslyDisableSandbox` escape is ignored entirely; a command must then be sandboxable or be listed in `excludedCommands`. Default `true`.
- `sandbox.autoAllowBashIfSandboxed` — with `true` (default), sandboxable Bash commands run without a prompt; set it to `false` to make every Bash command prompt even under the sandbox.
- `sandbox.filesystem.denyRead` — paths that must **not** be read inside the sandbox (OS level, applies to child processes too). In the base form this is the whole home directory.
- `sandbox.filesystem.allowRead` — releases individual paths again inside a denied region; **the more specific path wins**. This is the key to the inversion.
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

Covers Read/Edit/Write/WebFetch. Two things differ here from Area A:

**A boundary already exists.** For read-only tools the documentation states that no approval is required "within the working directory and additional directories" — outside it, therefore, one **is** required. In Manual mode Claude asks there; in auto mode the classifier decides at that boundary instead of the user.

**The inversion does not work here.** Under `permissions`, `deny` always wins and cannot be re-opened by any `allow`. A `Read(~/**)` deny could therefore not be carved out per project. What remains is a targeted block on the most valuable paths — deliberately incomplete, as a supplement to the working-directory boundary rather than a replacement for it.

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

### Parameters (Area B)

- `permissions.disableBypassPermissionsMode` — the value `"disable"` blocks the `--dangerously-skip-permissions` mode; takes effect from any scope, including user settings, and thus serves as self-protection against accidentally disabling all rules.
- `permissions.deny` — list of hard prohibitions, evaluated first and not overridable by any other level. `Read(<path>)` blocks the Read tool (and at the same time feeds the sandbox `denyRead`); `Bash(<cmd> *)` blocks a command (fragile against circumvention — only as defense in depth, not as the sole boundary).
- `permissions.ask` — like `deny`, but prompts instead of blocking. Particularly useful as `Bash(dangerouslyDisableSandbox:true)`: auto mode then stays in force everywhere, and only the single event "leaving the sandbox" is put to the user.
- `permissions.allow` — pre-approvals without a prompt; takes effect only after the folder is "trusted". Here it carries the `WebFetch(domain:…)` rules.
- `WebFetch(domain:<host>)` — as an `allow` entry: permits the WebFetch tool to reach this host **and** opens it in the sandbox network allowlist. One entry, two effects; replaces raw `curl` over Bash for allowed targets.
- `permissions.additionalDirectories` — additional directories that count as workspace; also extends the sandbox's write zone. Set only when the agent should deliberately work outside the project folder.

---

## One combined block for a solo machine

Base form A1 and Area B merged into a single `~/.claude/settings.json`. For unattended operation, add the three extra keys from A3 (`failIfUnavailable`, `allowUnsandboxedCommands`, `network`).

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

## Notes before you adopt this

- **The network lists add up.** The sandbox's effective allowlist is `sandbox.network.allowedDomains` **plus** the domains from the `WebFetch(domain:…)` allow rules. A domain may therefore appear in both blocks — that is intentional, so each block stays usable on its own, and it does no harm. Read the other way round: whoever releases a domain for WebFetch opens it for Bash as well.
- **Versions:** `sandbox.filesystem.denyRead`/`allowRead` and `sandbox.network.strictAllowlist` require newer Claude Code versions (strictAllowlist from v2.1.219). Check `claude --version`; `claude doctor` reports rejected keys.
- **Path prefix in user settings:** in `~/.claude/settings.json` a `.` path resolves to `~/.claude`, not to the project, and a pattern such as `**/.env` is anchored to the current directory — so it does not apply in every project. That is why `~/` is used throughout for home paths and `//` for filesystem-wide patterns: `//**/.env` matches `.env` anywhere.
- **Deny is absolute:** a user-level `Read` deny cannot be carved out by a project `allow` (deny always wins). If a single project needs read access to, say, a sample `.env`, narrow the user deny. In the sandbox this is different — there, `allowRead` inside `denyRead` is exactly the intended route.
- **Verify effectiveness:** after entering it, probe empirically (reading in the home outside the work area, writing to `/etc`, network to a non-listed host) — only that shows the boundary actually enforced, not the docs. A command that ran past the sandbox carries the prompt title "Bash command (unsandboxed)".
- **No security proof:** these rules lower the probability of misaccess but are a client-side control, not an insurmountable boundary. The hard boundary for high risk remains the structure: sandbox enabled **plus** container/VM with filtered egress.
