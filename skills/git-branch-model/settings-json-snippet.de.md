*Stand: 2026-09-16*

*Diese Datei ist das Gegenstück zur `CLAUDE-snippet.md` desselben Skills — und sie ersetzt sie nicht, sondern ergänzt sie: Der stille Trigger in der `CLAUDE.md` deckt die Anlässe ab (Release, Zweig anlegen oder zusammenführen, zentrale Datei ändern); der Hook hier deckt den einen Fall, in dem der Trigger bei manchen Modellen nicht zieht — das erste schreibende Git-Kommando in einem Projekt mit `.claude/git-branch-model.json`. Übernommen wird **alles unterhalb der Trennlinie**, nicht in eine `CLAUDE.md`, sondern in eine `settings.json`; dieser Text darüber bleibt zurück. Die Datei selbst bleibt im Skill-Ordner liegen und zeigt an ihrer Datumszeile, von welchem Stand der übernommene Eintrag ist.*

*Was der Hook tut: Vor jedem `git commit`, `push`, `checkout`, `restore`, `reset` oder `merge`, das Claude ausführen will, prüft er, ob das Projekt die Datei `.claude/git-branch-model.json` führt. Wenn ja, legt er der Instanz einen Satz in den Kontext: dass der Skill `git-branch-model` zu konsultieren ist. Er blockiert nichts und führt selbst nichts aus — die Entscheidung bleibt bei der Instanz, nur der Hinweis kommt garantiert an. Fehlt die Datei oder ist das Kommando nur lesend, schweigt er.*

*Der Block ist so gebaut, dass beim Standard-Ablageort `~/.claude/skills/` **nichts anzupassen ist**: `$HOME` löst die Shell auf, die das Hook-Kommando ausführt. Hast Du woandershin entpackt, ersetze den Pfad durch den absoluten Pfad Deines Skripts. Er muss danach stabil bleiben — wird der Ordner umbenannt oder verschoben, bricht der Hook **still**, denn Fehler eines Hooks landen nur im Debug-Log.*

*Zu beachten, weil `settings.json` JSON ist und kein Fließtext: Der Block wird nicht angehängt, sondern **eingefügt**. Hat Deine Datei schon einen `hooks`-Schlüssel, kommt `PreToolUse` als Geschwister der vorhandenen Ereignisnamen hinein, nicht als Ersatz des ganzen Objekts; hat sie schon ein `PreToolUse`-Array, kommt der Eintrag als weiteres Element hinein. Eine kaputte `settings.json` lässt Claude Code den Hook stillschweigend ignorieren.*

*Das Feld `if` schränkt den Hook auf Git-Kommandos ein, damit er nicht bei jedem Bash-Aufruf läuft. Kennt Deine Claude-Code-Version das Feld nicht, lässt Du es weg — der Hook läuft dann bei jedem Bash-Kommando, prüft aber selbst, ob es ein schreibendes Git-Kommando ist, und schweigt sonst. Es kostet dann nur einen Skriptstart mehr je Kommando.*

*Wohin: `~/.claude/settings.json` gilt für alle Projekte, `<projekt>/.claude/settings.json` nur für dieses eine. Ohne diesen Eintrag wirkt der Skill nur über den stillen Trigger und den Aufruf `/git-branch-model`; der garantierte Hinweis vor dem ersten schreibenden Git-Kommando fehlt dann.*

*Probe vorab, ohne auf ein echtes Git-Kommando zu warten — sie fängt genau den Fehler ab, der sonst still bleibt. Im Wurzelordner eines Projekts **mit** `.claude/git-branch-model.json` ausführen:*

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"git commit -m probe"},"cwd":"'"$PWD"'"}' \
  | python3 $HOME/.claude/skills/git-branch-model/notify_branch_model.py
```

*Erwartet: eine JSON-Zeile mit `additionalContext` und dem Skill-Namen. Dieselbe Probe in einem Ordner **ohne** die Datei muss nichts ausgeben. Kommt „No such file or directory", zeigt der Eintrag ins Leere.*

*Die eigentliche Probe danach: In einer frischen Sitzung eines Projekts mit der Datei etwas committen lassen. Der Skill `git-branch-model` muss geladen werden, bevor das Kommando läuft.*

---

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(git *)",
            "command": "python3 $HOME/.claude/skills/git-branch-model/notify_branch_model.py"
          }
        ]
      }
    ]
  }
}
```
