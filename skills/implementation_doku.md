# Implementierungsdoku des Vorhabens `skills/`

Diese Datei ist die übergreifende Dokumentation des Vorhabens `skills/` und trägt zweierlei. **Kapitel 1–7 sind die Vorgaben**, die beim Schreiben **jedes** Skills gelten: die technischen Voraussetzungen, die Regeln für Trigger und Dateien, die Messbefunde, auf denen diese Regeln beruhen, und das Verfahren, mit dem sich beides nachprüfen lässt. Sie standen vormals in `skill_vorgaben.md`; wo eine Skill-README kurz „Vorgaben, Kapitel n" schreibt, ist dieses Dokument gemeint. **Kapitel 8** hält die übergreifenden Feststellungen und Festlegungen der Neuordnung der Arbeitsanweisungen fest — was recherchiert und belegt ist, und nach welchem Modell die Anweisungen auf Skills und CLAUDE.md-Ebenen verteilt werden. Dem offiziellen Segmentschema der Arbeitsanweisungen (§2.3) folgt die Datei bewusst nicht; die Begründung steht zwei Absätze weiter.

Was hier **nicht** steht: der Arbeitsstand einzelner Skills. Die Skills stehen einzeln nebeneinander und werden nicht aufeinander aufbauend entwickelt — ein gemeinsamer Fahrplan und eine Protokollierung der Umsetzung würden mehr Pflege kosten, als sie einbringen. Was an einem Skill fertig und was offen ist und was er dem Nutzer bietet, steht deshalb in dessen eigener `README.md` (Kapitel 6.1); die Gesamt-`README.md` dieses Ordners nennt ihn nur in ihrer Übersichtstabelle (Kapitel 6.2). Ebenfalls nicht Gegenstand dieses Vorhabens ist `chat-export`: Er ist zwar als Skill implementiert, aber erheblich komplexer als das Definieren einer `SKILL.md` und wird deshalb als eigenes Vorhaben geführt.

**Dieses Vorhaben folgt bewusst anderen Regeln als der Rest des Repositories.** Die Arbeitsweise mit Konzept- und Implementierungsdoku, dreigeteilter Segmentstruktur, Fahrplan und Statusdatei (globale `CLAUDE.md`, Abschnitt 2) ist auf Softwareentwicklung zugeschnitten: auf einen zusammenhängenden Code, dessen Teile voneinander abhängen und dessen Entstehung nachvollziehbar bleiben muss. Hier entsteht kein Quellcode, sondern eine Sammlung einzeln nebeneinanderstehender Anweisungstexte. Jeder Skill ist für sich fertig oder unfertig, keiner baut auf einem anderen auf, und keiner wird später gegen eine Konzeptfassung geprüft. Ein gemeinsamer Fahrplan hätte deshalb nichts zu ordnen, und eine Protokollierung der Umsetzung nichts zu belegen. Was Kapitel 1–7 an Vorgaben tragen, entspricht der Sache nach Segment 2 — projektweite Festlegungen, an denen sich jeder einzelne Skill messen lassen muss.

Belegte Aussagen tragen ihre Quelle. **Beobachtung am laufenden System** und **Messung** sind als solche gekennzeichnet und von der offiziellen Dokumentation getrennt — Anthropic baut an diesen Werkzeugen laufend um, und die Doku schweigt zu einem Teil dessen, was hier zählt.

---

## 1 Was beim Schreiben vorausgesetzt wird

### 1.1 Dieses Verzeichnis ist nur die Quelle

Der Ordner `skills/` in diesem Repository wird von Claude Code nicht erkannt. Ein Skill wirkt erst, wenn er an einem der vorgesehenen Ladeorte liegt:

| Ort        | Pfad                                     | Gilt für                  |
| ---------- | ---------------------------------------- | ------------------------- |
| Persönlich | `~/.claude/skills/<skill-name>/SKILL.md` | alle Projekte des Nutzers |
| Projekt    | `.claude/skills/<skill-name>/SKILL.md`   | nur das jeweilige Projekt |

(belegt, [Extend Claude with skills](https://code.claude.com/docs/en/skills))

Daraus folgt die Grundregel für den Aufbau: Ein Skill-Ordner hier trägt **genau die Struktur, die er am Zielort haben wird** (Kapitel 5). Installieren ist dann im Kern das Kopieren des ganzen Ordners; nur bei mehreren Sprachfassungen kommt ein Handgriff hinzu (5.1).

### 1.2 Ladeverhalten

Wird ein Skill durch Trigger-Abgleich oder direkten Aufruf aktiviert, lädt **nur** der Inhalt seiner `SKILL.md`, und zwar als eine einzelne Nachricht, die für den Rest der Sitzung im Kontext bleibt; Claude liest die Datei in späteren Turns nicht erneut. Weitere Dateien im Skill-Ordner lädt Claude nur, wenn die `SKILL.md` ausdrücklich auf sie verweist. (belegt, [Extend Claude with skills](https://code.claude.com/docs/en/skills))

Zwei Konsequenzen, die beim Entwurf immer mitzudenken sind: Der Körper wird **nicht neu gelesen** — eine Regel, die erst spät geladen wird, rettet keine Entscheidung, die vorher gefallen ist. Und Zusatzdateien kosten nichts, solange niemand auf sie verweist.

### 1.3 Stiller Trigger

Ein *stiller Trigger* ist ein Absatz in der `CLAUDE.md` des Zielorts, der eine Bedingung benennt und auf einen Skill verweist. Er ist nicht Teil des Skills, sondern liegt außerhalb davon.

**Wozu.** Der vorgesehene Weg gleicht die `description` gegen die Anfrage ab. Das trägt, solange der Nutzer etwas verlangt, das dem Skill erkennbar entspricht — „übersetze mir das" findet den Übersetzungs-Skill. Es trägt nicht, wenn der Auslöser eine Beobachtung ist, die niemand ausspricht: dass eine zweite Instanz im Repository arbeitet, oder dass die anstehende Änderung größer ist, als die Frage klang. Dann gibt es keine Anfrage, gegen die abgeglichen werden könnte.

**Was er kostet.** Der Trigger-Absatz liegt dauerhaft im Kontext, der Skill-Körper nicht — das ist der ganze Zweck der Konstruktion. Die naheliegende Sorge, ein in der `CLAUDE.md` wiederholter Trigger-Wortlaut könne den Skill vorzeitig mitladen, ist gemessen und **widerlegt** (Kapitel 3).

**Ein Skill ohne stillen Trigger ist der Normalfall.** Gebraucht wird er nur, wenn die Auslösebedingung nicht aus der Nutzeranfrage selbst hervorgeht.

---

## 2 Vorgaben für Trigger

Diese Vorgaben gelten für die `description` eines Skills und für jeden `CLAUDE.md`-Absatz, der auf ihn verweist. **Die Reihenfolge der Punkte ist die Reihenfolge ihrer Wirkung** — wer an einem widerspenstigen Trigger arbeitet, prüft zuerst Punkt 1, nicht Punkt 2.

1. **Die Description entscheidet zuerst.** Sie beginnt mit dem Hauptanwendungsfall und verwendet die Begriffe, die der Nutzer von sich aus benutzen würde — nicht die projektinternen Fachbegriffe. Ein Warnhinweis, eine Einordnung oder ein Meta-Kommentar am Anfang verdrängt den Anwendungsfall von der Stelle, an der er wirkt, und kann den Trigger auf dem unempfindlichsten Modell vollständig unwirksam machen (Messung in Kapitel 3). **Sie steht durchgehend in der dritten Person** und spricht weder Claude noch den Nutzer an: „Erzeugt …", „Übersetzt …", „Verwenden, sobald …" — nicht „Du kannst damit …" und nicht „Verwenden, bevor **Du** …". Der Grund ist kein Stilgeschmack: Die Description wird in den Systemprompt eingefügt, und ein wechselnder Blickwinkel stört dort die Auswahl unter vielen Skills — *„Always write in third person. The description is injected into the system prompt, and inconsistent point-of-view can cause discovery problems"* (belegt, [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)). Für den **Körper** der `SKILL.md` gilt das nicht: Er wird erst nach der Auslösung gelesen und darf Claude direkt ansprechen.
2. **Ereignisförmig formulieren:** Der Auslöser ist ein beobachtbarer, diskreter Fakt, der ankommt — nicht eine Eigenschaft der laufenden Aufgabe. Beispiele nennen, wie sie der Nutzer formulieren würde: wörtliche Nähe senkt die Auslöseschwelle, und vorzeitiges Laden durch Wortlaut-Nähe ist widerlegt (Kapitel 3).
3. **Oder an eine Ankerhandlung binden:** Lässt sich der Auslöser nur als Aufgaben-Eigenschaft fassen („braucht Planung", „ist eine Softwareaufgabe"), wird die Prüfung an eine konkrete Handlung gebunden, die in jeder einschlägigen Sitzung ohnehin vorkommt: „Bevor du zum ersten Mal …, prüfe: …".
4. **Reine Hintergrund-Beobachtung von Aufgaben-Eigenschaften** („Behalte im Blick, ob …") ist die schwächste Form und **allein nicht ausreichend**. Sie funktioniert, wenn die Description gut ist, und versagt, sobald die Description nachlässt — sie hat also keine eigene Tragfähigkeit. Wo eine Eigenschaft der Auslöser ist, gehört zusätzlich ein Anker nach Punkt 3 dazu.
5. **Kalibriert wird auf das unempfindlichste Zielmodell** (Stand der Messung: Sonnet). Empfindlichere Modelle feuern dann höchstens zusätzlich, verpassen aber nichts; wo eine Auslösung garantiert sein muss, ist ein Hook der Weg, kein Trigger.

Prüfbar: Auf jede Description und jeden `CLAUDE.md`-Verweis lässt sich zeigen und sagen, ob er ereignisförmig oder geankert formuliert ist — oder eigenschaftsförmig und damit ein Verstoß; ebenso, ob die Description in der dritten Person steht.

### 2.1 Wo der Anker liegt

Bei einem Skill, der einen **Ablauf** beschreibt, liegt der Anker am Beginn dieses Ablaufs. Bei einem Skill, der ein **Regelwerk** ist und ab der ersten berührten Zeile durchgehend gilt, liegt er am frühestmöglichen Moment der Sitzung. Grund ist das Ladeverhalten (1.2): Weil der Körper nach dem Laden im Kontext bleibt und nicht neu gelesen wird, zählt allein der früheste Treffer. Momente, die der Skilltext selbst erwähnt (etwas benennen, etwas vorschlagen, eine Designentscheidung treffen), taugen deshalb nicht als Auslöser — sie kommen zu spät.

### 2.2 Länge der Description

Für die Skill-Listung gilt eine Grenze von **1.536 Zeichen** für `description` und `when_to_use` zusammen, einstellbar über `skillListingMaxDescChars`; unabhängig davon greift ein Budget von rund einem Prozent des Kontextfensters. Wird es eng, kürzt Claude Code die Beschreibungen fortschreitend und entfernt zuerst die der selten genutzten Skills (belegt, [Extend Claude with skills](https://code.claude.com/docs/en/skills)).

Daraus folgt eine Formulierungsregel, die nichts kostet: **Der Hauptanwendungsfall steht vorn.** Gekürzt wird von hinten — was am Ende steht, ist als Erstes weg. Trigger-Begriffe, auf die es ankommt, gehören in den ersten Satz, nicht in die abschließende Aufzählung. Die Reihenfolge ist auch dann einzuhalten, wenn die eigenen Beschreibungen weit unter der Grenze liegen: Das Budget hängt von der Zahl **aller** installierten Skills ab, nicht von unseren.

### 2.3 Skills erwähnen einander nicht

Zwei Trigger dürfen denselben Ankermoment benutzen. Mehrfachauslösung ist möglich und unschädlich. Kein Trigger-Absatz und kein Skill-Körper verweist jedoch auf einen anderen Skill dieses Verzeichnisses: Jeder muss einzeln installierbar bleiben, und ein Verweis auf etwas, das am Zielort fehlt, ist eine Sackgasse.

---

## 3 Was gemessen wurde

Dieses Kapitel ist durchgehend **Beobachtung am laufenden System** (Testreihe vom 14. August 2026, Claude Code mit Sonnet 5, Opus 5 und Fable 5; ein bis drei Läufe je Bedingung — Richtungsbefunde, keine Beweise). Die offizielle Doku sagt nur, dass Claude Skills nutzt, „when relevant to the task", und schweigt dazu, wann das eintritt. Es steht hier, damit niemand diese Befunde ein zweites Mal erarbeiten muss; das Verfahren, mit dem sie sich nachprüfen oder auf neue Modelle übertragen lassen, steht in Kapitel 4.

**Der stärkste Hebel ist die `description`, nicht der Trigger-Text.** Belegt durch einen Ausschlusstest mit identischem Prompt, identischem `CLAUDE.md`-Text und identischem Modell, bei dem allein die Description getauscht wurde:

| `description` des Skills | Sonnet | Opus | Fable |
| ------------------------ | ------ | ---- | ----- |
| schwach — beginnt mit „TESTSKILL, nicht produktiv", nennt einen Fachbegriff, der in der Anfrage nicht vorkommt | **feuert nicht** | feuert | feuert |
| gut — beginnt mit dem Anwendungsfall, verwendet die Begriffe der Anfrage | feuert | — | — |

Zwei Folgerungen: Eine schwache Description wird von den stärkeren Modellen **kompensiert**, von Sonnet nicht — wer auf Sonnet kalibriert, ist überall sicher. Und: Bevor man am Trigger-Text feilt, gehört die Description geprüft.

**Das erklärende Modell (Orientierungsmoment).** Eine „Beobachte im Hintergrund"-Anweisung hat keinen Ausführungsort — es gibt keinen mitlaufenden Hintergrundprozess, sondern nur den Moment am Anfang eines Turns, in dem das Modell die Nachricht einordnet: „Was ist das, was tue ich zuerst?" Nur dort kann ein Trigger greifen. Enthält die Nachricht eine unmittelbar ausführbare Aufgabe, konkurriert die naheliegende erste Handlung mit der Trigger-Anweisung. Daraus folgen drei Mechanismen — gemessen an Skills mit schwacher Description, sie beschreiben also den ungünstigsten Fall:

- **Ereignisförmige Trigger feuern.** Ein beobachtbarer, diskreter Fakt („ein zweiter Chat ist offen", „im Arbeitsbaum tauchen fremde Änderungen auf") löst zuverlässig aus — spätestens, wenn die Nachricht außer diesem Fakt nichts Bearbeitbares enthält.
- **Eigenschaftsförmige Trigger feuern im Arbeitsfluss schlecht — geankert dagegen zuverlässig.** Charakterisierungen der laufenden Aufgabe lösten in keinem Handszenario aus, auch nicht nach einer 30-Turn-Planungsdiskussion, die die Bedingung inhaltlich exakt erfüllte. Dieselbe Bedingung an eine Ankerhandlung gebunden feuerte sofort — im A/B-Vergleich bei identischem Prompt, gleichem Modell und **gleicher Description**, weshalb dieser Befund von der Description-Korrektur unberührt bleibt.
- **Erzwungene Orientierung aktiviert auch ungeankerte Trigger.** Kommt ein großer, unstrukturierter Textblock ohne direkt ausführbaren Auftrag an (Doku-Dump, Quelltext plus vager Wunsch), muss das Modell erst einordnen, was das ist — in diesem Klassifikationsschritt feuert alles, was passt, auch mehrere Skills gemeinsam.

**Nicht ursächlich sind zwei naheliegende Verdächtige:** weder der Umfang der `CLAUDE.md` (gemessen mit sechs gegen 207 Zeilen, kein Unterschied) noch eine im selben Prompt mitgelieferte Handlungsanweisung („…und deshalb gilt hier: keine schreibenden Git-Aufrufe").

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
- **Die Description des Testskills muss die des echten Skills sein** — sonst misst man sie statt dessen, was man messen will. Ein Warnhinweis „TESTSKILL, nicht produktiv" gehört **nicht** an den Anfang: Er verdrängt den Anwendungsfall von der Stelle, an der er wirkt, und hat in der ersten Testreihe dieses Vorhabens einen Teil der Negativbefunde erzeugt (Kapitel 3). Der Skill-**Körper** darf beliebig als Test gekennzeichnet sein; er wird erst nach der Auslösung gelesen.
- **Verifikation am Transkript, nie über die Selbstauskunft:** Im Session-JSONL unter `~/.claude/projects/<projektpfad>/` wird nach dem `Skill`-tool_use-Eintrag gesucht. Die sichtbare Meldung im Chat ist nur Komfort.
- **Frische Chats je Bedingung, Prompt-Leiter:** Negativkontrolle (themenfremd — darf nicht feuern), implizite Stufe (Situation ohne Schlüsselwörter der Description), eskalierte Stufe. Dazu immer eine Positivkontrolle — sonst ist „feuert nie" nicht von einem kaputten Aufbau unterscheidbar.
- **A/B nur bei gleichem Modell.** Das Modell steht je Antwort im Transkript.
- **Confounds vorher ausräumen:** `CLAUDE.md`-Anweisungen, die dasselbe Verhalten schon bedingungslos anordnen, für die Testdauer entfernen — sonst hat das Modell keinen Anlass, den Skill zu ziehen, weil der Bedarf anderweitig gedeckt ist.
- **Grenze des Verfahrens:** Die Denkblöcke sind im Transkript leer gespeichert — der interne Weg zur Auslösung ist nicht beobachtbar, nur das Verhalten. Erklärende Modelle wie das Orientierungsmoment bleiben deshalb falsifizierbare Deutungen.

**Der skriptbare Weg** (am laufenden System erprobt und bestätigt, 14. August 2026): Der Testaufbau kommt in ein isoliertes Wegwerf-Projekt, etwa im Scratchpad-Verzeichnis — ein Ordner mit `.claude/CLAUDE.md` (nur der zu testende stille Trigger) und `.claude/skills/<name>/SKILL.md` (der Ladeindikator). Dann ein Lauf je Bedingung mit `claude -p "<prompt>" --output-format json --model <modell>`. Der Beweis liegt im Stream: `--output-format stream-json --verbose` gibt jeden Schritt als eigenes Ereignis aus, und ein Skill-Aufruf erscheint darin als `tool_use` mit `"name": "Skill"`, gefolgt von einem `tool_result` mit `Launching skill: <name>`. **`--verbose` ist zwingend** — ohne die Option verweigert `--print` das Stream-Format. Modellvergleiche werden damit zur Schleife statt zur Handarbeit. Was der interaktive Weg weiterhin besser kann: den Verlauf über mehrere Turns beobachten, in denen sich eine Situation erst aufbaut; ein `-p`-Lauf ist einer Erstnachricht gleichwertig.

Der Minimalaufbau ist als Messinstrument gegengeprüft: Mit der vollständigen realen `CLAUDE.md` des Projekts als Umfeld ergab sich dasselbe Ergebnis wie mit der sechszeiligen Testfassung.

---

## 5 Aufbau eines Skill-Ordners

Jeder Skill liegt unter `skills/<skill-name>/`. Der Ordnername trägt **kein** Sprachkürzel; die Dateien darin tragen es (5.1). Enthalten sind:

- **`SKILL.md`** — verpflichtend. Frontmatter mit `name` (gleich dem Ordnernamen), `description` (der reguläre Trigger, nach Kapitel 2 formuliert) und `license`. Letzteres ist reine Deklaration für den Leser: „Claude Code accepts the field but doesn't act on it" (belegt, [Extend Claude with skills](https://code.claude.com/docs/en/skills)). Welche Lizenz gewählt wird, gibt Anthropic nicht vor (recherchiert am 14. August 2026); hier gilt einheitlich CC0, begründet in der Gesamt-README. Für den Umfang empfiehlt dieselbe Quelle, unter 500 Zeilen zu bleiben — eine Empfehlung, keine harte Grenze.
- **`README.md`** — verpflichtend. Die gesamte Dokumentation dieses Skills: was er leistet, wie er installiert wird, seine Feinheiten, sein Arbeitsstand und seine offenen Punkte. Aufbau nach 6.1; unter der Überschrift die Datumszeile (Projekt-CLAUDE.md, „Datumszeilen").
- **`CLAUDE-snippet.md`** — nur bei Skills mit stillem Trigger. Aufbau: ganz oben die Datumszeile (Projekt-CLAUDE.md, „Datumszeilen"), darunter eine kursive Kopfnotiz, die erklärt, was mit der Datei zu geschehen hat, darunter eine Trennlinie, darunter der zu übernehmende Absatz im Wortlaut. Die Trennlinie ist die maßgebliche Grenze: Was darunter steht, wird in die `CLAUDE.md` des Zielorts übernommen, was darüber steht — Datumszeile eingeschlossen — nicht.
- **Weitere Dateien** — nur, wenn die `SKILL.md` ausdrücklich auf sie verweist; sonst werden sie nie geladen (1.2).

**Ein Ordner darf vorübergehend nur die `README.md` enthalten.** Das ist der Zustand einer festgehaltenen Idee: Sie hat einen Namen, einen Platz und eine Stelle, an der ihr Stand nachlesbar ist, aber noch keine Anweisungen. Erst wenn entschieden ist, dass daraus ein Skill wird, kommt die `SKILL.md` dazu.

**Installiert wird durch Kopieren des gesamten Skill-Ordners** — die `CLAUDE-snippet.md` eingeschlossen. Sie darf am Zielort liegen bleiben, nachdem ihr Inhalt unterhalb der Trennlinie in die `CLAUDE.md` übernommen wurde: Wirksam ist allein die `CLAUDE.md`, die Datei selbst ist dort inert. Die frühere Pflicht, sie am Zielort zu löschen, schützte vor unbemerkt driftenden Trigger-Doppeln; diesen Schutz leistet jetzt die Datumszeile — an ihr ist ablesbar, von welchem Stand die installierte Kopie ist (Festlegung des Entwicklers vom 24. August 2026).

**Die `README.md` gehört mit an den Zielort.** Sie ist die Anwenderdokumentation des Skills (6.1), und die `SKILL.md` darf für Begründungen und Nachfragen des Nutzers auf sie verweisen (`${CLAUDE_SKILL_DIR}/README.md`) — so bleibt der Skilltext schlank, ohne dass Begründungen verloren gehen. Fehlt die README am Zielort, funktioniert der Skill trotzdem; nur Antworten auf Warum-Fragen fallen dünner aus. Ihr Vorhandensein wird nicht geprüft.

**Zusatzdateien, die zur Laufzeit gelesen oder geschrieben werden,** spricht der Skill über `${CLAUDE_SKILL_DIR}` an. Der Platzhalter wird laut offizieller Doku nur in Claude Code tatsächlich ersetzt; in claude.ai bliebe ein solcher Verweis wörtlicher Text bzw. die nötigen Datei-Werkzeuge fehlen ganz (belegt, [Extend Claude with skills](https://code.claude.com/docs/en/skills)). Ein Skill, der in beiden Umgebungen laufen soll, kann daraus seine Umgebung erkennen: Gelingt der Zugriff auf einen echten, aufgelösten Pfad, läuft er lokal.

**Zum `name`:** Kleinbuchstaben, Ziffern und Bindestriche, höchstens 64 Zeichen, keine XML-Tags, nicht die reservierten Wörter „anthropic" und „claude". Anthropic empfiehlt die Verlaufsform (`processing-pdfs`) und lässt Substantiv- und Handlungsformen ausdrücklich als Alternative zu (belegt, [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)); die Skills hier folgen der Substantivform. Kodiert ein Skill die Arbeitsweise einer bestimmten Person statt einer allgemein gültigen, gehört ein Kürzel in den Namen (`software-dev-doc-fh`). Das macht im Namen sichtbar, dass es andere Arbeitsweisen gibt, und lädt dazu ein, dafür einen eigenen Skill zu schreiben, statt diesen zu verbiegen.

### 5.1 Sprachfassungen

**In welcher Sprache ein Skill geschrieben und in welchen Sprachen er dokumentiert wird, entscheidet der Nutzer im Einzelfall.** Es gibt keine Pflicht zu zwei Fassungen: Ein Skill, den es nur auf Deutsch gibt, ist deshalb nicht unfertig. Ist eine weitere Fassung beschlossen, aber noch nicht geschrieben, gehört sie unter „Offen" in die README des Skills (6.1) — dorthin aber erst nach der Entscheidung, nicht vorsorglich.

**Solange es nur eine Fassung gibt, trägt sie kein Sprachkürzel.** Die Dateien heißen dann schlicht `SKILL.md`, `README.md` und `CLAUDE-snippet.md`, und beim Installieren ist an den Namen nichts zu tun.

Liegen mehrere Fassungen von `SKILL.md` oder `CLAUDE-snippet.md` vor, liegen sie im **selben** Ordner und werden durch ein Sprachkürzel unmittelbar vor der Endung `.md` unterschieden:

| Deutsch                  | Englisch                 |
| ------------------------ | ------------------------ |
| `SKILL.de.md`            | `SKILL.en.md`            |
| `CLAUDE-snippet.de.md`   | `CLAUDE-snippet.en.md`   |

Das Kürzel tragen dann beide Fassungen dieser Dateien. Wo dieses Dokument die bloßen Namen `SKILL.md` oder `CLAUDE-snippet.md` verwendet, ist die Datei unabhängig von ihrer Sprachfassung gemeint.

**Die `README.md` ist davon ausgenommen — bewusst asymmetrisch.** Bei mehreren Fassungen trägt nur die englische ein Kürzel (`README.en.md`); die deutsche heißt unverändert `README.md`, ganz ohne Kürzel. Grund (recherchiert 23. August 2026): GitHub und GitLab zeigen automatisch nur eine Datei namens exakt `README.md` an, sobald jemand einen Ordner im Web-Interface öffnet — ein Sprachkürzel verhindert das, unabhängig davon, für welche Sprache es steht. Da die Arbeitssprache dieses Repositories Deutsch ist (siehe unten), bekommt die deutsche Fassung deshalb den Vorrang: Sie ist es, die beim Browsen ohne einen Klick sichtbar wird.

**Beim Installieren sorgt ein Zusatzschritt für den Namen, den Claude Code erwartet.** Der Ordner wird vollständig kopiert; trägt die `SKILL.md` Sprachkürzel, wird die gewählte Fassung am Zielort zusätzlich als `SKILL.md` abgelegt — Claude Code erkennt keinen anderen Namen, eine `SKILL.de.md` allein ist kein Skill. Die Fassungen mit Kürzel sind am Zielort wirkungslos und dürfen liegen bleiben. Die `CLAUDE-snippet.md` braucht keinen Namensschritt: Ihr Inhalt wird ohnehin in die `CLAUDE.md` übernommen, die Datei selbst ist am Zielort inert (Kapitel 5). Der Ordnername bleibt in jedem Fall unverändert, denn er trug nie ein Kürzel.

Daraus folgen drei Festlegungen, die beim Schreiben leicht übersehen werden:

- Das Frontmatter-Feld **`name` trägt kein Sprachkürzel**. Es muss dem Ordnernamen gleichen (Kapitel 5), und der Ordner heißt in beiden Fassungen gleich. Die deutsche und die englische `SKILL` tragen also denselben `name`.
- Der **Slash-Aufruf** heißt entsprechend `/<skill-name>`, nie `/<skill-name>-de`. Wo die `description` ihn selbst nennt, gehört er ohne Kürzel dort hinein.
- Mehrere Fassungen sind **Übersetzungen desselben Skills**, keine mehreren Skills. Sie tragen dieselben Regeln, dieselben Anker und dieselbe Struktur. Weicht eine inhaltlich ab, ist das ein Fehler, kein Sprachunterschied.

**Was für eine weitere Fassung spricht.** Die Arbeitssprache dieses Repositories ist Deutsch, die Skills sollen aber weitergegeben werden können — `skills/` unterliegt anders als `chat-export/` und `home-.claude-sharing/` keiner Weitergabebeschränkung. Und die Sprache des Skilltextes ist eine Festlegung mit Wirkung: Der Körper der `SKILL.md` liegt nach dem Laden für den Rest der Sitzung im Kontext (1.2) und prägt die Sprache, in der Claude anschließend antwortet.

---

## 6 Die beiden README-Arten

Sie überschneiden sich nicht: Die README **am Skill** trägt alles, was über diesen einen Skill zu sagen ist — die Beschreibung dessen, was er leistet, seine Installation, seine Feinheiten und seinen Arbeitsstand. Sie ist damit zugleich seine Anwenderdokumentation und darf am Zielort liegen bleiben (Kapitel 5). Die **Gesamt-README** führt in das Vorhaben ein und listet die Skills, beschreibt aber keinen davon: Jeder Skill steht dort ausschließlich als Zeile der Übersichtstabelle. Damit gibt es zu einem Skill nur eine beschreibende Stelle, und sie liegt dort, wo auch gearbeitet wird.

### 6.1 README je Skill

Sie ist die vollständige Dokumentation dieses einen Skills und liest sich von „was ist das" zu „woran wird noch gearbeitet". Verlangte Reihenfolge:

1. **Überschrift** — Skillname und in einem Halbsatz, wozu er da ist.
2. **Statushinweis**, unmittelbar unter der Datumszeile und **ohne eigene Zwischenüberschrift**: ob der Skill benutzbar ist, mit demselben Symbol, das seine Zeile in der Übersichtstabelle der Gesamt-README trägt (6.2). Ist er es nicht uneingeschränkt, steht in einem Satz dabei, was fehlt, mit Verweis auf den Schlussabschnitt.
3. **Überblick** — was der Skill leistet, in Prosa. Die Kernaussage steht **fett** im ersten Satz. Umfassend genug, dass der Nutzer den Skill danach einschätzen kann, aber ohne Detailflut; dazu die **Abgrenzung**, wo sie nicht selbstverständlich ist: wofür der Skill ausdrücklich **nicht** gilt.
4. **Kapitel „Installation"** — die vollständige Anleitung, **konkretisiert auf diesen Skill**: echte Pfade statt Platzhalter, die tatsächlich vorhandenen Dateien statt des allgemeinen Falls. Nicht ein Verweis auf das Installationskapitel der Gesamt-README, sondern die Schritte selbst. Braucht der Skill **keinen** stillen Trigger, wird dieser Schritt ersatzlos weggelassen — er wird nicht als „entfällt hier" aufgeführt. Ein Schritt, am Zielort etwas zu löschen, kommt nicht vor (siehe Kapitel 5).
5. **Kapitel „Details"** — alles Weitere: Anwenderhinweise, Feinheiten des Verhaltens und die Hinweise, die dem weiteren Ausbau dienen, insbesondere die Regeln, deren Vereinfachung die Funktion zerstören würde.
6. **Kapitel „Stand und Offenes"** — zum Schluss und in dieser Folge:
   - **Status** — was fertig ist, in einem Satz.
   - **Offen** — die noch anstehenden Punkte als Liste. Diese Liste ersetzt den früheren Gesamt-Fahrplan des Vorhabens: Sie steht dort, wo die Arbeit stattfindet, und ist damit beim Öffnen des Skills sofort sichtbar. Erledigtes fliegt raus.
   - **Bewusst offen gelassene Entscheidungen**, sofern es welche gibt — Festlegungen, die der Skill absichtlich nicht trifft, weil sie ins Zielprojekt gehören. Das ist Vorwissen für die Weiterentwicklung, kein Versäumnis, und muss als solches erkennbar sein.

Steht ein Plan für den nächsten Schritt an einem Skill an, steht er hier — ausdetailliert unter „Offen", höchstens einer gleichzeitig, deutlich als noch nicht ausgeführt gekennzeichnet. Nach der Ausführung wird er ersetzt, nicht ergänzt.

### 6.2 Gesamt-README

Die `README.md` dieses Ordners ist der Einstieg in das Vorhaben: Sie sagt, wozu es das gibt, wie ein Skill installiert wird und welche Skills es gibt. Was ein einzelner Skill leistet, steht nicht hier, sondern in seiner eigenen README (6.1). Verlangter Aufbau:

1. **Die Skills im Einzelnen** — eine Tabelle über **alle** Skills des Ordners, auch die unfertigen und die, von denen bisher nur die Idee festgehalten ist. Je Zeile: der Ordnername, verlinkt auf die README des Skills; die Statussymbole; ein Satz zum Zweck. Darunter die Legende der Symbole. Mehr steht hier nicht — jede weitere Beschreibung gehört in die README des Skills (6.1). Diese Tabelle steht **vorn**: Wer die Gesamt-README öffnet, sucht in aller Regel einen Skill, nicht eine Begründung.
2. **Zweck des Vorhabens** — kurz und prägnant, ohne Herleitung.
3. **Skills beschaffen und installieren** — beginnt mit einem knappen Verweis auf die offizielle Doku zu Skills als Mechanismus, gefolgt vom Hinweis, dass die vorgesehene Trigger- und Ladetechnik hier um stille Trigger erweitert wurde (1.3). Danach die Zielorte, der Kopiervorgang und die Behandlung der `CLAUDE-snippet.md`: Trigger-Inhalt in die `CLAUDE.md` übernehmen; die Datei bleibt am Zielort liegen, ihre Datumszeile zeigt den Stand der Installation. Dazu die Regeln aus Kapitel 2 dieser Vorgaben in der Kurzfassung, damit niemand einen Trigger beim Anpassen unwirksam macht. Das alles im allgemeinen Fall — die auf den einzelnen Skill heruntergebrochene Anleitung steht in dessen eigener README (6.1).
4. **Offene Punkte des Vorhabens** — nur, was keinem einzelnen Skill zuzuordnen ist. Alles Skillbezogene steht in dessen README (6.1); eine zweite Liste hier würde sofort auseinanderdriften.

Dazu ein **Lizenzabschnitt**: CC0, mit einer Aufzählung dessen, was das für den Nutzer konkret bedeutet.

**Sprachfassungen.** Auch hier entscheidet der Nutzer, in welchen Sprachen die Gesamt-README vorliegt (5.1). Ihre Benennung folgt aber der Konvention der Wurzel-READMEs dieses Repositories, nicht dem Kürzel-Schema der Skill-Ordner: Die deutsche Fassung heißt `README.md`, jede weitere trägt ihr Kürzel (`README.en.md`).

---

## 7 Wortwahl im Skill-Text

**Ein Skill definiert seine Begriffe nicht, er benutzt eindeutige.** „Nutzer" ohne Zusatz bezeichnet immer den Menschen im Chat — dieses Wort ist im Systemprompt bereits so belegt, ein Skill erbt die Bedeutung umsonst. Geht es um den Menschen vor der fertigen Software, steht dort **„Endanwender"**, ausgeschrieben an jeder Fundstelle. Ein einleitender Absatz, der die Rollen erklärt, gehört nicht in einen Skill: Er kostet Kontext für etwas, das Claude schon weiß, und widerspricht der Empfehlung, nur Kontext zu ergänzen, den Claude nicht hat — *„Does this paragraph justify its token cost?"* (belegt, [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).

**Beobachtung am laufenden System** (16. August 2026): Die offiziell veröffentlichten `SKILL.md` unter `~/.claude/plugins/marketplaces/claude-plugins-official/` benutzen „the user" durchgehend, ohne ihn ein einziges Mal zu definieren; die eine Datei, die über den Menschen vor der fertigen Software spricht (`frontend-design`), setzt „end user" an die Fundstelle, ohne Vorrede.

Daneben gilt die allgemeine Empfehlung derselben Quelle, einen Begriff einmal zu wählen und durchzuhalten: *„Choose one term and use it throughout the Skill."*

Prüfbar: Auf jede Stelle, an der „Nutzer" allein steht, obwohl der Mensch vor der fertigen Software gemeint ist, lässt sich zeigen — das ist der Verstoß. Ebenso auf jeden Absatz, der Rollen oder Begriffe erst erklärt, statt sie zu benutzen.

---

## 8 Allgemeine Festlegungen der Neuordnung

### 8.1 Description-Budget der Skill-Listung — belegt und parametrierbar

Feststellung, recherchiert am 22. August 2026 gegen die offizielle Dokumentation ([Extend Claude with skills](https://code.claude.com/docs/en/skills)). Diese Grenzen stammen von Anthropic und sind keine Eigen-Festlegung dieses Repos; Kapitel 2.2 gibt sie nur wieder.

**Wie der Mechanismus arbeitet:** Claude Code lädt eine Listung aller Skill-Namen samt Beschreibungen in den Kontext. Die Namen sind darin **immer vollständig** enthalten; gekürzt werden nur die Beschreibungen. Das Budget dafür „scales at 1% of the model's context window". Läuft die Listung über, entfernt Claude Code Beschreibungen beginnend bei den am seltensten aufgerufenen Skills — „drops descriptions starting with the skills you invoke least, so the skills you use most keep their full text". Unabhängig vom Budget gilt je Skill eine Kappung von 1.536 Zeichen für `description` und `when_to_use` zusammen.

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
