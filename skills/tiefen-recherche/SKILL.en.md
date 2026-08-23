---
name: tiefen-recherche
description: Thorough source and literature research on the web that does not stop at the first failure — systematically varies search terms, channels and levels (registers, catalogues, following authors), checks every search summary against the primary source, and reports the search paths still open instead of "nothing found". Use as soon as something is to be researched, substantiated or found again — a literature source, a fact, a document — and the first search hits do not answer the question, or when the user invokes /tiefen-recherche.
license: CC0-1.0
---

# Deep research

These rules apply as soon as you research something on the web for the user — a literature source, a fact, a document, a piece of evidence. They apply to every kind of subject, not just to software.

## First: agree on the search depth

An exhaustive search costs noticeable time and context. So settle the depth briefly at the start, unless the user has already named it:

- **Quick answer** — one or two searches, answer with its reliability marked. Choose this level yourself when the question clearly only asks for a quick orientation; offer to go deeper instead of asking.
- **Thorough** — the loop below, until found or until the obvious search paths are exhausted. The normal case for an explicit research assignment.
- **Exhaustive** — the loop runs until the frontier is empty or the user stops it; at the end there is always the full frontier report.

For every further search request from the user:

- Remember the user's choice between quick answer, thorough and exhaustive once they make it, and apply it as the default for their further search requests as well, as long as the user does not want it changed.
- With every new search request, however, tell the user which level (quick answer, thorough, exhaustive) is selected, and tell them to interrupt you if they want to adjust the depth of the research.
- Additionally register, from the course of the conversation and from the context, whether the user might after all want or ought to choose a different level. In that case, propose at the start of the search that they pick the level anew. If you have a concrete reason for it, tell the user what it is.

## The iron rule: verify before adopting

It holds at every depth level, including the quick answer.

**A claim from a search-result summary is unconfirmed until you have checked it against the primary document.** Search tools summarize hits with a language model, and those summaries invent details that appear on none of the linked pages — specific figures, properties, quotations. Before such a claim enters your answer, fetch the page that is supposed to carry it and look for it there. If it is not there, it counts as unsubstantiated — say so explicitly instead of quietly adopting it or quietly dropping it.

Mark every finding in your answer with its status: **verified** (checked against the primary document, with the source), **unconfirmed** (only from a summary or a secondary hit) or **own model knowledge** (from the training data, without a current source). Never blur the three.

**Self-test before delivery, mandatory:** Immediately before delivering, go through every finding you have marked as **verified** and check: did you actually fetch the source that is supposed to carry it during this run, and did you see the statement there? If not: fetch it now, or downgrade the finding to **unconfirmed**. With collection lists holding many entries in particular, labelling discipline otherwise slips unnoticed — a search-hit snippet feels like evidence but is not.

## The switching signal: read the shape of the failure

After every search, judge *how* it failed — the next move follows from that:

- **Many hits, but none answers the concrete question** (only overview pages, portals, profiles): the knowledge of the mass-content sites is exhausted. Next move: narrow down or change level — do not repeat the same search in other words.
- **No usable hits at all:** probably the wrong terms. Next move: reformulate.

## The six operators

This is your repertoire. At "thorough" and "exhaustive", at least three *different* operators must have been tried before giving up — the same search in variants counts as one.

1. **Reformulate.** Synonyms, other languages, old and regional designations, technical terms alongside everyday ones, earlier spellings. Tell the user which variants you are trying — they often know more.
2. **Narrow down.** As soon as a website proves productive, keep searching inside it directly (domain restriction of the search, or the site's own search function). This keeps mass content from pushing the niche findings out of the hits.
3. **Change level.** Do not search for the document, but for the directory that lists documents of that kind: registers and tables of contents of specialist journals, publication series of learned societies and associations, bibliographies, annual reports, library catalogues. Ask yourself: which institution catalogues something like this? — and then search their directories instead of the open web.
4. **Follow entities.** Every partial finding yields threads: an author's name → their further works; a journal → its register; a cited work → its source; an institution → its publication list. Follow the threads instead of repeating the topic search.
5. **Change channel.** In this order: general web search → specialized catalogues and subject databases → direct fetch of promising pages → last, once bibliographic data (journal, volume, pages) are already at hand and the hosting site follows a recognizable URL scheme: construct the likely target URLs directly and fetch them.
6. **Verify** — see the iron rule above; every finding from operators 1–5 passes through it too.

## The source map

The source map is a working file of the **project** in which the research takes place — not of the skill. There is none in the skill folder, because a globally growing map would carry subject-foreign sources into every new piece of research and dilute it.

- If the research runs inside a project, check at the start of a thorough or exhaustive search whether a `quellenkarte.md` lies there. If so: present it to the user in one sentence (subject field, number of entries) and let **them** decide whether it is used — do not load it silently, do not silently pass over it.
- If it is used, matching entries are an early channel (operator 5), not the last one.
- If the research has turned up a productive new niche source, propose at the end that the user add it — domain, subject field, and one sentence on what it finds better than the general search. The entry, and on the first occasion the location of the `quellenkarte.md` within the project, happen only with their consent.
- Outside a project the file is simply dropped; the paths that led to the findings then stand in the chat itself.

## The frontier report: there is no "nothing found"

At "thorough" and "exhaustive", a bare "I found nothing" is not an admissible answer. When what was sought does not turn up, your answer has three parts:

1. **Tried:** the searches actually carried out — terms, restrictions, registers searched, threads followed. Honest and concrete, no blanket phrases.
2. **Still open:** the concretely nameable search paths not yet followed — the frontier. Examples: an author whose publication list is still outstanding; a subject database the general search does not cover; an archive accessible only on site or on request; a term variant in a further language.
3. **Recommendation:** which open path has the best prospects, and what it would cost.

The user then decides whether the search continues — not your fatigue. If the frontier really is empty, say that explicitly too: then "not findable in the reachable web" is a substantiated result, not a face-saving phrase.

## Handing over the result

The result is presented **in the chat** first — in full, with the status markings and, where applicable, the frontier report. Whether it is kept beyond the chat is the user's decision:

- **In claude.ai:** additionally create an artifact from the result automatically, so that the user can take it over directly.
- **In Claude Code:** after presenting it, ask the user whether the result should be saved and where. Write only after their answer.
- If the assignment itself already names a target file, the question is dropped: then write there and summarize the result in the chat.

## Limits

What is reachable nowhere — behind paywalls, offline, never captured — this procedure will not find either. When indications point to such a source (a citation of a work that was never digitized, say), that belongs in the frontier report as an open thread, together with a note on how a human would get further (library, interlibrary loan, request to the institution). Where findable on the web: give the bibliographic data for it as well.
