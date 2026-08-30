# web-code-editing — editing code on claude.ai

*Last updated: 2026-08-30*

*[Deutsche Fassung](README.md)*

**✅☑ Finished and usable.** Skill text in both languages, frontmatter set; trying it out as an uploaded skill is still ahead (see "State and open points"). — Usable for claude.ai / Claude Desktop (Chat + Cowork).

**The skill governs creating and changing code on claude.ai for an existing project** — with three cores: secure the sources completely before writing; return changed files mechanically as downloads instead of re-dictating them from context; small changes as a before/replace scheme in the chat. It is **for claude.ai only** (target world "web only", `skill-dev-doc.md` chapter 9.4): in Claude Code the Edit tool writes straight into the files, so none of this is needed there.

## Installation

Custom skills reach claude.ai as a ZIP via the skill settings (Pro/Max/Team/Enterprise, code execution enabled). One language version is chosen — `SKILL.de.md` or `SKILL.en.md` — and it goes into the ZIP renamed to `SKILL.md`. The ZIP is named `web-code-editing.zip`: claude.ai adopts the ZIP file name as the skill name. No further files belong to it; the READMEs are not needed inside the ZIP.

## Details

**The most important sentence of the skill is the one about `/mnt/project/`, and it exists because of a false self-report.** In the test of 28 August 2026 the instance at first denied — convinced, and with detailed reasoning — being able to access project knowledge files as files; only the developer's concrete script suggestion brought the correction: the files sit mounted under `/mnt/project/`. Without the explicit instruction, the next instance denies it again. The skill is the countermeasure.

**The mechanical return path is proven on a real project** (28 August 2026, project knowledge holding a packed code base of 39,898 lines): a 753-line file extracted exactly by its marker lines, one line inserted, proven by `diff` (`1a2`, rest bit-identical), offered as a download and shown as an artifact at the same time. Hence: extract, change by replacement, download plus diff — nothing passes through the answer, nothing gets re-dictated.

**The skill does not presuppose any particular form of the project knowledge.** Individual files, an archive, or a bundle file with whatever marker scheme — the agent first checks what is there, recognizes a marker scheme from the file's own header and a sample, and asks the user when it is not recognizable beyond doubt. The tool `pack-source-to-txt` of this repository is the way it *suggests* to the user when many files are needed — not a prerequisite.

**The paths `/mnt/project/` and `/mnt/user-data/outputs` are observation, not a promise.** Anthropic can change them; that is why the skill instructs to report their absence instead of quietly falling back to search.

**The artifact rule is deliberately worded timelessly.** The old version ("do not change artifacts any more") came from 2025 frontend errors that could destroy artifacts. The lasting reason is a different one: as a rule the user has long taken the content over into their code — the valid version sits with them, and a changed artifact would be a second truth.

**Within one chat, the shared code base is the normal case** (determination of the developer, 29 August 2026): the user takes produced code into their project right away and does not re-upload every intermediate state. Questions are asked on well-founded doubt — not routinely.

**Origin:** The skill processes items T8–T11 of the instruction inventory (artifact mechanics from the claude.ai project instructions of 2025/26) — checked against the frontend state of August 2026 rather than taken over: T11 (partial artifacts) was already obsolete within the sources and is gone without replacement, T9 is re-founded timelessly, T10 (before/replace scheme) lives on as the chat scheme. T6/T7 (announce, settle questions beforehand) stand at the beginning as "Before you write".

## State and open points

**Status:** Skill text finished in both language versions and talked through with the developer (29 August 2026). The load-bearing statements about the mechanics are proven on the live system (see Details).

**Open:**

- **Trying it out as an uploaded skill** — the text was developed against a real project but has never run as a custom skill on claude.ai. That will also settle the open check from `skill-dev-doc.md` 1.4 (does an uploaded skill pull bundled files — not needed here, but measurable).
- **A trigger paragraph for the instructions field** (global or per project) — whether the `description` alone fires reliably is what the trial will show.
- **Check on prompt attachments:** whether files attached to the prompt additionally sit as files in the execution environment (and would thus be readable exactly by code) is unverified — until then the skill treats them as a context source.
