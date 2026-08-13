# Implementierungsdokumentation: Nachladbare Claude-Code-Skills

Dieses Dokument ist die Konzeption des Vorhabens und wird mit Beginn der Implementierung parallel zum Code weitergepflegt. Es besteht aus drei Segmenten: **Segment 1** erklärt das System entlang der Abläufe, wie sie der Nutzer erlebt, und ist zugleich die Quelle der späteren Anwenderdokumentation. **Segment 2** enthält die projektweiten Vorgaben, die quer über alle künftigen Skills gelten und an denen sich jeder einzelne Skill messen lassen muss. **Segment 3** beschreibt die Einheiten — je ein eigenes, in sich geschlossenes Kapitel pro Skill.

Es gilt die Prosa-Code-Grenze: Dieses Dokument enthält keinen Implementierungscode, nur final beschlossene Schnittstellen (z. B. SKILL.md-Frontmatter) und Beispielschnipsel.

Dieses Vorhaben ist eigenständig, darf aber auf die Erfahrungen von `chats-export` und `home-.claude-sharing` zurückgreifen — beide teilen mit ihm dieselbe Nutzerschnittmenge (denselben Nutzer, dieselbe Arbeitsweise), ohne dass ihre projekteigenen Festlegungen hier bindend wären.

---

# 1 Zusammenhänge

## 1.1 Zweck des Vorhabens

Der Ordner `skills/` in diesem Repository ist die Quelle für wiederverwendbare, nachladbare Claude-Code-Skills. Ihr Zweck: Inhalte, die sonst in den allgemeinen `CLAUDE.md`-Dateien wiederholt stehen müssten, wandern stattdessen in einen Skill und werden nur bei Bedarf nachgeladen.

## 1.2 Dieses Projekt ist nur Quelle

Der Ordner `skills/` in diesem Repository wird von Claude Code nicht automatisch erkannt oder geladen. Damit ein Skill tatsächlich zur Verfügung steht, muss er unter einem der von Claude Code vorgesehenen Ladeorte liegen:

| Ort        | Pfad                                       | Gilt für                    |
| ---------- | ------------------------------------------- | ---------------------------- |
| Persönlich | `~/.claude/skills/<skill-name>/SKILL.md`   | alle Projekte des Nutzers    |
| Projekt    | `.claude/skills/<skill-name>/SKILL.md`     | nur das jeweilige Projekt    |

(belegt, [Extend Claude with skills](https://code.claude.com/docs/en/skills))

Der automatische „Transport" eines hier entwickelten Skills an einen dieser Zielorte ist derzeit **nicht** Teil dieses Vorhabens. Das könnte sich noch ändern — insbesondere, da `home-.claude-sharing` bereits einen Sync-Mechanismus für `~/.claude` unterhält, der thematisch naheliegt.

## 1.3 Bestätigtes Ladeverhalten

Wird ein Skill durch Trigger-Abgleich (Beschreibung passt zur Anfrage) oder direkten Aufruf aktiviert, lädt nur der Inhalt seiner `SKILL.md` als eine einzelne Nachricht in den Kontext. Weitere Dateien im Skill-Ordner lädt Claude nur dann, wenn die `SKILL.md` selbst ausdrücklich darauf verweist.

> *„In a regular session, skill descriptions are loaded into context so Claude knows what's available, but full skill content only loads when invoked."*
>
> *„When you or Claude invoke a skill, the rendered SKILL.md content enters the conversation as a single message and stays there for the rest of the session. […] Claude Code does not re-read the skill file on later turns."*

(belegt, [Extend Claude with skills](https://code.claude.com/docs/en/skills))

## 1.4 Testen ohne Ablage am Zielort

Weil ein Skill an seinem echten Zielort (1.2) allein durch Trigger-Abgleich automatisch geladen wird — ohne expliziten Auftrag, allein durch die im Hintergrund laufende Kontext-Zusammenfassung —, lässt sich ein Skill-Entwurf aus diesem Projekt heraus testen, ohne ihn dort abzulegen: Man weist Claude in einem Chat explizit an, eine bestimmte `SKILL.md`-Datei zu lesen und für den laufenden Chat exakt so zu berücksichtigen, als wäre sie im Hintergrund über ihre Trigger-Begriffe eingelesen worden. So lassen sich Skill-Inhalte inhaltlich prüfen, bevor sie an einem Ort landen, an dem sie ab sofort ungefragt automatisch greifen.

---

# 2 Vorgaben

*(Noch offen — es sind noch keine projektweiten Festlegungen abgestimmt.)*

---

# 3 Einheiten

## 3.1 Übersetzungs-Skill

Übersetzt Dokumente mit softwareentwicklungsnahem Inhalt — nicht auf README
beschränkt, nicht auf eine bestimmte Sprachrichtung. Bisher abgestimmt:

### Auslösung

Claude erkennt über den Trigger-Abgleich, dass für eine Übersetzung bereits
ein Skill vorliegt.

- **Mehrdeutiger Auftrag** (z. B. „kannst du das mal übersetzen" ohne
  weitere Angaben): Claude kündigt den Skill an — „Für eine Übersetzung
  habe ich bereits einen Skill. Wollen wir den verwenden? Wenn ja, würde
  ich Dir ein paar kurze prinzipielle Fragen stellen." — und wartet auf
  Zustimmung, bevor er fortfährt.
- **Expliziter Auftrag** (Zielsprache, Dokument usw. sind bereits
  benannt): Die Bestätigungsfrage entfällt, der Skill beginnt direkt mit
  den Kalibrierungsfragen.

### Kalibrierungsfragen

Nur gestellt, wenn die Antwort nicht schon aus dem bisherigen
Chat-Kontext hervorgeht:

1. **Zielsprache.**
2. **Fachjargon-Grad/Zielgruppe:** Claude kann den Inhalt fachlich
   einordnen und den üblichen Fachjargon-Bereich verwenden (einschließlich
   fremdsprachiger Fachbegriffe, wie sie unter Fachleuten des Themas
   üblich sind), oder auf Wunsch weniger fremdsprachige Begriffe
   verwenden, wenn eine andere Zielgruppe angesprochen werden soll.
3. **Ob ein bestehendes Glossar angewendet werden soll** (nur relevant,
   wenn eines vorliegt, siehe „Terminologie-Glossar" unten).

### Terminologie-Glossar

Feste Begriffsentscheidungen (z. B. „Pipe" bleibt „Pipe", „Zeitstempel"
wird übersetzt) werden in einer Glossar-Datei geführt, statt bei jeder
Übersetzung neu entschieden zu werden.

- **Umgebungs-Erkennung:** Claude prüft selbst, ob es lokal in Claude Code
  läuft (echter Datei-Zugriff) oder in claude.ai (kein dauerhafter
  Datei-Zugriff). Praktisch: Zugriffsversuch auf
  `${CLAUDE_SKILL_DIR}/glossar.md`. Gelingt das (echter, aufgelöster Pfad),
  läuft es lokal in Claude Code — `${CLAUDE_SKILL_DIR}` wird laut
  offizieller Doku nur dort tatsächlich ersetzt, in claude.ai bliebe ein
  solcher Verweis wörtlicher Text bzw. die nötigen Datei-Werkzeuge fehlen
  ganz (belegt, [Extend Claude with skills](https://code.claude.com/docs/en/skills)).
- **Läuft es lokal:** Glossar liegt unter `${CLAUDE_SKILL_DIR}/glossar.md`
  — im selben Ordner wie der Skill selbst.
- **Läuft es in claude.ai:** Glossar bleibt unerwähnt, kein Versuch, es zu
  führen.
- **Am Ende jeder Übersetzung** (nur lokal): Claude schlägt neu
  entstandene Begriffsentscheidungen zur Aufnahme ins Glossar vor und
  fragt nach Bestätigung, statt sie stillschweigend zu verwerfen oder
  blind zu übernehmen.

### Arbeitsprobe

Vor der vollständigen Übersetzung bietet der Skill eine Arbeitsprobe an,
anhand derer der Nutzer entscheidet, ob das Dokument so übersetzt werden
soll.

- **Standardgröße, ohne Rückfrage:** maximal 33 % des Dokuments **und**
  maximal rund 1000 Wörter — es gilt jeweils der kleinere Wert.
- **Standardlage:** ab Dokumentanfang.
- **Begründung der 1000-Wort-Grenze:** Bei längeren Dokumenten sinnvoll,
  weil der Anfang eines Dokuments manchmal noch nicht aus gewöhnlichem
  Fließtext besteht (Titel, Inhaltsverzeichnis usw.) — daher lieber etwas
  mehr als zu wenig.
- **Anpassung nur auf Wunsch:** Ist die Probe ab Dokumentanfang nicht
  aussagekräftig genug, kann der Nutzer sie verlängern oder an eine
  andere Stelle des Dokuments verlegen. Das wird nicht von vornherein
  erfragt.

### Umgang mit Codeblöcken

Zwei Arten von Codeblöcken werden unterschiedlich behandelt, ohne den
Nutzer danach zu fragen:

- **Wörtliche Wiedergabe** von echtem Tool-Output oder echtem Quellcode
  bleibt unangetastet — auch enthaltene Kommentare.
- **Illustrative, paraphrasierte Beispiele** (z. B. gekürzte
  Konfigurationskommentare) dürfen übersetzt werden.

**Erkennung, projektweit:** Claude sucht nicht nur im selben Ordner wie
das Dokument, sondern im gesamten erreichbaren Projekt nach einer echten
Quelle, die der Codeblock zeigen könnte — anhand eines erkennbaren,
eindeutigen Anhaltspunkts (Dateiname, unverwechselbare Zeile,
Variablenname), unabhängig von Tiefe oder Nachbarschaft (z. B. auch unter
`../../source/mein-modul/include/...`). Wird eine Übereinstimmung
gefunden: (nahezu) wörtlich → unangetastet lassen; erkennbar
gekürzt/paraphrasiert → übersetzbar. Wird nichts gefunden, greift der
konservative Default: Codeblock-Inhalt unangetastet lassen.

### Eigennamen, Produktnamen und wörtliche Marker

Grundsätzliche Regel, ohne Einzelfallprüfung: Eigennamen und Produktnamen
(z. B. „Claude") sowie wörtliche Code-Marker (z. B. `@Claude:`) werden nie
mitübersetzt oder ausgetauscht, auch wenn der umgebende Fachbegriff sonst
übersetzt wird — unabhängig davon, ob sie im Fließtext als Beispiel oder
als exakte Wiedergabe eines echten Markers auftreten.

*(Weitere Ausgestaltung folgt — siehe Fahrplan.)*
