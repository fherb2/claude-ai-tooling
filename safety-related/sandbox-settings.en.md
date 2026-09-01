# Sandbox and tool settings: snippets with per-parameter notes

*Last updated: 2026-09-01 · Statements verified against the Claude Code docs, a vendor reference configuration, the Trail of Bits threat model and four bug reports in the Claude Code repository. Sources at the end.*

**Scope:** Linux and macOS; on Windows only through WSL2 — the sandbox does not run natively there, and paths would be written differently (`//c/**/.env` instead of `//**/.env`).

**Each block states where it comes from:** *[Docs]* = from Anthropic's examples, *[NVIDIA]* = from the vendor reference for containers, *[adapted]* = derived from those.

## The most important part first

If you take away one statement, take this one: **against your own system, only a boundary outside Claude Code protects reliably** — a container, a VM, or a confined user account. The settings in this file are **steering**, not system protection: they slow down the everyday overreach and, in auto mode, ask the one question that matters.

Concretely, as of today:

- **What works reliably:** the permission layer (`permissions.*`) — read blocks, the bypass lock, the `ask` rule at the sandbox exit. It does not depend on bubblewrap.
- **What works with reservations:** the sandbox filesystem layer. `denyRead` is documented but demonstrably not always enforced, and the documented recommendation for blocking the home directory is a known, unfixed bug.
- **What is inadvisable today:** enabling the sandbox permanently while working with **git worktrees** — every git command then fails.

## What secures what

Four layers, and only the last two need a rule from you:

- **Writing: the sandbox default.** The write side is an allowlist — only the working directory, the session temp directory and added directories are permitted; everything else is blocked, without enumeration. `/etc`, `/usr`, other projects: closed.
- **Other people's data: the operating system.** Claude Code runs with the user's rights. Root-owned files and other users' home directories are already out of reach through the file permissions.
- **Your own secrets: `sandbox.credentials`.** There is a dedicated mechanism — and only it reaches **environment variables**. A token in `GITHUB_TOKEN` is never caught by a path list.
- **Self-escalation: write protection for your own configuration.** Whoever can write the `settings.json` or a hook grants themselves wider rights for the next run.

Important for placing all this: **what the sandbox covers at all** is stated categorically in the docs — "The sandbox isolates Bash subprocesses. Other tools operate under different boundaries." Writing memory, keeping session transcripts and loading skills are engine operations, not Bash subprocesses; `sandbox.denyRead` does not reach them and does not constrain Claude there.

## The state of the sandbox today: four documented limitations

These four come from bug reports in the Claude Code repository, and they are the reason the recommendations below turn out as they do.

**1. The documented recommendation for blocking the home directory is broken.** [Issue #40941](https://github.com/anthropics/claude-code/issues/40941) reports exactly the example from the docs (`denyRead: ["~/"]` plus `allowRead: ["."]`): wrong working directory, shell resets, `ls` and `git status` failing. The reporter: "The offending line is `"denyRead": ["~/"]`. Removing this line consistently fixes the problem." Labels `bug`, `has repro` — **closed as not planned** (30 March 2026).

**2. A faulty filesystem section can stop the sandbox from starting.** [Issue #50781](https://github.com/anthropics/claude-code/issues/50781): `bwrap: Can't create file at …: Read-only file system`, and with it **every** Bash command fails. Cause: the sandbox marks paths read-only via `denyWithinAllow`, and bwrap's own initialization wants to write exactly there — "The sandbox cannot bootstrap itself." Worth knowing: **`dangerouslyDisableSandbox` does not help** then, "because bwrap runs before this flag takes effect". Closed as not planned (19 April 2026).

**3. `denyRead` is not reliably enforced.** [Issue #61208](https://github.com/anthropics/claude-code/issues/61208), titled "Security: denyRead in sandbox not working": with `denyRead: ["//**"]` and a narrow `allowRead` list, files everywhere were still readable; the variants `["/"]` and `["~/"]` were equally ineffective. Labels `area:security`, `bug` — **closed as not planned** (21 May 2026). Practical consequence: **no `denyRead` entry counts as effective until you have probed it yourself.**

**4. The sandbox and git worktrees do not get along.** [Issue #80278](https://github.com/anthropics/claude-code/issues/80278) — **open and reproduced by maintainers** (22 July 2026): the sandbox masks `.git/config.worktree` with a read-denied `/dev/null` bind mount, whereupon **all** git commands fail, including `git status`. `extensions.worktreeConfig=true` is set automatically by `git worktree` and `git sparse-checkout`. The workarounds are all unpleasant: `excludedCommands: ["git *"]` (takes whole shell invocations out of the sandbox), `allowUnsandboxedCommands: true`, or turning filesystem isolation off.

---

## Area A – Sandbox

### A1 – protect secrets *[Docs]* — the form that works today

The intended route, from the sandbox documentation. Covers files **and** environment variables:

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

Both lists need extending with your own cases — what belongs there is under "What you have to determine yourself" below.

### A2 – prevent self-escalation *[NVIDIA]*

Claude Code protects some paths itself; the vendor reference sets them explicitly on top:

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

And if the network is to be held narrow *[adapted, domains after Trail of Bits]*:

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

### A4 – inverting the home directory *[Docs] — currently broken, do not use*

The docs describe how the whole home directory could be blocked and only the work released. That would be the only route covering Thunderbird, browser profiles and software installed in future **without enumerating them** — which is exactly why it would be the better one:

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

Per the docs this belongs in the project's `.claude/settings.json`, because `.` points at the project root only there. For several projects it could be split — `enabled` and `denyRead` into user settings, `allowRead: ["."]` per project — since "when you define the same filesystem array in multiple settings scopes, Claude Code merges them, combining paths from every scope".

**Even so: do not use it.** This very configuration is filed as a bug (#40941, above), and an attempt on 1 September 2026 confirmed it: the sandbox setup aborted with `bwrap: Can't create file at <project>/.mcp.json: Read-only file system`, after which no Bash command ran at all. The block is here so that you recognise it — not to adopt.

### Parameters (Area A)

- `sandbox.enabled` — turns the Bash sandbox on. For all projects it belongs in user settings, per the docs.
- `sandbox.credentials.files` — secret files: `mode: "deny"` refuses the read inside the sandbox; `mode: "mask"` shows a placeholder that the proxy substitutes only toward the allowed `injectHosts` (needs `network.tlsTerminate`).
- `sandbox.credentials.envVars` — the same for environment variables; `deny` removes them before every sandboxed command. **The only way to catch tokens in the environment.**
- `sandbox.filesystem.denyRead` — paths sandboxed commands must not read (OS level, applies to child processes too). **Check each one's effect individually, see limitation 3.**
- `sandbox.filesystem.allowRead` — releases paths again inside a denied region; the more specific path wins.
- `sandbox.filesystem.denyWrite` — blocks writing to individual paths inside the allowed zone; in A2 against self-escalation.
- `sandbox.filesystem.allowWrite` — allows writing outside the default write zone (docs example: `["~/.kube", "/tmp/build"]`).
- `sandbox.filesystem.disabled` — turns file isolation off entirely, keeps only network isolation. One of the workarounds for limitation 4 — with the corresponding loss.
- `sandbox.failIfUnavailable` — with `true`, abort instead of (default) running on unprotected (fail-open).
- `sandbox.allowUnsandboxedCommands` — with `false` ("strict sandbox mode") `dangerouslyDisableSandbox` is ignored. Note: against a failed sandbox **setup** (limitation 2) the escape does not help anyway.
- `sandbox.autoAllowBashIfSandboxed` — default `true`: sandboxable commands run without a prompt. The NVIDIA reference deliberately sets `false`.
- `sandbox.excludedCommands` — commands allowed to run outside the sandbox. One of the workarounds for limitation 4 (`["git *"]`) — but it then takes whole shell invocations out.
- `sandbox.enableWeakerNestedSandbox` — needed **inside containers**: bubblewrap runs reduced there and cannot mount a fresh `/proc`. Weakens isolation; do not set it outside containers.
- `sandbox.network.allowedDomains` / `strictAllowlist` / `deniedDomains` / `tlsTerminate` — domain allowlist, hard denial instead of prompting, blocklist with precedence, TLS termination as the prerequisite for masking.

---

## Area B – Agent tools (`permissions.*`)

**This layer works.** It does not depend on bubblewrap and is unaffected by the four limitations above. Two peculiarities:

**A boundary already exists.** For read-only tools the docs state that no approval is required "within the working directory and additional directories" — outside it, therefore, one is. In Manual mode Claude asks there; in auto mode the classifier decides.

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

The `ask` rule is the single most effective entry: auto mode stays in force everywhere, and only the one event "leaving the sandbox" is necessarily put to you — enforced by the client, not by the model.

### B2 – block environment-changing commands *[NVIDIA]*

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

**Caveat:** Bash deny rules are fragile against deliberate circumvention (variables, interpreter wrapping) — defense in depth, not a boundary.

### Parameters (Area B)

- `permissions.disableBypassPermissionsMode` — `"disable"` blocks `--dangerously-skip-permissions`; takes effect from any scope, including user settings.
- `permissions.deny` — hard prohibitions, evaluated first, not overridable by any level. `Read(<path>)` blocks the Read tool and at the same time feeds the sandbox `denyRead`.
- `permissions.ask` — like `deny`, but it asks. As `Bash(dangerouslyDisableSandbox:true)` it is the targeted boundary question at the sandbox exit.
- `permissions.allow` — pre-approvals; take effect only after the folder is "trusted".
- `WebFetch(domain:<host>)` — permits the WebFetch tool to reach this host **and** opens it in the sandbox network allowlist.
- `permissions.additionalDirectories` — additional working directories; also extends the sandbox's write zone.

---

## What you have to determine yourself

Because the inversion is unavailable, only enumeration remains — and you carry its price, permanently:

**An inventory of your secrets.** Nobody can do it for you; it depends on your installed software. At minimum you would go through: keys (`~/.ssh`, `~/.gnupg`); cloud CLIs (`~/.aws`, `~/.config/gcloud`, `~/.azure`, `~/.kube`, `~/.docker/config.json`); package registries (`~/.npmrc`, `~/.pypirc`, `~/.cargo/credentials.toml`, `~/.m2/settings.xml`); git (`~/.netrc`, `~/.git-credentials`); password management (`~/.password-store`, `~/.local/share/keyrings`, KeePass files — which live somewhere); mail (`~/.thunderbird`, Evolution); browsers (`~/.mozilla`, `~/.config/google-chrome`, Chromium, Brave); messengers; VPN configurations; editors' credential stores (JetBrains, VS Code); backup tools (restic, borg passwords); and the shell history, where tokens end up.

**A second inventory in the environment.** Tokens in environment variables are caught by no path list — only by `sandbox.credentials.envVars`. What is set on your machine, only you know.

**Upkeep on both surfaces.** Every path needs an entry for the Read tool and one for the sandbox. Partly automatic, because Read denies feed the sandbox — but only partly.

**Continuation without a trigger.** Every newly installed application may bring a new secret store, and nothing reminds you. That is the structural weakness of enumeration: it does not disappear, it merely moves from the machine to you.

**Empirical verification.** Because of limitation 3, no entry counts as effective before you have probed it: attempt the read, look at the result.

**And accepting what cannot be covered:** forgotten locations, shell history, leftovers in `/tmp`, everything a running process holds in memory.

## What only a container or VM achieves

Everything above is **client-side steering**. Against your own system, only a boundary outside Claude Code protects reliably. That is not an opinion but the agreement of every source checked: Anthropic recommends the bypass mode "only … in isolated environments like containers, VMs"; Anthropic runs its own Cowork product with Claude in a VM; a systematic macOS comparison concluded "the VM boundary is the security boundary"; and the entire Trail of Bits approach is a container.

**But that too is not unlimited:**

- A container protects **the host**, not its **contents**. Trail of Bits states plainly that in-container credentials are not isolated — "Claude, GitHub, and other tokens provided to container are simply accessible inside it". The mounted project directory is real and writable.
- **DNS remains an exfiltration channel**, even with a domain allowlist.
- **VS Code weakens the boundary:** Trail of Bits warns that "Reopen in Container" opens an RPC bridge through which code from the container can run **commands on the host**, and recommends the terminal over VS Code for untrusted code.

The sensible division is therefore: **container/VM as the boundary where it is worth it** — unattended runs, untrusted code, company and OT machines. **The settings as steering inside it** — they slow the everyday overreach and ask the one question that counts.

## Notes before you adopt this

- **Try it in a throwaway session first.** A faulty sandbox filesystem configuration can make the sandbox **setup** fail — then no Bash runs at all, and the escape hatch does not help (limitation 2).
- **With git worktrees: better keep the sandbox off** until #80278 is fixed.
- **The network lists add up.** Effective is `allowedDomains` **plus** the domains of the `WebFetch(domain:…)` rules. Whoever releases a domain for WebFetch opens it for Bash as well.
- **Path prefix in user settings:** `.` resolves to `~/.claude` there, not to the project, and `**/.env` is anchored to the current directory. Hence `~/` for home paths and `//` for filesystem-wide patterns: `//**/.env` matches `.env` anywhere.
- **Deny is absolute:** a user-level `Read` deny cannot be carved out by a project `allow`. In the sandbox this is different — there, `allowRead` inside `denyRead` is the intended route.
- **Changes take effect immediately:** "When you edit these filesystem lists during a session, Claude Code applies the change to the running session" — a test needs no new session.
- **No security proof.** These rules lower the probability of misaccess. They claim no more.

## Sources

**Claude Code docs:** [Sandboxing](https://code.claude.com/docs/en/sandboxing) · [Permissions](https://code.claude.com/docs/en/permissions) · [Settings](https://code.claude.com/docs/en/settings) · [Settings reference](https://code.claude.com/docs/en/settings-reference)

**Reference configurations:** NVIDIA AI Workbench, [Configure Claude Code Sandboxing in a Project Container](https://docs.nvidia.com/ai-workbench/user-guide/latest/quickstart/quickstart-claude-sandbox.html) · Trail of Bits, [claude-code-devcontainer](https://github.com/trailofbits/claude-code-devcontainer)

**Bug reports:** [#40941](https://github.com/anthropics/claude-code/issues/40941) documented recommendation breaks the working directory · [#50781](https://github.com/anthropics/claude-code/issues/50781) bwrap cannot bootstrap itself · [#61208](https://github.com/anthropics/claude-code/issues/61208) `denyRead` not enforced · [#80278](https://github.com/anthropics/claude-code/issues/80278) git worktrees break (open)
