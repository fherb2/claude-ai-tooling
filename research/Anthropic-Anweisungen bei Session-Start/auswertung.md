# Auswertung: Was Anthropic Claude Code beim Sitzungsstart mitgibt

*Stand: 2026-08-31 · Auswertung der drei Kontextberichte in diesem Ordner, ergänzt um Messungen am laufenden System*

## 1 Anlass und Methode

Anlass ist der Übergang von claude.ai auf Claude Code: Claude Code ist erkennbar darauf ausgerichtet, zur Beantwortung einer Frage sofort, ausdauernd und in beliebiger Tiefe auf dem Rechner zu suchen und zu testen. Die Frage war, welche Anweisungen Anthropic den Instanzen dafür beim Sitzungsstart mitgibt — und ob sich die Modelle darin unterscheiden.

**Verfahren:** Ein leeres Verzeichnis außerhalb jedes Projekts (`~/Downloads/kontextpruefung`), die globale `~/.claude/CLAUDE.md` für die Messung auskommentiert, je Modell eine frische Sitzung, deren allererste Nachricht der Prompt in `first-prompt.md` war. Der Prompt verbietet Werkzeugeinsatz und Allgemeinwissen, verlangt wörtliche Zitate mit Quellenkennzeichnung — (S) Systemprompt, (W) Werkzeugbeschreibung, (N) Nutzerkonfiguration, (R) Laufzeit-Einspielung — und erzwingt eine feste Gliederung, damit die Berichte vergleichbar sind. Erhoben am 31. August 2026 mit Opus 5, Sonnet 5 und Fable 5; die Berichte liegen als `kontext-bericht_*.md` daneben.

**Grenzen der Methode, vor dem Lesen zu kennen:**

- **Jedes Modell berichtet über sich selbst.** Dass ein Modell eine Passage zitiert, die ein anderes nicht nennt, beweist zunächst nur unterschiedliche Berichte, nicht sicher unterschiedliche Prompts. Anwesenheit ist starke Evidenz, Abwesenheit schwache. (Die Berichtslängen streuen: Opus 212, Fable 124, Sonnet 101 Zeilen.) Für die zentralen Unterschiede dieses Papiers wurde eine vierte, unabhängige Fable-Sitzung als Gegenprobe herangezogen.
- **Die (R)-Einspielungen hängen am Sitzungszustand, nicht nur am Modell.** Die drei Sitzungen erhielten drei verschiedene auto-mode-Hinweise; das kann Modus- statt Modellunterschied sein.
- **Die Claude-Code-Version wurde nicht notiert.** Für eine Wiederholung: `claude --version` und den Berechtigungsmodus je Lauf mitprotokollieren. Der mitgegebene Kontext ändert sich mit jedem Update, unangekündigt.

## 2 Der gemeinsame Befund: Eigeninitiative dicht geregelt, Grenzen fast leer

Alle drei Berichte zeichnen dasselbe Bild, und Opus hat es selbst so zusammengefasst: „Der Kontext regelt Eigeninitiative sehr dicht, räumliche und systemische Grenzen dagegen fast gar nicht.“

### 2.1 Der Antrieb

Die Modelle werden nachdrücklich auf selbständiges Durcharbeiten eingestellt:

- Fable: „You are operating autonomously. The user is not watching in real time and cannot answer questions mid-task, so asking 'Want me to…?' or 'Shall I…?' will block the work.“ und „Do not stop because the context or session is long.“
- Opus: „When you have enough information to act, act.“ und „make routine judgment calls yourself, and check in only when different readings would lead to materially different work.“
- Sonnet: „Bias toward working without stopping for clarifying questions […] make the reasonable call and keep going; they'll redirect you if needed.“ (dort als Laufzeit-Hinweis)

Auch die Rückfrage selbst ist rationiert — das Frage-Werkzeug ist bei allen dreien nur für Entscheidungen zugelassen, „that is genuinely the user's to make“.

### 2.2 Die Bremsen — abstrakt statt konkret

Dem Antrieb steht bei Opus und Fable im Wesentlichen **ein einziges allgemeines Prinzip** gegenüber: „For actions that are hard to reverse or outward-facing, confirm first unless durably authorized“. Fable ergänzt eine Beweisprüfung vor zustandsändernden Kommandos („check that the evidence actually supports that specific action“) und „Before deleting or overwriting, look at the target.“ Konkrete Verbotslisten erhält von den dreien nur Sonnet (siehe 3).

### 2.3 Die Fehlanzeigen — bei allen drei Modellen gleich

Wörtlich aus den Fehlanzeigen-Abschnitten der Berichte:

- **Dateisystem:** „Keine ausdrücklichen räumlichen Grenzen des Dateisystemzugriffs (kein Gebot, im Projektordner zu bleiben; kein Verbot für Home oder systemweite Pfade).“ (Fable) — Sonnet bekommt das Gegenteil sogar positiv gesagt: „Assume this tool is able to read all files on the machine.“ (W:Read)
- **Betriebssystem:** „keine Aussage zu Paketinstallation, `sudo`, Systemkonfiguration, Diensten (start/stop/enable) oder zum Umgang mit fremden laufenden Prozessen.“ (Opus)
- **Netzwerk:** „Keine allgemeine Aussage, ob und in welchem Umfang Internetzugriff (Downloads, beliebige Webabfragen) grundsätzlich erlaubt ist.“ (Sonnet) Geregelt ist nur die Abgabe nach außen („Sending content to an external service publishes it“) und der Schutz der Nutzer-E-Mail-Adresse.

**Die Dimension „ob und wie tief losgeforscht wird“ ist also von Anthropic ungeregelt — modellübergreifend.** Es gibt keinen Ort im mitgegebenen Material, an dem eine Instanz angehalten würde, vor einer systemweiten Erkundung zu fragen.

### 2.4 Warum die Berechtigungsmechanik das nicht auffängt

Die Rechteverwaltung (Nachfrage-Dialoge, Modi, Sandbox) läuft außerhalb des Prompts und erzwingt technisch. Sie steuert aber nicht, aus zwei Gründen. Erstens fragt sie auf **Befehlsebene** — einzelne Kommandos, deren Wirkung ein Nutzer kaum je kompetent beurteilen kann; eine **Ebenen-Frage** („darf ich systemweit in Konfigurationsdateien lesen?“) kennt weder die Mechanik noch der Prompt. Zweitens erzeugt sie **Klick-Müdigkeit**: Jede Nachfrage kostet eine Nutzeraktion, die allermeisten Fälle sind harmlos, und so landet man im auto-Modus — womit die Freigabe genau dann pauschal erteilt ist, wenn die Instanz besonders tief ins System will. Die Mechanik versagt also nicht technisch, sondern am Menschen.

## 3 Die Modellunterschiede

### 3.1 Git-Schutz bekommt nur Sonnet

Der gewichtigste Unterschied. Sonnet trägt ein vollständiges Git-Schutzprotokoll, wörtlich unter anderem:

> „NEVER update the git config“ · „NEVER run destructive git commands (push --force, reset --hard, checkout ., restore ., clean -f, branch -D) unless the user explicitly requests these actions“ · „NEVER skip hooks (--no-verify, --no-gpg-sign, etc) unless the user explicitly requests it“ · „NEVER run force push to main/master, warn the user if they request it.“ · „prefer adding specific files by name rather than using 'git add -A'“ · „Always create NEW commits rather than amending“

**Opus und Fable haben davon nichts.** Ihr gesamter Git-Teil besteht aus wenigen Zeilen in der Bash-Werkzeugbeschreibung: „Commit or push only when the user asks. If on the default branch, branch first.“ plus Formalia (Co-Authored-By-Zeile, `gh`-CLI, keine interaktiven Flags). Beide Berichte melden ausdrücklich: zu force-push, `reset --hard`, Branch-Löschung, History-Rewrite steht nichts. Gegenprobe am eigenen Kontext einer vierten Fable-Sitzung: bestätigt.

Wer seine Arbeitsregeln also auf „das verbietet Claude Code doch selbst“ stützt, hat bei zwei von drei Modellen unrecht.

### 3.2 Konkretheit der Vorsichtsregeln

Sonnet erhält Kategorien mit Beispiellisten: „Destructive operations: deleting files/branches, dropping database tables, killing processes, rm -rf, overwriting uncommitted changes“ · „Hard-to-reverse operations: force-pushing […], git reset --hard, […] removing or downgrading packages/dependencies, modifying CI/CD pipelines“ · „Actions visible to others […]: pushing code, […] sending messages (Slack, email, GitHub), […] modifying shared infrastructure or permissions“ — und positiv: „Generally you can freely take local, reversible actions like editing files or running tests.“ Opus und Fable erhalten stattdessen nur das abstrakte Prinzip aus 2.2.

### 3.3 Autonomie-Rahmung

Fable trägt den stärksten Antrieb (2.1) samt Abschlusszwang („End your turn only when the task is complete or you are blocked on input only the user can provide.“). Sonnet trägt als einziges eine ausdrückliche Bremse für explorative Fragen: „For exploratory questions […] respond in 2-3 sentences with a recommendation […] Don't implement until the user agrees.“ — und zugleich als einziges eine Aufforderung zu eigenmächtigem Testen im Browser („start the dev server and use the feature in a browser before reporting the task as complete“). Opus trägt die strengste Umfangsdisziplin: „The requested scope is the deliverable — don't quietly narrow, widen, or transform it.“

### 3.4 Kleinere Unterschiede

- **Wissensstand:** Opus meldet „knowledge cutoff is May 2026“, Sonnet und Fable „January 2026“.
- **URL-Verbot** („NEVER generate or guess URLs“) berichtet nur Sonnet.
- **Laufzeit-Hinweise (auto mode)** waren dreimal verschieden: Opus bekam „Arbeit über Bash statt Read/Edit/Write“, Sonnet „nicht für Klärfragen anhalten“ plus eine Sichern-vor-Verwerfen-Regel, Fable berichtet keinen. Hier ist der Modus-Confound am größten (siehe 1).
- **Ein innerer Widerspruch, von Opus selbst gemeldet:** (S) „Prefer the dedicated file/search tools over shell commands when one fits“ gegen (R, auto mode) „make file changes with sed, heredocs, or short scripts, rather than using the dedicated Read, Edit, or Write tools.“ — „beide stehen wörtlich so im Kontext“. Anthropics eigene Schichten kollidieren also bereits untereinander; die Instanz löst das nach eigenem Ermessen auf (Opus: „da sie spezifischer und später eingespielt ist“).

### 3.5 Deutung — als Vermutung gekennzeichnet

Das Muster passt zu fähigkeitsabhängigem Prompting: Dem als stärker eingestuften Modell wird mehr eigenes Urteil zugetraut (abstrakte Prinzipien, stärkerer Autonomie-Rahmen), dem kleineren werden konkrete Listen und Arbeitsprotokolle mitgegeben. Belegt ist das nicht; es ist die sparsamste Erklärung des Befunds. Praktisch folgt daraus so oder so: **Die mitgegebenen Leitplanken sind eine Funktion von Modell und Version — kein verlässlicher Boden.**

## 4 Was außerhalb des Arbeitsordners entsteht — gemessen am laufenden System

Unabhängig vom Prompt-Inhalt hinterlässt jede Sitzung Daten außerhalb des Projekts. Gemessen am 31. August 2026 auf einem Linux-Arbeitsrechner (Beobachtung, kein Anthropic-Beleg):

- **Sitzungsprotokolle** unter `~/.claude/projects/<projektpfad>/`, eine JSONL-Datei je Sitzung. Hier: 190 MB über 20 Projektordner, ältestes Protokoll vom 4. August. Entscheidend: **Die Protokolle enthalten die Werkzeugergebnisse, also die Inhalte aller gelesenen Dateien.** Was die Instanz je gelesen hat, liegt damit als Kopie im Home — auch aus Wegwerf-Sitzungen: Selbst die drei Messsitzungen dieser Erhebung haben dauerhafte Protokollordner erzeugt. Die Aufbewahrungsdauer ist konfigurierbar (`cleanupPeriodDays`; auf diesem System bewusst 1095 Tage); der Standardwert ist gegen die aktuelle Anthropic-Doku zu prüfen.
- **Memory** unter `~/.claude/projects/<projektpfad>/memory/`: Der Systemprompt weist die Instanz an, dort selbständig zu schreiben und sogar zu löschen („write to it directly“, „delete memories that turn out to be wrong“). Auf diesem System tragen drei Projekte echte Memory-Dateien.
- **Scratchpad** unter `/tmp/claude-1000/<projektpfad>/<session-id>/scratchpad`, je Sitzung eines; der Prompt verlangt, es statt `/tmp` zu benutzen. Lebensdauer ist **kein** Claude-Merkmal, sondern Sache des Systems: Hier liegt `/tmp` auf tmpfs (weg bei jedem Neustart) mit 30-Tage-Alterung durch systemd-tmpfiles. Auf einem Dauerläufer ohne solche Regel bleiben Scratchpads liegen — das ist je Rechner zu prüfen (`/usr/lib/tmpfiles.d/`, `findmnt /tmp`).

Für Regelwerke folgt daraus eine Falle: Eine Regel „keine Änderungen außerhalb des freigegebenen Ordners“ ohne Ausnahme für diese Engine-Bereiche widerspräche dem ausgelieferten Verhalten in jeder einzelnen Sitzung.

## 5 Bedeutung für Rechner in Unternehmen

Die Befunde oben, auf Unternehmensumgebungen angewendet:

**Lesen heißt Übertragen.** Die Inferenz läuft auf Anthropic-Servern; jede Datei, die die Instanz liest, verlässt mit dem Kontext den Rechner — und landet zusätzlich als Kopie im lokalen Sitzungsprotokoll. Da es keine räumliche Lesegrenze gibt (2.3) und Lesen von der Mechanik freizügig behandelt wird, ist der relevante Umfang nicht „das Projekt“, sondern alles, was das Nutzerkonto lesen kann: eingebundene Netzlaufwerke, `~/.ssh`, Browser-Profile, Zugangsdaten in Konfigurationsdateien. Ein „lokaler“ Agent auf einem Firmenrechner mit gemounteten Shares ist faktisch ein Agent mit Leserecht auf diesen Shares.

**Die lokalen Ablagen sind ein eigenes Thema.** Protokolle mit Dateiinhalts-Kopien über Monate bis Jahre (konfigurationsabhängig), Memory-Dateien mit Wissen über Nutzer und Projekte, Scratchpad-Reste je nach `/tmp`-Politik — relevant für Offboarding, Datenlöschkonzepte, Audits, und besonders dort, wo Home-Verzeichnisse zwischen Rechnern synchronisiert oder zentral gesichert werden: Die Kopien wandern mit.

**Klick-Governance funktioniert nicht.** Wer die Kontrolle auf die Nachfrage-Dialoge stützt, stützt sie auf Befehlsebenen-Fragen, die Nutzer nicht beurteilen können, und auf eine Ermüdungsdynamik, die zuverlässig im auto-Modus endet — pauschale Freigabe genau dann, wenn die Instanz tief ins System will. Steuerung muss stromaufwärts ansetzen: ob und wie die Instanz überhaupt zu forschen beginnt, und dass sie **Ebenen-Fragen** stellt („darf ich systemweit Konfigurationen lesen?“) statt Kommando-Fragen. Dieses Konzept muss man ihr in eigenen Anweisungen mitgeben — im ausgelieferten Material existiert es nicht.

**Leitplanken sind modell- und versionsabhängig.** Der Git-Fall (3.1) zeigt es exemplarisch: Was für ein Modell „von Anthropic abgedeckt“ ist, fehlt beim nächsten vollständig, und alles kann sich mit jedem Update ändern. Eine Firmenrichtlinie darf sich deshalb auf keine mitgelieferte Regel verlassen. Konsequenz in drei Schichten: erstens eigene, immer geladene Anweisungstexte mit den Grenzen — dafür existiert eine organisationsweit verwaltete Ebene: eine Managed-Policy-CLAUDE.md (Linux: `/etc/claude-code/CLAUDE.md`, macOS: `/Library/Application Support/ClaudeCode/CLAUDE.md`), die vor allen Nutzer- und Projektdateien lädt und von einzelnen Nutzern nicht abwählbar ist („Managed policy CLAUDE.md files cannot be excluded“; belegt, [Memory-Doku](https://code.claude.com/docs/en/memory)). Dieselbe Quelle zieht die Grenze zur Mechanik ausdrücklich: „Settings rules are enforced by the client regardless of what Claude decides to do. CLAUDE.md instructions shape Claude's behavior but are not a hard enforcement layer.“ — und: „To block an action regardless of what Claude decides, use a PreToolUse hook instead.“; zweitens mechanische Durchsetzung, wo sie trägt (Deny-Regeln, Sandbox, eigene Konten, Netzsegmentierung); drittens regelmäßige Nachmessung mit einem festen Verfahren wie dem hier archivierten — die mitgegebenen Prompts sind ein bewegliches Ziel.

## 6 Bedeutung für Rechner in Produktionsanlagen

In OT-Umgebungen verschiebt sich die Gewichtung: Nicht Vertraulichkeit ist das erste Risiko, sondern **Verfügbarkeit** — und dafür ist die Befundlage ungünstiger als für Bürorechner.

**Eingriffe ins System sind praktisch ungeregelt.** Zu Diensten, Prozessen, Paketinstallation und Systemkonfiguration steht in keinem der drei Kontexte etwas (2.3); die Bremsen sind ein abstrakter Satz je Modell. Zugleich ermuntert der Prompt zum Durchgreifen — Sonnet wörtlich: „try to identify root causes and fix underlying issues“. Was in der Softwareentwicklung eine Tugend ist, ist an einer laufenden Anlage ein Störfall: Ein „Fix underlying issues“ kann ein Dienst-Neustart, ein Paket-Update oder ein Konfigurationsumbau sein.

**Die Werkzeuge reichen weit.** Volle Shell; Kommandos bis zehn Minuten Laufzeit; Hintergrundjobs, die über Gesprächszüge hinweg weiterlaufen („it keeps running across turns“). Zum Netzwerk gibt es keinerlei Nutzungsregel — ein Rechner mit Route zu SPS, SCADA oder OPC-UA-Servern macht diese für die Instanz mit Bordmitteln erreichbar, und nichts im mitgegebenen Material thematisiert das auch nur.

**Folgerungen für OT:** Agenten dieser Art gehören nicht auf Maschinen mit Schreib- oder Netzzugriff auf Anlagentechnik; wo Analyse gewünscht ist, dann über eigene, lesend beschränkte Konten auf segmentierten Kopien oder Spiegeln. Der auto-Modus verbietet sich dort grundsätzlich — er ist die pauschale Vorabfreigabe für genau die Eingriffe, die niemand vorab überblickt. Und als Arbeitsverfahren taugt das Muster „Tiefenprüfung vor Eingriff“: erst eine ausschließlich lesende Analyse der möglichen Sekundärwirkungen, deren Ergebnis ein Mensch bewertet, dann — in einem getrennten, einzeln freigegebenen Schritt — der Eingriff. Auch dieses Verfahren muss man der Instanz als eigene Anweisung mitgeben; von Haus aus kennt sie es nicht.

## 7 Wiederholung der Messung

Der Wert dieser Erhebung liegt im Vergleich über die Zeit. Für die nächste Runde (Vorschlag: in einem Jahr, zusätzlich bei größeren Claude-Code-Versionssprüngen):

- `first-prompt.md` unverändert wiederverwenden — nur so bleiben die Berichte diffbar.
- Je Lauf zusätzlich notieren: `claude --version`, aktives Modell, Berechtigungsmodus, Startverzeichnis, ob eine globale CLAUDE.md aktiv war.
- Dieselbe Gegenprobe wie hier: mindestens einen zentralen Unterschied an einer unabhängigen Sitzung desselben Modells verifizieren, bevor er als Modellunterschied gilt.
- Die Messungen zu Kapitel 4 (Protokollgrößen, Aufbewahrung, `/tmp`-Politik) mit erheben — sie ändern sich unabhängig vom Prompt.
