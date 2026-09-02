*Last updated: 2026-09-02*

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

# Sandbox

When a file access fails with "Read-only file system" or "Permission denied" although the path lies inside the released area, the most likely cause is not the user's system but the sandbox: it protects certain paths — its own configuration (`settings.json`, `skills/`, `hooks/`) and credential locations — by mounting them read-only or masking them entirely. The first message then means "write-protected", the second "invisible to you"; both sound like a defect or a permission problem and are nothing but policy.

**The crucial part: those mounts apply to you alone.** What `mount` shows you describes your sandbox namespace, not the machine. The user sees the same path unhindered and can change or delete it. So never present such an observation as a statement about their system; name the suspicion for what it is and ask them — they see the other half.

# Earlier sessions as a source

When you need the course of an earlier chat session — when something was decided, in what order and on what grounds — or when you want to research facts from earlier chat sessions that were never noted down outside the session, then search the transcripts under `~/.claude/projects/<project-path-with-hyphens>/`: one JSONL file per session. Date them by the first timestamp inside the content, not by the file time, which a sync between machines shifts.
