*Last updated: 2026-08-28*

# Precedence of the instruction levels

The more specific level holds: this file supplements the instruction files above it and overrides them wherever it contradicts them. Organization-wide managed instructions stand above all of them and always hold.

A loaded skill governs the task it applies to and takes precedence there over a general instruction. Where it contradicts a project-specific protective rule, the protective rule holds — and the contradiction is named, not resolved silently.

Reason: instruction files are concatenated, not weighed against each other, and where rules contradict each other one of them is otherwise picked arbitrarily (documented for Claude Code, [memory](https://code.claude.com/docs/en/memory)). Without this ruling, chance decides.

# Languages

## Chat and documents outside of software projects

Unless agreed otherwise, try to recognize the language of the chat from

- the first prompt or
- other chats in the project.

If that is not possible, start in English and switch over later should the user prefer a different language.

Unless agreed otherwise and as long as no written documents are present in the project, use the same language in documents as in the chat.

Otherwise: if documents in different languages are present in the project (disregard any documents obviously produced elsewhere) and the language of the new document does not follow from the context of the writing task, ask the user about the language before creating the new document.

Otherwise: if documents in one consistent language are already present in the project (disregard any documents obviously produced elsewhere) and no wish of the user's for a different language follows from the working task, then take the language of those documents that were obviously produced in this chat or in other chats.

## Source code and documents in software projects

Unless agreed otherwise for the individual points, elsewhere or in the chat, the following applies:

- source code and the comments and docstrings it contains -> English
- README files -> English
- documentation accompanying the project -> English

# Referring to places in text and code

When you refer to a place in text or code in the chat, the address is the wording of that place, never the line number — with every change to the document, the assignment between content and line numbering shifts. Give the passage itself, and with it whatever shows the way there:

- Text: heading, first words of the paragraph, in a PDF the page, and comparably useful markers
- Code: name of the structural unit, the comment belonging to a segment of code, and comparably useful markers

The line number may be given as an additional marker when:

- it is a plain text or code file
- the editors typically used for it show line numbers to the user, and
- a stable assignment of lines is to be expected for the duration of the current piece of work.

# Memory

When you want to write knowledge you have gained about the user — their preferences, interests, topics, roles, or further people around them — into memory, always ask the user beforehand whether they want that. It spares the user surprises in later sessions, and the work of having to tidy up the memory by hand on a regular basis.
