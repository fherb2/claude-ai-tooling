# parallel-sessions — mehrere Claude-Sitzungen gleichzeitig im selben Repository, sauber getrennt über Git-Worktrees

*Stand: 2026-08-26*

*[English version](README.en.md)*

**✅☑ Fertig und nutzbar.** Anweisungen vollständig, Frontmatter gesetzt, stiller Trigger vorhanden; deutsche und englische Fassung.

**Gibt jeder gleichzeitig arbeitenden Claude-Sitzung ihren eigenen Git-Worktree mit eigener Werkbank und macht damit die Frage überflüssig, welche Sitzung committen darf.** Zwei Sitzungen im selben Arbeitsbaum überschreiben einander lautlos — das Tückische ist nicht der Konflikt, den Git melden würde, sondern das unbemerkte Mitwandern fremder Zwischenstände. Der Skill trennt die Sitzungen physisch: je Sitzung ein Worktree, darin eine kurzlebige Werkbank vom Integrationsbranch, Abschluss per Squash-Merge. Zentrale Dateien, die überall aktuell sein müssen (Projekt-CLAUDE.md, Editor-Konfiguration, `.gitignore`), liegen auf einem eigenen orphanen **Infra-Branch** und werden nicht gemergt, sondern von jeder Sitzung per `git restore --source` in den eigenen Worktree geholt. Für Projekte ohne dieses Modell enthält der Skill als Rückfallweg die alte Sofortregel: erst die Git-Schreibhoheit klären, dann arbeiten.

**Abgrenzung:** Der Skill gilt nur für Claude Code lokal an einem Git-Repository, nicht für claude.ai. Er regelt die Zusammenarbeit der Sitzungen, nicht das Release-Verfahren eines Projekts (wann etwas vom Integrations- in den Releasebranch wandert); dazu sagt er nichts.

## Installation

1. **Zielort wählen.** Der Skill gilt entweder für alle Projekte des Nutzers oder nur für eines:

   | Ort        | Pfad                                  | Gilt für                  |
   | ---------- | ------------------------------------- | ------------------------- |
   | Persönlich | `~/.claude/skills/parallel-sessions/` | alle Projekte des Nutzers |
   | Projekt    | `.claude/skills/parallel-sessions/`   | nur dieses Projekt        |

2. **Eine Sprachversion des Ordners `parallel-sessions/` kopieren.** Er enthält `SKILL.de.md`/`SKILL.en.md`, `rules.de.md`/`rules.en.md`, `CLAUDE-snippet.de.md`/`CLAUDE-snippet.en.md`, diese `README.md` und `README.en.md`; mit gehören alle Dateien der gewählten Sprache. Die gewählte SKILL-Fassung heißt am Zielort `SKILL.md` — ob umbenannt oder zusätzlich abgelegt, ist gleichgültig; Claude Code erkennt ausschließlich diesen Namen. Die Regeldatei behält ihren Namen: Die `SKILL.md` verweist auf sie, und dieser Verweis ist der einzige Weg, auf dem die Regeln geladen werden; wer sie umbenennt, zieht den Verweis mit. Die Datumszeilen von README und Snippet zeigen am Zielort, von welchem Stand die Installation ist.

3. **Stillen Trigger übernehmen.** Der Inhalt der zur gewählten Sprache passenden `CLAUDE-snippet`-Datei **unterhalb der Trennlinie** kommt in die `CLAUDE.md` des Zielorts; die Snippet-Dateien bleiben am Zielort liegen, wirksam ist allein die `CLAUDE.md`. Ohne diesen Schritt bemerkt der Skill die Situation nicht: Niemand sagt von sich aus „hier arbeitet gerade eine zweite Instanz".

4. **Je Projekt einrichten.** Das Worktree-Modell wird nicht durch die Installation wirksam, sondern durch die Ersteinrichtung im Projekt (Branches, Infra-Dateiliste, die Datei `.claude/git-worktree-model.json`). Sie geschieht im Chat, auf Wunsch des Nutzers; der Skill führt durch die Schritte. Ohne sie wirkt nur der Rückfallweg.

Die `README.md` gehört mit an den Zielort: Die `SKILL.md` verweist für alle Begründungen auf sie, und Claude zieht sie bei Nachfragen des Nutzers heran. Fehlt sie dort, funktioniert der Skill trotzdem — Antworten auf Warum-Fragen fallen dann nur dünner aus. Geprüft wird ihr Vorhandensein nicht.

## Details

**Zweigeteilt: dünne `SKILL.md`, nachgeladene Regeldatei.** Der Skill löst absichtlich breit aus — auch in Sitzungen, in denen das Worktree-Modell gar nicht vereinbart ist. Damit diese Sitzungen nicht den vollen Regeltext im Kontext tragen, klärt die `SKILL.md` nur die Lage und lädt die Regeldatei (`rules.de.md`/`rules.en.md`) erst, wenn das Modell gilt oder eingerichtet werden soll; die Sofortregel für den modellfreien Fall steht vollständig in der `SKILL.md` selbst (Teilung nach Kapitel 5.2 der Vorgaben, 26. August 2026).

**Warum ein orphaner Infra-Branch mit `restore` statt eines Merge-Flusses.** Der Abschluss einer Werkbank ist ein Squash-Merge, und Squashes löschen die Abstammung: Würde die zentrale Änderung per Merge in die Werkbänke verteilt und die Werkbank danach gesquasht, wüsste der Integrationsbranch nichts von der gemeinsamen Herkunft — der nächste Merge desselben Infra-Standes rechnete mit einer veralteten Merge-Basis und erzeugte Konflikte in Dateien, in denen es nie einen echten Konflikt gab. `git restore --source=<infra>` umgeht die Abstammung vollständig: Es gibt zu jeder Infra-Datei nur eine gültige Fassung (die auf dem Infra-Branch), und Überschreiben ist immer die richtige Auflösung. Genau deshalb ist die Regel „keine dauerhafte Änderung an Infra-Dateien außerhalb des Infra-Branches" nicht Ordnungsliebe, sondern die Bedingung, unter der das Verfahren konfliktfrei ist.

**Warum die Verteilung pull-basiert ist.** Der Infra-Branch drückt nichts in die Werkbänke; jede Sitzung holt sich den Stand selbst — beim Sitzungsbeginn und im ersten Schritt der Abschluss-Checkliste automatisch. Das macht zeitweilige Abweichung zum gewollten Zustand statt zum Fehler: Ein Experiment — eine zentrale Änderung, die erst eine Sitzung erproben soll, bevor sie für alle gilt, etwa ein neuer Trigger-Absatz in der CLAUDE.md oder ein Hook in den Settings — ist schlicht ein nicht ausgeführter Abgleich plus eine markierte lokale Änderung. Beendet wird es durch denselben Abgleich — ein Befehl, kein Zurückeditieren. Möglich ist das überhaupt erst durch die Worktrees: Claude lädt die Projekt-CLAUDE.md aus dem Worktree der jeweiligen Sitzung, im geteilten Arbeitsbaum sähen alle Sitzungen jede Testregel.

**Warum eine eigene Datei `git-worktree-model.json` statt eines Blocks in einer geteilten Vereinbarungsdatei.** Eine geteilte Datei bräuchte Koexistenz-Regeln — wem welcher Schlüssel gehört, wer was nie anfasst —, und diese Regeln müssten als Dauertext in jedem Skill stehen, der die Datei mitbenutzt: Kontextkosten in jedem Turn, nur um ein vermeidbares Problem zu verwalten. Die eigene Datei löst das durch Existenz statt durch Regeln; ihr Vorhandensein ist zugleich das Erkennungszeichen, dass das Modell im Projekt vereinbart ist. Nebeneffekt: Der Skill ist portabel, weil er in fremden Projekten keine vorhandene Vereinbarungsdatei voraussetzt. Das `git-`-Präfix im Namen senkt das Risiko einer Kollision mit künftigen Engine-Dateien in `.claude/` und ist inhaltlich ehrlich: Ohne Git — Worktrees, Branches, `restore` — bliebe von der Methode nichts übrig.

**Arbeit über mehrere Rechner.** Git synchronisiert Branches, nie Worktree-Verzeichnisse — der Abend-Push nimmt die Werkbank mit, aber der andere Rechner muss den Worktree lokal neu anbinden. Deshalb ist der Ablageort deterministisch aus dem Repo-Pfad abgeleitet (`.claude/worktrees/` im Repository): Jede Sitzung findet auf jedem Rechner denselben Ort, ohne dass etwas ausgehandelt werden muss. Den Fortsetzungsablauf (Push mit `-u` beim ersten Mal, Anbinden an den Remote-Branch, Infra-Abgleich) trägt die Regeldatei.

**Warum die Werkbänke im Repository liegen und nicht daneben.** Ein Geschwisterordner neben dem Repository erfüllt die Determinismus-Bedingung genauso — er hat aber einen Nachteil, der in der Praxis schwerer wiegt: Er liegt außerhalb des Ordners, den der Editor geöffnet hat. Der Entwickler sieht dann nicht, woran gearbeitet wird, und wechselt er dorthin, gilt das Verzeichnis als anderes Projekt. `.claude/worktrees/` ist zugleich der Ort, an dem Claude Code seine eigenen Worktrees anlegt; ein Wechsel dorthin mit `EnterWorktree` braucht deshalb keine gesonderte Freigabe. Der Ordner muss in die `.gitignore`, sonst taucht sein Inhalt im Haupt-Checkout als unversioniert auf (Festlegung vom 25. August 2026, nach der ersten Arbeitssitzung im Modell).

**Was ein Wechsel in den Worktree kostet und bringt.** Bleibt die Sitzung im Haupt-Checkout stehen und arbeitet über absolute Pfade, erzwingt niemand etwas — es gelten allein die Regeln des Skills. Wechselt sie mit `EnterWorktree` hinein, läuft der Chat weiter (nur die Ablage des Transkripts wandert mit), und Claude Code blockiert von da an selbst jeden Schreibzugriff auf den Haupt-Checkout, jede Umleitung von Git dorthin und jedes Kommando, dessen Ziel es nicht verifizieren kann — darunter Heredocs mit nicht gequoteten Begrenzern, mit denen sich mehrzeilige Commit-Nachrichten schreiben lassen. Der Squash-Merge findet im Haupt-Checkout statt und verlangt deshalb vorher `ExitWorktree`. Belegt: [Worktrees](https://code.claude.com/docs/en/worktrees).

**Aufgeräumt wird nicht von selbst.** Claude Codes automatischer Sweep entfernt nur Worktrees von Subagenten und Hintergrundsitzungen; die per `--worktree` oder von Hand angelegten rührt er nie an (ebenda). Eine beendete Sitzung hinterlässt ihre Werkbank also samt Branch, und ein sauberer Arbeitsbaum bedeutet dabei nicht, dass nichts zu retten wäre — die Arbeit steckt dann im Branch. Genau das ist am 25. August 2026 passiert: eine Werkbank mit einem unverschmolzenen Commit über 17 Dateien, gefunden erst, als eine neue Sitzung dieselben Dateien anfassen wollte. Deshalb steht die Prüfung mit `git worktree list` jetzt am Sitzungsbeginn.

**Die Freigabestufen des Skills** (Tabelle in der Regeldatei) regeln abschließend, was automatisch geschieht, was einmal je Sitzung oder je Projekt bestätigt wird und was jedes Mal — ausdrücklich auch dann, wenn anderswo für vergleichbare Tätigkeiten anderes vereinbart ist. Sie sind der Punkt, an dem der Skill dem Nutzer Arbeit abnimmt, ohne ihm Entscheidungen abzunehmen: Alles mit Wirkung über den eigenen Worktree hinaus bleibt zustimmungspflichtig.

**Regeln, deren Vereinfachung die Funktion zerstört:**

- Der Infra-Branch wird nie gemergt und nie von einem anderen Branch abgeleitet. Wer ihn „der Einfachheit halber" von `master` abzweigt, lädt dazu ein, ihn zu mergen — und kippt damit einen veralteten Gesamtstand über den Zielbranch.
- Werkbank-Arbeit erreicht den Integrationsbranch nur per Squash. Ein „schneller Merge-Commit" zwischendurch macht die Checkpoint-Historie zum Teil des Integrationsbranches und die spätere Squash-Disziplin wirkungslos.
- Experimente an Infra-Dateien enden durch den Abgleich, nie durch Merge und nie durch Handrückbau. Die Marken (`INFRA-EXPERIMENT`) sind keine Dekoration: Die Abschluss-Checkliste findet vergessene Experimente über sie — mechanisch, nicht durch Erinnerung.
- Der Squash-Commit im Haupt-Checkout wird ohne `-a` ausgeführt. Mit `-a` wandert unversionierte Handarbeit des Nutzers in den Squash.

**Technische Voraussetzung:** Git mit Worktree-Unterstützung; die Ersteinrichtung nutzt `git worktree add --orphan` und braucht dafür Git ≥ 2.42. Der Alltag kommt mit älteren Versionen aus.

**Erweitern.** Die projektkonkreten Namen (Branches, Präfix, Ablageort, Infra-Dateiliste) gehören in die `.claude/git-worktree-model.json` des Projekts (Felder: `integration_branch`, `release_branch`, `workbench_prefix`, `worktree_dir`, `infra_branch`, `infra_files`), nicht in den Skilltext — sonst gilt ein Projektschema plötzlich für alle Projekte.

## Stand und Offenes

**Status:** Vollständige Neufassung, mit dem Entwickler durchgesprochen und freigegeben (24./25. August 2026); die frühere Fassung (nur Schreibhoheits-Klärung, Worktrees bloß erklärt) lebt als Rückfallweg weiter. Entschieden sind: die Freigabestufen wie in der `SKILL.md`; das Werkbank-Schema `claude-wb/<topic>` mit Schrägstrich und englischem `<topic>`; der Skill-Name ohne Personenkürzel, weil das Modell als allgemein einsetzbar gilt; der Worktree-Ablageort `.claude/worktrees/` im Repository (deterministisch aus dem Repo-Pfad ableitbar — Voraussetzung für die Arbeit über mehrere Rechner per abendlichem Push und morgendlichem Pull — und im Blickfeld des Editors; der frühere Geschwisterordner neben dem Repository war es nicht). Installiert beim Entwickler (`~/.claude/skills/parallel-sessions/`, deutsche SKILL-Fassung); dieses Repository ist zugleich das erste Einsatzprojekt des Modells. Seit dem 26. August 2026 ist der Skill zweigeteilt: dünne `SKILL.md` als Lageklärung, Abläufe und Regeln in `rules.de.md`/`rules.en.md` (siehe Details).

**Bewusst offen gelassen.** Die konkreten Branch-Namen (Integrations-, Release-, Infra-Branch), das Werkbank-Präfix, der Ablageort und die Infra-Dateiliste sind Festlegungen des jeweiligen Projekts und stehen in dessen `.claude/git-worktree-model.json` — der Skill trägt nur das Verfahren und die Rollen.
