---
name: common-code-generation
description: Rules for writing and changing code — English identifiers, no unrequested extension of the functional scope, careful use of processing time and memory; names and optimizations are proposed, not decided. Use before code is written or changed for the first time in a session, or before an optimization is proposed, or when the user calls /common-code-generation. The rules do not apply to ongoing promotions on the CLI or in Scratch.
license: CC0-1.0
---

# General rules for writing code

## Scope and boundaries

These rules apply as soon as code is written or changed in a session — and from then on throughout, not only for the step that triggered them.

Not covered by these rules:

- The obligation to present a plan before changing a file and to wait for approval. It belongs in the project's `CLAUDE.md` and stays there: a skill is only likely to be loaded, whereas a safeguard has to take effect reliably.
- The structure of concept and implementation documentation, and the handling of temporary debug code. There are separate skills for those.
- These rules do not apply to code that is intended to be executed directly on the command line for ongoing actions or that is used to complete tasks in Scratch.

## Language and naming in source code

Everything that appears in the source code — identifiers, comments and docstrings — you write in English.

When you name parts of the code yourself, then:

- propose them to the user for decision, in a clearly arranged form
- short, accurate terms are better than long ones
- build "self-documenting code" as far as the styling rules allow
- always treat the applicable code styling rules as taking precedence, and draw the user's attention to it when they want to break them. The user always has the last word, though, and ranks above the styling rules.

## Writing code in general

Produce only the code that is strictly necessary for the task at hand, and no extensions or improvements you thought up yourself. Nice-to-have features, and improvements to software quality that have not been explicitly agreed, can still be added afterwards. Propose such extensions and improvements early, during planning, to the developer. What of them is taken over, and in what form, is their decision.

Never extend the functional scope already realized in the code unless this has been settled with the user in detail beforehand.

## Resource-efficient coding

The most important resources are generally:

- processing time, especially in
  - loops
  - frequently called functions
  - I/O operations (waiting for hardware, or for information passing between parts of an application or between systems)
- main memory
- mass storage

You can infer further resources from the context, or the user names them explicitly.

Where optimizations of different resources work against each other, ask the user for the priority and give them the information needed to decide.

Where several options are available that improve resource efficiency appreciably, put them forward before you implement.

Your base knowledge already holds every trick and technique for optimizing code. Use that potential in every development task. Before you propose optimization variants while writing code, however, check the gain achieved against reality, so that you only put forward viable proposals:

- Is the optimization, and the coding effort it costs, worth it in the real use case of this software? That is always the central question, and the limiting factor need not be the coding effort alone — the increased likelihood of building in undetected errors counts as well.
  If you want to answer this question for yourself, you may find that you still know far too little about the use case, and perhaps about the intended structure of the software. Try to assess your own state of knowledge first. So: how is the software meant to be used? What hardware will the application run on? Are there communication paths to other hardware to take into account? Do you already know most of what the software is meant to contain in its final state? Ask when you have gaps that bear on this optimization option. It may also be that the user does not yet know precisely. – If the ongoing planning and coding process has already put you very much in the picture, you can also simply turn to the user in between and describe what you propose as an improvement, but always name the knowledge your recommendation rests on. The user may be much further along in planning that has never been written down, and in the light of those facts your optimization proposal may be pointless or impractical.
- How much optimization is achievable compared with the parts of the program that cannot be optimized further? Meaning: is the effect of the optimization relevant at all on the scale of the application as a whole? If it is not, you build yourself extra effort and extra opportunities for error with no real benefit.

### Prior knowledge in loops

When you are asked to program loops in which more than one break criterion for a single pass occurs at the start or partway through, try to work out — from your understanding of the application's task and of the data to be processed — how you can arrange these decisions and the code that follows them so that, averaged over the passes, an early decision ends the pass and the total processing time of the loop is thereby minimized. This requires prior knowledge about the data to be processed. If you do not have that knowledge, ask the user whether they can support the optimization with it.

With such loops, remember that compilers do not translate code into machine code in the order in which it appears in the source. Point out to the user how they can influence the compiler so that the optimization can be guaranteed by the order of decision processes alone (compiler directives, arguments …).
