*Stand: 2026-09-16*

*Diese Datei ist das Gegenstück zur `CLAUDE-snippet.md` desselben Skills — und sie ersetzt sie nicht, sondern ergänzt sie: Der stille Trigger in der `CLAUDE.md` deckt die Anlässe ab (Release, Zweig anlegen oder zusammenführen, zentrale Datei ändern); der Hook hier deckt den einen Fall, in dem der Trigger bei manchen Modellen nicht zieht — das erste schreibende Git-Kommando in einem Projekt mit `.claude/git-branch-model.json`. Übernommen wird **alles unterhalb der Trennlinie**, nicht in eine `CLAUDE.md`, sondern in eine `settings.json`; dieser Text darüber bleibt zurück. Die Datei selbst bleibt im Skill-Ordner liegen und zeigt an ihrer Datumszeile, von welchem Stand der übernommene Eintrag ist.*

*Was der Hook tut: Vor jedem `git commit`, `add`, `push`, `checkout`, `restore`, `reset` oder `merge`, das Claude ausführen will, prüft er, ob das Projekt die Datei `.claude/git-branch-model.json` führt und ob der Skill `git-branch-model` in dieser Sitzung schon geladen wurde (er liest das aus dem Sitzungstranskript, das Claude Code ihm nennt). Ist die Datei da und der Skill noch nicht geladen, **verweigert er dieses eine Kommando** mit der Begründung, zuerst den Skill zu konsultieren — die Instanz lädt ihn daraufhin und wiederholt das Kommando, das dann durchgeht. Die Blockade trifft also höchstens einmal je Sitzung, und der Abgleich der Verwaltungsdateien, den der Skill vorschreibt, läuft **vor** dem ersten Schreiben, nicht danach. Ist der Skill schon geladen, fehlt die Datei oder ist das Kommando nur lesend, schweigt der Hook. Kann er das Transkript nicht lesen, blockiert er nicht, sondern legt nur einen Hinweis in den Kontext — nie eine Sperre auf unsicherer Grundlage.*

*Der Block ist so gebaut, dass beim Standard-Ablageort `~/.claude/skills/` **nichts anzupassen ist**: `$HOME` löst die Shell auf, die das Hook-Kommando ausführt. Hast Du woandershin entpackt, ersetze den Pfad durch den absoluten Pfad Deines Skripts. Er muss danach stabil bleiben — wird der Ordner umbenannt oder verschoben, bricht der Hook **still**, denn Fehler eines Hooks landen nur im Debug-Log.*

*Zu beachten, weil `settings.json` JSON ist und kein Fließtext: Der Block wird nicht angehängt, sondern **eingefügt**. Hat Deine Datei schon einen `hooks`-Schlüssel, kommt `PreToolUse` als Geschwister der vorhandenen Ereignisnamen hinein, nicht als Ersatz des ganzen Objekts; hat sie schon ein `PreToolUse`-Array, kommt der Eintrag als weiteres Element hinein. Eine kaputte `settings.json` lässt Claude Code den Hook stillschweigend ignorieren.*

*Das Feld `if` schränkt den Hook auf Git-Kommandos ein, damit er nicht bei jedem Bash-Aufruf läuft. Kennt Deine Claude-Code-Version das Feld nicht, lässt Du es weg — der Hook läuft dann bei jedem Bash-Kommando, prüft aber selbst, ob es ein schreibendes Git-Kommando ist, und schweigt sonst. Es kostet dann nur einen Skriptstart mehr je Kommando.*

*Wohin: `~/.claude/settings.json` gilt für alle Projekte, `<projekt>/.claude/settings.json` nur für dieses eine. Ohne diesen Eintrag wirkt der Skill nur über den stillen Trigger und den Aufruf `/git-branch-model`; der garantierte Hinweis vor dem ersten schreibenden Git-Kommando fehlt dann.*

*Probe vorab, ohne auf ein echtes Git-Kommando zu warten — sie fängt genau den Fehler ab, der sonst still bleibt. Im Wurzelordner eines Projekts **mit** `.claude/git-branch-model.json` ausführen; das leere Transkript steht für „Skill noch nicht geladen":*

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"git commit -m probe"},"cwd":"'"$PWD"'","transcript_path":"/dev/null"}' \
  | python3 $HOME/.claude/skills/git-branch-model/notify_branch_model.py
```

*Erwartet: eine JSON-Zeile mit `"permissionDecision": "deny"` und der Begründung, die den Skill nennt. Dieselbe Probe in einem Ordner **ohne** die Datei muss nichts ausgeben. Kommt „No such file or directory", zeigt der Eintrag ins Leere.*

*Die eigentliche Probe danach: In einer frischen Sitzung eines Projekts mit der Datei etwas committen lassen. Das erste Git-Kommando muss mit der Begründung des Hooks abgewiesen werden, die Instanz den Skill `git-branch-model` laden und das Kommando dann wiederholen.*

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
