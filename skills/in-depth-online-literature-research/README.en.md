# in-depth-online-literature-research — research that does not give up too early

*Last updated: 2026-08-30*

**✅☑ Finished and usable.** Instructions complete, frontmatter set, German and English version available. No silent trigger needed (reasons under "Details"). — No difference in content between the version for claude.ai / Claude Desktop (Chat + Cowork) and Claude Code.

**Turns a web search into a procedure: Claude systematically varies search terms, channels and search levels, checks every claim against the primary source, and reports the search paths still open instead of "nothing found".** The occasion for it is a recurring experience: the general web search reliably finds mass-content sites, but specialist articles, association publications and regional sources in particular disappear behind whatever is linked most often — and the summaries the search engines supply along the way invent details that appear on none of the linked pages.

Against this the skill sets three things. First, the **duty to verify**: whatever stands only in a search summary counts as unconfirmed until the page carrying it has been fetched and the statement seen there; every finding is marked as *verified*, *unconfirmed* or *own model knowledge*. Second, **six search operators** as a mandatory repertoire — reformulate (including into other languages), narrow down onto a productive website, change level (do not search for the document but for the register that lists it), follow entities such as authors and journals, change channel, verify. Third, the **frontier report**: if the search stays unsuccessful, "nothing found" is not an admissible answer; instead Claude lists what was tried and which search paths are still open — which puts the decision to stop with the user, not with Claude's fatigue.

Three conveniences come on top. Before larger pieces of research the **search depth** is agreed (quick answer, thorough, exhaustive), because an exhaustive search costs noticeable time and context. An optional **source map** in the project collects niche sources that have proven themselves. And the **result** is presented in the chat first; whether and where it gets saved is the user's decision.

The skill applies to **every kind of research** — literature, facts, documents, evidence — not only to software topics. It is **not** meant as a procurer of the unreachable: what lies behind a paywall, is offline or was never captured will not be found by this procedure either; it merely names such cases cleanly instead of papering over them. Nor does it govern whether and where research results are stored permanently — the user decides that case by case.

## Installation

### Claude Code

1. **Download the package.** `downloads/in-depth-online-literature-research_en_local.zip`

2. **Unpack it.** The archive contains a folder `in-depth-online-literature-research/` with all the files. Unpack it into `~/.claude/skills/` — then the skill applies to all projects — or into `.claude/skills/` in the project, then only there. An existing folder of the same name is replaced; nothing old is left behind.

### claude.ai and Claude Desktop (Chat + Cowork)

1. **Download the package.** `downloads/in-depth-online-literature-research_en_web.zip`

2. **Upload it.** Upload the archive in the application's management area for skills. The skill then applies to your account — not to your organization, and not at the same time in Claude Code.

There is no silent trigger here: the skill fires through its `description` or is called with `/in-depth-online-literature-research`; the reasoning is under "Details". Both packages carry the same content — they are separate only so that the name says where the archive belongs. The source map falls away wherever there is no file access.

## Details

**The duty to verify is the core, not an addition.** It holds at every depth level, including the quick answer. Whoever weakens it while adapting the skill gets back exactly what the skill was built against: convincing-sounding figures and quotations that stand in no source.

**The self-test before delivery.** Immediately before answering, Claude goes through every finding marked *verified* and checks whether the source carrying it was actually fetched during this run; otherwise it is fetched now or downgraded to *unconfirmed*. This is not ornament: in a collection search with more than twenty findings it was measurable how labelling discipline slips — several entries carried "verified" although their source had never been fetched. With single questions the rule rarely bites, with lists almost always.

**Why there is no fixed number of search attempts.** Nobody knows in advance how many runs are needed. The stopping criterion is therefore not a counter but a state: the search ends when something was found, when the frontier is empty, or when the user stops it. The obligation to write down the list of open search paths at all incidentally forces the strategies to be thought through — the form of accounting produces the search behaviour. Simplify it to "try hard" and nothing of it remains.

**Changing level is the most productive operator** and at the same time the one that does not happen without an explicit instruction: do not search for the article, but for the register of the journal, the publication series of the learned society, the library catalogue. In the trials this was the move that found a source which the general search could not deliver even with the exact title.

**The source map belongs in the project, not in the skill folder.** A globally growing map would carry subject-foreign sources into every new piece of research and dilute it; after an installation there would moreover be two versions drifting apart. Binding it to the project keeps it thematically clean by itself. The price is accepted deliberately: no automatic transfer of learning between projects.

**Why no silent trigger.** The trigger as a rule stands in the request itself ("research", "find a source", "substantiate"), and in the trials the skill fired on Sonnet — the least sensitive target model — without any addition to the `CLAUDE.md`. One gap remains: a question that sounds harmless at first and turns out to be difficult only in the middle of the work may escape the trigger, because the skill selection happens at the beginning of a turn. Whoever notices this in daily use adds a `CLAUDE.md` paragraph binding to the first web search as an action.

**What the environment cannot do.** The fetching tool upgrades `http://` addresses to `https://` unconditionally. Plain HTTP legacy sites — no rarity among association and private pages — are unreachable as a result. The skill does not lose such findings, but correctly downgrades them to *unconfirmed* and names the reason; a glance with one's own browser then settles them in seconds.

## State and open points

**Status:** Finished and ready for use. The German version was written on 23 August 2026 and tried out in two content tests — a hard case of finding (a specialist article the general search does not deliver) and an open collection search in an unfamiliar subject field and an unfamiliar language; both passed, and from the second came the self-test against slipping labelling discipline. The English version was written on 24 August 2026 as a translation of the German one.

**Open:** Two trials are still outstanding — measuring the effectiveness of the self-test, and the claude.ai branch of the result handover. The steps for them are kept in the [work plan](../../work-plan.md) (in German). Both concern the safeguards, not usability: the skill is finished and ready for use.

**Deliberately left open:** Whether a source map is kept, where it lies within the project, and whether a project keeps several of them, is decided by the user in the target project — the skill prescribes neither location nor cut. Splitting into several maps is only worthwhile once a project demonstrably houses two subject-foreign strands of research.
