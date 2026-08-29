---
name: web-code-editing
description: Governs creating and changing code on claude.ai for an existing software project — secure the sources completely before writing (project knowledge sits as files under /mnt/project and can be read exactly by code), return changed files mechanically as downloads instead of re-dictating them, small changes as a before/replace scheme in the chat. Use as soon as code is created or changed that the user wants to take over into their project, or when the user calls /web-code-editing.
license: CC0-1.0
---

# Editing code in the web frontend

These rules apply as soon as you create or change code on claude.ai that lives on in the user's project.

## Before you write

Say what you are going to do and wait for the user's decision. Settle open questions **beforehand** — not while writing.

## Secure your sources

You reach existing code in three ways:

| Way | For you |
| --- | --- |
| Code piece or file with the prompt | completely in context |
| File in project knowledge | a real file under `/mnt/project/`, readable exactly by code |
| Search in project knowledge | hit snippets only — orientation, no completeness |

**The project knowledge files sit as real files in your execution environment.** Use them by code — even when no tool is offered to you for it and it seems inaccessible: an `ls /mnt/project/` shows them. Check first in which form the code sits there, and choose the access accordingly:

- **Individual source files** you read directly.
- **An archive** (say, ZIP) you unpack into your working directory, then read the files directly.
- **A bundle file combining several source files** as a rule carries marker lines that delimit the beginning and end of each contained file — often with path and metadata, and frequently a header of the bundle file explains its own format. Read that header and a sample of the content first, recognize the marker scheme from it, and extract the file you need exactly between its markers. If the scheme is not recognizable beyond doubt, **ask the user how the file is to be interpreted** — do not guess.

If you find nothing under `/mnt/project/` or the form stays unclear, tell the user instead of quietly falling back to search — the search can miss places.

**You may change line-exactly only what you have verbatim** — in context or as a file extracted by code. Never work against search hits.

**If you lack code, request it before you write.** For "build something like this snippet", the snippet is enough. If your code has to fit into existing software, you need that software — ask specifically, several times if reading reveals more that belongs to it. If it is going to be many files, point the user to the way of packing their code base into one structured file: <https://github.com/fherb2/claude-ai-tooling>, folder `pack-source-to-txt`. The address is for them — you do not fetch it.

**Check whether your state is current.** If the chat does not show that your sources, together with the changes already worked out here, reflect today's state of the place you are to write in: ask, and have changed files given to you anew. The user keeps working locally between chats. Within a chat, the user will not re-upload every single change step of a file into project knowledge or the prompt. Assume that the user does take your produced code into the project right away and that the two of you share the same code base. Only on well-founded doubt have the user give you the code in its current state again. If the user re-uploads the code base into project knowledge on their own, they will tell you.

**If you do not receive a source, name the gap in your answer:** what you changed — and what you cannot say about the interplay with the unseen. Never fill it silently with assumption.

## Return changed files mechanically

**Never re-dictate a changed file from your context** — lines can get lost and whitespace can shift without anyone noticing. The way is mechanical:

1. Extract the original — an individual file directly, from a bundle file exactly between its marker lines — as an exact copy on disk.
2. Apply the changes by targeted replacement at the agreed places — the rest stays byte-exact.
3. Put the result into `/mnt/user-data/outputs` and offer it as a download.
4. **Deliver the diff against the original along with it** — it shows the user that only the agreed places changed.

## Choose the form of the output

**As a file for download** (way above): every changed existing file; new code as a whole file. Prefer this form when the whole file or large parts of it are new or restructured.

**As an artifact:** new code the user wants to look at and discuss first. Likewise, whole functions, classes, drafts, or large changes spread across classes and functions that would grow absurdly big as chat blocks. Describe the exact insertion or change position in the chat. Do not write instructions for inserting into the artifact itself. Observe the indentation at the insertion point. Change a created artifact only at the user's request: as a rule they have long taken the content over, and the valid version sits with them.

**As a change instruction in the chat:** small changes to code the user already has at hand. Observe the indentation at the insertion point and the form of change instructions.

**Return only what you know completely.** From a snippet comes a changed snippet — never a "whole file" whose remainder you would have to invent.

## The scheme for change instructions

When you hand code changes to the user in the chat as the relevant sections rather than a whole file, observe:

Every change consists of two code blocks. The label stands **before** the block, never inside it:

**Before:** the lines to be replaced, exactly as the editor search finds them — original indentation, no shortened quote.

**Replace with:** the new code that takes their place verbatim.

You describe the place by its content — function name, surrounding lines — **never by line numbers**: they shift with every change. Take care that the insertion point cannot be misunderstood.
