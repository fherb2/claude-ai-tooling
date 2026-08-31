*Stand: 2026-08-31*

# Planung

Wenn Du etwas planst, wobei hier nicht wiederkehrende Aufgaben gemeint sind, und der Ablageort der Planung nicht klar geregelt ist, frage den Nutzer, ob er die Planung

- als Chat-Output,
- als File im Projekt oder
- als Planungsfile in `~/.claude`

erstellt haben möchte.

# Memory/Speicher

Wenn Du Informationen im Memory-Bereich ablegen willst und die folgende Fragestellung noch nicht geklärt ist, frage den Nutzer, ob

- Du das in Deinem eigenen Memory-Bereich ablegen darfst (`~/.claude`),
- Du es im Projekt ablegen sollst (`<projekt>/.claude` oder an einen anderen Ort)
- oder Du es Dir nur im Kontext dieser Sitzung merken sollst.

# Frühere Sitzungen als Quelle

Brauchst Du den Verlauf einer früheren Chat-Sitzung — wann etwas entschieden wurde, in welcher Reihenfolge und mit welcher Begründung —, oder möchtest Du Fakten früherer Chat-Sitzungen recherchieren, die nicht außerhalb der Sitzung notiert wurden, dann durchsuche die Protokolle unter `~/.claude/projects/<projektpfad-mit-bindestrichen>/`: eine JSONL-Datei je Sitzung. Datiere sie über den ersten Zeitstempel im Inhalt und nicht über die Dateizeit, die eine Synchronisation zwischen Rechnern verschiebt.
