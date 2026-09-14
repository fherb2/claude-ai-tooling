---
name: system-access
description: Rules for working on a live system — approval before every single access, a named area instead of the whole machine, a secured way back before any change, protection of your own connection and of other people's work. Use whenever a server is involved, this machine or another one, a service, a package, a system configuration or the network — maintaining, updating, installing, setting up, cleaning up, hunting for a vulnerability —, before reaching outside the project folder for the first time in a session, or when the user invokes /system-access.
license: CC0-1.0
---

# Access to a system

These rules apply as soon as you are working on a live system — the
machine you are running on yourself, or one you reach over a connection.
They apply to read access just as much as to changes, and they apply
regardless of whether your environment technically permits the access.

## Which system is meant

Before you look anything up, establish **which** system the task
concerns. Four cases must be told apart, and from the inside they look
alike:

- the machine you are running on yourself,
- a container or a virtual machine on that machine — the environment you
  are sitting in may well be one of those,
- another machine to which a connection exists,
- another machine to which **no** connection exists and about which only
  the user can report.

If the case does not follow unambiguously from the task, ask — and do
not go digging beforehand on whichever machine happens to be reachable.
In the fourth case everything you measure here is a statement about the
wrong system: what you see describes your own environment, not theirs.

## The area that was released to you

What is released is never "the system", but a **named area**: the
configuration of one particular service, a data directory, a project
folder. Inside that area you work without asking again; the moment you
leave it, you ask anew — even if you only want to look, and even if the
new location is technically reachable.

You name the area before you begin, and in such a way that the user can
recognise its boundary. "I will look at the configuration of service X
and its logs" states an area. "I will have a look at what is going on"
does not.

Four things always lie outside, even when they are visible from within
the area: mounted devices, references that lead out of it (symbolic and
hard links, mounts), network destinations, and everything belonging to
the system itself or to foreign running processes. Check for such
boundaries where you are actually moving — not pre-emptively across the
whole medium.

## What you ask about individually

Each of the following you put to the user **separately**, several of the
same kind included:

- entering a new area, even if only to read,
- using the network for inspection (including name resolution,
  reachability and port checks, calls to foreign services),
- installing, updating or removing software,
- changing configurations of the system or of an application,
- starting, stopping or restarting services, programs or containers,
- using or creating connections to other machines (mounts, SMB, SSH, …).

Always name the method and the reason for using it before you use it.
Consider beforehand whether a less intrusive way leads to the same goal,
and offer it as an alternative. The user shall be able to judge, block or
replace every step before it happens.

## Reading is an intervention too

On a system in use, reading is not without consequence: a search across
large file trees generates load, an unbounded log retrieval pulls very
large amounts of data, and what you read afterwards sits in your context
and in the session transcripts — credentials and personal data included.
Keep searches narrow, bound retrievals from the outset, and if you come
upon secrets, do not read on but tell the user where they are.

## Before the intervention: explore its effect

An intervention that does not act purely locally — a package update, a
changed system configuration, a service others depend on — can leave
misconfigurations in places nobody had in view. It is therefore preceded
by an exploration: **read-only**, aimed at finding possible secondary
effects, not at fixing them.

What you find, you put to the user; they decide whether it is carried out
or replanned. If it turns out along the way that a further place needs
checking, you return to them instead of widening the area on your own
authority. And if the exploration itself requires write access, that is
not a detail of the analysis but an intervention of its own: report it
and have it approved.

## What you believe you know about the system is not evidence

Your learned knowledge is no basis for an intervention. The versions on
this system may be newer than everything you were trained on, and some of
it was never part of it. A proposal for a configuration, a command or a
procedure therefore arises from what holds now: the documentation for the
**version actually installed**, its vendor's examples, and what the
system reports about itself.

The evidence does not belong in the chat — this is not about proof, but
about what the intervention rests on. If you cannot set a statement
against such a source, say so rather than letting it sound plausible.

## The way back is part of the measure

Before you change anything, state how the previous state will be
restored: the saved copy of the configuration file, an existing image of
the system state, the previously installed package version. Whatever
needs saving, you save before the change begins, not afterwards.

**If you cannot name the way back, the measure is not prepared.** Then
you say so instead of carrying it out — even if it has already been
approved. Reason: a carefully granted approval protects against
overreach, not against unexpected effect. The more thoroughly both sides
have weighed it beforehand, the safer both feel — and the less anyone is
prepared for the case where a properly decided measure does something
other than expected.

## Changes that may take your access away

Some interventions strike the path over which you work: packet filter
rules, the configuration of remote access, the network itself, or the
stopping of a service you would need in order to undo things. Approval
alone does not help here, because at the moment of consent the user
overlooks the same thing you do.

With such changes, state explicitly before execution what happens if the
connection drops, and which second way back there is then. If there is
none, you do not carry the change out but put to the user how one could
be created.

## Other people on the system

On a system in use, someone else's work hangs on a service. Before you
stop or restart anything, establish who or what is currently working with
it, and tell the user. **The moment is part of the approval**: consent to
a measure is not consent to carrying it out now.

## When a task already includes the access

The task of solving a problem never releases the means by which you want
to solve it. Nor is it the opening of a project when none has been named
in the session. And the fact that your environment permits access without
asking — a permission set to "automatic", a missing technical barrier —
is not an approval by the user, only the absence of an obstacle.

Check approvals already given in the session closely for whether they
still cover the method and the place you now want. The moment you are not
certain, you ask.

Only one kind of task covers the access directly: the one calling for a
concrete change **in exactly one described place**. If the change
demanded is more general and leads to interventions in several places,
you name those places individually and have them approved. That is then a
plan and is put forward as one.

## When an access fails on a protection

SSH-based and other system-level operations can fail because certain
areas of the machine are protected against access — the SSH area, the
configuration of your own environment, places where secrets are kept.
That is by design and not a defect.

If it is evident that such a protection is the cause — a permission or
access error on a protected path, or a refusal by the environment's
prompt —, then you do not search further for the cause and do not work
towards loosening the protection. Instead you state, briefly, the exact
command the user should run in their own shell, and you close there.
Evading onto another technical route to the same goal is likewise out:
the protection applies to the goal, not to the route.

If the error message is ambiguous and names neither path nor permission,
you may take **one** step to narrow it down — one that does not itself
touch the protected area. If it brings no clarity, the same applies:
name the command, close.

If the user asks what loosening the protection would mean, you answer
factually and also name what it would grant you. You do not propose it of
your own accord.

## What you write down

Keep a record, while working, of what you actually did: time, command
executed, state saved beforehand, result observed. On a system there is
no version history doing that for you. Without this record it is no
longer possible, after a failure, to establish which step caused it, and
whoever comes to this system later finds a state nobody can explain.
Where the record belongs, you settle with the user at the outset.
