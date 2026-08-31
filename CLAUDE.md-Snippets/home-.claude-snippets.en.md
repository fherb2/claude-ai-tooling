*Last updated: 2026-08-31*

# Planning

When you plan something — and recurring tasks are not what is meant here — and it is not clearly settled where the plan is to be kept, ask the user whether they want the plan

- as chat output,
- as a file in the project or
- as a plan file in `~/.claude`.

# Memory

When you want to store information in the memory area and the following question has not been settled yet, ask the user whether

- you may put it into your own memory area (`~/.claude`),
- you should put it into the project (`<project>/.claude` or somewhere else)
- or you should merely remember it within the context of this session.

# Earlier sessions as a source

When you need the course of an earlier session — when something was decided, in what order and on what grounds — then search the transcripts under `~/.claude/projects/<project-path-with-hyphens>/`: one JSONL file per session. Date them by the first timestamp inside the content, not by the file time, which a sync between machines shifts.
