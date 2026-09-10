# vscode-dev-container

*Last updated: 2026-09-10*

*[Deutsche Fassung](README.md)*

**A dev container for VS Code that draws the line between agent and machine correctly from the start** — narrow mounts instead of the whole home, an SSH agent instead of key files, the network boundary on the host. It carries a C compiler, Python and Poetry, and is meant as a base for other things to build on.

This folder provides the **recipe**, not a finished image: a Dockerfile, a `devcontainer.json`, and the surrounding conditions that belong to them. The image is built locally, on the machine that opens the container.

The reasoning is not repeated here. It lives in [`../safety-related/vscode-topologies.de.md`](../safety-related/vscode-topologies.de.md), which also sets out which constellation of editor, SSH and container draws which boundary — and which one it does not.

## What is inside

- **Ubuntu 24.04** with `build-essential` (C compiler) and Git
- **The distribution's system Python (3.12)** as an untouched base for tooling and skills
- **Poetry** and **uv**, each in its own environment via `pipx`, so neither sits in an environment a project uses
- **`openssh-client`**, so the forwarded agent has a client at all — without it, git over SSH has no transport
- **`bubblewrap` and `socat`**, without which Claude Code's built-in sandbox does not start
- **No Claude Code CLI.** The VS Code extension bundles its own copy; adding a second one would cost several hundred megabytes for nothing
- A prompt showing the git branch and the active Python environment

Interpreters for individual projects are **not** baked in. They are fetched when needed — by Poetry from the `pyproject.toml`, or by `uv` through `use-python`.

## Requirements on the machine that opens the container

- Docker and the VS Code **Dev Containers** extension
- A running **SSH agent** with a loaded key (`ssh-add -l` shows it). Without `SSH_AUTH_SOCK` the socket mount fails
- An existing `~/.gitconfig` and an existing `~/.claude` — both are mounted, not created
- `USER` and `HOME` set. Both are present in an ordinary login session; without them the Dockerfile defaults apply (`dev`, `/home/dev`), and the path no longer matches for synchronisation

When working over **Remote SSH**, this means the *remote* machine, not the laptop: that is where the dev container tooling runs and where the project and `~/.claude` live. The agent therefore has to reach that far, via `ForwardAgent`.

## Adopting it in a project

Copy the two folders `.devcontainer/` and `.claude/` into the root of your project, then run **Dev Containers: Reopen in Container** in VS Code. The first run builds the image, which takes a few minutes; afterwards it is cached.

The folders already carry the names they will have in the target project — nothing to rename, nothing to sort into place file by file. `.claude/settings.json` is why the second folder belongs with it: it sets the built-in sandbox for this project such that it starts at all inside the container (see "Which Claude settings carry into the container").

To add something — JupyterLab, a vendor SDK, further libraries — append to the Dockerfile or derive from it with `FROM`. **Not** through the `features` block of `devcontainer.json`: the tooling applies that on top of the image afterwards, and it is lost when deriving.

## The mounts

| What | Target in the container | Mode |
| --- | --- | --- |
| Project folder | `~/git/<folder name>` | rw |
| `~/.claude` | the same path as outside | rw |
| `~/.gitconfig` | the same path as outside | **ro** |
| SSH agent socket | `/ssh-agent` | rw |

Everything else in the home stays out — `~/.ssh`, `~/.aws`, `~/.gnupg`, other projects. That is the point: what is not mounted does not exist for the container, and no rule has to hold for it.

`docker.sock` is **never** mounted. That would amount to root on the host.

### The agent socket: two quirks from the field test

**The path is resolved only when the container is *created*, not on every start.** `${localEnv:SSH_AUTH_SOCK}` freezes into the container configuration. If a different `ssh-agent` runs later (new login, new terminal, reboot), the mount points at a socket that no longer exists — and Docker then refuses to **restart the existing** container:

```text
Error response from daemon: invalid mount config for type "bind":
bind source path does not exist: /tmp/ssh-XXXXXXXX/agent.NNNN
```

That is not a defect of this building block but a property of variable resolution. The remedy: **recreate** the container rather than restarting it (remove the container, then "Reopen in Container" — a mere "Reload Window" is not enough, because it keeps using the frozen configuration).

**And with VS Code Desktop, its own forwarding wins anyway.** Measured inside the container: `$SSH_AUTH_SOCK` pointed at `/tmp/vscode-ssh-auth-….sock`, not at our `/ssh-agent` mount — VS Code forwards the agent itself and overrides our `containerEnv` value. In practice that does no harm (`ssh-add -l` listed the keys correctly), but it means: **our mount is inert under VS Code Desktop.** It stays right nonetheless, because it is the only route that also carries **without** VS Code Desktop — a browser client, the `devcontainer` CLI, a plain `docker run`.

### Why the path is chosen this way

Claude Code stores session transcripts under `~/.claude/projects/<project-path-with-dashes>/`, so the key is derived from the **absolute path of the project**. If the project sat at `/workspace` inside the container, the same work would get different keys inside and outside, and synchronisation between machines would miss.

The project is therefore normalised to `~/git/<folder name>`, regardless of where it sits on the host. As long as projects on the machines involved also live under `~/git/`, the key is the same inside, outside, and on every machine.

**The exception to know about:** if a project on the host does *not* live under `~/git/`, the container path differs from the native one — that single project then has two separate histories, depending on whether it was worked on with or without the container.

### Interaction with `home-.claude-sharing`

Synchronising `~/.claude` runs through Syncthing **on the host operating system**, not in the container. Through the mount, the container sees the current state anyway.

**No second watcher may run inside the container.** It would observe the same files as the one on the host and report conflicts that are not conflicts.

And one consequence to accept deliberately: the container writes into a synchronised directory. Session transcripts from the container therefore reach every machine involved.

**The second consequence is the more uncomfortable one, and the field test surfaces it immediately:** `~/.claude` is mounted **whole**, not as a project-scoped subset. The session history of **all** projects and all machines therefore lies open inside the container — `ls ~/.claude/projects/` showed more than thirty entries in the test, from unrelated repositories to scratchpad directories. Anyone drawing this container's boundary around a single project should know that it does not hold for the chat history: a compromised process inside the container could read the transcripts of other projects too, along with everything ever discussed in them.

A project-scoped subset would be technically possible (mounting only `~/.claude/projects/<key>/` instead of `~/.claude`), but it takes credentials, skills and settings away with it — precisely what the mount is there for. This conflict is **not** resolved here; it is deliberately decided in favour of usability and stands as such under "Open".

## Python in the container

**The base stays untouched.** System Python 3.12 is what skill scripts and the compaction hook invoke. No selection changes it.

**Poetry projects** need nothing further: Poetry reads the `pyproject.toml`, fetches a matching interpreter if needed (`poetry python install`, available since Poetry 2.1 and marked experimental by its authors), and activates its own environment.

**Without Poetry**, `use-python` serves:

```bash
use-python           # report the current selection and the prepared environments
use-python 3.11      # fetch the interpreter if needed, prepare the environment,
                     # remember it and activate it right away
use-python system    # drop the selection
```

The selection lives in `~/.config/devcontainer/python-version`, the environments under `~/.venvs/`. Both sit in the container's own layer: they survive every **restart** and are gone after a **rebuild**. New shells apply the remembered selection by themselves; if you then move into a Poetry project, Poetry wins. The prompt always shows whichever environment is actually active.

Automatic activation only takes effect in **interactive** shells, because it hangs at the end of `.bashrc`. A task started non-interactively sees the system Python.

## Network boundary

**It belongs on the host, not in the container.** The container has passwordless `sudo`; a packet filter rule inside it could be changed from inside. Docker provides the `DOCKER-USER` chain for user rules, which survives restarts of the daemon and leaves the rest of the firewall alone. On the machine running the container:

```bash
iptables -I DOCKER-USER -d 10.0.0.0/8     -j DROP
iptables -I DOCKER-USER -d 172.16.0.0/12  -j DROP
iptables -I DOCKER-USER -d 192.168.0.0/16 -j DROP
iptables -I DOCKER-USER -j RETURN
```

Effect: traffic into private address ranges is dropped, the internet stays open — repositories, package indexes and documentation remain reachable.

**This is not a template to copy.** Where a machine has devices attached that belong to the task — cameras, measurement hardware, an internal mirror — each needs an `ACCEPT` line **before** the `DROP` lines. The rule stays a deny list with named exceptions rather than an allow list. These exceptions have to be settled per machine.

**Two limits of this rule:**

With `--network host`, `DOCKER-USER` does **not** apply — the chain sits in the forwarding path for bridge networks, and a container in the host's network namespace bypasses it. Anyone who needs device discovery over broadcast, and therefore sets `--network host`, needs a different barrier. *This is derived from Docker's network architecture and has not been measured.*

And it does not protect against what the container reaches through an **allowed** host: a permitted address is open on all ports.

## Which Claude settings carry into the container

Of the two layers in [`../safety-related/sandbox-settings.de.md`](../safety-related/sandbox-settings.de.md), only one carries.

**The permission layer (`permissions.*`) works unchanged.** It does not depend on bubblewrap. Read denials, the bypass lock and the question at the sandbox exit belong here too.

**The sandbox layer (`sandbox.*`) runs weakened inside a container — but it is not redundant.** This distinction is worth spelling out, because an earlier version of this README claimed the opposite.

Exactly **one** thing is weakened, and the docs name it: with `enableWeakerNestedSandbox`, the inner sandbox bind-mounts the container's existing `/proc` instead of mounting a fresh one — "it exposes process information to sandboxed commands that a fresh `/proc` mount would hide". A sandboxed command therefore sees the container's other processes. That is a real concession, and it is the only one stated there.

**Not** affected are the filesystem denials, the network allowlist and the protected paths — those rest on bind mounts, the proxy and fixed deny rules, not on a fresh `/proc`. And that is exactly where the inner sandbox does something the container boundary does not: **the container decides what is reachable at all; the inner sandbox decides what a single Bash command may touch of it.** Within the already-reachable area it prevents a `.claude/settings.json` or a git hook from being written, and it can narrow the network per command beyond what the `DOCKER-USER` rule does. That is not a duplicate of the container boundary but a second, finer layer inside it.

This is why the building block ships the sandbox **enabled** — `.claude/settings.json` sets `enabled` and `enableWeakerNestedSandbox` — and why the image carries `bubblewrap` and `socat`, without which it does not start at all. Anyone who weighs process visibility higher than the gain can switch it off with `"enabled": false` in that same file; that is a deliberate decision, not a default.

Because `~/.claude` is mounted, the host's configuration applies inside unchanged — skills and hooks included. That is why the system Python has to stay reachable regardless of the environment selection.

## Checklist

Walk through this once after the first start. No promise counts until it has been probed. The "probed" column records what was actually observed in the field test on two machines on 5/7 September 2026.

| Check | Expected | probed |
| --- | --- | --- |
| `whoami` | your user name (when built locally) | ✅ `herbrand` |
| `pwd` | `~/git/<folder name>`, identical to the host path | ✅ |
| `echo "$HOME"` | the host home path, not `/home/dev` | ✅ |
| `ls ~/.claude/projects/` | contains the project's key | ⚠️ contains **all** projects, see "Interaction with `home-.claude-sharing`" |
| `ls ~/.ssh` | does not exist | ✅ |
| `ssh-add -l` | lists the key — the agent carries | ✅ (after adding `openssh-client`) |
| `use-python` | reports itself, even with no version chosen | ✅ `selected: system` |
| Open the Claude extension | panel starts, a session is possible | ✅ v2.1.263 |
| `git -C <project> fetch` | works without a passphrase | open |
| `curl -s -o /dev/null -w '%{http_code}' https://github.com` | `200` | open |
| Connection attempt to an internal address | fails once the `DOCKER-USER` rule is in place | open — rule not yet set |

## Open

- **Settle the `DOCKER-USER` rule per machine**, with the exceptions for the devices attached there (cameras, measurement hardware). Without it the corporate network is reachable from the container. This is the point at which the building block delivers its third protection goal or fails to.
- **The conflict around `~/.claude` is unresolved.** The entire chat history of all projects sits inside the container; a project-scoped subset would take credentials, skills and settings away with it. Deliberately decided in favour of usability, not solved.
- **The `--network host` case is unverified** (see "Network boundary").
- **The editor's back channel stays open.** With VS Code Desktop as the front end, code in the container can drive commands on the machine you sit at, through the remote control interface. No setting of this container closes that; where it matters, only a browser client helps. Details in the topology report.
- **A prebuilt image used without a build step** carries the defaults `dev` and `/home/dev`. Synchronisation then requires adjusting the home path at runtime, which is not built here.

### What the field test settled

The first build has run, on two machines. It is therefore **no longer** open — what surfaced in the process now sits in this README and in the Dockerfile. Three points that were not properties of this building block, but cost hours and are recorded here as warning signs:

- **Aborted container starts leave running processes behind.** "Cancel" in the VS Code UI does not terminate the `devContainersSpecCLI.js` process; it keeps running and blocks the next attempt, with no error message and no network traffic. Find it with `ps aux | grep <project name>`, end it with `kill`.
- **`docker buildx` can be missing even though the package is installed.** On the second machine, `~/.docker` was owned by `nobody` (UID 65534) with mode `0710` — Docker could not read its own configuration and reported `unknown command: docker buildx`. Fixed with `chown`. Where the wrong ownership came from is unexplained.
- **The VS Code Server is fetched fresh from Microsoft for every new container** (some 230 MB, `update.code.visualstudio.com`). It is not part of the image and, on a slow line, is the single longest item of the start.
