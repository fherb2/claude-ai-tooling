# Pack Source for AI

A **shell script that bundles project source files into a single, structured text file** ready for upload to an AI agent's knowledge base.

Useful for working via web AI agents, or in an insecure environment where the AI agent is not meant to have direct access to the computer.

**Example use** with Claude:

1. Run `./packsrc.sh` on the command line.
2. Drag the new `project_source.txt` file into the project knowledge on Claude.ai.

   Done. The entire source code now sits in that one file, structured and searchable.

> **Note:** The header generated in `project_source.txt` merely describes the format – it is not directed at any specific AI agent, nor does it instruct any agent to do anything. The actual instructions are contained in `project_source.instructions.md` (option `-i`), which is entered at the point where the agent receives its instructions. Reason: Several agents deliberately treat the content of uploaded documents as data and do not reliably follow any instructions contained therein.

---

## Overview

`packsrc.sh` collects source files from one or more project directories into a single `project_source.txt`. Every file is wrapped in unambiguous metadata blocks that allow an AI agent — or any other tool — to:

- identify which files are included and where they live in the project tree,
- distinguish current index results from stale cached ones via a run-level timestamp,
- determine when each individual file was last modified.

The primary use case is uploading `project_source.txt` as a knowledge document to an AI agent (such as [Claude](https://claude.ai)), giving it precise and up-to-date context about the entire codebase in one place.

**Web-based versions of AI agents can therefore also be used to drive software development forward or to check code for errors and make changes.** This is not quite as convenient as having the agent read and edit the code directly within the project, but it is far less time-consuming than one might imagine. This allows you to work **in security-critical environments** where unsupervised or poorly supervised access to system resources is not permitted. (A skill is currently being developed to further optimise this use case.)

### Don’t forget the .gitignore entry

The output file contains the entire source code and would take up unnecessary space in the Git repository. So don’t forget to include the entry (including the short description file):

```plaintext
# packaged source code by packsrc script and it's AI instruction file
project_source.txt
project_source.instruction.md
```

---

## Features

**Configuration takes place in the header of the script**, so the script is usually run within the project without any arguments or a configuration file, and it generates the source code text file `project_source.txt`.

The text file is **structured using meta-prefixesstructured using meta-prefixes** `#!PKSRC: ...` and **is self-descriptive** thanks to its header. However, processing by an AI agent can be optimised using the auxiliary file `project_source.instruction.md`.

- **Multi-directory support** — scan one or more source directories per run; configurable via `SOURCE_DIRS`.
- **Recursive whole-project scan** — use `"./"` as a `SOURCE_DIRS` entry to scan the entire project root recursively, instead of listing individual subdirectories.
- **Configurable file extensions** — define which suffixes are always included; add more temporarily via CLI flags (`-md`, `-txt`).
- **Extension-less files** — an empty-string entry (`""`) in `BASE_EXTENSIONS` matches files that have no dot in their name at all (e.g. `Dockerfile`, `Makefile`).
- **Explicit file list** — `EXPLICIT_FILES` includes individual files by exact name or path instead of by extension, so unrelated files sharing the same extension aren't dragged in, and files outside `SOURCE_DIRS` (including the project root) can be added too.
- **Directory exclusion** — skip build artefacts, caches, or backup folders by bare directory name, at any depth, via `EXCLUDE_DIRS`.
- **Default dot-exclusion** — files and directories whose name starts with `.` (e.g. `.git`, `.vscode`, `.env`, `.gitignore`) are always skipped in `SOURCE_DIRS` scans, unless explicitly listed in `EXPLICIT_FILES`.
- **Structured `#!PKSRC` metadata markers** — every file block carries a run timestamp and the file's individual last-modification time.
- **Self-describing header** — a preamble explains, in three separately searchable sections (`NOTE_TO_READER`, `FORMAT_DESCRIPTION`, `DATE_TIME_CHECK`), how the file is structured and how to recognise stale search results. Each section carries its own `#!PKSRC` marker, so even a single fragment of the file remains self-describing when a retrieval system hands out nothing else.
- **Instructions file for AI agents** — `-i` additionally writes `project_source.instructions.md`, which carries the actual instructions. Header and instructions file are built from the same text blocks inside the script and therefore cannot drift apart.
- **Graceful handling of missing entries** — a `SOURCE_DIRS` or `EXPLICIT_FILES` entry that does not exist emits a warning on stderr; the rest of the output is produced normally.
- **Alphabetically sorted output** — files are sorted by path across all directories combined, so the result is deterministic and easy to diff. Files with identical names in different directories are NOT deduplicated — each is listed separately, distinguishable by its path in the block header.

---

## Requirements


| Requirement | Notes                                             |
| ----------- | ------------------------------------------------- |
| Bash ≥ 4.0 | Standard on Linux                                 |
| GNU`find`   | Standard on Linux; macOS:`brew install findutils` |
| GNU`stat`   | Standard on Linux; macOS:`brew install coreutils` |
| GNU`date`   | Standard on Linux; macOS:`brew install coreutils` |

> **macOS note:** The script uses `stat -c` and `date -d`, which are GNU extensions. On macOS, install [coreutils](https://formulae.brew.sh/formula/coreutils) via Homebrew and ensure the GNU tools are on your `PATH` (the Homebrew formula explains how).

---

## Installation

Copy the script into the root of your project — no further dependencies are needed:

```bash
git clone https://codebase.helmholtz.cloud/FWF/tools/pack-source-for-ai.git
cp pack-source-for-ai/packsrc.sh /path/to/your/project/
chmod +x /path/to/your/project/packsrc.sh
```

The script is intentionally self-contained so it can be dropped into any project without modification (edit only the `CONFIGURATION` section).

---

## Configuration

Open the script and edit the `CONFIGURATION` section near the top — everything below the `DO NOT EDIT` line is driven by these variables:

```bash
# Directories to scan (relative to the script, without leading ./)
# Default: ("source") — keeps the classic single-directory layout
# "./" scans the whole project root recursively instead of a named subdir
# Some examples:
SOURCE_DIRS=("source" "shared" "tools" "tests" "submodules")

# File extensions included in every run (without leading dot)
# "" matches files with no dot in their name at all (e.g. "Dockerfile")
# Default is an example for Python+CUDA use cases:
BASE_EXTENSIONS=("py" "cu")

# Directory names pruned at any depth inside the scanned trees
# Example
EXCLUDE_DIRS=("backup" "__pycache__" ".git")

# Individual files included by exact name/path instead of by extension
EXPLICIT_FILES=("Dockerfile.watchdog" "./docker-compose.yml" "~/.config/foo.conf")
```


| Variable          | Default                    | Description                                                                                                                                             |
| ----------------- | -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `SOURCE_DIRS`     | `("source")`               | Directories to scan. Relative paths, no leading`./`. `"./"` scans the entire project root recursively. Non-existent entries are skipped with a warning. |
| `BASE_EXTENSIONS` | `("py" "cu")`              | Always-included file suffixes.`""` matches files with no dot in their name at all.                                                                      |
| `EXCLUDE_DIRS`    | `("backup" "__pycache__")` | Directory names excluded at any depth in every scanned tree.                                                                                            |
| `EXPLICIT_FILES`  | `()`                       | Individual files included by exact name/path — see below.                                                                                              |

### `EXPLICIT_FILES` entry forms


| Form                      | Example                  | Meaning                                                                                                                                          |
| ------------------------- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| bare name (no leading`/`) | `"Dockerfile.watchdog"`  | Searched for by exact filename anywhere inside`SOURCE_DIRS`. `EXCLUDE_DIRS` still applies; the default dot-exclusion is bypassed for this entry. |
| `./relative/path`         | `"./docker-compose.yml"` | Exact single file, relative to the project root.                                                                                                 |
| `/absolute/path`          | `"/etc/hosts"`           | Exact single file, absolute machine path.                                                                                                        |
| `~/path`                  | `"~/.config/foo.conf"`   | Exact single file, relative to the user's home directory.                                                                                        |

All three path-prefixed forms (`./`, `/`, `~/`) always bypass the default dot-exclusion rule, since they name one specific file explicitly.

### Default dot-exclusion

Any file or directory whose bare name starts with `.` (e.g. `.git`, `.vscode`, `.env`, `.gitignore`) is skipped everywhere in `SOURCE_DIRS` scans, at any depth, for both the regular `BASE_EXTENSIONS` matching and bare-name `EXPLICIT_FILES` searches. This is always active and not configurable. The only way to include such a file is to list it explicitly in `EXPLICIT_FILES` using the `./`, `/` or `~/` form.

---

## Usage

```bash
# Standard run — uses SOURCE_DIRS, BASE_EXTENSIONS, EXCLUDE_DIRS and
# EXPLICIT_FILES from config
./packsrc.sh

# Also include Markdown files for this run only (not saved to BASE_EXTENSIONS)
./packsrc.sh -md

# Also include plain-text files for this run only
./packsrc.sh -txt

# Also write the instructions file for AI agents
./packsrc.sh -i

# Combine flags
./packsrc.sh -md -txt

# Show help
./packsrc.sh -h
```

**Output** is always **written to `./project_source.txt` in the directory from which the script is invoked**. The file is overwritten on every run. With `-i`, `./project_source.instructions.md` is written alongside it; its content does not depend on the run, so invoking it again writes an identical file.

---

## Output format

**`project_source.txt` is a plain-text file with the following structure:**

```
#!PKSRC:HEADER:BEGIN | project_source.txt | pksrc_ts: 2025-03-14_10-23-45
#
#!PKSRC:HEADER:NOTE_TO_READER
# < what the two sections below are for >
#
#!PKSRC:HEADER:FORMAT_DESCRIPTION
# < structure of the file and meaning of its fields >
#
#!PKSRC:HEADER:DATE_TIME_CHECK
# < how to recognise stale search results >
#
#!PKSRC:HEADER:END

#!PKSRC:FILE:BEGIN | ./source/main.py | pksrc_ts: 2025-03-14_10-23-45 | file_mtime: 2025-03-13_18-42-01
< file contents >

#!PKSRC:FILE:END | ./source/main.py

#!PKSRC:FILE:BEGIN | ./shared/utils.py | pksrc_ts: 2025-03-14_10-23-45 | file_mtime: 2025-03-12_09-15-33
< file contents >

#!PKSRC:FILE:END | ./shared/utils.py
```

### Metadata fields


| Field        | Scope      | Description                                                                    |
| ------------ | ---------- | ------------------------------------------------------------------------------ |
| `pksrc_ts`   | Run-level  | Timestamp of this script invocation. Identical for every block in one file.    |
| `file_mtime` | File-level | Last modification time of the individual source file at the moment of the run. |

The `#!PKSRC` prefix does not appear in normal Python, CUDA, shell, or configuration source code, making the markers unambiguous even when the file is used as a full-text search index.

### Stale-result detection

The `DATE_TIME_CHECK` section of the header describes the mechanism: every block repeats the `pksrc_ts` of the run it came from. When an agent answers out of an earlier, cached retrieval, the quoted content carries an older `pksrc_ts` than the `#!PKSRC:HEADER:BEGIN` line of the currently uploaded file. Where the two values differ, the result is superseded.

`file_mtime` lets you (and the AI) verify whether a specific source file was actually touched during a given implementation step, without having to look at git history.

### The `project_source.instructions.md` file

The header describes; it does not command. That is deliberate: several AI agents treat the content of an uploaded document as data on purpose and do not reliably honour instructions found inside it — in the extreme, such instructions are judged to be an injection attempt. Only what sits in the channel provided for it is honoured reliably.

`./packsrc.sh -i` therefore additionally writes `project_source.instructions.md`. Paste its content into wherever your agent takes its standing instructions — Claude project instructions, the instructions field of a Gemini Gem, `AGENTS.md`, `CLAUDE.md`, or the system prompt of your own tooling.

The two sections `FORMAT_DESCRIPTION` and `DATE_TIME_CHECK` exist exactly once in the script, in the functions `emit_format_description` and `emit_date_time_check`; both the header and the instructions file are built from them. To change the wording, change it there — **not** in `project_source.instructions.md`, which the next `-i` run overwrites. The copy kept in this repository was produced that way and serves as a preview; if you copy only `packsrc.sh` into a project of your own, generate it there with `-i`.

---

## Typical workflow

1. **Configure once** — set `SOURCE_DIRS`, `BASE_EXTENSIONS`, `EXCLUDE_DIRS` and `EXPLICIT_FILES` for your project.
2. **Set up once** — run `./packsrc.sh -i` and paste the content of `project_source.instructions.md` into your AI agent's standing instructions.
3. **Regenerate** — run the script after each relevant commit or work session.
4. **Upload** — place `project_source.txt` in your AI project's knowledge base (e.g. as a project document in Claude).
5. **Work** — the AI now has accurate, timestamped context for all source files and can detect outdated index results.

It is recommended to add `project_source.txt` to `.gitignore` since it is a generated artefact. 

---

## Development / Testing

An acceptance/regression test for this script is provided in `full_script_test.py`.

**Requirements:** Python 3.10+, standard library only — no third-party packages, no virtual environment needed. Tested against the system Python 3.12 on Ubuntu 24.04. If a future test ever needs a package that isn't in the standard library, set up a project-local virtual environment first (e.g. `python3 -m venv .venv && source .venv/bin/activate`).

**Run it:**

```bash
python3 full_script_test.py
```

**What it does:** the test builds an isolated fixture tree under `./test_project/` that plays the role of a simulated project root (so `SOURCE_DIRS=("./")`, project-root-level `EXPLICIT_FILES` entries, etc. can all be exercised). For each of several scenarios (named `SOURCE_DIRS` entries, the recursive `"./"` entry, the `-md` flag) it generates a scenario-specific *copy* of `packsrc.sh` with an adjusted `CONFIGURATION` block, runs that copy, and compares the resulting `project_source.txt` against the expected file set. **The real `packsrc.sh` is never modified.**

- On success, `test_project/` and `test_results/` are deleted again; only the console PASS/FAIL report remains.
- On failure (or any unexpected error), both directories are left in place for manual inspection, and the script prints their paths.
- Either way, both directories are wiped and rebuilt at the *start* of every run, so a previous failed run can never affect the next one.

To add new test cases (fixture files or whole new scenarios), see the module docstring at the top of `full_script_test.py` — it documents both extension points in detail.

Add `test_project/` and `test_results/` to `.gitignore` as well, in case a failed run ever leaves them behind.

---

## Revision History

- **2026-06-19** — Initial version.
- **2026-07-03** — Added `EXPLICIT_FILES` config (bare name / `./` / `/` / `~/` forms), empty-string `BASE_EXTENSIONS` entry for extension-less files, recursive `"./"` `SOURCE_DIRS` entry, default dot-exclusion for hidden files/directories, `full_script_test.py` acceptance test suite, and `-h`/`--no-cleanup`/`--clean-up` command line options.
- **2026-08-15** – Modified for use with any AI agents; self-description improved; creates a separate instruction file for AI agents

---

## License

MIT License

Copyright (c) 2025 Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
