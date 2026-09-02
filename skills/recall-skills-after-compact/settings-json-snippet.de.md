*Stand: 2026-09-02*

*Diese Datei ist das Gegenstück zur `CLAUDE-snippet.md` anderer Skills: Sie trägt den Baustein, der bei der Installation an seinen Wirkort übernommen wird — hier aber nicht in eine `CLAUDE.md`, sondern in eine `settings.json`. Übernommen wird **alles unterhalb der Trennlinie**; dieser Text darüber bleibt zurück. Die Datei selbst bleibt im Skill-Ordner liegen und zeigt an ihrer Datumszeile, von welchem Stand der übernommene Eintrag ist.*

*Zwei Dinge unterscheiden diesen Baustein von einem CLAUDE.md-Schnipsel, und beide muss man wissen, bevor man ihn einsetzt:*

*1. **`settings.json` ist JSON, kein Fließtext** — der Block wird nicht angehängt, sondern **eingefügt**. Hat Deine Datei schon einen `hooks`-Schlüssel, kommt `SessionStart` als Geschwister der vorhandenen Ereignisnamen hinein, nicht als Ersatz des ganzen Objekts. Hat sie schon ein `SessionStart`-Array, kommt der Eintrag als weiteres Element hinein. Eine kaputte `settings.json` lässt Claude Code den Hook stillschweigend ignorieren.*

*2. **Der Pfad muss angepasst werden** — er zeigt auf das Skript in dem Ordner, in den Du das Paket entpackt hast. Steht das Paket unter `~/.claude/skills/`, ist der Pfad unten bis auf `<user>` richtig. Der Pfad muss anschließend stabil bleiben: Wird der Ordner umbenannt, bricht der Hook **still** — Fehler eines Hooks landen nur im Debug-Log.*

*Wohin: `~/.claude/settings.json` gilt für alle Projekte, `<projekt>/.claude/settings.json` nur für dieses eine. Ohne diesen Eintrag bleibt die Fähigkeit über `/recall-skills-after-compact` von Hand aufrufbar; der garantierte Auslöser bei jeder Kompression fehlt dann.*

*Zur Probe: In einer Sitzung, in der schon mindestens ein Skill geladen wurde, `/compact` ausführen. Danach muss die Liste der zuvor geladenen Skills auftauchen und von Claude vorgelegt werden.*

---

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "compact",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /home/<user>/.claude/skills/recall-skills-after-compact/recall_skills_after_compact.py"
          }
        ]
      }
    ]
  }
}
```
