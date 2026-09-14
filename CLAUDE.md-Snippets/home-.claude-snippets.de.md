*Stand: 2026-09-02*

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

# Sandbox

Scheitert ein Dateizugriff mit „Das Dateisystem ist nur lesbar" oder „Keine Berechtigung", obwohl der Pfad im freigegebenen Bereich liegt, ist die wahrscheinlichste Ursache nicht das System des Nutzers, sondern die Sandbox: Sie schützt bestimmte Pfade — ihre eigene Konfiguration (`settings.json`, `skills/`, `hooks/`) und Geheimnisorte — indem sie sie schreibgesperrt einhängt oder ganz maskiert. Die erste Meldung heißt dann „schreibgeschützt", die zweite „für Dich unsichtbar"; beide klingen nach Defekt oder Rechteproblem und sind doch nur Regel.

**Das Entscheidende: Diese Einhängungen gelten nur für Dich.** Was `mount` Dir zeigt, beschreibt Deinen Sandbox-Namensraum, nicht den Rechner. Der Nutzer sieht denselben Pfad ungehindert und kann ihn ändern oder löschen. Gib solche Beobachtungen deshalb nie als Aussage über sein System aus, sondern benenne den Verdacht als das, was er ist, und frage ihn — er sieht die andere Hälfte.

# Frühere Sitzungen als Quelle

Brauchst Du den Verlauf einer früheren Chat-Sitzung — wann etwas entschieden wurde, in welcher Reihenfolge und mit welcher Begründung —, oder möchtest Du Fakten früherer Chat-Sitzungen recherchieren, die nicht außerhalb der Sitzung notiert wurden, dann durchsuche die Protokolle unter `~/.claude/projects/<projektpfad-mit-bindestrichen>/`: eine JSONL-Datei je Sitzung. Datiere sie über den ersten Zeitstempel im Inhalt und nicht über die Dateizeit, die eine Synchronisation zwischen Rechnern verschiebt.
