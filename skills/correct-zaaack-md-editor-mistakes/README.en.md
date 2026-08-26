# correct-zaaack-md-editor-mistakes — find and repair damaged whitespace in Markdown tables

*Last updated: 2026-08-26*

*[Deutsche Fassung](README.md)*

✅☑ **Finished and usable, in both language versions.** Tools, skill text and silent trigger are in place, the frontmatter is set. What is still open is stated in the closing section — none of it stands in the way of use.

## Overview

**Some WYSIWYG editors for Markdown damage the tables of the file they are editing when saving. This skill lets Claude find and repair that damage on its own, without the user having to point it out on every occasion.** The behavior was observed on `zaaack.markdown-editor` for VSCode; the tools, however, do not ask about the editor but about the damage, and are therefore not tied to it.

The skill does three things. It lets Claude recognize the artifacts as soon as they first show up. It obtains a standing authorization from the user so that the repair afterwards runs without asking — otherwise Claude, by its other rules, puts every file change up for a decision first, and there would be no automation at all. And it puts the outcome on record in the project memory, so the question is not asked afresh in every session.

**Scope.** The skill does not format Markdown and does not tidy up tables. It repairs exactly two kinds of damaged whitespace in table rows and leaves everything else untouched: no word, no punctuation, no column alignment, no double blank lines. It only takes effect where Claude can read and write files; in claude.ai it is pointless, because the tools are missing and `${CLAUDE_SKILL_DIR}` is not resolved there.

## Installation

**1. Choose the target location.**

| Location | Path | Applies to |
| --- | --- | --- |
| Personal | `~/.claude/skills/correct-zaaack-md-editor-mistakes/` | all of the user's projects |
| Project | `.claude/skills/correct-zaaack-md-editor-mistakes/` | this project only |

Whoever uses that editor at all uses it just about everywhere — the personal location is therefore the obvious one. The single argument against it is `SKIP` (see "The scope"): the exception list is project-related, and a personal installation carries the same one for all projects.

**2. Copy one language version of the folder.** The folder name stays as it is. `SKILL` and `CLAUDE-snippet` are kept here in two languages; all files of the chosen language come along, README and tools included. The chosen SKILL version is called `SKILL.md` at the target location — whether renamed or additionally placed makes no difference; Claude Code recognizes that name and no other, so a `SKILL.de.md` on its own is not a skill. The date lines show the state of the installation.

```text
SKILL.de.md  or  SKILL.en.md            ->  additionally place as SKILL.md
README.md, README.en.md                 ->  copied unchanged
CLAUDE-snippet.de.md, CLAUDE-snippet.en.md  ->  copied unchanged
md_table_artifacts.py, scan_md_tables.py, fix_md_tables.py
```

Which language follows the one usually worked in: once loaded, the body of the `SKILL.md` stays in the context for the rest of the session and shapes the language Claude answers in afterwards.

A `__pycache__/` appears as soon as the tools have run once. It does not belong at the target location and is not put under version control either.

**The `README.md` is not an extra with this skill but a requirement.** With other skills its absence at the target location only costs depth of reasoning on follow-up questions; here the `SKILL.md` explicitly points to it for the hook setup, instead of dragging that description along in the context permanently. If it is missing, the pointer leads nowhere.

**3. Take over the silent trigger.** The content **below the separator line** in `CLAUDE-snippet.de.md` resp. `CLAUDE-snippet.en.md` goes into the `CLAUDE.md` of the target location — for a personal installation into `~/.claude/CLAUDE.md`, for a project one into the project's. The italic paragraphs above the separator are the instructions for that and are not copied along; they also state what must not be dropped when the wording is adapted. The snippet files travel along to the target location and stay there: only the `CLAUDE.md` is effective; their date lines show which state the adopted trigger is from.

Without this step the skill still works, but is only loaded when it is called explicitly with `/correct-zaaack-md-editor-mistakes` or when a request comes close enough to its description. With this skill that is the standard case of failure: nobody asks of their own accord to have tables checked for spaces.

**4. Optionally set up the hook** — see "Reliability: the hook".

## Details

### What the editor does

Two kinds are on record.

**Swallowed spaces** in front of an opening delimiter for inline code or bold text. Examples from this repository, before the repair:

```text
this is how it stood          this is how it must read
GNU`find`                    GNU `find`
macOS:`brew install jq`      macOS: `brew install jq`
claude.ai**und** lokal       claude.ai **und** lokal
```

Visible if you watch out for it — and easy to overlook for exactly that reason.

**These examples sit in a code block and not in a table, and that is not a matter of taste.** The tools do not tell a documented counter-example apart from a real defect: were the broken versions to sit in a table row, the scanner would take them for findings and the repair tool would repair the documentation until it showed nothing any more. That is precisely what happened while this file was being written — eleven reported "artifacts" in a file that only describes. The scanner looks at lines beginning with `|` and at nothing else; a code block is immune to it. Whoever reformats the examples brings the fault back.

**No-break spaces** (U+00A0) in place of ordinary ones. This is the worse kind: there is no difference to be seen in the rendered text and none in the editor either, but any search over the wording fails. Whoever searches for "Vorgaben automatisch" does not find the line, although it is right there. Six such characters stood in this repository, all of them in tables, none on purpose.

**What has not been measured:** whether the editor swallows spaces outside tables as well. So far artifacts have turned up in table rows only, and the tools therefore look nowhere else. Whether there are further kinds is likewise open. Whoever finds one extends `md_table_artifacts.py` — and records it here.

### The three limits — and why they are drawn where they are

They stand, with their reasons, in the docstrings of `md_table_artifacts.py`. There, because they have to be read when the core is rebuilt: all three look like sloppiness and are not.

**A space is restored only *in front of* a delimiter, never *behind* it.** A suffix glued to a code span is regular prose: `` `uuid`s `` means "several uuid" and is right as it stands. Whoever makes the rule symmetrical destroys such places. The scanner reports them under `notes`, so that a person looks them over once.

**Single-asterisk `*italic*` is not detected.** What is detected is `**bold**` and `` `code` ``. With a single asterisk the risk of confusion with list markers and multiplication signs is too great, and a wrong repair would be silent. No tool catches this gap — it is the one point where Claude has to look for itself. One such place turned up in this repository and was repaired by hand.

**Double blank lines in front of tables are not touched.** The Markdown linter reports them (`MD012`), 35 times in this repository. They do not change how the page renders, and the editor puts them back at the next save — cleaning up against that is wasted effort.

### How the tools are built

Three files, and each split has its reason.

`md_table_artifacts.py` carries the rules: what counts as an artifact, what falls within scope, how a table row is repaired, and which kinds of artifact are repairable at all. It is only ever imported, never called. **The reason is not tidiness:** before, the detection stood in both commands, and two versions of the same rule drift apart. Then the scanner reports places the repair tool does not touch — or, worse, the repair tool changes something the scanner never reported.

`scan_md_tables.py` is given **one** path and descends into every branch by itself. It never writes, so that a wrongly set switch in a hook cannot do silent damage.

`fix_md_tables.py` reads the scanner's list from `stdin` and works through the named files only.

**No state on disk.** The scanner writes its JSON to `stdout`; in the repair step it flows straight on without touching the disk. No intermediate file means: no stale list, nothing to clean up, nothing left lying around between sessions.

**The list carries paths and counts, never line numbers.** The repair tool re-reads every file anyway and derives its repairs from the current content. A line number would be stale the moment something is saved between the two runs, and would make it edit the wrong place. For the same reason the repair step runs the scanner again instead of keeping a list.

**Two lists, and the difference is the heart of the matter.** `files` is the work list and alone determines the exit code. `notes` holds what is reported but deliberately never repaired. Were the notes in the work list, the blank test could never come out clean: the exit code would stay 1 forever, and a hook would fire on every commit without there ever being anything to do. That is exactly how the first version was built, and in this repository the fault would have struck at once — `home-.claude-sharing/offener_fall_chatprotokolle.md` carries a deliberate `` `uuid`s `` in line 101.

### The scope: `SKIP`

`SKIP` in `md_table_artifacts.py` names the path fragments that are never looked at. At present those are `/.git/` and this repository's folder of retired working instructions. **This is the one project-related setting** — whoever takes the tools into another project reviews the list first.

`SKIP` sits in the core and not in the repair tool, so that the scope is not decided in two places.

### Reliability: the hook

A skill is loaded when something points to it — not with certainty. For "at every commit, without exception" that is not enough. Only a hook achieves that, because Claude Code executes it without a model having to decide in favor of it: *"certain actions always happen rather than relying on the LLM to choose to run them"* ([Automate actions with hooks](https://code.claude.com/docs/en/hooks-guide)).

The entry belongs in the project's `.claude/settings.json` — per the documentation the level that may be version-controlled and shared. Two events carry the task:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "python3 ~/.claude/skills/correct-zaaack-md-editor-mistakes/scan_md_tables.py \"$CLAUDE_PROJECT_DIR\" | python3 ~/.claude/skills/correct-zaaack-md-editor-mistakes/fix_md_tables.py" }]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "if": "Bash(git commit*)", "command": "python3 ~/.claude/skills/correct-zaaack-md-editor-mistakes/scan_md_tables.py \"$CLAUDE_PROJECT_DIR\" | python3 ~/.claude/skills/correct-zaaack-md-editor-mistakes/fix_md_tables.py && git -C \"$CLAUDE_PROJECT_DIR\" add -A" }]
      }
    ]
  }
}
```

Three fine points about that:

**The path has to be absolute.** With an absolute root path the scanner emits absolute paths, and with that the repair tool's working directory becomes irrelevant. With a relative path both would have to run from the same directory — an unnecessary assumption inside a hook.

**The `git add -A` in the commit hook** is needed because the hook runs before the commit: without staging again, the repair does not land in the very commit it is meant to rescue. The extent `-A` matches this repository's rule of always committing the whole project; whoever commits selectively needs something else here.

**Not restricted to `*.md`.** The matcher `Edit|Write` fires after every file change, not only after Markdown ones. That is deliberate: a full pass over this repository takes 50 ms, a fifth of which is interpreter startup — a restriction would save nothing and would call for a condition syntax that was not verified here.

**One gap remains, and it is fundamental.** When the user saves in their editor, no tool of Claude's runs — so no hook on tool events fires either. Their changes only come to light when Claude next touches the file or commits. The `FileChanged` event would be meant for this but will not serve: its matcher takes literal filenames only, "Claude Code splits this value into literal filenames rather than evaluating it as a regex" ([Hooks reference](https://code.claude.com/docs/en/hooks)), and the permitted character set is confined to "letters, digits, `_`, and `|` only". For "all `*.md`" one would have to list every file individually.

### What ends up in the memory — and what does not

The skill has Claude record whether this project is affected, and **a refusal as well**. Without the second half, the question starts afresh in every session.

What is recorded is a finding about the project, not a claim about the user. The reason: artifacts in a file only prove that the file has been through such an editor — that may have been a colleague, or an old commit.

**The project memory sits under `~/.claude/projects/<project>/memory/` and holds for this project only.** In the next repository the question starts over. Whoever uses that editor everywhere is better off taking the finding into `~/.claude/CLAUDE.md`; the skill proposes that but does not write there itself.

### State of knowledge

Detection and repair are demonstrated against a test tree of edge cases: a folder name with a space and an emoji (survives the trip through JSON into the repair tool), a deliberate suffix on a code span (unchanged, by checksum comparison), `.git` excluded (likewise), a file without tables passed over. Blank test afterwards with an empty work list and exit code 0.

On the real repository: 67 Markdown files, 1,037 KB, 28 of them with tables. First clean-up run: 40 swallowed spaces and 6 no-break ones across 8 files. Runtime of the scanner over the whole tree 50 ms.

Not demonstrated is everything expressly marked "not measured" above — in particular whether the editor does damage outside tables.

### Firing: measured on 24 August 2026

Procedure per chapter 4.2 of the internal guidelines: a throwaway project with a `CLAUDE.md` carrying nothing but the trigger, and a load indicator whose `description` is the real one. Demonstrated from the stream of `claude -p --output-format stream-json --verbose`, not from the model's own account. One run per condition — a directional finding, not a proof.

| Condition | Sonnet 5 | Opus 5 |
| --- | --- | --- |
| off-topic question (must not fire) | does not fire | does not fire |
| "add a table row to `doku.md`" | fires | fires |
| "commit the changes" | fires | fires |
| asked about spaces explicitly | fires | fires |

**The trigger fires early enough.** With Opus the skill call was the very first action, with Sonnet the second — in both cases before the file was first read. That is the property chapter 2.1 insists on: a later hit no longer rescues a decision that has already been made.

**The standing authorization has no effect while it lives in the skill alone.** An A/B comparison with the same prompt, the same models and the same skill; the only thing changed was the `CLAUDE.md` entry:

| The authorizing sentence sits … | Sonnet 5 | Opus 5 |
| --- | --- | --- |
| in the skill body only | plan presented, nothing repaired | plan presented, nothing repaired |
| in the `CLAUDE.md` entry as well | repaired and reported | repaired and reported |

The reason is precedence. The rule "no file change without a plan presented first" sits in the `CLAUDE.md` and holds unconditionally; an authorization that sits in the skill body alone comes up against it and loses. Both models decided the same way without hesitating. **Whoever wants the automation has to take the authorizing sentence into the `CLAUDE.md` entry** — in the skill alone it is inert.

A side finding that confirms the limit of the authorization: in the effective version both models repaired the whitespace without asking, reported it afterwards — and still presented the *actual* task, a new table row, as a plan. So the authorization covers exactly what it names and no more. The production scanner confirmed afterwards: no findings left, the models' manual repair matched what the tool would have done.

## Status and open points

**Status.** Finished and usable. Tools verified, skill text and silent trigger written out, frontmatter set, both language versions present.

**Split checked and rejected** (25 August 2026). The division into a thin `SKILL.md` and a rules file loaded on demand (guidelines, chapter 5.2) fails here on the third condition: whether a project is affected only shows after a run of the tools, and their description is the rules part — the clarification would have to load it anyway.

**Open:**

- **Whether the editor does damage outside tables** has not been measured. Should such a case turn up, it belongs in `md_table_artifacts.py` and in this README.

**On the name.** `correct-zaaack-md-editor-mistakes` names one particular editor, although the tools ask about the damage and not about who caused it — they bite with any editor that does the same thing. A name like `md-table-whitespace` would last longer. The name is a deliberate choice and not an oversight; whoever changes it changes the folder name, the `name` in the frontmatter of both `SKILL` versions, the slash call, and the reference in both `CLAUDE-snippet` versions along with it.

**Deliberately left open:**

- **Whether a hook is set up is the target project's decision.** The skill sets none and can set none; it names one and describes the setup.
- **The content of `SKIP`** belongs to the target project. The current list is this repository's and not a recommendation.
