*Last updated: 2026-09-15*

*This file is not part of the skill. It holds the silent trigger that fires the skill. When installing: copy everything below the separator line into the `CLAUDE.md` of the target location; this file stays behind there, only the `CLAUDE.md` takes effect. Without the trigger the skill only runs on an explicit `/system-access` call.*

*The wording names events first, in the words a user would use, and additionally ties the check to an action — the first access outside the project folder. Unlike the other triggers in this repository, the last paragraph carries a rule core of its own. That is not a duplication of the skill and must not be dropped when shortening: it is what still protects when the skill has not been loaded — and after a compaction it is the only part of it left in context.*

---

## Access to a system

Where a server is concerned, this machine or another one, a service, a
package, a system configuration or the network — maintaining, updating,
installing, setting up, cleaning up, hunting for a vulnerability —,
consult the skill `system-access` first.

This already holds when a mere question or problem about a computer
arrives: then too you consult it before you look anything up, and first
establish which machine is meant — not the one that happens to be
reachable.

And before you reach outside the project folder for the first time in a
session, even if only to read, or start, stop, connect to or reconfigure
a running program, a service or a container, local or over the network,
consult it as well. What triggers this is your own action, even if the
user never spoke of access at all.

Until it is loaded, this holds: a task never releases along with it the
means by which you intend to carry it out, and an environment that does
not stop you has permitted you nothing. Ask before each such access
separately, name the method and the reason, and change nothing whose way
back you cannot state.
