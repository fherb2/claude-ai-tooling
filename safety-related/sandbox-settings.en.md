# Sandbox and tool settings: snippets with per-parameter notes

*Last updated: 2026-09-01 · All statements verified against the Claude Code docs (code.claude.com/docs/en/sandboxing, .../settings, .../permissions, .../permission-modes) on 1 September 2026.*

**Scope:** Linux and macOS; on Windows only through WSL2 — the sandbox does not run natively there, and paths would be written differently (`//c/**/.env` instead of `//**/.env`). The one documented macOS deviation concerns credential *masking*: there macOS blocks the file instead of substituting the value; plain `deny` rules are unaffected.

Purpose of this file: ready-to-paste `settings.json` snippets, and beneath them **one line per parameter** (parameter — description), so you need not read through the whole sandbox documentation. `settings.json` is strict JSON and carries **no** comments; that is why the explanations live here as lists next to the blocks.

**Each block states where it comes from:** *[Docs]* = verbatim from Anthropic's examples, *[NVIDIA]* = from the vendor reference configuration for containers, *[adapted]* = derived from those, *[untested]* = not tried out here. Sources at the end.

## What secures what

Before writing rules, it is worth asking what is actually still open. Four layers — and only the last two need a rule:

- **Writing: the sandbox default.** The write side is an allowlist — only the working directory, the session temp directory and explicitly added directories are permitted; **everything else is blocked**, without anyone having to enumerate it. `/etc`, `/usr`, other projects: closed.
- **Other people's data: the operating system.** Claude Code runs with the user's rights, no more. Root-owned files and other users' home directories are already out of reach through the file permissions.
- **Your own secrets: `sandbox.credentials`.** There is a dedicated mechanism for this — and only it reaches **environment variables** as well. A token in `GITHUB_TOKEN` is never caught by a path list.
- **Self-escalation: write protection for your own configuration.** Whoever can write the `settings.json` or a hook grants themselves wider rights for the next run.

## The two enforcement surfaces

The sandbox and the agent tools are separate, and both need a rule:

- **Area A – Sandbox (`sandbox.*`)** covers **Bash and every child process it spawns**, OS-enforced (bubblewrap/Seatbelt). A `python script.py` run through Bash is thereby boxed in.
- **Area B – Agent tools (`permissions.*`)** covers **Read, Edit, Write, WebFetch**. These do not run through the sandbox but through the permission system. The NVIDIA reference puts it briefly: "Deny rules on Read and Edit only block Claude's built-in file tools" — OS-level enforcement additionally needs the sandbox rules.

The two interlock: `Read` deny rules and `Edit` rules from Area B additionally feed the sandbox's filesystem configuration, and `WebFetch(domain:…)` rules feed its network allowlist.

---

## Area A – Sandbox

### A1 – protect secrets *[Docs]*

The intended route, verbatim from the sandbox documentation. Covers files **and** environment variables:

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

Extend both lists with your own cases — `~/.gnupg`, `~/.netrc`, `~/.npmrc`, `~/.git-credentials`, `~/.password-store`, and among the variables whatever tokens live in your environment.

### A2 – prevent self-escalation *[NVIDIA]*

Claude Code protects some paths on its own; the vendor reference sets them explicitly on top:

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

### A3 – hardening for unattended runs *[Docs]*

```json
{
  "sandbox": {
    "enabled": true,
    "failIfUnavailable": true,
    "allowUnsandboxedCommands": false
  }
}
```

And, if the network is to be held narrow *[adapted, domains after Trail of Bits]*:

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

### A4 – inverting the home directory *[Docs] [failed for us]*

The documentation describes how to block the whole home directory and release only the work — the only route that also covers Thunderbird, browser profiles and software installed in future without enumerating them:

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

**Per the documentation this belongs in the project's `.claude/settings.json`**, because `.` points at the project root only there; in user settings `.` resolves to `~/.claude`, and the project files would stay blocked.

**Test note (1 September 2026):** A variant of this configuration in **user** settings, with the project's *parent* directory instead of `.` in `allowRead`, made the sandbox unusable here: even its setup aborts with `bwrap: Can't create file at <project>/.mcp.json: Read-only file system` — bubblewrap can no longer create the masking of the protected paths inside the project, and every Bash command fails with it. The **documented** form (project settings, `allowRead: ["."]`) is **untested** here. So try it in a throwaway session first. Worth noting for context: the only real-world vendor configuration known to us (NVIDIA) does without the inversion and protects credentials in a targeted way instead.

### Parameters (Area A)

- `sandbox.enabled` — turns the Bash sandbox on; without this `true`, none of the other `sandbox.*` entries take effect.
- `sandbox.credentials.files` — secret files: `mode: "deny"` refuses the read inside the sandbox; `mode: "mask"` shows a placeholder that the proxy substitutes only toward the allowed `injectHosts` (needs `network.tlsTerminate`).
- `sandbox.credentials.envVars` — the same for environment variables; `deny` removes them before every sandboxed command. **The only way to catch tokens in the environment.**
- `sandbox.filesystem.denyRead` — paths that must not be read inside the sandbox (OS level, applies to child processes too).
- `sandbox.filesystem.allowRead` — releases individual paths again inside a denied region; the more specific path wins. The basis of the inversion in A4.
- `sandbox.filesystem.denyWrite` — blocks writing to individual paths inside the allowed zone; in A2 against self-escalation.
- `sandbox.filesystem.allowWrite` — allows writing outside the default write zone, in case a subprocess must write to a fixed location (docs example: `["~/.kube", "/tmp/build"]`).
- `sandbox.filesystem.disabled` — turns file isolation off entirely and keeps only network isolation; set it only for workloads you trust not to escalate their own access.
- `sandbox.failIfUnavailable` — with `true`, abort when the sandbox cannot start, instead of (default) running on unprotected (fail-open).
- `sandbox.allowUnsandboxedCommands` — with `false` ("strict sandbox mode") `dangerouslyDisableSandbox` is ignored entirely.
- `sandbox.autoAllowBashIfSandboxed` — default `true`: sandboxable commands run without a prompt. The NVIDIA reference deliberately sets `false`, wanting to be asked despite the sandbox.
- `sandbox.excludedCommands` — commands allowed to run outside the sandbox (e.g. `docker`, which does not work inside it).
- `sandbox.enableWeakerNestedSandbox` — needed **inside containers**: bubblewrap runs in a reduced mode there and cannot mount a fresh `/proc`. Weakens isolation; do not set it outside containers.
- `sandbox.network.allowedDomains` — domain allowlist for outbound traffic; empty = no network. Keep it as narrow as possible.
- `sandbox.network.strictAllowlist` — non-listed hosts are **denied** instead of prompted; takes effect only from user/managed/CLI settings.
- `sandbox.network.deniedDomains` — a blocklist with precedence.
- `sandbox.network.tlsTerminate` — the proxy terminates TLS itself; prerequisite for credential masking.

---

## Area B – Agent tools (`permissions.*`)

Two things differ here from Area A:

**A boundary already exists.** For read-only tools the documentation states that no approval is required "within the working directory and additional directories" — outside it, therefore, one **is** required. In Manual mode Claude asks there; in auto mode the classifier decides at that boundary instead of the user.

**The inversion does not work here.** Under `permissions`, `deny` always wins and cannot be re-opened by any `allow`.

### B1 – secrets, bypass lock, the boundary question *[adapted]*

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

The `ask` rule is the single most effective entry: auto mode stays in force everywhere, and only the one event "leaving the sandbox" is necessarily put to the user — enforced by the client, not by the model.

### B2 – block environment-changing commands *[NVIDIA]*

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

Keeps the agent from rebuilding its own environment. **Caveat:** Bash deny rules are fragile against deliberate circumvention (variables, interpreter wrapping) — defense in depth, not a boundary.

### Parameters (Area B)

- `permissions.disableBypassPermissionsMode` — the value `"disable"` blocks `--dangerously-skip-permissions`; takes effect from any scope, including user settings, and thus serves as self-protection.
- `permissions.deny` — hard prohibitions, evaluated first, not overridable by any other level. `Read(<path>)` blocks the Read tool and at the same time feeds the sandbox `denyRead`.
- `permissions.ask` — like `deny`, but it asks. As `Bash(dangerouslyDisableSandbox:true)` it is the targeted boundary question at the sandbox exit.
- `permissions.allow` — pre-approvals; take effect only after the folder is "trusted".
- `WebFetch(domain:<host>)` — permits the WebFetch tool to reach this host **and** opens it in the sandbox network allowlist.
- `permissions.additionalDirectories` — additional working directories; also extends the sandbox's write zone.

---

## Notes before you adopt this

- **Try it in a throwaway session first.** A faulty sandbox filesystem configuration can make the sandbox **setup** fail, not just individual commands — then no Bash runs at all (it happened to us, see A4).
- **The network lists add up.** The effective allowlist is `sandbox.network.allowedDomains` **plus** the domains of the `WebFetch(domain:…)` allow rules. Whoever releases a domain for WebFetch opens it for Bash as well.
- **DNS remains an exfiltration channel**, even with a domain allowlist — named as such by Trail of Bits. An egress allowlist is effective, but not tight.
- **VS Code as a special case:** Trail of Bits warns that "Reopen in Container" opens an RPC bridge through which code from the container can run **commands on the host**, and recommends the terminal over VS Code for untrusted code.
- **Path prefix in user settings:** `.` resolves to `~/.claude` there, not to the project, and `**/.env` is anchored to the current directory. Hence `~/` for home paths and `//` for filesystem-wide patterns: `//**/.env` matches `.env` anywhere.
- **Deny is absolute:** a user-level `Read` deny cannot be carved out by a project `allow`. In the sandbox this is different — there, `allowRead` inside `denyRead` is the intended route.
- **Versions:** `strictAllowlist` from v2.1.219; check `claude --version`, `claude doctor` reports rejected keys.
- **Verify effectiveness:** after entering it, probe empirically — only that shows the boundary actually enforced, not the docs. A command that ran past the sandbox carries the prompt title "Bash command (unsandboxed)".
- **No security proof:** these rules lower the probability of misaccess but are a client-side control. The hard boundary for high risk remains the structure: sandbox **plus** container/VM with filtered egress — and even there, in-container credentials stay unprotected.

## Sources

- Claude Code docs: [Sandboxing](https://code.claude.com/docs/en/sandboxing) · [Permissions](https://code.claude.com/docs/en/permissions) · [Settings](https://code.claude.com/docs/en/settings) · [Settings reference](https://code.claude.com/docs/en/settings-reference)
- NVIDIA AI Workbench, [Configure Claude Code Sandboxing in a Project Container](https://docs.nvidia.com/ai-workbench/user-guide/latest/quickstart/quickstart-claude-sandbox.html)
- Trail of Bits, [claude-code-devcontainer](https://github.com/trailofbits/claude-code-devcontainer)
