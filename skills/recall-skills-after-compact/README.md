# recall-skills-after-compact — nach der Kompression an die geladenen Skills erinnern

*Stand: 2026-09-02*

*[English version](README.en.md)*

**✅ Fertig und nutzbar.** Skript gegen reale Transkripte und Fehlerfälle getestet; der Praxistest an einer echten Kompression steht noch aus (siehe „Stand und Offenes").

**Nach jeder Kontext-Kompression legt diese Fähigkeit der Instanz — und über sie dem Nutzer — die Liste der in der Sitzung bereits geladenen Skills vor.** Die Entscheidung, ob und welche davon neu geladen werden, bleibt beim Nutzer; es wird nichts selbständig nachgeladen. Dies ist die erste **garantierte Fähigkeit** dieses Repos: Ausgelöst wird sie nicht über einen stillen Trigger, sondern über einen **Hook** — einen Ereignis-Einhänger der Claude-Code-Engine, der bei seinem Ereignis immer läuft. Zusätzlich lässt sie sich jederzeit von Hand aufrufen: `/recall-skills-after-compact` beantwortet mitten in der Sitzung die Frage „welche Skills waren hier schon geladen?" — dasselbe Skript, zweiter Zündweg.

**Warum es sie braucht.** Eine Kompression ersetzt den Gesprächsverlauf durch eine Zusammenfassung. Claude Code spielt danach zwar die `SKILL.md`-Texte aufgerufener Skills automatisch wieder ein — aber gedeckelt (5.000 Token je Skill, 25.000 gesamt, älteste fliegen zuerst) und **ohne** die nachgeladenen Regeldateien, die bei zweigeteilten Skills die eigentlichen Regeln tragen. Die stillen Trigger greifen erst beim nächsten passenden Anlass wieder. Dazwischen weiß niemand, was fehlt — Fehlendes hinterlässt im Kontext kein Loch. Diese Lücke schließt die Erinnerungsliste.

## Wie sie arbeitet

- **Anker:** `SessionStart`-Hook mit Matcher `compact`. Feuert bei automatischer Kompression und bei manuellem `/compact`; bewusst **nicht** bei `/clear` — ein Neustart soll leer sein.
- **Weg:** Das Skript liest das stdin-JSON des Hooks, nimmt daraus `transcript_path` (dokumentiertes Eingabefeld), geht das Sitzungs-Transkript zeilenweise durch und sammelt alle `Skill`-Werkzeugaufrufe der Hauptkonversation (Sidechains von Subagenten bewusst ausgenommen) — dedupliziert, mit Anzahl und letztem Zeitpunkt.
- **Ausgabe:** Die Liste geht auf stdout, und stdout eines `SessionStart`-Hooks wird laut Doku dem Kontext der Instanz hinzugefügt („adds plain-text stdout as context that Claude can see and act on"). Der Text ist einsprachig englisch — er ist Maschinen-Input; die Instanz trägt die Liste dem Nutzer in der Chat-Sprache vor.
- **Auf Zuruf:** Beim Aufruf über `/recall-skills-after-compact` übergibt die Instanz den Transkriptpfad als Argument; das Skript gibt dann nur die Liste aus. Die `SKILL.md` trägt `disable-model-invocation: true` — sie kostet keinen Dauerkontext (laut Doku steht ihre Description dann nicht in der Listung) und kann nur vom Nutzer gestartet werden.
- **Fehlerverhalten:** Leerer Befund oder jeder Fehler (kaputtes Eingabe-JSON, fehlender oder unlesbarer Transkriptpfad) erzeugt im Hook-Modus **keine** stdout-Ausgabe — nur eine stderr-Meldung — und Exit 0. Die Sitzung wird nie gestört.

## Installation

##### Claude Code

1. **Paket herunterladen.** `downloads/recall-skills-after-compact_de_local.zip`

2. **Entpacken.** Das Archiv enthält einen Ordner `recall-skills-after-compact/` mit allen Dateien. Entpacke ihn nach `~/.claude/skills/` — dann gilt die Fähigkeit für alle Projekte — oder nach `.claude/skills/` im Projekt, dann nur dort. Ein vorhandener Ordner gleichen Namens wird ersetzt; es bleibt nichts Altes liegen.

3. **Hook verdrahten.** Das musst Du händisch tun. Alles dazu steht in `settings-json-snippet.md`: der fertige Eintrag unterhalb der Trennlinie, darüber wohin er gehört, wie er in eine bestehende `settings.json` eingefügt wird und welcher Pfad anzupassen ist. Die Datei bleibt danach im Skill-Ordner liegen; ihre Datumszeile zeigt, von welchem Stand der übernommene Eintrag ist.

   Ohne diesen Schritt wirkt nur der Slash-Aufruf `/recall-skills-after-compact`; der garantierte Auslöser bei Kompression fehlt. In diesem Repository liegt die `settings.json` auf dem Infra-Branch — dort wird sie geändert.

4. **Wirksamkeit prüfen:** In einer Sitzung mit mindestens einem Skill-Aufruf `/compact` ausführen — die Liste muss danach als Kontext-Notiz auftauchen und von der Instanz vorgetragen werden.

## Grenzen

- Gezählt werden nur echte `Skill`-Werkzeugaufrufe. Ein Skill, dessen Regeln auf anderem Weg in den Kontext kamen (etwa eine direkt per Read geladene Regeldatei ohne Skill-Aufruf), fehlt in der Liste.
- Das Transkriptformat ist laut Anthropic-Doku intern und kann sich mit Claude-Code-Versionen ändern. Bricht es, wird der Hook still (stderr-Meldung, Exit 0) statt störend — die Erinnerung bleibt dann aber aus, bis das Skript nachgezogen ist.
- Voraussetzung: `python3` im PATH. Bewusst keine `jq`-Abhängigkeit: Auf einem Rechner ohne `jq` fiele der Hook still aus, und ein stiller Ausfall ist bei einem Erinnerungs-Hook besonders tückisch.
- Was beim Verdrahten schiefgehen kann — unangepasster Pfad, zerschossenes JSON, späteres Umbenennen des Ordners — steht bei der Sache selbst, in `settings-json-snippet.md`.

## Stand und Offenes

**Status:** Gebaut und getestet am 2. September 2026 — gegen drei reale Transkripte (darunter eine 15-MB-Sitzung mit drei Skills in sechs Aufrufen; Zählung deckungsgleich mit unabhängiger Handauszählung) und drei Fehlerfälle (leerer Input, fehlender Pfad, kein JSON — alle still auf stdout, Exit 0).

**Offen:** Der Praxistest an einer echten Kompression — die nächste anstehende lange Sitzung führt ihn aus.

**Lizenz:** CC0-1.0, wie die übrigen Skills dieses Repositories.
