# 🚧 translation-task — Übersetzung software-entwicklungsnaher Dokumente

*Stand: 2026-08-25*

**🚧 In Arbeit.** Einsetzbar, aber noch nicht abgenommen: Fünf Festlegungen in der `SKILL.md` sind noch offen (siehe „Stand und Offenes" am Ende).

Übersetzt Dokumente mit softwareentwicklungsnahem Inhalt — README-Dateien, Konzept- und Implementierungsdokumente, Anleitungen. Kein allgemeiner Übersetzer: Er ist auf Texte ausgelegt, in denen Fachbegriffe, Codeblöcke, Dateinamen und Software-Produktnamen zwischen Prosa stehen und je eigenen Regeln folgen. Auf eine Sprachrichtung ist er nicht festgelegt.

Vor der Arbeit klärt er Zielsprache und Fachjargon-Grad und legt eine Arbeitsprobe vor, statt gleich das ganze Dokument zu übersetzen. Danach hält er sich an feste Regeln für die drei Dinge, an denen eine Fachübersetzung üblicherweise scheitert: Codeblöcke, Eigennamen und die Einheitlichkeit der Begriffe.

## Installation

1. **Zielort wählen.** Der Skill gilt entweder für alle Projekte des Nutzers oder nur für eines:


   | Ort         | Pfad                                 | Gilt für                 |
   | ----------- | ------------------------------------ | ------------------------- |
   | Persönlich | `~/.claude/skills/translation-task/` | alle Projekte des Nutzers |
   | Projekt     | `.claude/skills/translation-task/`   | nur dieses Projekt        |
2. **Ordner `translation-task/` unter seinem unveränderten Namen kopieren.** Er enthält `SKILL.md` und diese `README.md`. Ein Sprachkürzel trägt bisher keine der beiden Dateien, weil es nur die deutsche Fassung gibt; die `SKILL.md` heißt also schon so, wie Claude Code sie erwartet, und muss nicht umbenannt werden. Sobald die englische Fassung dazukommt, heißen die Dateien `SKILL.de.md` und `SKILL.en.md` — dann wird genau eine davon kopiert, und ihr Kürzel entfällt dabei.
3. **Die Auslösung** geht vom Nutzer selbst aus („übersetze mir das") und wird von der regulären `description` erreicht. Unabhängig davon lässt sich der Skill jederzeit mit `/translation-task` aufrufen.

## Details

**Der Ablauf einer Übersetzung.** Zuerst klärt der Skill Zielsprache und Fachjargon-Grad. Dann legt er eine Arbeitsprobe vor — höchstens ein Drittel des Dokuments und höchstens rund 1000 Wörter —, damit über Ton und Begriffe entschieden werden kann, bevor der ganze Text übersetzt ist. Erst danach folgt die vollständige Übersetzung.

**Codeblöcke.** Übersetzt werden sie nur, wenn sie erkennbar illustrativ sind und keine echte Quelle im Projekt haben. Der Skill sucht dafür projektweit nach einer solchen Quelle. Genau diese Suche ist der Grund, warum echter Werkzeug-Output nicht versehentlich übersetzt wird — wer die Regeln erweitert, sollte sie deshalb nicht vereinfachen.

**Eigennamen und wörtliche Marker.** Eigennamen, Produktnamen und Marker wie `@Claude:` bleiben immer unangetastet.

**Das Glossar.** Begriffsentscheidungen wandern in eine Datei `glossar.md` im Skill-Ordner; sie ist der vorgesehene Ort für eigene Festlegungen und wächst im Betrieb.

**Umgebungserkennung.** Der Skill erkennt selbst, ob er lokal in Claude Code oder in claude.ai läuft, und führt das Glossar nur lokal. In claude.ai erwähnt er es gar nicht erst, statt eine Datei zu versprechen, die niemand wiederfindet.

## Stand und Offenes

**Status:** Anweisungen vollständig, Frontmatter gesetzt. Die Erprobung am Zielort findet statt, wenn der Skill dort gebraucht wird.

**Offen:** Fünf Festlegungen stehen noch aus; sie sind in der `SKILL.md` unter „Noch nicht festgelegt" benannt. Der Schritt dazu steht im [Fahrplan](../../work-plan.md).

**Bewusst offen gelassen:** Das Glossar wird nicht mitgeliefert. Es entsteht im Betrieb und ist projektabhängig; eine leere Vorlage würde nur suggerieren, es gäbe einen Startbestand.
