*Stand: 2026-09-02*

*Diese Datei ist das Gegenstück zur `CLAUDE-snippet.md` anderer Skills: Sie trägt den Baustein, der bei der Installation an seinen Wirkort übernommen wird — hier aber nicht in eine `CLAUDE.md`, sondern in eine `settings.json`. Übernommen wird **alles unterhalb der Trennlinie**; dieser Text darüber bleibt zurück. Die Datei selbst bleibt im Skill-Ordner liegen und zeigt an ihrer Datumszeile, von welchem Stand der übernommene Eintrag ist.*

*Der Block ist so gebaut, dass beim Standard-Ablageort `~/.claude/skills/` **nichts anzupassen ist**: `$HOME` löst die Shell auf, die das Hook-Kommando ausführt. Hast Du woandershin entpackt, ersetze den Pfad durch den absoluten Pfad Deines Skripts. Er muss danach stabil bleiben — wird der Ordner umbenannt oder verschoben, bricht der Hook **still**, denn Fehler eines Hooks landen nur im Debug-Log.*

*Zu beachten, weil `settings.json` JSON ist und kein Fließtext: Der Block wird nicht angehängt, sondern **eingefügt**. Hat Deine Datei schon einen `hooks`-Schlüssel, kommt `SessionStart` als Geschwister der vorhandenen Ereignisnamen hinein, nicht als Ersatz des ganzen Objekts; hat sie schon ein `SessionStart`-Array, kommt der Eintrag als weiteres Element hinein. Eine kaputte `settings.json` lässt Claude Code den Hook stillschweigend ignorieren.*

*Wohin: `~/.claude/settings.json` gilt für alle Projekte, `<projekt>/.claude/settings.json` nur für dieses eine. Ohne diesen Eintrag bleibt die Fähigkeit über `/recall-skills-after-compact` von Hand aufrufbar; der garantierte Auslöser bei jeder Kompression fehlt dann.*

*Probe vorab, ohne auf eine Kompression zu warten — sie fängt genau den Fehler ab, der sonst still bleibt:*

```bash
python3 $HOME/.claude/skills/recall-skills-after-compact/recall_skills_after_compact.py \
  "$(ls -t ~/.claude/projects/*/*.jsonl | head -1)"
```

*Kommt eine Liste oder die Meldung „No Skill tool invocations found", stimmen Pfad und Skript. Kommt „No such file or directory", zeigt der Eintrag ins Leere.*

*Die eigentliche Probe danach: In einer Sitzung, in der schon mindestens ein Skill geladen wurde, `/compact` ausführen. Die Liste der zuvor geladenen Skills muss auftauchen und von Claude vorgelegt werden.*

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
            "command": "python3 $HOME/.claude/skills/recall-skills-after-compact/recall_skills_after_compact.py"
          }
        ]
      }
    ]
  }
}
```
