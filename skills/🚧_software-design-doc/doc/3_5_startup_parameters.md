## 3.5 Skillstart und Skill-Parameter

Stand (2026-09-17): Vorschlag; das Prinzip „ablesen statt fragen, Doku wächst an Festlegungen, Abwahl je Projekt" ist entschieden, die Einzelheiten sind es nicht.

### 3.5.1 Ablauf beim Skillstart

Der Skill wird durch den geankerten Trigger aus `CLAUDE-snippet.md` geladen, sobald eine Software-Änderung über eine lokal begrenzte Korrektur hinausgeht, oder durch Aufruf. Dann in dieser Reihenfolge:

1. **Skill-Parameterdatei lesen.** `.claude/software-design-doc.json`. Steht dort `mode: off`, endet der Skill: Er fordert nichts, schlägt nichts vor, zitiert keine Regel; vorhandene Doku in fremder Form wird vor Änderungen gelesen und dort gepflegt, wo das Projekt sie selbst pflegt.
2. **Ablesen, was ablesbar ist.** Fehlt die Datei oder ein Feld: Doku-Ordner (Rollenmarker, eine `decisions.md`, die üblichen Ordnernamen), Register, Dateien mit geplanten Schritten (Rolle `plan`, `work-plan.md`, `fahrplan.md`, Abschnitt „Offen" einer README), Layout der Prosa (Zeilenlängen: ein Absatz je Zeile oder Umbruch mit Leerzeilen), vorhandene Rollen.
3. **Fragen, was nicht ablesbar ist** — einmal je Sitzung, knapp, ohne Skill-Vokabular. Typisch: „Das Projekt hat keine begleitende Doku; soll ich Festlegungen, die den Code überdauern, ab jetzt festhalten — und wo?" Die Antwort gilt für die Sitzung; das Anlegen der Skill-Parameterdatei wird angeboten, nie stillschweigend getan.
4. **Lage bestimmen** (Kapitel 3.1) und die passenden Regelteile nachladen: `rules-hardness.md` und `rules-register.md` immer, `rules-planning.md` bei Planungsarbeit, `standard.md` bei Fragen zur Methodik.

### 3.5.2 Die Skill-Parameterdatei

Standardname `.claude/software-design-doc.json`; jeder Skill-Parameter hat einen Standardwert, und fehlt die Datei, gilt in allem der Standard (Vorgabe 2.9). Die Doku nennt sie im Folgenden Skill-Parameterdatei, damit der Dateiname an einer Stelle austauschbar bleibt.

| Skill-Parameter | Werte | Standard | Bedeutung |
|---|---|---|---|
| `mode` | `on`, `off` | `on` | Abwahl je Projekt |
| `doc_dir` | Pfad | abgelesen | Ordner der Doku |
| `register` | Pfad | `<doc_dir>/decisions.md` | Register (Kapitel 3.2) |
| `planned_steps` | Liste von Pfaden | abgelesen | Dateien mit geplanten Schritten (Kapitel 3.4) |
| `marking` | `define+relate`, `define`, `full` | `define+relate` | Pflicht der Zitatmarker |
| `friction_threshold` | Zahl | 2 | Reibungsschwelle; Funktion `global` eine Stufe höher |
| `assumptions_on_approval` | `accept`, `keep` | `accept` | Wirkung der Planfreigabe auf Annahmen (Kapitel 3.1) |
| `impact_model` | `hops`, `weighted` | `hops` | Auswirkungsrechnung (Kapitel 3.6) |
| `impact_lib` | `unknown`, `on`, `off` | `unknown` | ob die optionale Bibliothek `networkx` benutzt wird; der Entwickler wird einmal gefragt (Kapitel 1.7.4 und 3.6.1) |
| `impact_cutoff` | Zahl | 1 bei `hops`, 0,40 bei `weighted` | Tiefe bzw. Abbruchschwelle |
| `layout` | `one-line`, `wrapped` | abgelesen | wie die Instanz Prosa schreibt |
| `lint_signals` | Liste | eingebaute Liste DE/EN | Signalwörter des Lints (Kapitel 3.6) |

Die Skill-Parameter wohnen bewusst in einer Datei mit dem Namen des Skills unter `.claude/`, wie `git-workbench.json` und `git-branch-model.json`: Projektwerte gehören ins Projekt, nicht in den Skilltext.

### 3.5.3 Die Doku wächst an Festlegungen, nicht an Pflichten

Keine Struktur wird gefordert, die nichts zu halten hat. Die erste Festlegung, die den Code überdauert, braucht ein Zuhause — eine Datei, die der Skill vorschlägt; der erste Marker legt das Register an; der erste Text, der Festlegungen aus verschiedenen Orten in Beziehung setzt, bekommt die Rolle `relate` vorgeschlagen; der erste Fall von mehr als einem nächsten Schritt bekommt einen Ort für geplante Schritte vorgeschlagen. Die Ausbaustufe eines Projekts ist, was es hat — nicht, was ein Skill-Parameter sagt. Die Dreiteilung des Vorläufers (Anhang A) bleibt die Empfehlung für Projekte, die groß werden (Kapitel 3.3).

### 3.5.4 Repositories mit mehreren Vorhaben

**Dass ein Repository mehrere Vorhaben mit eigener Doku tragen kann, steht in Kapitel 1.5.** Hier steht, wie der Skill das zugehörige Vorhaben findet. Die Skill-Parameterdatei ist der Standard des Repositories. Ein Vorhaben mit eigener Doku weicht ab, indem seine Dateien Rollenmarker und eine `[register: pfad]`-Zeile tragen; der Skill folgt dann dem Vorhaben, in dem die berührten Dateien liegen — keine zweite Skill-Parameterdatei je Vorhaben, die Zeile im Dokument reicht (entschieden am 2026-09-24, vormals Q-19). Das entspricht der Regel dieses Repositories, dass jedes Vorhaben eigenständig aufgebaut ist.

### 3.5.5 Entscheidungsgrundlagen

> **[Q-17] Entscheidungsgrundlage — `layout` als Skill-Parameter**
> Kontext: Ob ein Absatz eine Zeile ist oder umbricht, lässt sich aus einer vorhandenen Doku messen; bei leerer Doku gibt es nichts zu messen, und die Instanz muss wissen, wie sie schreiben soll.
> Optionen: (a) Skill-Parameter mit Standard `one-line`, abgelesen wenn möglich; (b) keiner, immer ablesen, bei leerer Doku fragen; (c) keiner, immer `one-line`.
> Vorschlag: (a).
> Gewicht: klein · Blockiert: Fahrplanschritt 3
> Antwort:

> **[Q-18] Entscheidungsgrundlage — `impact_cutoff` als ein Feld für beide Modelle**
> Kontext: Bei `hops` ist der Abbruch eine Tiefe (1, 2), bei `weighted` eine Schwelle (0,40). Ein Feld mit modellabhängiger Bedeutung ist kurz, aber missverständlich.
> Optionen: (a) ein Feld `impact_cutoff`; (b) zwei Felder `impact_hops` und `impact_threshold`; (c) `impact_model` trägt den Wert mit: `hops:1`, `weighted:0.40`.
> Vorschlag: (c) — ein Feld, keine Missverständnisse.
> Gewicht: klein · Blockiert: Fahrplanschritt 3
> Antwort:

