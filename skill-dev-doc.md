# Skill-Entwicklung: Vorgaben und Umgebungswissen

Diese Datei ist die Bauanleitung für **jeden Skill dieses Repositories** — gleich in welchem Ordner er entsteht. Sie lag bis zum 27. August 2026 als `skills/implementation-doc.md` in einem einzelnen Vorhaben, galt aber längst darüber hinaus: Auch `chat-export` ist ein Skill, nur einer mit eigenem Werkzeugbau, und die Projekt-`CLAUDE.md` verweist für alle Vorhaben hierher.

**Kapitel 1–5 und 7 sind die Vorgaben**, die beim Schreiben jedes Skills gelten: die technischen Voraussetzungen und das Verhalten der Umgebung, die Regeln für Trigger und Dateien, die Messbefunde, auf denen diese Regeln beruhen, und das Verfahren, mit dem sich beides nachprüfen lässt. Wo eine Skill-README kurz „Vorgaben, Kapitel n“ schreibt, ist dieses Dokument gemeint. **Kapitel 6** regelt die Verwaltung des Vorhabens `skills/` — READMEs und Fahrplan —, **Kapitel 8** hält die Festlegungen der Neuordnung der Arbeitsanweisungen fest. Dem offiziellen Segmentschema der Arbeitsanweisungen (§2.3) folgt die Datei bewusst nicht; die Begründung steht zwei Absätze weiter.

**Umgebungs- und Inferenzverhalten gehört ausdrücklich hierher.** Ein Skill ist kein Softwaremodul: Statt Code entstehen sprachliche Anweisungen, und ausgeführt werden sie nicht von einem Compiler, sondern durch Inferenz. Wie die Inferenz-Maschine und ihre Umgebung sich verhalten — was geladen wird und wann, was ein Trigger auslöst, was eine Zielwelt kann und was nicht — ist deshalb kein Fremdkörper in dieser Doku, sondern ihr Gegenstand. Kapitel 1, 3 und 8.1 tun das seit jeher; seit dem 27. August 2026 ist es benannte Festlegung statt stillschweigender Praxis.

Was hier **nicht** steht: der Arbeitsstand einzelner Skills und die anstehende Arbeit. Was an einem Skill fertig ist und was er dem Nutzer bietet, steht in dessen eigener `README.md` (Kapitel 6.1); die Gesamt-`README.md` von `skills/` nennt ihn nur in ihrer Übersichtstabelle (Kapitel 6.2). Die anstehenden Schritte samt ihrer Reihenfolge trägt `work-plan.md` in der Projektwurzel (Kapitel 6.3). Eine `status.md` führt das Vorhaben `skills/` nicht: Die Skills stehen einzeln nebeneinander und werden nicht aufeinander aufbauend entwickelt, eine Protokollierung der Umsetzung hätte also nichts zu belegen. Eine Ausnahme davon ist `chat-export`: Er führt eine eigene Implementierungsdoku und einen eigenen Fahrplan in seinem Ordner, weil er erheblich komplexer ist als das Definieren einer `SKILL.md`. Die Begründung steht in der `README.md` von `skills/`; die Regel, dass dieses Material nicht mitreist, in Kapitel 5.

**Dieses Vorhaben folgt bewusst anderen Regeln als der Rest des Repositories.** Die Arbeitsweise mit Konzept- und Implementierungsdoku, dreigeteilter Segmentstruktur, Fahrplan und Statusdatei (globale `CLAUDE.md`, Abschnitt 2) ist auf Softwareentwicklung zugeschnitten: auf einen zusammenhängenden Code, dessen Teile voneinander abhängen und dessen Entstehung nachvollziehbar bleiben muss. Hier entsteht kein Quellcode, sondern eine Sammlung einzeln nebeneinanderstehender Anweisungstexte. Jeder Skill ist für sich fertig oder unfertig, keiner baut auf einem anderen auf, und keiner wird später gegen eine Konzeptfassung geprüft. Eine Protokollierung der Umsetzung hätte deshalb nichts zu belegen; einen Fahrplan führt das Vorhaben dagegen sehr wohl, weil auch nebeneinanderstehende Arbeiten eine Reihenfolge und einen benannten nächsten Schritt brauchen (Kapitel 6.3). Was Kapitel 1–7 an Vorgaben tragen, entspricht der Sache nach Segment 2 — projektweite Festlegungen, an denen sich jeder einzelne Skill messen lassen muss.

Belegte Aussagen tragen ihre Quelle. **Beobachtung am laufenden System** und **Messung** sind als solche gekennzeichnet und von der offiziellen Dokumentation getrennt — Anthropic baut an diesen Werkzeugen laufend um, und die Doku schweigt zu einem Teil dessen, was hier zählt.

---

## 1 Was beim Schreiben vorausgesetzt wird

### 1.1 Dieses Verzeichnis ist nur die Quelle

Der Ordner `skills/` in diesem Repository wird von Claude Code nicht erkannt. Ein Skill wirkt erst, wenn er an einem der vorgesehenen Ladeorte liegt — persönlich unter `~/.claude/skills/<skill-name>/` oder projektlokal unter `.claude/skills/<skill-name>/` (belegt, [Extend Claude with skills](https://code.claude.com/docs/en/skills); die Zielorte samt Installationsablauf stehen in der Gesamt-README).

Daraus folgt die Grundregel für den Aufbau: Ein Skill-Ordner hier trägt **genau die Struktur, die er am Zielort haben wird** (Kapitel 5) — mit dem einen Unterschied, dass hier alle Sprachfassungen nebeneinanderliegen. Welche davon an den Zielort gelangt und welche Dateien dabei umbenannt werden, entscheidet das Installationspaket; das Verfahren steht einheitlich in 5.3, die Schritte für den Nutzer als Vorlage in 6.1.

### 1.2 Ladeverhalten

Wird ein Skill durch Trigger-Abgleich oder direkten Aufruf aktiviert, lädt **nur** der Inhalt seiner `SKILL.md`, und zwar als eine einzelne Nachricht, die für den Rest der Sitzung im Kontext bleibt; Claude liest die Datei in späteren Turns nicht erneut. Weitere Dateien im Skill-Ordner lädt Claude nur, wenn die `SKILL.md` ausdrücklich auf sie verweist. (belegt, [Extend Claude with skills](https://code.claude.com/docs/en/skills))

Zwei Konsequenzen, die beim Entwurf immer mitzudenken sind: Der Körper wird **nicht neu gelesen** — eine Regel, die erst spät geladen wird, rettet keine Entscheidung, die vorher gefallen ist. Und Zusatzdateien kosten nichts, solange niemand auf sie verweist.

### 1.3 Stiller Trigger

Ein *stiller Trigger* ist ein Absatz in der `CLAUDE.md` des Zielorts, der eine Bedingung benennt und auf einen Skill verweist. Er ist nicht Teil des Skills, sondern liegt außerhalb davon.

Wozu er da ist, erklärt die Gesamt-README. Für das Schreiben zählen zwei Dinge: Der Trigger-Absatz liegt dauerhaft im Kontext, der Skill-Körper nicht — das ist der ganze Zweck der Konstruktion. Und die naheliegende Sorge, ein in der `CLAUDE.md` wiederholter Trigger-Wortlaut könne den Skill vorzeitig mitladen, ist gemessen und **widerlegt** (Kapitel 3).

**Ein Skill ohne stillen Trigger ist der Normalfall.** Gebraucht wird er nur, wenn die Auslösebedingung nicht aus der Nutzeranfrage selbst hervorgeht.

### 1.4 Die zweite Zielwelt: claude.ai

Was ein Skill dort kann und was nicht — erarbeitet am 27. August 2026, Beleglage je Aussage ausgewiesen. Die Vorgabe, die daraus folgt, steht in Kapitel 9.

**Claude Desktop ist zwei Umgebungen in einem Programm** (Beobachtung des Entwicklers am laufenden System, 30. August 2026). Der Reiter *Chat + Cowork* verhält sich wie claude.ai: Er sieht die Skills, die im claude.ai-Konto hochgeladen sind, und die Arbeit läuft vollständig bei Anthropic. Der Reiter *Code* ist dagegen Claude Code mit einem anderen Frontend — er liest die Skills aus `~/.claude`, kann Ordner anbinden und arbeitet unmittelbar auf dem Rechner. Eine Desktop-Installation bringt Claude Code also mit; wer es im Terminal nutzen will, installiert es trotzdem ein zweites Mal.

**Daraus folgt die Schreibweise dieser Doku:** „Claude Desktop (Chat + Cowork)“ zählt zu claude.ai, „Claude Desktop (Code-Reiter)“ zu Claude Code. Steht irgendwo nur „Claude Desktop“, ist die Anwendung als Ganzes gemeint — etwa ihr lokaler Zustand unter `~/.claude`, den beide Reiter teilen.

**Was sich unverändert überträgt:**

- **Der stille Trigger.** claude.ai hat auf beiden Ebenen ein Feld für Anweisungen: eines global für das Konto — die Entsprechung zur `~/.claude/CLAUDE.md` — und eines je Projekt. Beide werden geschrieben wie eine `CLAUDE.md`, es geht nichts verloren. (Beobachtung des Entwicklers aus laufender Nutzung.)
- **Die Zweiteilung** aus Kapitel 5.2. Custom Skills werden dort als **ZIP** hochgeladen (Settings → Features; Pro, Max, Team, Enterprise, Voraussetzung ist aktivierte Code-Ausführung), und das Nachladen weiterer Dateien ist ausdrücklich vorgesehen: *„If those instructions reference other files … Claude reads those files too“*, mit *„None until accessed“* als Token-Kosten (belegt, [Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)). Unterschiedlich ist allein der **Pfad-Ausdruck**: `${CLAUDE_SKILL_DIR}` ersetzt nur Claude Code (belegt, [Skills](https://code.claude.com/docs/en/skills)); auf claude.ai bliebe er wörtlicher Text.
- **Das Description-Budget** (8.1) gilt dort ebenso: Jeder installierte Skill kostet dauerhaft seine Beschreibung in der Listung, ob er auslöst oder nicht.

**Wo die Grenze verläuft — und sie ist asymmetrisch:**

- **Der Lesepfad ist mechanisch möglich.** *„Files in your projects are now accessible through Claude's computing environment while remaining in context“* (belegt, [Create and edit files](https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude)) — ein Skript im Container kann Projektwissen-Dateien also lesen. Der Nachsatz ist die Einschränkung: Sie bleiben dabei im Kontext, der Container spart keinen Kontext.
- **Der Rückweg ist zweigeteilt.** Ein **Artefakt** schreibt die Instanz — sein Inhalt läuft durch die Inferenz und ist eine Abschrift, keine Ersetzung; daran ändert auch nichts, dass Artefakte inzwischen in der Ausführungsumgebung entstehen (*„Claude now uses the computing environment to create artifacts“*, belegt, ebd.). Ein **Download** dagegen kann mechanisch entstehen: Datei im Container per Ersetzung ändern, nach `/mnt/user-data/outputs` legen, als Download anbieten — der Inhalt läuft nicht durch die Antwort. Kompletter Roundtrip beobachtet am 28. August 2026 (siehe unten).
- **Der Lesepfad ist im RAG-Fall bestätigt und präzisiert:** Die Projektwissen-Dateien liegen unter **`/mnt/project/`** als echte Dateien gemountet — auch bei einer Wissensbasis weit über dem Kontextfenster. Beobachtet am 28. August 2026 an einem realen Projekt (gepackte Codebasis mit 39.898 Zeilen): eine 753-Zeilen-Quelldatei anhand ihrer `#!PKSRC:`-Token exakt extrahiert, eine Zeile eingefügt, per `diff` nachgewiesen (`1a2`, Rest bitidentisch), als Download bereitgestellt und als Artefakt angezeigt. **Wichtig: Die Selbstauskunft der Instanz verneinte diesen Zugriff zunächst überzeugt** — erst der konkrete Skript-Vorschlag brachte die Korrektur. Ein Skill, der diesen Weg braucht, muss ihn ausdrücklich anweisen (`ls /mnt/project/`), sonst scheitert er an der falschen Selbstauskunft. Die Pfade sind Beobachtung, keine Zusage.
- **Kein Zugriff auf den Rechner des Nutzers.** Die Ausführungsumgebung ist eine VM bei Anthropic; kein Repo, kein Git, keine lokalen Dateien. Das ist das Kriterium, an dem sich die Gruppe eines Skills entscheidet (Kapitel 9).
- **Grenzen nebenbei:** 30 MB je Datei für Up- und Download; das öffentliche Teilen von Konversationen mit File-Artefakten aus der Code-Ausführung ist für Free-, Pro- und Max-Konten deaktiviert (belegt, ebd.).

**Eine offene Prüffrage**, fällig beim ersten hochgeladenen Skill:

1. **Zieht ein hochgeladener Skill dort wirklich seine zweite Datei?** Das Nachladen ist belegt, aber von uns nicht beobachtet. Ein zweigeteilter Skill hochladen und nachsehen genügt.

*(Beantwortet am 28. August 2026: Ob eine reine Textdatei als Download herauskommt — ja; eine geänderte `.py` kam im Roundtrip-Test als Download an, siehe oben.)*

---

## 2 Vorgaben für Trigger

Diese Vorgaben gelten für die `description` eines Skills und für jeden `CLAUDE.md`-Absatz, der auf ihn verweist. **Die Reihenfolge der Punkte ist die Reihenfolge ihrer Wirkung** — wer an einem widerspenstigen Trigger arbeitet, prüft zuerst Punkt 1, nicht Punkt 2.

1. **Die Description entscheidet zuerst.** Sie beginnt mit dem Hauptanwendungsfall und verwendet die Begriffe, die der Nutzer von sich aus benutzen würde — nicht die projektinternen Fachbegriffe. Ein Warnhinweis, eine Einordnung oder ein Meta-Kommentar am Anfang verdrängt den Anwendungsfall von der Stelle, an der er wirkt, und kann den Trigger auf dem unempfindlichsten Modell vollständig unwirksam machen (Messung in Kapitel 3). **Sie steht durchgehend in der dritten Person** und spricht weder Claude noch den Nutzer an: „Erzeugt …“, „Übersetzt …“, „Verwenden, sobald …“ — nicht „Du kannst damit …“ und nicht „Verwenden, bevor **Du** …“. Der Grund ist kein Stilgeschmack: Die Description wird in den Systemprompt eingefügt, und ein wechselnder Blickwinkel stört dort die Auswahl unter vielen Skills — *„Always write in third person. The description is injected into the system prompt, and inconsistent point-of-view can cause discovery problems“* (belegt, [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)). Für den **Körper** der `SKILL.md` gilt das nicht: Er wird erst nach der Auslösung gelesen und darf Claude direkt ansprechen.
2. **Ereignisförmig formulieren:** Der Auslöser ist ein beobachtbarer, diskreter Fakt, der ankommt — nicht eine Eigenschaft der laufenden Aufgabe. Beispiele nennen, wie sie der Nutzer formulieren würde: wörtliche Nähe senkt die Auslöseschwelle, und vorzeitiges Laden durch Wortlaut-Nähe ist widerlegt (Kapitel 3).
3. **Oder an eine Ankerhandlung binden:** Lässt sich der Auslöser nur als Aufgaben-Eigenschaft fassen („braucht Planung“, „ist eine Softwareaufgabe“), wird die Prüfung an eine konkrete Handlung gebunden, die in jeder einschlägigen Sitzung ohnehin vorkommt: „Bevor du zum ersten Mal …, prüfe: …“.
4. **Reine Hintergrund-Beobachtung von Aufgaben-Eigenschaften** („Behalte im Blick, ob …“) ist die schwächste Form und **allein nicht ausreichend**. Sie funktioniert, wenn die Description gut ist, und versagt, sobald die Description nachlässt — sie hat also keine eigene Tragfähigkeit. Wo eine Eigenschaft der Auslöser ist, gehört zusätzlich ein Anker nach Punkt 3 dazu.
5. **Kalibriert wird auf das unempfindlichste Zielmodell** (Stand der Messung: Sonnet). Empfindlichere Modelle feuern dann höchstens zusätzlich, verpassen aber nichts; wo eine Auslösung garantiert sein muss, ist ein Hook der Weg, kein Trigger.

Prüfbar: Auf jede Description und jeden `CLAUDE.md`-Verweis lässt sich zeigen und sagen, ob er ereignisförmig oder geankert formuliert ist — oder eigenschaftsförmig und damit ein Verstoß; ebenso, ob die Description in der dritten Person steht.

### 2.1 Wo der Anker liegt

Bei einem Skill, der einen **Ablauf** beschreibt, liegt der Anker am Beginn dieses Ablaufs. Bei einem Skill, der ein **Regelwerk** ist und ab der ersten berührten Zeile durchgehend gilt, liegt er am frühestmöglichen Moment der Sitzung. Grund ist das Ladeverhalten (1.2): Weil der Körper nach dem Laden im Kontext bleibt und nicht neu gelesen wird, zählt allein der früheste Treffer. Momente, die der Skilltext selbst erwähnt (etwas benennen, etwas vorschlagen, eine Designentscheidung treffen), taugen deshalb nicht als Auslöser — sie kommen zu spät.

### 2.2 Länge der Description

Die Skill-Listung hat ein begrenztes Budget, und beim Überlauf kürzt Claude Code die Beschreibungen. Der Mechanismus samt Grenzen und Stellschrauben steht in Kapitel 8.1.

Daraus folgt eine Formulierungsregel, die nichts kostet: **Der Hauptanwendungsfall steht vorn.** Gekürzt wird von hinten — was am Ende steht, ist als Erstes weg. Trigger-Begriffe, auf die es ankommt, gehören in den ersten Satz, nicht in die abschließende Aufzählung. Die Reihenfolge ist auch dann einzuhalten, wenn die eigenen Beschreibungen weit unter der Grenze liegen: Das Budget hängt von der Zahl **aller** installierten Skills ab, nicht von unseren.

### 2.3 Skills erwähnen einander nicht

Zwei Trigger dürfen denselben Ankermoment benutzen. Mehrfachauslösung ist möglich und unschädlich. Kein Trigger-Absatz und kein Skill-Körper verweist jedoch auf einen anderen Skill dieses Verzeichnisses: Jeder muss einzeln installierbar bleiben, und ein Verweis auf etwas, das am Zielort fehlt, ist eine Sackgasse.

---

## 3 Was gemessen wurde

Dieses Kapitel ist durchgehend **Beobachtung am laufenden System** (Testreihe vom 14. August 2026, Claude Code mit Sonnet 5, Opus 5 und Fable 5; ein bis drei Läufe je Bedingung — Richtungsbefunde, keine Beweise). Die offizielle Doku sagt nur, dass Claude Skills nutzt, „when relevant to the task“, und schweigt dazu, wann das eintritt. Es steht hier, damit niemand diese Befunde ein zweites Mal erarbeiten muss; das Verfahren, mit dem sie sich nachprüfen oder auf neue Modelle übertragen lassen, steht in Kapitel 4.

**Der stärkste Hebel ist die `description`, nicht der Trigger-Text.** Belegt durch einen Ausschlusstest mit identischem Prompt, identischem `CLAUDE.md`-Text und identischem Modell, bei dem allein die Description getauscht wurde:

| `description` des Skills | Sonnet | Opus | Fable |
| ------------------------ | ------ | ---- | ----- |
| schwach — beginnt mit „TESTSKILL, nicht produktiv“, nennt einen Fachbegriff, der in der Anfrage nicht vorkommt | **feuert nicht** | feuert | feuert |
| gut — beginnt mit dem Anwendungsfall, verwendet die Begriffe der Anfrage | feuert | — | — |

Zwei Folgerungen: Eine schwache Description wird von den stärkeren Modellen **kompensiert**, von Sonnet nicht — wer auf Sonnet kalibriert, ist überall sicher. Und: Bevor man am Trigger-Text feilt, gehört die Description geprüft.

**Das erklärende Modell (Orientierungsmoment).** Eine „Beobachte im Hintergrund“-Anweisung hat keinen Ausführungsort — es gibt keinen mitlaufenden Hintergrundprozess, sondern nur den Moment am Anfang eines Turns, in dem das Modell die Nachricht einordnet: „Was ist das, was tue ich zuerst?“ Nur dort kann ein Trigger greifen. Enthält die Nachricht eine unmittelbar ausführbare Aufgabe, konkurriert die naheliegende erste Handlung mit der Trigger-Anweisung. Daraus folgen drei Mechanismen — gemessen an Skills mit schwacher Description, sie beschreiben also den ungünstigsten Fall:

- **Ereignisförmige Trigger feuern.** Ein beobachtbarer, diskreter Fakt („ein zweiter Chat ist offen“, „im Arbeitsbaum tauchen fremde Änderungen auf“) löst zuverlässig aus — spätestens, wenn die Nachricht außer diesem Fakt nichts Bearbeitbares enthält.
- **Eigenschaftsförmige Trigger feuern im Arbeitsfluss schlecht — geankert dagegen zuverlässig.** Charakterisierungen der laufenden Aufgabe lösten in keinem Handszenario aus, auch nicht nach einer 30-Turn-Planungsdiskussion, die die Bedingung inhaltlich exakt erfüllte. Dieselbe Bedingung an eine Ankerhandlung gebunden feuerte sofort — im A/B-Vergleich bei identischem Prompt, gleichem Modell und **gleicher Description**, weshalb dieser Befund von der Description-Korrektur unberührt bleibt.
- **Erzwungene Orientierung aktiviert auch ungeankerte Trigger.** Kommt ein großer, unstrukturierter Textblock ohne direkt ausführbaren Auftrag an (Doku-Dump, Quelltext plus vager Wunsch), muss das Modell erst einordnen, was das ist — in diesem Klassifikationsschritt feuert alles, was passt, auch mehrere Skills gemeinsam.

**Nicht ursächlich sind zwei naheliegende Verdächtige:** weder der Umfang der `CLAUDE.md` (gemessen mit sechs gegen 207 Zeilen, kein Unterschied) noch eine im selben Prompt mitgelieferte Handlungsanweisung („…und deshalb gilt hier: keine schreibenden Git-Aufrufe“).

Nebenbefunde derselben Testreihe:

- **Wortlaut-Echo senkt die Schwelle stark:** Nachrichten, die Begriffe der Description oder des `CLAUDE.md`-Absatzes fast wörtlich enthalten, lösten aus, wo inhaltsgleiche Umschreibungen schwiegen.
- **Keine Anhäufung:** Semantischer Kontext, der sich über viele Turns aufbaut, löst für sich genommen nicht aus — es gibt keinen Mechanismus, der rückblickend bilanziert.
- **Keine Fehlauslösung durch Wortlaut-Nähe:** Ein in der `CLAUDE.md` wiederholter Trigger-Wortlaut lud den Skill in keinem Lauf vorzeitig; bei themenfremden Prompts schwieg er durchweg.
- **Modellabhängig ist die Schwelle, nicht der Mechanismus:** Opus und Fable feuerten schon auf eine Ein-Satz-Fehlerbeschreibung, bei der Sonnet in allen Läufen schwieg; Fable unterschied dabei zwischen passenden und unpassenden Skills, Opus feuerte pauschal alle.

---

## 4 Wie geprüft wird

**Keines der beiden Verfahren ist Voraussetzung dafür, dass ein Skill als fertig gilt.** Sie stehen hier für den Fall, dass eine Frage offen ist oder ein Befund auf ein neues Modell übertragen werden soll — nicht als Pflichtschritt vor der Freigabe. Wurde gemessen, gehört das Ergebnis in die README des Skills; wurde nicht gemessen, ist das kein Mangel und wird nirgends vermerkt.

### 4.1 Inhalt prüfen, ohne den Skill am Zielort abzulegen

Man weist Claude in einem Chat ausdrücklich an, eine bestimmte `SKILL.md` zu lesen und für den laufenden Chat exakt so zu berücksichtigen, als wäre sie über ihre Trigger-Begriffe eingelesen worden. So lässt sich der Inhalt prüfen, bevor er an einem Ort landet, an dem er ab sofort ungefragt greift. Das prüft **nur** den Inhalt, nicht die Auslösung.

### 4.2 Auslösung messen

Die Auslösung lässt sich nur mit echter Ablage am Zielort testen — der Trigger-Abgleich läuft nur über dort liegende Skills.

- **Wegwerf-Skill als Ladeindikator:** ein Testskill, dessen Körper einzig anweist, das eigene Laden sofort und unübersehbar zu melden.
- **Die Description des Testskills muss die des echten Skills sein** — sonst misst man sie statt dessen, was man messen will. Ein Warnhinweis „TESTSKILL, nicht produktiv“ gehört **nicht** an den Anfang: Er verdrängt den Anwendungsfall von der Stelle, an der er wirkt, und hat in der ersten Testreihe dieses Vorhabens einen Teil der Negativbefunde erzeugt (Kapitel 3). Der Skill-**Körper** darf beliebig als Test gekennzeichnet sein; er wird erst nach der Auslösung gelesen.
- **Verifikation am Transkript, nie über die Selbstauskunft:** Im Session-JSONL unter `~/.claude/projects/<projektpfad>/` wird nach dem `Skill`-tool_use-Eintrag gesucht. Die sichtbare Meldung im Chat ist nur Komfort.
- **Frische Chats je Bedingung, Prompt-Leiter:** Negativkontrolle (themenfremd — darf nicht feuern), implizite Stufe (Situation ohne Schlüsselwörter der Description), eskalierte Stufe. Dazu immer eine Positivkontrolle — sonst ist „feuert nie“ nicht von einem kaputten Aufbau unterscheidbar.
- **A/B nur bei gleichem Modell.** Das Modell steht je Antwort im Transkript.
- **Confounds vorher ausräumen:** `CLAUDE.md`-Anweisungen, die dasselbe Verhalten schon bedingungslos anordnen, für die Testdauer entfernen — sonst hat das Modell keinen Anlass, den Skill zu ziehen, weil der Bedarf anderweitig gedeckt ist.
- **Grenze des Verfahrens:** Die Denkblöcke sind im Transkript leer gespeichert — der interne Weg zur Auslösung ist nicht beobachtbar, nur das Verhalten. Erklärende Modelle wie das Orientierungsmoment bleiben deshalb falsifizierbare Deutungen.

**Der skriptbare Weg** (am laufenden System erprobt und bestätigt, 14. August 2026): Der Testaufbau kommt in ein isoliertes Wegwerf-Projekt, etwa im Scratchpad-Verzeichnis — ein Ordner mit `.claude/CLAUDE.md` (nur der zu testende stille Trigger) und `.claude/skills/<name>/SKILL.md` (der Ladeindikator). Dann ein Lauf je Bedingung mit `claude -p "<prompt>" --output-format json --model <modell>`. Der Beweis liegt im Stream: `--output-format stream-json --verbose` gibt jeden Schritt als eigenes Ereignis aus, und ein Skill-Aufruf erscheint darin als `tool_use` mit `"name": "Skill"`, gefolgt von einem `tool_result` mit `Launching skill: <name>`. **`--verbose` ist zwingend** — ohne die Option verweigert `--print` das Stream-Format. Modellvergleiche werden damit zur Schleife statt zur Handarbeit. Was der interaktive Weg weiterhin besser kann: den Verlauf über mehrere Turns beobachten, in denen sich eine Situation erst aufbaut; ein `-p`-Lauf ist einer Erstnachricht gleichwertig.

Der Minimalaufbau ist als Messinstrument gegengeprüft: Mit der vollständigen realen `CLAUDE.md` des Projekts als Umfeld ergab sich dasselbe Ergebnis wie mit der sechszeiligen Testfassung.

---

## 5 Aufbau eines Skill-Ordners

Jeder Skill liegt unter `skills/<skill-name>/`. Der Ordnername trägt **kein** Sprachkürzel; die Dateien darin tragen es (5.1). Enthalten sind:

- **`SKILL.md`** — verpflichtend. Frontmatter mit `name` (gleich dem Ordnernamen), `description` (der reguläre Trigger, nach Kapitel 2 formuliert) und `license`. Letzteres ist reine Deklaration für den Leser: „Claude Code accepts the field but doesn't act on it“ (belegt, [Extend Claude with skills](https://code.claude.com/docs/en/skills)). Welche Lizenz gewählt wird, gibt Anthropic nicht vor (recherchiert am 14. August 2026); hier gilt einheitlich CC0, begründet in der Gesamt-README. Für den Umfang empfiehlt dieselbe Quelle, unter 500 Zeilen zu bleiben — eine Empfehlung, keine harte Grenze.
- **`README.md`** — verpflichtend. Die gesamte Dokumentation dieses Skills: was er leistet, wie er installiert wird, seine Feinheiten, sein Arbeitsstand und seine offenen Punkte. Aufbau nach 6.1; unter der Überschrift die Datumszeile (Projekt-CLAUDE.md, „Datumszeilen“).
- **`CLAUDE-snippet.md`** — nur bei Skills mit stillem Trigger. Aufbau: ganz oben die Datumszeile (Projekt-CLAUDE.md, „Datumszeilen“), darunter eine kursive Kopfnotiz, die erklärt, was mit der Datei zu geschehen hat, darunter eine Trennlinie, darunter der zu übernehmende Absatz im Wortlaut. Die Trennlinie ist die maßgebliche Grenze: Was darunter steht, wird in die `CLAUDE.md` des Zielorts übernommen, was darüber steht — Datumszeile eingeschlossen — nicht.
- **`settings-json-snippet.md`** — nur bei Fähigkeiten mit Hook-Auslöser (5.0), und dann anstelle der `CLAUDE-snippet.md`. Gleicher Aufbau, gleiche Trennlinien-Regel; sie trägt den `settings.json`-Eintrag statt eines CLAUDE.md-Absatzes.
- **Weitere Dateien** — nur, wenn die `SKILL.md` ausdrücklich auf sie verweist; sonst werden sie nie geladen (1.2).
- **`downloads/`** — die fertig geschnürten Installationspakete (5.3). Er gehört **nicht** an den Zielort; beim Packen bleibt er außen vor.
- **Entwicklungsmaterial** — Implementierungsdoku, eigener Fahrplan, Testsuite, Belegmaterial. Ein Werkzeug, das dem **Anwender** dient, gehört nicht dazu, auch wenn es der Diagnose dient: Es wandert mit. Es gehört ebenfalls nicht an den Zielort. Diesen Fall gibt es bisher einmal, bei `chat-export`; die Begründung steht in der `README.md` von `skills/`.

**Was nicht mitreist, entscheidet die Dateiliste beim Packen** (5.3) und nicht der Ordner: Das Paket entsteht aus einer ausdrücklich übergebenen Aufzählung, nicht aus einem Ordnerinhalt. Deshalb ist es unschädlich, dass Skill und Entwicklungsmaterial in einem Ordner liegen — aber es ist auch der Grund, warum die Aufzählung beim Wachsen eines Skills nachgezogen werden muss.

**Ein Ordner darf vorübergehend nur die `README.md` enthalten.** Das ist der Zustand einer festgehaltenen Idee: Sie hat einen Namen, einen Platz und eine Stelle, an der ihr Stand nachlesbar ist, aber noch keine Anweisungen. Erst wenn entschieden ist, dass daraus ein Skill wird, kommt die `SKILL.md` dazu.

**Wie installiert wird, steht in der Gesamt-README.** Für das Schreiben zählt daran nur, dass verpflichtend allein die `SKILL.md` unter diesem Namen ist; alles Weitere ist Empfehlung. Die `CLAUDE-snippet`-Datei wandert in der übernommenen Sprache mit und bleibt am Zielort liegen: Wirksam ist allein die `CLAUDE.md`, die Datei daneben ist das Vergleichsstück, an dessen Datumszeile der Nutzer den Stand des übernommenen Triggers abliest (Festlegung des Entwicklers vom 24./25. August 2026).

**Die `README` gehört mit an den Zielort.** Sie ist die Anwenderdokumentation des Skills (6.1), und die `SKILL.md` darf für Begründungen und Nachfragen des Nutzers auf sie verweisen — so bleibt der Skilltext schlank, ohne dass Begründungen verloren gehen. **Ein solcher Verweis darf sich nicht auf den Dateinamen verlassen:** Beim Installieren kann umbenannt worden sein, eine `README.md` am Zielort kann also englisch sein und eine deutsche Fassung unter anderem Namen liegen. Wer aus ihr zitieren will, sieht im Skill-Ordner nach, statt einen Namen vorauszusetzen. Findet er sie nicht, ist das kein Fehlerfall — die Antwort auf eine Warum-Frage fällt dann eben dünner aus.

**Die Installation ist Sache des Nutzers; Claude unterstützt sie, überwacht sie aber nicht.** Weder wird ungefragt geprüft, ob eine Installation vollständig oder aktuell ist, noch, ob der Inhalt einer `CLAUDE.md` zum mitgelieferten Snippet passt. Fällt beiläufig etwas auf, ist das höchstens einen Hinweis wert. Nur wenn der Nutzer ausdrücklich eine Prüfung verlangt, wird geprüft und benannt, was fehlt — und auch dann nicht mehr als das.

**Zusatzdateien, die zur Laufzeit gelesen oder geschrieben werden,** spricht der Skill über `${CLAUDE_SKILL_DIR}` an. Der Platzhalter wird laut offizieller Doku nur in Claude Code tatsächlich ersetzt; in claude.ai bliebe ein solcher Verweis wörtlicher Text bzw. die nötigen Datei-Werkzeuge fehlen ganz (belegt, [Extend Claude with skills](https://code.claude.com/docs/en/skills)). Ein Skill, der in beiden Umgebungen laufen soll, kann daraus seine Umgebung erkennen: Gelingt der Zugriff auf einen echten, aufgelösten Pfad, läuft er lokal.

**Zum `name`:** Kleinbuchstaben, Ziffern und Bindestriche, höchstens 64 Zeichen, keine XML-Tags, nicht die reservierten Wörter „anthropic“ und „claude“. Anthropic empfiehlt die Verlaufsform (`processing-pdfs`) und lässt Substantiv- und Handlungsformen ausdrücklich als Alternative zu (belegt, [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)); die Skills hier folgen der Substantivform. Kodiert ein Skill die Arbeitsweise einer bestimmten Person statt einer allgemein gültigen, gehört ein Kürzel in den Namen (`software-dev-doc-fh`). Das macht im Namen sichtbar, dass es andere Arbeitsweisen gibt, und lädt dazu ein, dafür einen eigenen Skill zu schreiben, statt diesen zu verbiegen.

### 5.0 Fähigkeiten mit Hook-Auslöser

**Nicht jede Fähigkeit wird von einem Trigger ausgelöst; manche von einem Ereignis der Engine.** Ein **Hook** ist technisch nur ein Eintrag in einer `settings.json`, der bei einem bestimmten Ereignis ein Kommando ausführt — kein Ordner wird dafür eingelesen, keine Datei automatisch gefunden (belegt, [Automate actions with hooks](https://code.claude.com/docs/en/hooks-guide): „To create a hook, add a `hooks` block to a settings file"). Für den Nutzer ist das dennoch dasselbe wie ein Skill: eine Fähigkeit, die er installiert, damit Claude sich in einer bestimmten Lage richtig verhält. **Deshalb leben solche Bausteine ebenfalls unter `skills/`** und nicht in einem eigenen Verzeichnis (Festlegung des Entwicklers vom 2. September 2026). Der Unterschied, den der Nutzer erlebt, ist nicht die Bauart, sondern die Verlässlichkeit: Ein stiller Trigger zieht wahrscheinlich, ein Hook läuft garantiert.

Wann welche Form: **Braucht die Fähigkeit Urteilsvermögen, ist sie ein Skill; muss sie garantiert stattfinden, braucht sie einen Hook.** Beides zusammen geht — der Hook stößt deterministisch an, sein stdout legt der Instanz die situative Anweisung in den Kontext. Ein Skill kann Hooks auch selbst in seinem Frontmatter definieren; die greifen aber erst **nach** seinem ersten Aufruf und taugen deshalb nicht dafür, den Skill überhaupt garantiert auszulösen.

Für den Aufbau folgt daraus, abweichend von Kapitel 5:

- **Statt `CLAUDE-snippet.md` eine `settings-json-snippet.md`**, gleich gebaut und gleich behandelt: Datumszeile ganz oben, darunter die kursive Kopfnotiz, darunter die Trennlinie, darunter der zu übernehmende Block. Übernommen wird auch hier nur, was unterhalb der Trennlinie steht; die Datei bleibt am Zielort liegen und ist an ihrer Datumszeile als Vergleichsstück lesbar. Sie ist die vierte Datei, die beim Packen umbenannt wird (5.3): `settings-json-snippet.<sprache>.md` → `settings-json-snippet.md`. Zwei Dinge gehören zwingend in ihre Kopfnotiz, weil sie ein CLAUDE.md-Schnipsel nicht kennt: dass JSON **eingefügt statt angehängt** wird (vorhandener `hooks`-Schlüssel, vorhandenes Ereignis-Array), und wie es sich mit dem Skriptpfad verhält.
- **Der Pfad im Kommando trägt keinen Platzhalter, sondern `$HOME`.** Hooks sind laut Doku Shell-Kommandos („Hooks are user-defined shell commands"; `"type": "command"` „runs a shell command"), die Shell löst die Variable also auf — beim Standard-Ablageort `~/.claude/skills/` ist damit **nichts** anzupassen. Begründung aus dem Schaden: Ein Platzhalter wie `/home/<user>/…` sieht wie ein fertiger Pfad aus, wird mitkopiert und übersehen, und der Hook scheitert danach **still**, weil seine Fehler nur ins Debug-Log gehen. Genau so ist der erste Praxistest von `recall-skills-after-compact` am 2. September 2026 fehlgeschlagen.
- **Und die Kopfnotiz trägt eine Probe, die ohne das Ereignis auskommt** — beim Kompressions-Hook also eine, die das Kommando von Hand ausführt, statt auf eine Kompression zu warten. Bei einer Fähigkeit, deren Ausfall unsichtbar ist, ist die billige Vorabprobe kein Komfort, sondern der einzige Weg, den Aufbau überhaupt zu prüfen.
- **Die Sprachfassungen unterscheiden sich nur in der Kopfnotiz.** Der Block unterhalb der Trennlinie ist JSON und in beiden Fassungen zeichengleich.
- **Die `SKILL.md` bleibt trotzdem sinnvoll** — als schlanker Zweitzugang „auf Zuruf" mit `disable-model-invocation: true`. Dann steht ihre Description laut Doku **nicht** in der Skill-Listung, die Fähigkeit kostet also keinen Dauerkontext und ist doch als `/kommando` verfügbar. Zugleich ist der Ordner damit ein regulärer Skill-Ordner; ein Ordner ohne `SKILL.md` unter `skills/` ist nirgends dokumentiert und wäre eine unbelegte Annahme.
- **Zielwelt ist immer nur `local`.** Hooks gibt es auf claude.ai nicht; es entstehen also nur `_de_local`- und `_en_local`-Pakete (5.3).
- **Der Skriptpfad im Settings-Eintrag muss stabil bleiben.** Eine Umbenennung des Ordners bricht den Hook **still** — Fehler eines Hooks landen nur im Debug-Log. Das gehört in die Grenzen-Sektion der README.
- **Das Skript scheitert still und mit Exit 0.** Ein Hook, der bei einem Fehler lärmt oder abbricht, stört jede Sitzung; Fehler gehen auf stderr, stdout bleibt leer.

- **Was ein Hook der Instanz in den Kontext legt, ist eine Anweisung — und wird als solche befolgt.** Deshalb trägt der Text nur, was zu tun ist, und ausdrücklich die Grenze dessen; jede mitgelieferte Erklärung des Mechanismus lädt zum Nachforschen ein. Belegt am ersten Praxistest von `recall-skills-after-compact` (2. September 2026): Die Fassung mit erklärendem Satz führte dazu, dass die Instanz die gesamte Skill-Installation prüfte, statt bloß eine Liste vorzulegen.

**Was eine Kompaktierung für die stillen Trigger dieses Repos bedeutet** (dokumentiert, [Explore the context window](https://code.claude.com/docs/en/context-window), am 2. September 2026 am laufenden System bestätigt): „The skill listing does not reload" — die Beschreibungsliste der verfügbaren Skills wird nach einer Verdichtung **nicht** wieder eingespielt. Ein stiller Trigger in der CLAUDE.md überlebt zwar (die wird neu geladen), zeigt danach aber ins Leere. Wer Triggerempfindlichkeit misst (Kapitel 4.2), misst deshalb nur den unkomprimierten Fall; für den Zustand danach ist die Verfügbarkeit die Grenze, nicht die Formulierung.

Erster Baustein dieser Art: `recall-skills-after-compact`.

### 5.1 Sprachfassungen

**In welcher Sprache ein Skill geschrieben und in welchen Sprachen er dokumentiert wird, entscheidet der Nutzer im Einzelfall.** Es gibt keine Pflicht zu zwei Fassungen: Ein Skill, den es nur auf Deutsch gibt, ist deshalb nicht unfertig. Ist eine weitere Fassung beschlossen, aber noch nicht geschrieben, gehört sie unter „Offen“ in die README des Skills (6.1) — dorthin aber erst nach der Entscheidung, nicht vorsorglich.

**Solange es nur eine Fassung gibt, trägt sie kein Sprachkürzel.** Die Dateien heißen dann schlicht `SKILL.md`, `README.md` und `CLAUDE-snippet.md`, und beim Installieren ist an den Namen nichts zu tun.

Liegen mehrere Fassungen von `SKILL.md` oder `CLAUDE-snippet.md` vor, liegen sie im **selben** Ordner und werden durch ein Sprachkürzel unmittelbar vor der Endung `.md` unterschieden:

| Deutsch                  | Englisch                 |
| ------------------------ | ------------------------ |
| `SKILL.de.md`            | `SKILL.en.md`            |
| `CLAUDE-snippet.de.md`   | `CLAUDE-snippet.en.md`   |

Das Kürzel tragen dann beide Fassungen dieser Dateien. Wo dieses Dokument die bloßen Namen `SKILL.md` oder `CLAUDE-snippet.md` verwendet, ist die Datei unabhängig von ihrer Sprachfassung gemeint.

**Die `README.md` ist davon ausgenommen — bewusst asymmetrisch.** Bei mehreren Fassungen trägt nur die englische ein Kürzel (`README.en.md`); die deutsche heißt unverändert `README.md`, ganz ohne Kürzel. Grund (recherchiert 23. August 2026): GitHub und GitLab zeigen automatisch nur eine Datei namens exakt `README.md` an, sobald jemand einen Ordner im Web-Interface öffnet — ein Sprachkürzel verhindert das, unabhängig davon, für welche Sprache es steht. Da die Arbeitssprache dieses Repositories Deutsch ist (siehe unten), bekommt die deutsche Fassung deshalb den Vorrang: Sie ist es, die beim Browsen ohne einen Klick sichtbar wird.

**Beim Installieren darf umbenannt werden.** Die gewählte `SKILL`-Fassung muss am Zielort `SKILL.md` heißen — eine `SKILL.de.md` allein ist kein Skill —, und ebenso darf eine `README.en.md` dort zu `README.md` werden. Der Ordnername bleibt unverändert, denn er trug nie ein Kürzel. Daraus folgt, was ein installierter Ordner **nicht** verrät: Aus einem Dateinamen lässt sich die Sprache seines Inhalts nicht ableiten. Wer den Inhalt braucht, sieht hinein, statt aus dem Namen zu schließen.

Daraus folgen drei Festlegungen, die beim Schreiben leicht übersehen werden:

- Das Frontmatter-Feld **`name` trägt kein Sprachkürzel**. Es muss dem Ordnernamen gleichen (Kapitel 5), und der Ordner heißt in beiden Fassungen gleich. Die deutsche und die englische `SKILL` tragen also denselben `name`.
- Der **Slash-Aufruf** heißt entsprechend `/<skill-name>`, nie `/<skill-name>-de`. Wo die `description` ihn selbst nennt, gehört er ohne Kürzel dort hinein.
- Mehrere Fassungen sind **Übersetzungen desselben Skills**, keine mehreren Skills. Sie tragen dieselben Regeln, dieselben Anker und dieselbe Struktur. Weicht eine inhaltlich ab, ist das ein Fehler, kein Sprachunterschied.

**Was für eine weitere Fassung spricht.** Die Arbeitssprache dieses Repositories ist Deutsch, die Skills sollen aber weitergegeben werden können. Und die Sprache des Skilltextes ist eine Festlegung mit Wirkung: Der Körper der `SKILL.md` liegt nach dem Laden für den Rest der Sitzung im Kontext (1.2) und prägt die Sprache, in der Claude anschließend antwortet.

### 5.2 Zweiteilung: dünne `SKILL.md`, nachgeladener Regelteil

**Ein Skill, der nach dem Auslösen erst klärt, ob er überhaupt angewendet wird, trägt seine Regeln nicht in der `SKILL.md`.** Sie enthält dann nur dreierlei: den Geltungsbereich, die Klärung samt Absage, und die Anweisung, bei Zustimmung eine zweite Datei desselben Ordners zu lesen (`${CLAUDE_SKILL_DIR}/<datei>.md`). Alles Weitere steht in dieser zweiten Datei. **Sie heißt einheitlich `rules.md`**, bei mehreren Sprachfassungen `rules.de.md`/`rules.en.md` nach 5.1 (Festlegung des Entwicklers vom 26. August 2026; Dateinamen sind englisch).

**Braucht ein Skill mehr als eine nachgeladene Datei**, tragen sie sprechende Namen statt Nummern — englisch, kleingeschrieben, mit Bindestrichen, dazu das Sprachkürzel nach 5.1 (Festlegung des Entwicklers vom 30. August 2026). Drei Rollen sind dabei zu unterscheiden:

- **Ein Regelzweig** heißt `rules-<zweig>.md`. Trennt der Zweig zwei Zielwelten, benennt er nicht das Produkt, sondern die Fähigkeit, an der die Regeln hängen — `rules-local` gegen `rules-handover` statt `rules-code` gegen `rules-web`. Ein Produktname altert mit jedem neuen Produkt, eine Fähigkeit nicht.
- **Was mehrere Zweige gemeinsam brauchen**, bekommt eine eigene Datei, die die Zweige ihrerseits nachladen. Sonst steht derselbe Inhalt mehrfach da und driftet auseinander — die Kette `SKILL.md` → Regelzweig → gemeinsame Datei ist ausdrücklich zulässig; das Verbot in 2.3 betrifft nur Verweise auf **andere Skills**.
- **Ein Klärungsschritt vor dem Regelteil** — etwa eine Entscheidung, die der Nutzer treffen muss — steht in einer eigenen Datei und lädt danach den Regelzweig. So kostet ein Nein nur die Klärungsseite.

Beleg für die Bauform ist `temp-debug-code` (30. August 2026): `SKILL.md` → `rules-local` beziehungsweise `user-choice` → `rules-handover`, beide Zweige laden bei Bedarf `marks`.

Der Grund steckt im Ladeverhalten (1.2): Weitere Dateien im Skill-Ordner lädt Claude nur, wenn die `SKILL.md` ausdrücklich auf sie verweist — und was einmal geladen ist, bleibt für den Rest der Sitzung im Kontext. Ein Skill, der auf eine Lage auslöst, in der er oft doch nicht zum Zug kommt, schleppt seinen vollen Text sonst in jeder dieser Sitzungen mit, ohne je benutzt zu werden. Mit der Teilung kostet er dann nur die Klärungsseite.

**Zwei Skills wären der falsche Weg** — sie müssten gemeinsam installiert werden, und 2.3 verbietet ohnehin, dass ein Skill auf einen anderen verweist. Die zweite Datei im selben Ordner löst beides.

**Vorgeschlagen wird die Teilung, wenn alle drei Bedingungen zutreffen:**

1. **Die Abwahl ist ein realistischer Ausgang** — der Skill löst auf eine Lage aus, die er nicht sicher trifft, und der Nutzer verneint die Anwendung erwartbar häufig.
2. **Der Regelteil ist deutlich länger als die Klärung.**
3. **Die Entscheidung ist ohne den Regelteil zu treffen.** Beleg ist `correct-zaaack-md-editor-mistakes` (geprüft am 25. August 2026): Er erfüllt die ersten beiden Bedingungen, aber ob ein Projekt betroffen ist, zeigt erst ein Lauf seiner Werkzeuge — und deren Beschreibung ist der Regelteil. Die Klärung müsste ihn also ohnehin laden, und die Teilung spart nichts.

Fehlt eine der Bedingungen, bringt die Teilung nichts: Ein Skill, der immer gilt, sobald er auslöst, spart nichts; ein kurzer Regelteil rechtfertigt den zusätzlichen Ladeschritt nicht; und wer den Regelteil schon zur Klärung braucht, lädt ihn ohnehin. Entsteht ein neuer Skill oder wächst ein bestehender, wird diese Prüfung vorgenommen und die Teilung vorgeschlagen; entschieden wird sie vom Nutzer.

**In der `SKILL.md` bleibt außerdem der Satz, der die Teilung begründet.** Ohne ihn liest sich die dünne Datei wie ein unfertiger Skill und wird beim nächsten Aufräumen wieder zusammengelegt.

Die zweite Datei folgt der Sprachregel aus 5.1 wie die `SKILL` selbst und wandert bei der Installation in der gewählten Sprache mit.

**Die Teilung trägt in beiden Zielwelten.** Auf claude.ai ist das Nachladen gebündelter Dateien ausdrücklich vorgesehen; unterschiedlich ist allein der Pfad-Ausdruck im Ladebefehl (1.4). Wo die Fassungen einer Zielwelt weiter auseinandergehen, ist dieselbe Konstruktion zugleich der Ort dafür — eine Regeldatei je Zielwelt (9.2).

Prüfbar: Auf jede `SKILL.md`, die beide Bedingungen erfüllt und trotzdem ihren ganzen Regeltext trägt, lässt sich zeigen — das ist der Verstoß. Ebenso auf jede Zusatzdatei, auf die keine `SKILL.md` verweist: Sie wird nie geladen.

### 5.3 Download-Pakete

**Ein Skill wird als fertiges Archiv zum Herunterladen angeboten, nicht als Ordner zum Zusammenkopieren** (Festlegung des Entwicklers vom 30. August 2026). Sobald ein Skill mehr als zwei Dateien hat, ist das Zusammenstellen von Hand fehleranfällig, und beim Aktualisieren merkt niemand, wenn eine Datei fehlt.

**Wo sie liegen.** In `downloads/` im Ordner des Skills. Dieser Ordner ist nicht Teil des Skills und wird nie mitgepackt.

**Welche es gibt.** Sprache mal Zielwelt — das ergibt zwei oder vier. Maßgeblich ist allein der Vermerk hinter dem Statushinweis in der README des Skills (6.1): Er nennt, für welche Varianten der Skill benutzbar ist. Kombinationen, die es dort nicht gibt, werden auch nicht angelegt.

**Wie sie heißen.** `<skill>_<language>_local.zip` beziehungsweise `<skill>_<language>_web.zip` — dreiteilig auch dann, wenn es nur eine Zielwelt gibt, damit sie im Namen steht. `local` meint Claude Code, `web` meint claude.ai und Claude Desktop (Chat + Cowork).

**Was darin liegt.** Ein einziger Ordner mit dem Namen des Skills, darin die Dateien — so verlangt es die Doku für den Upload auf claude.ai (belegt, [How to create custom Skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)), und beim lokalen Entpacken nach `~/.claude/skills/` entsteht damit genau der richtige Ordner. Der Test zeigt, dass der Upload auch andere Formen annimmt; maßgeblich ist trotzdem die dokumentierte, weil nur sie zugesagt ist.

**Was hineingehört:** die `SKILL`-Fassung der Sprache, die README derselben Sprache, alle nachgeladenen Dateien (5.2) sowie das Snippet der passenden Zielwelt. Die README wandert immer mit — sie ist die Anwenderdokumentation und beim Nutzer besser aufgehoben als im Repo.

**Umbenannt werden genau drei Dateien:** die gewählte `SKILL`-Fassung zu `SKILL.md`, die README der Sprache zu `README.md` und das Snippet der Zielwelt zu `CLAUDE-snippet.md`. Sprache und Zielwelt stehen ja schon im Namen des Archivs.

**Alle übrigen Dateien behalten ihren Namen** — und das ist kein Schönheitsfehler, sondern der Grund, warum das Packen einfach bleibt: Die `SKILL.md` nennt die nachgeladenen Dateien beim Namen. Hieße `rules-local.de.md` im Paket plötzlich `rules-local.md`, müsste jeder Verweis im Text mitgezogen werden, und genau das geht still schief. Die drei umbenannten Dateien sind davon nicht betroffen: Auf die `SKILL.md` verweist niemand, und README und Snippet werden nur von der Installationsanleitung genannt, die den neuen Namen ohnehin verwendet.

**Daraus folgt für jeden Verweis auf eine nachgeladene Datei: mit Sprachkürzel.** Die README nennt sie `rules-local.de.md`, die englische Fassung `rules-local.en.md` — nicht `rules-local.md`. Der kürzere Name stimmt nirgends: weder im Repo noch im Paket. Aufgefallen ist das erst bei der Prüfung des ersten gepackten Skills, dessen Aufbau-Tabelle alle vier nachgeladenen Dateien ohne Kürzel führte (30. August 2026).

**Und die Kopfnotiz eines Snippets nennt die andere Zielwelt-Fassung nicht beim Namen.** Sie liegt im Paket nicht daneben, sondern in einem anderen Archiv; ein Dateiname an dieser Stelle zeigt beim Nutzer ins Leere. Der Verweis geht deshalb auf das andere **Paket**, nicht auf die andere Datei.

**Wie gepackt wird.** `zip -9 -o -X`, die Einträge in sortierter Reihenfolge übergeben (`find … | LC_ALL=C sort | zip … -@`). Der Reihe nach: `-9` kostet bei diesen Dateigrößen nichts und spart beim Herunterladen; `-o` setzt das Datum des Archivs auf das der jüngsten enthaltenen Datei, womit man dem Paket ansieht, von welchem Stand es ist; `-X` lässt uid, gid und Zeitzonen-Extras weg, die sonst von Rechner zu Rechner verschieden ausfallen. Die Dateien selbst behalten ihre eigene mtime (`cp -p` beim Zusammenstellen). Zusammen mit der sortierten Reihenfolge ergibt gleicher Inhalt damit gleiche Bytes — ein Neubau ohne Änderung erzeugt keinen neuen Blob in git.

**Die Auswahl ist Handarbeit, die Prüfung nicht.** Welche Dateien ins Paket gehören und welche drei umbenannt werden, entscheidet die Instanz für jeden Skill neu; dafür gibt es bewusst kein Skript — ein Skill wird ein- bis dreimal in seinem Leben gepackt, und ein Skript müsste bei jeder Strukturänderung nachgezogen werden. Nach dem Packen wird der Inhalt jedes Archivs aufgelistet und angesehen, ob die Dateiliste stimmt; die beiden Fragen, die sich mechanisch beantworten lassen, übernehmen die Werkzeuge aus Anhang A — ob jede Datei, auf die aus dem Paket heraus verwiesen wird, auch darin liegt (A.2), und ob das Paket noch dem Stand seiner Quellen entspricht (A.3). Der Aktualitätsprüfer gehört dabei an das Ende **jeder** Sitzung, in der an einem Skill gearbeitet wurde: Ein Paket veraltet nicht beim Packen, sondern bei der nächsten Änderung danach.

---

## 6 READMEs und Fahrplan

Drei Dateiarten, die sich nicht überschneiden. Die README **am Skill** trägt alles, was über diesen einen Skill zu sagen ist — die Beschreibung dessen, was er leistet, seine Installation, seine Feinheiten und seinen Arbeitsstand. Sie ist damit zugleich seine Anwenderdokumentation und darf am Zielort liegen bleiben (Kapitel 5). Die **Gesamt-README** führt in das Vorhaben ein und listet die Skills, beschreibt aber keinen davon: Jeder Skill steht dort ausschließlich als Zeile der Übersichtstabelle. Damit gibt es zu einem Skill nur eine beschreibende Stelle, und sie liegt dort, wo auch gearbeitet wird. Der **Fahrplan** (6.3) beschreibt gar nichts, sondern trägt die anstehenden Schritte des Vorhabens.

### 6.1 README je Skill

Sie ist die vollständige Dokumentation dieses einen Skills und liest sich von „was ist das“ zu „woran wird noch gearbeitet“. Verlangte Reihenfolge:

1. **Überschrift** — Skillname und in einem Halbsatz, wozu er da ist.
2. **Statushinweis**, unmittelbar unter der Datumszeile und **ohne eigene Zwischenüberschrift**: ob der Skill benutzbar ist, mit demselben Symbol, das seine Zeile in der Übersichtstabelle der Gesamt-README trägt (6.2). Ist er es nicht uneingeschränkt, steht in einem Satz dabei, was fehlt, mit Verweis auf den Schlussabschnitt.
3. **Überblick** — was der Skill leistet, in Prosa. Die Kernaussage steht **fett** im ersten Satz. Umfassend genug, dass der Nutzer den Skill danach einschätzen kann, aber ohne Detailflut; dazu die **Abgrenzung**, wo sie nicht selbstverständlich ist: wofür der Skill ausdrücklich **nicht** gilt.
4. **Kapitel „Installation“** — wörtlich die Vorlage weiter unten, mit dem Namen des Skills statt `<skill>` und dem Sprachkürzel der jeweiligen README statt `<language>`. Gilt der Skill für beide Zielwelten, stehen beide Vorlagen als Unterabschnitte untereinander; gilt er nur für eine, steht nur diese. Braucht der Skill **keinen** stillen Trigger, entfällt dessen Schritt ersatzlos — er wird nicht als „entfällt hier“ aufgeführt. Ein Schritt, am Zielort etwas zu löschen, kommt nicht vor (siehe Kapitel 5).
5. **Kapitel „Details“** — alles Weitere: Anwenderhinweise, Feinheiten des Verhaltens und die Hinweise, die dem weiteren Ausbau dienen, insbesondere die Regeln, deren Vereinfachung die Funktion zerstören würde.
6. **Kapitel „Stand und Offenes“** — zum Schluss und in dieser Folge:
   - **Status** — was fertig ist, in einem Satz.
   - **Offen** — was an diesem Skill noch aussteht, knapp, mit Verweis auf den Fahrplan (6.3). Die README sagt, *dass* etwas offen ist; der Fahrplan sagt, *was zu tun ist und in welcher Reihenfolge*. Was zwar geplant, aber noch nicht auf der Tagesordnung ist, bleibt dagegen hier und wird als solches gekennzeichnet — der Fahrplan trägt keine Zukunftsvisionen.
   - **Bewusst offen gelassene Entscheidungen**, sofern es welche gibt — Festlegungen, die der Skill absichtlich nicht trifft, weil sie ins Zielprojekt gehören. Das ist Vorwissen für die Weiterentwicklung, kein Versäumnis, und muss als solches erkennbar sein.

Der ausdetaillierte Plan eines anstehenden Schrittes steht im Fahrplan (6.3), nicht hier. Einzige Ausnahme ist ein Plan, der den Inhalt des Skills selbst betrifft und mit ihm zusammen übernommen wird: Der steht unter „Offen“, höchstens einer gleichzeitig, deutlich als noch nicht ausgeführt gekennzeichnet, und wird nach der Ausführung ersetzt, nicht ergänzt.

#### Die beiden Vorlagen für das Installationskapitel

Wörtlich zu übernehmen, mit dem Namen des Skills statt `<skill>` und dem Kürzel der jeweiligen README statt `<language>`. Bei zwei Zielwelten stehen beide untereinander, jede unter ihrer eigenen Zwischenüberschrift.

**Vorlage A — Claude Code:**

> ##### Claude Code
>
> 1. **Paket herunterladen.** `downloads/<skill>_<language>_local.zip`
>
> 2. **Entpacken.** Das Archiv enthält einen Ordner `<skill>/` mit allen Dateien. Entpacke ihn nach `~/.claude/skills/` — dann gilt der Skill für alle Projekte — oder nach `.claude/skills/` im Projekt, dann nur dort. Ein vorhandener Ordner gleichen Namens wird ersetzt; es bleibt nichts Altes liegen.
>
> 3. **Stillen Trigger übernehmen.** Das musst Du händisch tun. Claude erkennt dann leichter aus dem Kontext heraus, ob der Skill geladen werden soll. Dazu: Aus `CLAUDE-snippet.md` kommt **alles unterhalb der Trennlinie** in die `CLAUDE.md` des gewählten Orts. Der kursive Text darüber bleibt zurück; die Datei selbst bleibt im Skill-Ordner liegen und zeigt an ihrer Datumszeile, von welchem Stand der übernommene Trigger ist.
>
>    Ohne diesen Schritt wirkt der Skill nur beim ausdrücklichen Aufruf mit `/<skill>`.

**Vorlage B — claude.ai und Claude Desktop (Chat + Cowork):**

> ##### claude.ai und Claude Desktop (Chat + Cowork)
>
> 1. **Paket herunterladen.** `downloads/<skill>_<language>_web.zip`
>
> 2. **Hochladen.** Im dafür vorgesehenen Verwaltungsfeld für Skills der Anwendung das Archiv hochladen. Der Skill gilt danach für Dein Konto — nicht für Deine Organisation, und nicht gleichzeitig in Claude Code.
>
> 3. **Stillen Trigger übernehmen.** Das musst Du händisch tun. Claude erkennt dann leichter aus dem Kontext heraus, ob der Skill geladen werden soll. Dazu: Aus `CLAUDE-snippet.md` im Archiv kommt **alles unterhalb der Trennlinie** in das Anweisungsfeld — global für das Konto oder für das einzelne Projekt.
>
>    Ohne diesen Schritt wirkt der Skill nur beim ausdrücklichen Aufruf mit `/<skill>`.

Der dritte Schritt entfällt bei Skills ohne stillen Trigger ersatzlos. Das Verwaltungsfeld ist bewusst nicht mit seinem heutigen Namen genannt: Der Weg dorthin ändert sich, die Sache nicht.

**Vorlage C — Fähigkeit mit Hook-Auslöser (5.0):** wie Vorlage A, aber der dritte Schritt lautet nicht „Stillen Trigger übernehmen", sondern **„Hook verdrahten"**, und er verweist auf `settings-json-snippet.md` statt den Block selbst abzudrucken — dort steht er samt allem, was beim Einfügen zu beachten ist. In der README bleiben nur zwei Sätze: was ohne diesen Schritt fehlt (in der Regel bleibt die Fähigkeit per Slash-Aufruf erreichbar, der garantierte Auslöser fehlt), und wo die `settings.json` im jeweiligen Projekt liegt. Ein vierter Schritt nennt die Probe, an der der Nutzer die Wirksamkeit erkennt.

Der Grund für die Aufteilung ist derselbe wie beim stillen Trigger: Was der Nutzer irgendwohin kopiert, gehört in eine Datei, die mitreist und ihren Stand ausweist — nicht in Prosa, die beim Kopieren zurückbleibt. Die README sagt **dass** und **wozu**, das Snippet sagt **was** und **wie**.

### 6.2 Gesamt-README

Die `README.md` dieses Ordners ist der Einstieg in das Vorhaben: Sie sagt, wozu es das gibt, wie ein Skill installiert wird und welche Skills es gibt. Was ein einzelner Skill leistet, steht nicht hier, sondern in seiner eigenen README (6.1). Verlangter Aufbau:

1. **Die Skills im Einzelnen** — eine Tabelle über **alle** Skills des Ordners, auch die unfertigen und die, von denen bisher nur die Idee festgehalten ist. Je Zeile: der Ordnername, verlinkt auf die README des Skills; die Statussymbole; ein Satz zum Zweck. Darunter die Legende der Symbole. Mehr steht hier nicht — jede weitere Beschreibung gehört in die README des Skills (6.1). Diese Tabelle steht **vorn**: Wer die Gesamt-README öffnet, sucht in aller Regel einen Skill, nicht eine Begründung.
2. **Zweck des Vorhabens** — kurz und prägnant, ohne Herleitung.
3. **Skills beschaffen und installieren** — beginnt mit einem knappen Verweis auf die offizielle Doku zu Skills als Mechanismus, gefolgt vom Hinweis, dass die vorgesehene Trigger- und Ladetechnik hier um stille Trigger erweitert wurde (1.3). Danach die Zielorte, der Kopiervorgang und die Behandlung der `CLAUDE-snippet.md`: Trigger-Inhalt in die `CLAUDE.md` übernehmen; die Datei bleibt am Zielort liegen, ihre Datumszeile zeigt den Stand der Installation. Dazu die Regeln aus Kapitel 2 dieser Vorgaben in der Kurzfassung, damit niemand einen Trigger beim Anpassen unwirksam macht. Das alles im allgemeinen Fall — die auf den einzelnen Skill heruntergebrochene Anleitung steht in dessen eigener README (6.1).
4. **Offene Punkte des Vorhabens** — ein Verweis auf den Fahrplan (6.3) und auf die READMEs der einzelnen Skills, keine eigene Liste. Zwei Listen driften sofort auseinander.

Dazu ein **Lizenzabschnitt**: CC0, mit einer Aufzählung dessen, was das für den Nutzer konkret bedeutet.

**Sprachfassungen.** Auch hier entscheidet der Nutzer, in welchen Sprachen die Gesamt-README vorliegt (5.1). Ihre Benennung folgt aber der Konvention der Wurzel-READMEs dieses Repositories, nicht dem Kürzel-Schema der Skill-Ordner: Die deutsche Fassung heißt `README.md`, jede weitere trägt ihr Kürzel (`README.en.md`).

### 6.3 Fahrplan

`work-plan.md` liegt neben der Gesamt-README und trägt die **anstehenden Schritte in der Reihenfolge ihrer Bearbeitung**. Er ist eine Entwicklungsdatei, keine README: Er trägt keine Sprachfassung, wird nicht mit an einen Zielort kopiert und entfällt, wenn das Vorhaben fertig ist.

Die Grenze zu den READMEs ist scharf und wird gebraucht, sonst entstehen zwei Listen, die auseinanderdriften:

- **Die README beschreibt den Zustand** — was fertig ist, was der Skill leistet, was an ihm noch aussteht, und was zwar geplant, aber noch nicht auf der Tagesordnung ist. Letzteres wird als solches gekennzeichnet und bleibt dort.
- **Der Fahrplan beschreibt die Schritte** — was als Nächstes zu tun ist, in welcher Reihenfolge und mit welchem Plan. Er trägt keine Zukunftsvisionen: Was noch niemand vorhat, ist kein Schritt.

Je Schritt so viel Detail, wie eine neue Sitzung zur Wiederaufnahme braucht, ohne den Chat zu kennen. Erledigte Schritte fliegen raus; die Nummern der übrigen werden dabei **nicht** neu vergeben (Projekt-`CLAUDE.md`, „Fahrplan-Nummerierung“).

Eine `status.md` führt dieses Vorhaben nicht (siehe Einleitung).

Prüfbar: Auf jeden Fahrplaneintrag, der nur einen Zustand beschreibt statt einer Handlung, lässt sich zeigen — und ebenso auf jede README, die einen ausdetaillierten Plan trägt, obwohl er in den Fahrplan gehört (Ausnahme in 6.1).

---

## 7 Wortwahl im Skill-Text

**Ein Skill definiert seine Begriffe nicht, er benutzt eindeutige.** „Nutzer“ ohne Zusatz bezeichnet immer den Menschen im Chat — dieses Wort ist im Systemprompt bereits so belegt, ein Skill erbt die Bedeutung umsonst. Geht es um den Menschen vor der fertigen Software, steht dort **„Endanwender“**, ausgeschrieben an jeder Fundstelle. Ein einleitender Absatz, der die Rollen erklärt, gehört nicht in einen Skill: Er kostet Kontext für etwas, das Claude schon weiß, und widerspricht der Empfehlung, nur Kontext zu ergänzen, den Claude nicht hat — *„Does this paragraph justify its token cost?“* (belegt, [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).

**Beobachtung am laufenden System** (16. August 2026): Die offiziell veröffentlichten `SKILL.md` unter `~/.claude/plugins/marketplaces/claude-plugins-official/` benutzen „the user“ durchgehend, ohne ihn ein einziges Mal zu definieren; die eine Datei, die über den Menschen vor der fertigen Software spricht (`frontend-design`), setzt „end user“ an die Fundstelle, ohne Vorrede.

Daneben gilt die allgemeine Empfehlung derselben Quelle, einen Begriff einmal zu wählen und durchzuhalten: *„Choose one term and use it throughout the Skill.“*

Prüfbar: Auf jede Stelle, an der „Nutzer“ allein steht, obwohl der Mensch vor der fertigen Software gemeint ist, lässt sich zeigen — das ist der Verstoß. Ebenso auf jeden Absatz, der Rollen oder Begriffe erst erklärt, statt sie zu benutzen.

---

## 8 Allgemeine Festlegungen der Neuordnung

### 8.1 Description-Budget der Skill-Listung — belegt und parametrierbar

Feststellung, recherchiert am 22. August 2026 gegen die offizielle Dokumentation ([Extend Claude with skills](https://code.claude.com/docs/en/skills)). Diese Grenzen stammen von Anthropic und sind keine Eigen-Festlegung dieses Repos; Kapitel 2.2 gibt sie nur wieder.

**Wie der Mechanismus arbeitet:** Claude Code lädt eine Listung aller Skill-Namen samt Beschreibungen in den Kontext. Die Namen sind darin **immer vollständig** enthalten; gekürzt werden nur die Beschreibungen. Das Budget dafür „scales at 1% of the model's context window“. Läuft die Listung über, entfernt Claude Code Beschreibungen beginnend bei den am seltensten aufgerufenen Skills — „drops descriptions starting with the skills you invoke least, so the skills you use most keep their full text“. Unabhängig vom Budget gilt je Skill eine Kappung von 1.536 Zeichen für `description` und `when_to_use` zusammen.

**Stellschrauben, alle offiziell dokumentiert:**

- `skillListingBudgetFraction` (Setting): hebt das Budget an, z. B. `0.02` = 2 % des Kontextfensters.
- `SLASH_COMMAND_TOOL_CHAR_BUDGET` (Umgebungsvariable): setzt stattdessen einen festen Zeichenwert.
- `skillListingMaxDescChars` (Setting): ändert die 1.536-Zeichen-Kappung je Skill.
- `skillOverrides` mit `"name-only"`: listet nachrangige Skills ohne Beschreibung und gibt so Budget für andere frei.

**Diagnose:** `/doctor` schätzt die Kontextkosten der Listung und nennt die größten Posten; beim Überlauf schreibt Claude Code zusätzlich eine Warnung ins Debug-Log (`--debug`). Die Skills-Zeile in `/context` zeigt die Größe der Listung **nach** Anwendung des Budgets (ab v2.1.196; davor zählte sie den vollen Text und konnte ein Mehrfaches des Budgets anzeigen).

**Folgerung für dieses Vorhaben:** Viele Skills sind kein hartes Hindernis, sondern eine Stellschraubenfrage. Es bleibt die Formulierungsregel aus Kapitel 2.2: Der Hauptanwendungsfall steht vorn, denn gekürzt wird von hinten.

### 8.2 Arbeitsmodell für die Verteilung der Anweisungen

Festlegung, vom Entwickler am 22. August 2026 bestätigt. Sie ist der Maßstab, nach dem jede Anweisung ihrem Ort zugeordnet wird:

1. **Skills sind der Normalfall.** Praktisch jede Anweisung ist zweckgebunden und bekommt ein Skill-Zuhause mit stillem Trigger.
2. **Die zentrale `~/.claude/CLAUDE.md` bleibt minimal:** Chat auf Deutsch, Duzen, und die Trigger-Tafel (die stillen Trigger der Skills). Zieht ein Skill nicht, ist das der Notfall — der Entwickler wiederholt den Auftrag mit Hinweis auf den zu beachtenden Skill.
3. **Die Projekt-`CLAUDE.md` ist der Ausnahmefall:** nur für irreversible projektspezifische Schutzfälle und für wirklich Nicht-Wiederverwendbares, das sich nicht über Kontext oder Skills abfangen lässt.
4. **claude.ai ist zweite Zielwelt, kein Sonderfall:** Auch dort gibt es zentrale und projektlokale Anweisungen sowie hochladbare Skills. Manche Skills gelten beidseitig, manche nur auf einer Seite — entwickelt werden alle in diesem Vorhaben.

### 8.3 Geltungsbereich: Claude arbeitet nicht nur am Code

Festlegung, vom Entwickler am 22. August 2026 vorgegeben. Claude wird weit über das Coden hinaus eingesetzt; dass die bisher gesammelten Anweisungen fast nur vom Coden handeln, ist Zufall ihrer Herkunft, keine Aussage über die Nutzung. Daraus folgt für jede Anweisung und jeden Skill: Eine Regel, die nur fürs Coden gilt, muss ausdrücklich so deklariert sein — in der `description`, im Trigger und im Skill-Körper —, damit sie eine Claude-Instanz in anderen Arbeitsformen nicht bindet. Eine Dokumentation beschreibt nicht zwingend eine Software, ein Plan ist nicht zwingend ein Softwareentwicklungsplan.

Prüffrage bei jeder Zuordnung eines Anweisungs-Postens: Gilt er nur beim Coden, in allen Arbeitsformen oder in einer anderen, benennbaren Arbeitsform? Die Antwort ist Teil der Zuordnung und wird mit festgehalten.

---

## 9 Zielwelten

Jeder Skill gehört in genau eine von drei Gruppen. Was die Zielwelten technisch können, steht in 1.4; hier steht, was daraus für den Bau folgt. Festlegung des Entwicklers vom 27./28. August 2026.

### 9.1 Die drei Gruppen

- **web + code** — der Skill ist in beiden Zielwelten sinnvoll. Wie weit die Fassungen auseinandergehen, entscheidet 9.2.
- **nur code** — der Skill braucht, was es auf claude.ai nicht gibt: Zugriff auf die Dateien des Nutzers, Git, den lokalen Rechner.
- **nur web** — der Skill regelt etwas, das es nur dort gibt (Artefakt-Mechanik, Projektwissen-Uploads).

**Das Zuordnungskriterium ist der Datenweg, nicht das Thema.** Ein Skill, der nur Verhalten regelt, überträgt sich; sobald er Daten anfasst, entscheidet die Frage, ob sie ihn erreichen und ob sein Ergebnis zurückkommt (1.4). Reine Verhaltensregeln sind deshalb fast immer web+code, und der teuerste Fall ist ein Skill, dessen Ergebnis mechanisch zurückgeschrieben werden muss.

**Es gibt keine vierte Gruppe für Claude Cowork, und das ist eine Entscheidung, kein Versehen** (Festlegung des Entwicklers vom 30. August 2026). Cowork arbeitet über angebundene Ordner unmittelbar auf dem Rechner des Nutzers und fiele damit nach dem Datenweg-Kriterium nicht zu „nur web“ — es wäre eine eigene Lage. Bewertet wird sie hier vorerst nicht; die Begründung steht in der zentralen `README.md` des Repositories. Was in diesem Kapitel „web“ heißt, meint deshalb claude.ai-Chat und den Reiter *Chat + Cowork* von Claude Desktop, nicht die Cowork-Arbeitsweise mit angebundenen Ordnern. Wer diese Ausklammerung aufhebt, fängt hier an.

### 9.2 Wie tief die Fassungen auseinandergehen — vier Bauformen

Zwei getrennte Skills sind nie der Weg (2.3). Gestaffelt nach dem, was sich tatsächlich unterscheidet:

| Unterschied | Bauform |
| --- | --- |
| ein Wort — etwa der Ablageort einer Anweisung | **Ein Skilltext**, der beide Orte nennt |
| ein Absatz — ein Prüfschritt hat in einer Welt kein Werkzeug | **Ein Skilltext** mit kurzem Verzweigungsabsatz |
| ein ganzer Mechanismus | **Eigene Regeldatei je Zielwelt**; beim Installieren wird die passende mitgenommen, wie heute schon die Sprachfassung |
| die Zielwelt kann die Sache nicht | **keine Fassung** — begründet in der README des Skills festhalten |

Die dritte Zeile kostet nichts Zusätzliches: Die Zweiteilung aus 5.2 trägt die Zielwelt genauso wie die Sprache. Nur der Ladebefehl im Gate nennt dann einen anderen Pfad-Ausdruck (1.4).

### 9.3 Aufnahmekriterium: Nutzen gegen Dauerkosten

**Ein Skill wird für eine Zielwelt nur gebaut, wenn sein Nutzen dort die Dauerkosten seiner Description trägt.** Die Description steht bei jedem installierten Skill dauerhaft in der Listung, ob er auslöst oder nicht (8.1) — und das ist die einzige Kostenstelle, die keine Zweiteilung wegnimmt.

Der teuerste Fall ist deshalb nicht der große Skill, sondern der **selten gebrauchte mit breitem Trigger**: Er lädt oft und nützt selten. Bei ihm ist die Frage nicht, wie man ihn billiger macht, sondern ob er in dieser Welt überhaupt installiert gehört.

**Technische Zuordnung und Nutzungsentscheidung sind zweierlei.** Die Gruppe sagt, was möglich ist; ob eine mögliche Fassung auch entsteht, entscheidet der Entwickler je Skill — und erst dann, wenn er sie braucht. Eine offene Nutzungsentscheidung ist kein Mangel und wird als solche vermerkt.

### 9.4 Zuordnung der vorhandenen Skills

Stand 30. August 2026. „Web-Fassung“ nennt die Nutzungsentscheidung, nicht die technische Möglichkeit.

| Skill | Gruppe | Web-Fassung | Grund |
| --- | --- | --- | --- |
| `common-code-generation` | web + code | ja | Reine Verhaltensregeln, fasst keine Dateien an. Ein Wort ändert sich: der Ablageort der Plan-Regel |
| `in-depth-online-literature-research` | web + code | ja | Websuche gibt es beidseitig; die Quellenkarte kann Claude dort nicht schreiben, nur vorschlagen |
| `temp-debug-code` | web + code | ja, gebaut | Seit dem 30. August 2026 in ein Tor und zwei Regelzweige geteilt (5.2): Mit Dateizugriff handelt Claude selbst, sonst entscheidet der Nutzer über die Kennzeichnung, und die Methodenleiter kommt hinzu. Die Suchläufe führt dort er aus, nicht Claude. Ob der Skill auf claude.ai installiert wird, bleibt Nutzungsentscheidung nach 9.3 |
| `pedantic-text-editing` | web + code | nein, vorerst | Technisch machbar: Das Ersetzungsskript existiert (`apply_findings.py`), der mechanische Rückweg über `/mnt/user-data/outputs` ist beobachtet (1.4). Der Entwickler hat den Skill am 30. August 2026 dennoch auf Claude Code beschränkt — das Skript müsste für die Web-Welt erst überarbeitet werden. Eine Web-Fassung kommt später |
| `correct-zaaack-md-editor-mistakes` | nur code | — | Die Werkzeuge liefen im Container, aber die Markdown-Dateien des Nutzers kommen nicht hinein und die Korrektur nicht zurück |
| `parallel-sessions` | nur code | — | Git-Worktrees haben auf claude.ai keinen Gegenstand |
| `chat-export` | nur code | — | Braucht Browser-Anbindung und ein Skript auf dem Rechner des Nutzers |
| `recall-skills-after-compact` | nur code | — | Fähigkeit mit Hook-Auslöser (5.0); Hooks und Sitzungstranskripte gibt es nur in Claude Code |

`web-code-editing` ist zugeordnet: **nur web** — er regelt Quellen und Rückgabewege des Web-Frontends; in Claude Code schreibt das Edit-Werkzeug direkt in die Dateien (fertiggestellt in beiden Sprachfassungen am 29. August 2026, Erprobung als hochgeladener Skill offen). Die Skills, die nur unter `~/.claude/skills/` liegen (`konzept-segmentierung`, `konsistenzpruefung`), sind hier nicht bewertet — sie sind nicht im Repo.

Prüfbar: Auf jeden Skill ohne Gruppenangabe in dieser Tabelle lässt sich zeigen — das ist die Lücke. Und auf jede Web-Fassung, die gebaut wurde, ohne dass 9.3 dafür beantwortet ist.

---

## Anhang A — Packen und Prüfen

Die drei Werkzeuge, mit denen die Pakete aus 5.3 entstehen und geprüft werden, stehen hier als Quelltext und nicht als Datei im Repo. Das ist Absicht: So muss der Code bei jedem Gebrauch durch den Kontext der Instanz, die ihn benutzt — er wird gelesen, bevor er läuft, statt ungelesen ausgeführt zu werden. Bei zwei bis drei Läufen im Leben eines Skills ist das der bessere Tausch. Der Preis ist bekannt: Der Code läuft nie in der Fassung, in der er hier steht, ein Tippfehler fällt erst beim nächsten Gebrauch auf. Wer ihn dabei findet, zieht diesen Anhang nach.

Die Prosa-Code-Grenze der Arbeitsanweisungen (§2.2) steht dem nicht entgegen. Sie schützt Konzept- und Implementierungsdokumente eines Produkts davor, den Code vorwegzunehmen, gegen den sie später geprüft werden. Diese Datei ist kein solches Dokument, sondern die laufende Anweisung und Definition des Vorhabens selbst — und die beiden Werkzeuge sind kein Produkt, sondern Werkbank. Für Skill-Texte und Implementierungsdokumentation bleibt die Grenze unverändert.

**Was auch alle drei zusammen nicht leisten:** Eine Datei, die ins Paket gehört, auf die aber nirgends ein Verweis zeigt, fehlt unbemerkt. Der Packer kennt nur seine Argumentliste, der Verweisprüfer nur die Namen, die im Text vorkommen, und der Aktualitätsprüfer nur das, was bereits im Archiv liegt. Keines der drei kann wissen, was fehlt — diese eine Lücke schließt allein der Blick auf die Dateiliste.

### A.1 Der Packer

Baut ein Archiv aus einer ausdrücklich übergebenen Dateiliste, einmal je Paket aufgerufen:

```
build-zip.sh <skill-ordner> <skill-name> <zip-name> <quelle>:<ziel> [<quelle>:<ziel> ...]
```

`<quelle>` ist relativ zum Skill-Ordner, `<ziel>` der Name im Archiv — dort werden die drei Umbenennungen aus 5.3 gesetzt.

```bash
#!/usr/bin/env bash
# Baut ein Installationspaket eines Skills.
# Zeitstempel: jede Datei behält ihren eigenen (cp -p), das Archiv bekommt
# per -o den der jüngsten Datei. Kompression 9, -X ohne uid/gid-Extras,
# Einträge sortiert -> gleicher Inhalt ergibt gleiche Bytes.
set -euo pipefail
DIR=$1; NAME=$2; ZIPNAME=$3; shift 3
STAGE=$(mktemp -d)
mkdir -p "$STAGE/$NAME"
for pair in "$@"; do
  src=${pair%%:*}; dst=${pair##*:}
  [ -f "$DIR/$src" ] || { echo "FEHLT: $DIR/$src" >&2; exit 1; }
  cp -p "$DIR/$src" "$STAGE/$NAME/$dst"
done
mkdir -p "$DIR/downloads"
OUT=$(cd "$DIR/downloads" && pwd)/$ZIPNAME
rm -f "$OUT"
( cd "$STAGE" && find "$NAME" -type f | LC_ALL=C sort | zip -9 -o -X -q "$OUT" -@ )
rm -rf "$STAGE"
echo "$ZIPNAME  $(stat -c%s "$OUT") Bytes  Archivdatum $(stat -c%y "$OUT" | cut -d. -f1)"
```

Laut scheitert er in drei Fällen: bei einer fehlenden Datei (`FEHLT:`, Exitcode 1), bei einem Skill mit Unterordner, weil das Zielverzeichnis im Staging nicht angelegt wird, und bei einem Doppelpunkt im Dateinamen, weil das Paar dann falsch zerlegt und die Quelle nicht gefunden wird. Still bleibt allein die in der Argumentliste vergessene Datei.

### A.2 Der Verweisprüfer

Öffnet jedes gebaute Archiv, sammelt alle Verweise auf `.md`- und `.py`-Dateien ein — die in Backticks ebenso wie die als Markdown-Link — und meldet, welche davon im Archiv nicht liegen. `CLAUDE.md` ist ausgenommen: Sie liegt am Zielort, nicht im Paket. Ausgeführt aus `skills/` heraus prüft er über `*/downloads/*.zip` alle Pakete aller Skills auf einmal.

```python
import zipfile, re, glob
back = re.compile(r'`([A-Za-z][A-Za-z0-9_.-]*\.(?:md|py))`')
link = re.compile(r'\]\((?!https?:)([A-Za-z][A-Za-z0-9_.-]*\.(?:md|py))\)')
EXTERN = {"CLAUDE.md"}
for zp in sorted(glob.glob("*/downloads/*.zip")):
    z = zipfile.ZipFile(zp)
    members = [m for m in z.namelist() if not m.endswith("/")]
    names = {m.split("/", 1)[1] for m in members}
    miss = {}
    for m in members:
        t = z.read(m).decode("utf-8", "replace")
        for kind, pat in (("Text", back), ("Link", link)):
            for ref in set(pat.findall(t)):
                if ref not in names and ref not in EXTERN:
                    miss.setdefault((ref, kind), set()).add(m.split("/", 1)[1])
    print(f"{'ok' if not miss else 'FEHLT':5} {zp.split('/')[-1]}")
    for (ref, kind), where in sorted(miss.items()):
        print(f"        {kind}: {ref}  <- {', '.join(sorted(where))}")
```

Meldet er für jedes Archiv `ok`, ist jeder namentliche Verweis auflösbar. Sonst nennt er zu jedem Fehlverweis die Datei, in der er steht, damit die Korrektur nicht gesucht werden muss.

**Zwei Fundarten meldet er, die keine Fehler sind,** und das mit Absicht: Verweise auf Dateien des Repositories, die nie in ein Paket gehören (`skill-dev-doc.md` etwa), und Dateinamen, die bloß als Beispiel in Prosa oder Tabellen stehen. Beide auszufiltern hieße, dem Werkzeug eine Liste von Ausnahmen mitzugeben, die selbst gepflegt werden müsste — und eine übersehene Ausnahme verschwiege dann einen echten Fehler. Sie werden deshalb beim Ansehen des Ergebnisses aussortiert, nicht im Werkzeug.

### A.3 Der Aktualitätsprüfer

Beantwortet die Frage, die die beiden anderen nicht stellen: **Ist das Paket noch auf dem Stand seiner Quellen?** Er vergleicht jede Datei im Archiv byte-weise gegen die Dateien im Skill-Ordner und meldet, was mit keiner mehr übereinstimmt.

Der Vergleich läuft über den Inhalt, nicht über den Namen. Deshalb braucht das Werkzeug die Umbenennungsregeln aus 5.3 nicht zu kennen: Eine `SKILL.de.md`, die im Paket `SKILL.md` heißt, findet ihren Partner trotzdem. Ausgeführt wird er wie A.2 aus `skills/` heraus.

```python
import zipfile, glob, pathlib
for zp in sorted(glob.glob("*/downloads/*.zip")):
    src = {p.read_bytes() for p in pathlib.Path(zp.split("/")[0]).iterdir() if p.is_file()}
    z = zipfile.ZipFile(zp)
    bad = [n.split("/", 1)[1] for n in z.namelist() if not n.endswith("/") and z.read(n) not in src]
    print(f"{'ok' if not bad else 'VERALTET':9} {zp.split('/')[-1]}" + (f"  -> {', '.join(bad)}" if bad else ""))
```

**Er gehört an das Ende jeder Sitzung, in der an einem Skill gearbeitet wurde** — nicht nur an das Ende des Packens. Der Anlass ist nämlich meistens ein späterer: Am 30. August 2026 sind die beiden `web-code-editing`-Pakete veraltet, weil nach dem Packen und nach dem Release noch ein Absatz in beide READMEs kam. Aufgefallen ist das nur zufällig, beim Erproben des Packers aus A.1 gegen ein bestehendes Archiv.

Zwei Grenzen: Tragen zwei Dateien denselben Inhalt, würde eine Verwechslung nicht auffallen — für den Zweck belanglos, weil das Paket dann trotzdem korrekten Inhalt trägt. Und er sieht nur in den Skill-Ordner selbst, nicht in Unterordner.
