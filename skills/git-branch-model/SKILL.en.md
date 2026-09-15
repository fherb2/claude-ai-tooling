---
name: git-branch-model
description: Governs the branching model of a Git project — a development branch as the main line, a release branch for the published state, topic branches per task, and a management branch for files that must be identical on every branch (the project CLAUDE.md, editor and tool configuration, .gitignore), distributed by overlaying instead of merging. Use as soon as something is to go into the release or onto master, a branch is created or merged, a central file of the project is to be changed, or the project keeps the file .claude/git-branch-model.json, or when the user calls /git-branch-model.
license: CC0-1.0
---

# Branching model of a Git project

This file only establishes whether the branching model holds in this project; the roles, procedures and rules live in a rules file of the same folder and are loaded only once it holds or is to be set up. The split is deliberate: the skill also fires in projects that keep no branching model, and then the context stays free.

## Establish the situation

1. **The project keeps the branching model** — recognizable by the file `.claude/git-branch-model.json`; the branch names, the kind of release transfer and the list of management files are in that file, not in the skill. **Then read `${CLAUDE_SKILL_DIR}/rules.en.md` in full and work by it from then on.** If no file of that name is there, look in the skill folder for whichever rules file exists — it may have been renamed during installation. Until you have read it, execute no writing Git command.
2. **No branching model, but an occasion** — the user wants to bring something into the release, merge a branch or change a central file. Then offer the initial setup of the model — in two sentences and without pushing, since it changes their way of working. If they want it, read the rules file as in case 1: the initial setup is in there.
3. **Neither:** this skill then demands nothing, and the rules file is not loaded.

## Explain, do not presume

When this skill takes effect in a project for the first time — at the initial setup, or at the first intervention the user did not ask for themselves — say in a few sentences what the model does and what you are about to do. The user may simply have installed the skill and be watching what happens. For everything beyond that, the README lies in this skill's folder: name it as the reference and quote from it when asked, instead of reconstructing. Its file name is not reliable — look in the folder; if you do not find it, answer without it.
