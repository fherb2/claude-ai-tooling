# 🚧 web-code-artefacts — Umgang mit Code-Artefakten im Web-Frontend

*Stand: 2026-08-23*

Regelt, wann Code als Artefakt entsteht und wann als Änderungsanweisung im Chat, und in welcher Form Änderungen an bereits übernommenem Code mitgeteilt werden (Vorher-/Ersetzen-mit-Codeblock, keine Zeilennummern).

**Status:** Rohfassung. Der Inhalt ist eine unveränderte Übernahme aus einer `CLAUDE.md` des Nutzers — bisher nur eine Aufzählung, kein Frontmatter, keine `description`, keine Gliederung. Als Skill damit noch nicht lauffähig: Ohne `name` und `description` gibt es weder Auffindbarkeit noch Aufruf über `/web-code-artefacts`.

**Offen:**

- Frontmatter anlegen (`name`, `description`, `license`); die `description` nach Kapitel 2 der Vorgaben formulieren — dritte Person, Hauptanwendungsfall vorn.
- Den Text in Abschnitte gliedern und vom Ich-Ton der Vorlage („ich entscheide", „sage mir also") auf die Anrede an Claude umstellen.
- Entscheiden, ob der Skill einen stillen Trigger braucht. Der Auslöser — es entsteht Code im Web-Frontend — ist eine Umgebungsbedingung, keine Anfrage; die reguläre Description erreicht ihn womöglich nicht.
- Klären, ob der Skill überhaupt in Claude Code gehört: Artefakte gibt es dort nicht. Möglicherweise ist sein Zielort ausschließlich claude.ai.
- In die Gesamt-README aufnehmen.
