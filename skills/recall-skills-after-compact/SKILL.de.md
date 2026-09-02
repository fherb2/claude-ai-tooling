---
name: recall-skills-after-compact
description: Listet auf Zuruf, welche Skills in der laufenden Sitzung bereits über das Skill-Werkzeug geladen wurden — dasselbe Skript, das der zugehörige SessionStart-Hook nach jeder Kontext-Kompression automatisch ausführt. Aufruf durch den Nutzer mit /recall-skills-after-compact.
disable-model-invocation: true
license: CC0-1.0
---

# Geladene Skills dieser Sitzung auflisten

Führe das Skript dieses Ordners mit dem Transkriptpfad der laufenden Sitzung aus und trage das Ergebnis dem Nutzer vor. Lade keinen Skill selbständig nach — die Entscheidung liegt beim Nutzer.

**Den Transkriptpfad bestimmst Du so** (Aufbau belegt in der Sessions-Doku): `~/.claude/projects/<projekt>/<session-id>.jsonl`, wobei `<projekt>` der Pfad des Arbeitsverzeichnisses mit `-` anstelle aller nicht-alphanumerischen Zeichen ist. Kennst Du Deine Session-ID — sie taucht etwa im Scratchpad-Pfad auf —, nimm die Datei dieses Namens. Sonst nimm die zuletzt geänderte `.jsonl` des Ordners: Die laufende Sitzung wächst mit jedem Zug, ihre Datei ist praktisch immer die jüngste.

```bash
python3 "${CLAUDE_SKILL_DIR}/recall_skills_after_compact.py" <transkriptpfad>
```

Meldet das Skript „No Skill tool invocations found", wurden in der Sitzung bisher keine Skills über das Skill-Werkzeug aufgerufen — sag das so, statt es zu deuten. Gezählt werden nur echte Skill-Werkzeugaufrufe der Hauptkonversation; anders in den Kontext gelangte Regeln (etwa eine direkt per Read geladene Datei) erfasst die Liste nicht.
