# git-workbench — wie eine Claude-Sitzung committet: direkt, auf einer Werkbank oder isoliert im eigenen Worktree

*Stand: 2026-09-15*

*[English version](https://github.com/fherb2/claude-ai-tooling/blob/master/skills/git-workbench/README.en.md)*

**✅☑ Fertig und nutzbar.** Anweisungen vollständig, Frontmatter gesetzt, stiller Trigger vorhanden; deutsche und englische Fassung. — Benutzbar mit Claude Code.

**Legt fest, in welcher Körnung und wie isoliert eine Claude-Sitzung in einem Git-Repository committet — und löst damit zwei Probleme auf einmal: dass Absicherungs-Commits einer Maschine die Historie in unlesbare Schrittchen zerlegen, und dass zwei Sitzungen im selben Arbeitsbaum einander lautlos überschreiben.** Drei Betriebsarten: `direct` committet jeden freigegebenen Schritt dauerhaft auf dem aktuellen Zweig; `workbench` sichert Zwischenstände auf einem kurzlebigen Zweig ab und bringt sie am Ende per Squash als einen Commit in Menschenkörnung auf den Entwicklungszweig; `worktree` tut dasselbe in einem eigenen Git-Worktree, sodass mehrere Sitzungen gleichzeitig arbeiten können, ohne sich zu berühren. Ohne Festlegung fragt der Skill einmal je Sitzung (`ask`). Dazu eine Push-Regel, die vor jedem Push nach unveröffentlichten Commits auf allen lokalen Zweigen fragt, damit beim Rechnerwechsel nichts strandet.

**Abgrenzung:** Der Skill gilt nur für Claude Code lokal an einem Git-Repository, nicht für claude.ai. Er regelt das Committen einer Sitzung, nicht die Zweige des Projekts — welcher Zweig der Entwicklungszweig ist, wie in den Release übernommen wird, wie zentrale Dateien verteilt werden. Führt das Projekt dafür eine Datei `.claude/git-branch-model.json`, liest der Skill daraus den Namen des Entwicklungszweigs; sonst fragt er danach. Mehr braucht er nicht.

## Installation

1. **Paket herunterladen.** `downloads/git-workbench_de_local.zip`

2. **Entpacken.** Das Archiv enthält einen Ordner `git-workbench/` mit allen Dateien. Entpacke ihn nach `~/.claude/skills/` — dann gilt der Skill für alle Projekte — oder nach `.claude/skills/` im Projekt, dann nur dort. Ein vorhandener Ordner gleichen Namens wird ersetzt; es bleibt nichts Altes liegen.

3. **Stillen Trigger übernehmen.** Das musst Du händisch tun. Claude erkennt dann leichter aus dem Kontext heraus, ob der Skill geladen werden soll. Dazu: Aus `CLAUDE-snippet.md` kommt **alles unterhalb der Trennlinie** in die `CLAUDE.md` des gewählten Orts. Der kursive Text darüber bleibt zurück; die Datei selbst bleibt im Skill-Ordner liegen und zeigt an ihrer Datumszeile, von welchem Stand der übernommene Trigger ist.

   Ohne diesen Schritt wirkt der Skill nur beim ausdrücklichen Aufruf mit `/git-workbench`.

4. **Je Projekt einrichten — optional.** Ohne Konfigurationsdatei fragt der Skill in jeder Sitzung einmal nach der Betriebsart. Wer das nicht will, legt `.claude/git-workbench.json` an — im Chat, auf Wunsch; der Skill führt durch die Schritte und erklärt dabei, was ab dann automatisch geschieht. Für `worktree` gehört außerdem der Worktree-Ordner in die `.gitignore`.

Die `README.md` bringt das Paket mit, und das aus gutem Grund: Die `SKILL.md` verweist für alle Begründungen auf sie, und Claude nennt sie beim ersten Wirksamwerden als Nachschlagewerk und zitiert bei Nachfragen aus ihr. Wer den Skill nur installiert und zusieht, was passiert, bekommt so die Erklärung dann, wenn er sie braucht. Fehlt die README, funktioniert der Skill trotzdem — Antworten auf Warum-Fragen fallen dann nur dünner aus.

## Details

**Dreigeteilt: dünne `SKILL.md`, Kernregeln, Worktree-Regeln.** Die `SKILL.md` bestimmt nur die Betriebsart und lädt `rules.de.md` (beziehungsweise `rules.en.md`) mit den Regeln, die in jeder Betriebsart gelten. Nur in `worktree` kommt `rules-worktree.de.md` hinzu — Anlegen, verwaiste Werkbänke, Rechnerwechsel, die Kollision mit der Sandbox. So kostet die Maschinerie für parallele Sitzungen in den anderen Betriebsarten keinen Kontext (Teilung nach Kapitel 5.2 der Vorgaben).

**Warum es die Werkbank gibt: Körnung, nicht Parallelität.** Eine Claude-Sitzung will nach jedem Teilschritt einen Rückkehrpunkt — ein Missverständnis, das erst drei Schritte später auffällt, soll durch ein Zurücksetzen korrigierbar sein. Diese Rückkehrpunkte sind Maschinenkörnung; in der Historie des Entwicklungszweigs will sie niemand lesen. Die Werkbank übersetzt: Zwischenstände auf einem eigenen Zweig, am Ende ein Squash zu dem einen Commit, den ein Mensch gesetzt hätte. Daraus folgt die eine Regel, die den Squash hier richtig und anderswo falsch macht: **Commits, die ein Mensch gesetzt hat, behalten ihre Körnung; Absicherungs-Commits einer Maschine werden auf Menschenkörnung gebracht.** Ein Themenzweig des Nutzers wird deshalb gemergt, eine Werkbank gesquasht.

**Warum `direct` eine Betriebsart ist und keine Nachlässigkeit.** Wartet der Nutzer auf die Sitzung und niemand arbeitet parallel, ist jeder freigegebene Schritt ohnehin ein Commit in Menschenkörnung — die Werkbank hätte nichts zu übersetzen. Dann ist der direkte Commit die einfachere und ehrlichere Form. Der Skill kennt sie ausdrücklich, damit die Instanz eine solche Entscheidung des Nutzers nicht Sitzung um Sitzung neu in Frage stellt, sondern als gültige Variante ausführt.

**Warum der Skill fragt, statt zu raten.** Ohne Konfigurationsdatei gilt `ask`: Beim ersten schreibenden Git-Kommando nennt die Sitzung ihren Zweig und ihre Lage und schlägt eine Betriebsart vor. Das ist bewusst eine Handlung als Anker und kein „Sitzungsbeginn" — den Zustand erkennt eine Instanz nicht zuverlässig, das erste schreibende Kommando kommt in jeder einschlägigen Sitzung vor. Ebenso beim Entwicklungszweig: Der aktuell ausgecheckte Zweig ist ein Vorschlag, keine Annahme. Git hat kein Signal für „das ist der Entwicklungszweig", und der Standardzweig des Remotes ist oft gerade der Release-Zweig.

**Warum der Skill den Entwicklungszweig nirgends speichert.** Er braucht genau einen Wert von außen. Führt das Projekt ein Zweigmodell, steht der Wert in dessen Datei — ein Fakt, ein Zuhause. Speicherte der Skill ihn zusätzlich, gäbe es zwei Fassungen, die auseinanderdriften. Führt das Projekt kein Zweigmodell, ist die Frage einmal je Sitzung billiger als eine zweite Wahrheit. Aus demselben Grund gibt es keine Zustandsdatei: Welche Werkbänke und Worktrees existieren, weiß Git (`git worktree list`, die Zweigliste); eine Datei daneben veraltet.

**Die Push-Regel.** Git synchronisiert Zweige einzeln. Wer abends `dev` pusht und morgens am anderen Rechner weiterarbeitet, findet dort keine Werkbank und keinen anderen Zweig, der nicht ebenfalls gepusht wurde. Deshalb prüft der Skill vor jedem Push alle lokalen Zweige auf unveröffentlichte Commits und fragt je Fund, ob er mitgepusht werden soll — mit Ja als Vorschlag. Die Regel hängt nicht am Begriff „Werkbank": Auch in `direct` gibt es Zweige, die zurückbleiben können. Ein Zweig ohne Upstream-Verknüpfung ist dabei der tückischste Fall, weil `git status` für ihn schweigt; deshalb wird er beim ersten Push mit `-u` verknüpft. Genau daran ist im ersten Einsatzprojekt eine ganze Arbeitssitzung auf einem Rechner unbemerkt liegengeblieben, während auf dem anderen weitergearbeitet wurde.

**Warum die Werkbänke im Repository liegen und nicht daneben.** Ein Geschwisterordner neben dem Repository wäre ebenso deterministisch aus dem Repo-Pfad ableitbar — er läge aber außerhalb des Ordners, den der Editor geöffnet hat: Der Nutzer sieht dann nicht, woran gearbeitet wird, und wechselt er dorthin, gilt das Verzeichnis als anderes Projekt. `.claude/worktrees/` ist zugleich der Ort, an dem Claude Code seine eigenen Worktrees anlegt; ein Wechsel dorthin mit `EnterWorktree` braucht deshalb keine gesonderte Freigabe. Der Ordner muss in die `.gitignore`, sonst taucht sein Inhalt im Haupt-Checkout als unversioniert auf — Worktrees sind Arbeitskopien des Repositories, keine Projektdateien.

**Was ein Wechsel in den Worktree kostet und bringt.** Bleibt die Sitzung im Haupt-Checkout stehen und arbeitet über absolute Pfade, erzwingt niemand etwas — es gelten allein die Regeln des Skills. Wechselt sie mit `EnterWorktree` hinein, läuft der Chat weiter (nur die Ablage des Transkripts wandert mit), und Claude Code blockiert von da an selbst jeden Schreibzugriff auf den Haupt-Checkout, jede Umleitung von Git dorthin und jedes Kommando, dessen Ziel es nicht verifizieren kann — darunter Heredocs mit nicht gequoteten Begrenzern, mit denen sich mehrzeilige Commit-Nachrichten schreiben lassen. Der Squash findet im Haupt-Checkout statt und verlangt deshalb vorher `ExitWorktree`. Belegt: [Worktrees](https://code.claude.com/docs/en/worktrees).

**Aufgeräumt wird nicht von selbst.** Claude Codes automatischer Sweep entfernt nur Worktrees von Subagenten und Hintergrundsitzungen; die per `--worktree` oder von Hand angelegten rührt er nie an (ebenda). Eine beendete Sitzung hinterlässt ihre Werkbank also samt Zweig, und ein sauberer Arbeitsbaum bedeutet dabei nicht, dass nichts zu retten wäre — die Arbeit steckt dann im Zweig. Genau das ist am 25. August 2026 passiert: eine Werkbank mit einem unverschmolzenen Commit über 17 Dateien, gefunden erst, als eine neue Sitzung dieselben Dateien anfassen wollte. Deshalb steht die Prüfung mit `git worktree list` am Anfang der Worktree-Regeln.

**Arbeit über mehrere Rechner.** Git synchronisiert Zweige, nie Worktree-Verzeichnisse — der Abend-Push nimmt die Werkbank mit, aber der andere Rechner muss den Worktree lokal neu anbinden. Deshalb ist der Ablageort deterministisch aus dem Repo-Pfad abgeleitet: Jede Sitzung findet auf jedem Rechner denselben Ort, ohne dass etwas ausgehandelt werden muss. Den Fortsetzungsablauf trägt die Worktree-Regeldatei.

**Der Rückfallweg ohne Isolation: Schreibhoheit klären.** Arbeitet eine zweite Sitzung im selben Arbeitsbaum und ist `worktree` nicht die Betriebsart, fragt der Skill zuerst, welche Sitzung schreibende Git-Kommandos ausführen darf, und bietet die Isolation an. Das ist die älteste Regel dieses Skills; sie bleibt, weil nicht jedes Projekt Worktrees will.

**Bekannte Einschränkung: Kollision mit der Bash-Sandbox.** Ist die Sandbox aktiv, maskiert sie `.git/config.worktree`, sobald `git worktree` läuft — danach scheitert jedes Git-Kommando, auch `git status` ([Issue #80278](https://github.com/anthropics/claude-code/issues/80278), offen, von Maintainern reproduziert). Die Worktree-Regeldatei erkennt am Sitzungskontext, ob die Sandbox aktiv ist, und warnt dann zur Laufzeit, statt stillschweigend in die Kollision zu laufen (Abschnitt „Bekannte Kollision", markiert mit `TEMP ISSUE-80278` und zum Entfernen vorgesehen, sobald das Issue behoben ist). Betroffen ist nur die Betriebsart `worktree`; `direct` und `workbench` brauchen kein `git worktree`.

**Die Freigabestufen des Skills** (Tabelle in der Regeldatei) regeln abschließend, was automatisch geschieht, was einmal je Sitzung oder je Projekt bestätigt wird und was jedes Mal — ausdrücklich auch dann, wenn anderswo für vergleichbare Tätigkeiten anderes vereinbart ist. Sie sind der Punkt, an dem der Skill dem Nutzer Arbeit abnimmt, ohne ihm Entscheidungen abzunehmen: Alles mit Wirkung über die eigene Werkbank hinaus bleibt zustimmungspflichtig.

**Regeln, deren Vereinfachung die Funktion zerstört:**

- Werkbank-Arbeit erreicht den Entwicklungszweig nur per Squash. Ein „schneller Merge-Commit" zwischendurch macht die Absicherungs-Historie zum Teil der Hauptlinie und die spätere Squash-Disziplin wirkungslos.
- Der Squash-Commit wird ohne `-a` ausgeführt. Mit `-a` wandert unversionierte Handarbeit des Nutzers in den Squash.
- Der Squash wird ausdrücklich in den Haupt-Checkout adressiert. Ein Squash im Worktree der Werkbank merged den Zweig in sich selbst; die Kette bricht ab (viermal an einem Tag beobachtet, 26. August 2026).
- Verwaiste Worktrees werden gemeldet, nicht übergangen.

**Technische Voraussetzung:** Git mit Worktree-Unterstützung für die Betriebsart `worktree`; `direct` und `workbench` kommen mit jedem Git aus.

**Erweitern.** Die projektkonkreten Werte gehören in die `.claude/git-workbench.json` des Projekts (Felder: `mode` mit `direct`, `workbench`, `worktree` oder `ask`; `workbench_prefix`; `worktree_dir`), nicht in den Skilltext — sonst gilt ein Projektschema plötzlich für alle Projekte. Das `git-`-Präfix im Dateinamen senkt das Risiko einer Kollision mit künftigen Engine-Dateien in `.claude/` und ist inhaltlich ehrlich: Ohne Git bliebe von der Methode nichts übrig.

## Stand und Offenes

**Status:** Neufassung vom 15. September 2026 als Nachfolger des Skills `parallel-sessions`, der Zweigmodell und Werkbank vermischte. Das Zweigmodell — Entwicklungs-, Release- und Verwaltungszweig samt Verteilung der zentralen Dateien — ist herausgelöst und eine eigene Fähigkeit; dieser Skill trägt nur noch, wie eine Sitzung committet. Neu gegenüber dem Vorgänger: die Betriebsarten `direct` und `workbench` ohne Worktree, `ask` als Standard, die Push-Regel für alle Zweige statt nur für die offene Werkbank, und die Worktree-Regeln als eigene, nur bei Bedarf geladene Datei. Aus dem Vorgänger übernommen und unverändert entschieden: das Werkbank-Schema `claude-wb/<topic>` mit Schrägstrich und englischem `<topic>`; der Worktree-Ablageort `.claude/worktrees/` im Repository; die Freigabestufen.

**Bewusst offen gelassen.** Betriebsart, Werkbank-Präfix und Ablageort sind Festlegungen des jeweiligen Projekts und stehen in dessen `.claude/git-workbench.json` — der Skill trägt nur das Verfahren. Welcher Zweig der Entwicklungszweig ist, legt der Skill ebenfalls nicht fest: Er liest es aus dem Zweigmodell des Projekts, wenn es eines gibt, und fragt sonst.
