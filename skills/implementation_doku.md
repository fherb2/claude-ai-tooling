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

Weil ein Skill an seinem echten Zielort (1.2) allein durch Trigger-Abgleich automatisch geladen wird — ohne expliziten Auftrag, allein durch die im Hintergrund laufende Kontext-Zusammenfassung —, lässt sich ein Skill-Entwurf aus diesem Projekt heraus testen, ohne ihn dort abzulegen: Man weist Claude in einem Chat explizit an, eine bestimmte `SKILL.md`-Datei zu lesen und für den laufenden Chat exakt so zu berücksichtigen, als wäre sie im Hintergrund über ihre Trigger-Begriffe eingelesen worden. So lassen sich Skill-Inhalte inhaltlich prüfen, bevor sie an einem Ort landen, an dem sie ab sofort ungefragt automatisch greifen. Dieses Verfahren prüft nur den Inhalt eines Skills, nicht seine Auslösung — dafür siehe 1.6.

## 1.5 Trigger-Verhalten: wann ein Skill von selbst feuert

Dieses Kapitel ist durchgehend **Beobachtung am laufenden System** (Testreihe vom 14. August 2026, Claude Code mit Sonnet 5, Opus 5 und Fable 5; ein bis drei Läufe je Bedingung — Richtungsbefunde, keine Beweise), nicht durch offizielle Doku belegt. Die offizielle Doku sagt nur, dass Claude Skills nutzt, „when relevant to the task", und schweigt dazu, wann das eintritt. Das Testverfahren, mit dem sich diese Befunde nachprüfen oder auf neue Modelle übertragen lassen, steht in 1.6.

**Der stärkste Hebel ist die `description`, nicht der Trigger-Text.** Das wurde erst in der Nachmessung erkannt und stellt einiges richtig, was zuvor der Formulierung des stillen Triggers zugeschrieben worden war. Belegt durch einen Ausschlusstest mit identischem Prompt, identischem CLAUDE.md-Text und identischem Modell, bei dem allein die Description getauscht wurde:

| `description` des Skills | Sonnet | Opus | Fable |
| ------------------------- | ------ | ---- | ----- |
| schwach — beginnt mit „TESTSKILL, nicht produktiv", nennt einen Fachbegriff (`claude-workbench`), der in der Anfrage nicht vorkommt | **feuert nicht** | feuert | feuert |
| gut — beginnt mit dem Anwendungsfall, verwendet die Begriffe der Anfrage („zweite Instanz", „dasselbe Repository") | feuert | — | — |

Zwei Folgerungen: Eine schwache Description wird von den stärkeren Modellen **kompensiert**, von Sonnet nicht — wer auf Sonnet kalibriert, ist überall sicher. Und: Bevor man am Trigger-Text feilt, gehört die Description geprüft; sie entscheidet zuerst. Das deckt sich mit der offiziellen Empfehlung, den Hauptanwendungsfall voranzustellen und Begriffe zu wählen, die der Nutzer von sich aus benutzt (2.1).

**Das erklärende Modell (Orientierungsmoment):** Eine „Beobachte im Hintergrund"-Anweisung hat keinen Ausführungsort — es gibt keinen mitlaufenden Hintergrundprozess, sondern nur den Moment am Anfang eines Turns, in dem das Modell die Nachricht einordnet: „Was ist das, was tue ich zuerst?" Nur in diesem Moment kann ein Trigger greifen. Enthält die Nachricht eine unmittelbar ausführbare Aufgabe, konkurriert die naheliegende erste Handlung mit der Trigger-Anweisung.

Daraus folgen drei Mechanismen — mit der Einschränkung, dass sie an Skills mit schwacher Description gemessen wurden und deshalb den ungünstigsten Fall beschreiben:

- **Ereignisförmige Trigger feuern.** Ein beobachtbarer, diskreter Fakt, der als eigenständige Beobachtung ankommt („ein zweiter Chat ist offen", „im Arbeitsbaum tauchen Änderungen auf, die nicht aus dieser Sitzung stammen"), löst zuverlässig aus — spätestens, wenn die Nachricht außer diesem Fakt nichts Bearbeitbares enthält.
- **Eigenschaftsförmige Trigger feuern im Arbeitsfluss schlecht — geankert dagegen zuverlässig.** Charakterisierungen der laufenden Aufgabe („das braucht eine Planungsphase", „das ist eine Softwareaufgabe") lösten in keinem der Handszenarien aus, auch nicht nach einer 30-Turn-Planungsdiskussion, die die Bedingung inhaltlich exakt erfüllte. Dieselbe Bedingung an eine Ankerhandlung gebunden („Bevor du in einer Sitzung zum ersten Mal einen Lösungsweg vorschlägst oder eine Datei änderst, prüfe: …") feuerte sofort — im A/B-Vergleich bei identischem Prompt, gleichem Modell und **gleicher Description**, weshalb dieser Befund von der Description-Korrektur unberührt bleibt. Das ursprünglich notierte „feuert nie" war zu absolut: Mit guter Description feuerte auch die reine Überwachungsformel im ersten Turn.
- **Erzwungene Orientierung aktiviert auch ungeankerte Trigger.** Kommt ein großer, unstrukturierter Textblock ohne direkt ausführbaren Auftrag an (Doku-Dump, Quelltext plus vager Wunsch), muss das Modell erst einordnen, was das ist — in diesem Klassifikationsschritt wird die Instruktionsliste konsultiert, und es feuert alles, was passt, auch mehrere Skills gemeinsam.

**Nicht ursächlich sind zwei naheliegende Verdächtige.** Weder der Umfang der `CLAUDE.md` (gemessen mit sechs gegen 207 Zeilen, kein Unterschied) noch eine im selben Prompt mitgelieferte Handlungsanweisung („…und deshalb gilt hier: keine schreibenden Git-Aufrufe") verhinderten das Auslösen, solange die Description gut war.

Nebenbefunde derselben Testreihe:

- **Wortlaut-Echo senkt die Schwelle stark:** Nachrichten, die Begriffe der Skill-Description oder des CLAUDE.md-Absatzes fast wörtlich enthalten, lösten aus, wo inhaltsgleiche Umschreibungen schwiegen.
- **Keine Anhäufung:** Semantischer Kontext, der sich über viele Turns aufbaut, löst für sich genommen nicht aus — es gibt keinen Mechanismus, der rückblickend bilanziert.
- **Widerlegt ist die Ausgangssorge dieser Testreihe:** Ein in CLAUDE.md wiederholter Trigger-Wortlaut lädt den Skill nicht vorzeitig — in keinem einzigen Lauf gab es eine Fehlauslösung bei themenfremden Prompts.
- **Modellabhängig ist die Schwelle, nicht der Mechanismus:** Die Positivmechanismen trugen auf allen drei Modellen. Aber Opus und Fable feuerten schon auf eine Ein-Satz-Fehlerbeschreibung, bei der Sonnet in allen Läufen schwieg; Fable unterschied dabei zwischen passenden und nicht passenden Skills, Opus feuerte pauschal alle. Dasselbe Gefälle zeigt die Description-Matrix oben. Sonnet ist die unempfindlichste gemessene Referenz und deshalb der Maßstab, auf den kalibriert wird.
- **Konvergenz mit der Werkzeug-Doku:** Die Beschreibung des `update-config`-Skills von Claude Code nennt dieselbe Grenze als Designannahme — automatisierte „immer wenn X"-Verhalten erfordern Hooks in `settings.json`, „the harness executes these, not Claude". Wo eine Auslösung garantiert sein muss, sind Hooks der Weg; Skill-Trigger bleiben probabilistisch.

## 1.6 Trigger-Verhalten testen

Gegenstück zu 1.4: Dort wird der Inhalt geprüft, ohne den Skill am Zielort abzulegen. Die **Auslösung** lässt sich dagegen nur mit echter Ablage am Zielort (1.2) testen — der Trigger-Abgleich läuft nur über dort liegende Skills. Das Verfahren, mit dem die Befunde in 1.5 entstanden sind:

- **Wegwerf-Skill als Ladeindikator:** Ein Testskill, dessen Körper einzig anweist, das eigene Laden sofort und unübersehbar im Chat zu melden. Die Description trägt die zu testende Trigger-Formulierung.
- **Die Description des Testskills muss die des echten Skills sein** — sonst misst man sie statt dessen, was man messen will. Der naheliegende Warnhinweis „TESTSKILL, nicht produktiv" gehört **nicht** an den Anfang: Er verdrängt den Anwendungsfall von der Stelle, an der er wirkt, und hat in der ersten Testreihe dieses Vorhabens einen Teil der Negativbefunde erzeugt (1.5). Wenn ein solcher Hinweis sein muss, dann am Ende. Der Skill-**Körper** darf beliebig als Test gekennzeichnet sein; er wird erst nach der Auslösung gelesen.
- **Verifikation am Transkript, nie über die Selbstauskunft:** Im Session-JSONL unter `~/.claude/projects/<projektpfad>/` wird nach dem `Skill`-tool_use-Eintrag gesucht. Die sichtbare Meldung im Chat ist nur Komfort; beweiskräftig ist der Tool-Aufruf im Transkript.
- **Frische Chats je Bedingung, Prompt-Leiter:** Negativkontrolle (themenfremder Prompt — darf nicht feuern), implizite Stufe (Situation beschrieben, ohne Schlüsselwörter der Description), eskalierte Stufe. Dazu immer eine Positivkontrolle (Prompt, der sicher feuern muss) — sonst ist „feuert nie" nicht von einem kaputten Aufbau unterscheidbar.
- **A/B nur bei gleichem Modell:** Das Modell steht je Antwort im Transkript. Formulierungsvergleiche auf verschiedenen Modellen vermischen Formulierungs- und Schwelleneffekt (1.5, Modellabhängigkeit).
- **Confounds vorher ausräumen:** CLAUDE.md-Anweisungen, die dasselbe Verhalten bereits bedingungslos anordnen (im Testfall: die Plan-Pflicht aus §1.3 der globalen und „Wo ein Plan steht" der Projekt-CLAUDE.md), für die Testdauer entfernen — mit Sicherungskopie und exakter Wiederherstellung danach. Sonst hat das Modell keinen Anlass, den Skill zu ziehen: Der Bedarf ist schon anderweitig gedeckt.
- **Grenze des Verfahrens:** Die Denkblöcke sind im Transkript leer gespeichert (nur eine Signatur) — der interne Weg zur Auslösung ist nicht beobachtbar, nur das Verhalten. Deutungen wie das Orientierungsmoment-Modell in 1.5 bleiben deshalb erklärende Modelle, falsifizierbar über weitere Verhaltenstests.

### Der skriptbare Weg: Tests im nicht-interaktiven Modus

Die Befunde in 1.5 entstanden in Handarbeit — je ein Chat pro Bedingung, Transkript hinterher ausgewertet. Dasselbe geht nicht-interaktiv und damit wiederholbar. Am laufenden System erprobt und bestätigt (14. August 2026):

- **Der Testaufbau kommt in ein isoliertes Wegwerf-Projekt**, etwa im Scratchpad-Verzeichnis: ein Ordner mit `.claude/CLAUDE.md` (nur der zu testende stille Trigger) und `.claude/skills/<name>/SKILL.md` (der Ladeindikator). So wirken weder die realen Projektregeln noch die realen Skills als Störgröße — die Confound-Bereinigung entfällt, statt sie an echten Dateien vornehmen und wieder zurücknehmen zu müssen.
- **Ein Lauf je Bedingung:** `claude -p "<prompt>" --output-format json --model <modell>` in diesem Ordner. Das Ergebnisobjekt enthält unter anderem `result` (die Antwort), `session_id`, `num_turns`, `total_cost_usd` und eine Token-Aufstellung je beteiligtem Modell.
- **Der Beweis liegt im Stream:** `claude -p "<prompt>" --output-format stream-json --verbose --model <modell>` gibt jeden Schritt als eigenes Ereignis aus, und ein Skill-Aufruf erscheint darin als `tool_use` mit `"name": "Skill"` und dem Skill-Namen im `input`, gefolgt von einem `tool_result` mit `Launching skill: <name>`. Damit ist die Auslösung maschinell prüfbar, ohne sich auf die Selbstauskunft des Modells zu verlassen. **`--verbose` ist hier zwingend** — ohne die Option verweigert `--print` das Stream-Format mit einer Fehlermeldung.
- **Modellvergleiche werden zur Schleife:** `--model` je Lauf gesetzt, derselbe Prompt, derselbe Ordner. Genau die Schwellenunterschiede aus 1.5 lassen sich so in einem Durchgang messen statt in mehreren Chats von Hand.

Was der interaktive Weg weiterhin besser kann: den Verlauf über mehrere Turns beobachten, in denen sich eine Situation erst aufbaut. Ein `-p`-Lauf ist einer Erstnachricht gleichwertig — Eskalationsleitern über mehrere Nutzerbeiträge brauchen entweder `--resume` oder den Chat.

**Der Weg ist als Messinstrument geprüft, nicht nur plausibel:** Er hat einen aus den Handmessungen bekannten Negativbefund reproduziert und anschließend dessen Ursache von zwei anderen Verdächtigen getrennt (1.5). Die Sorge, der Minimalaufbau sei zu künstlich, um übertragbar zu sein, wurde gegengeprüft — mit der vollständigen realen `CLAUDE.md` des Projekts als Umfeld ergab sich dasselbe Ergebnis wie mit der sechszeiligen Testfassung.

## 1.7 Stiller Trigger

**Begriff.** Ein *stiller Trigger* ist ein Absatz in der `CLAUDE.md` des Zielorts, der eine Bedingung benennt und auf einen Skill verweist. Er ist nicht Teil des Skills, sondern liegt außerhalb davon — und er ist das, was den Skill in Situationen auslöst, die die reguläre Technik nicht erreicht.

**Abgrenzung zum regulären Trigger.** Der von Anthropic vorgesehene Weg gleicht die `description` des Skills gegen die Anfrage ab (1.3). Das trägt, solange der Nutzer etwas verlangt, das dem Skill erkennbar entspricht — „übersetze mir das" findet den Übersetzungs-Skill. Es trägt nicht, wenn der Auslöser eine Beobachtung ist, die niemand ausspricht: dass eine zweite Instanz im Repository arbeitet, oder dass die anstehende Änderung größer ist, als die Frage klang. In diesen Fällen gibt es keine Anfrage, gegen die abgeglichen werden könnte.

**Warum „still".** Der Nutzer ruft ihn nicht auf und sieht ihn nicht — er steht in einer Datei, die ohnehin in jeder Sitzung geladen wird, und wirkt von dort aus im Hintergrund. Sichtbar wird er erst durch seine Folge: Der Skill meldet sich, ohne dass jemand ihn verlangt hätte.

**Was er kostet und was nicht.** Der Trigger selbst liegt dauerhaft im Kontext, der Skill-Körper nicht — das ist der ganze Zweck der Konstruktion (1.1). Die naheliegende Sorge, ein in der `CLAUDE.md` wiederholter Trigger-Wortlaut könne den Skill vorzeitig mitladen, ist gemessen und widerlegt (1.5).

**Wie er formuliert sein muss,** damit er überhaupt auslöst, steht als Vorgabe in 2.1; die Messung dahinter in 1.5. Die technische Form — Datei `CLAUDE-snippet.md` im Skill-Ordner, Übernahme in die `CLAUDE.md`, anschließendes Löschen — regelt 2.2.

---

# 2 Vorgaben

## 2.1 Trigger-Formulierung

Soll ein Skill automatisch feuern (nicht nur per `/skill-name`-Aufruf), gilt für seine Description und für jeden CLAUDE.md-Absatz, der auf ihn verweist. **Die Reihenfolge der folgenden Punkte ist die Reihenfolge ihrer Wirkung** — wer an einem widerspenstigen Trigger arbeitet, prüft zuerst Punkt 1, nicht Punkt 2.

1. **Die Description entscheidet zuerst.** Sie beginnt mit dem Hauptanwendungsfall und verwendet die Begriffe, die der Nutzer von sich aus benutzen würde — nicht die projektinternen Fachbegriffe. Ein Warnhinweis, eine Einordnung oder ein Meta-Kommentar am Anfang verdrängt den Anwendungsfall von der Stelle, an der er wirkt, und kann den Trigger auf dem unempfindlichsten Modell vollständig unwirksam machen (Messung in 1.5).
2. **Ereignisförmig formulieren:** Der Auslöser ist ein beobachtbarer, diskreter Fakt, der ankommt — nicht eine Eigenschaft der laufenden Aufgabe. Beispiele nennen, wie sie der Nutzer formulieren würde: wörtliche Nähe senkt die Auslöseschwelle (1.5), und vorzeitiges Laden durch Wortlaut-Nähe ist widerlegt.
3. **Oder an eine Ankerhandlung binden:** Lässt sich der Auslöser nur als Aufgaben-Eigenschaft fassen („braucht Planung", „ist eine Softwareaufgabe"), wird die Prüfung an eine konkrete Handlung gebunden, die in jeder einschlägigen Sitzung ohnehin vorkommt: „Bevor du zum ersten Mal … , prüfe: …".
4. **Reine Hintergrund-Beobachtung von Aufgaben-Eigenschaften** („Behalte im Blick, ob …") ist die schwächste Form und **allein nicht ausreichend**. Sie funktioniert, wenn die Description gut ist, und versagt, sobald die Description nachlässt — sie hat also keine eigene Tragfähigkeit. Wo eine Eigenschaft der Auslöser ist, gehört zusätzlich ein Anker nach Punkt 3 dazu.
5. **Kalibriert wird auf das unempfindlichste Zielmodell** (Stand der Messung: Sonnet). Empfindlichere Modelle feuern dann höchstens zusätzlich, verpassen aber nichts; wo eine Auslösung garantiert sein muss, ist ein Hook der Weg, kein Trigger (1.5).

Prüfbarkeit im Sinne des Aufnahmetests: Auf jede Description und jeden CLAUDE.md-Verweis lässt sich zeigen und sagen, ob er ereignisförmig oder geankert formuliert ist — oder eigenschaftsförmig und damit ein Verstoß.

**Länge der `description` und was bei Überschreitung passiert.** Für die Skill-Listung gilt eine Grenze von **1.536 Zeichen** für `description` und `when_to_use` zusammen, einstellbar über `skillListingMaxDescChars`; unabhängig davon greift ein Budget von rund einem Prozent des Kontextfensters. Wird es eng, kürzt Claude Code die Beschreibungen fortschreitend und entfernt zuerst die der selten genutzten Skills (belegt, [Extend Claude with skills](https://code.claude.com/docs/en/skills)).

Daraus folgt eine Formulierungsregel, die nichts kostet: **Der Hauptanwendungsfall steht vorn.** Gekürzt wird von hinten — was am Ende der Beschreibung steht, ist als Erstes weg. Trigger-Begriffe, auf die es ankommt, gehören deshalb in den ersten Satz, nicht in die abschließende Aufzählung. Die Doku empfiehlt außerdem, Begriffe zu verwenden, die der Nutzer von sich aus benutzen würde — was sich mit dem gemessenen Wortlaut-Echo aus 1.5 deckt.

Die Grenze ist großzügig: Die Beschreibungen der hier entwickelten Skills liegen zwischen 399 und 481 Zeichen, also bei rund einem Drittel. Ein Anlass zur Kürzung besteht nicht; die Reihenfolge ist trotzdem einzuhalten, weil das Budget von der Zahl der insgesamt installierten Skills abhängt und nicht von unseren.

## 2.2 Aufbau eines Skill-Ordners

Jeder Skill liegt in diesem Vorhaben unter `skills/<skill-name>/` und trägt **genau die Struktur, die er am Zielort haben wird** (1.2). Das Installieren ist dadurch ein Kopiervorgang ohne Umbau — und ein Blick in den Ordner zeigt, was der Nutzer bekommt.

- **`SKILL.md`** — verpflichtend. Frontmatter mit `name` (gleich dem Ordnernamen), `description` (der reguläre Trigger, nach 2.1 formuliert) und `license`. Letzteres ist reine Deklaration für den Leser: „Claude Code accepts the field but doesn't act on it" (belegt, [Extend Claude with skills](https://code.claude.com/docs/en/skills)). Für den Umfang der Datei empfiehlt dieselbe Quelle, unter 500 Zeilen zu bleiben — eine Empfehlung, keine harte Grenze.
- **`CLAUDE-snippet.md`** — nur bei Skills mit stillem Trigger (1.7). Aufbau: eine kursive Kopfnotiz, die erklärt, was mit der Datei zu geschehen hat, darunter eine Trennlinie, darunter der zu übernehmende Absatz im Wortlaut. Die Trennlinie ist die maßgebliche Grenze: Was darunter steht, wird in die `CLAUDE.md` des Zielorts übernommen, was darüber steht, nicht.
- **Weitere Dateien** — nur, wenn die `SKILL.md` ausdrücklich auf sie verweist; sonst werden sie nie geladen (1.3).

**Die `CLAUDE-snippet.md` wird am Zielort gelöscht,** sobald ihr Inhalt in der `CLAUDE.md` steht. Grund ist die Regel gegen zwei gleichrangige Fassungen derselben Festlegung: Bliebe sie liegen, gäbe es den Trigger zweimal, und die Fassungen driften beim nächsten Anpassen auseinander. Im Quellverzeichnis hier bleibt sie natürlich bestehen.

**Ein Skill ohne stillen Trigger ist der Normalfall,** nicht die Ausnahme. Er wird nur dann gebraucht, wenn die Auslösebedingung nicht aus der Nutzeranfrage selbst hervorgeht (1.7).

## 2.3 Aufbau der README

Die `README.md` dieses Vorhabens ist die vollständige Anwenderdokumentation der Skills. Sie überschneidet sich inhaltlich mit dieser Implementierungsdoku — das ist gewollt und kein Verstoß gegen die Regel vom einzigen normativen Zuhause: Die README zeigt **das Ergebnis** (was es gibt, wie man es benutzt), diese Doku die **Herleitung und die Anforderungen** (warum es so ist, was noch offen ist). Wer nur benutzen will, liest die README; wer weiterentwickelt, diese Doku.

Verlangter Aufbau:

1. **Zweck des Vorhabens** — kurz und prägnant, ohne Herleitung.
2. **Skills beschaffen und installieren** — beginnt mit einem knappen Verweis auf die offizielle Doku zu Skills als Mechanismus, gefolgt vom Hinweis, dass die vorgesehene Trigger- und Ladetechnik hier um stille Trigger erweitert wurde (1.7). Danach die Zielorte, der Kopiervorgang und die Behandlung der `CLAUDE-snippet.md`: Inhalt in die `CLAUDE.md` übernehmen, Datei danach löschen. Dazu die Regel aus 2.1 in der Kurzfassung, damit niemand einen Trigger beim Anpassen unwirksam macht.
3. **Die Skills im Einzelnen** — je Skill: wozu er dient, was er konkret tut und bewirkt, Besonderheiten, Erweiterungsmöglichkeiten samt der Regeln, deren Verletzung die Funktion zerstört, und Installationsschritte nur dann, wenn sie vom allgemeinen Weg abweichen.

Dazu ein **Lizenzabschnitt**: CC0, mit einer Aufzählung dessen, was das für den Nutzer konkret bedeutet.

---

# 3 Einheiten

## 3.1 `translation-task`

Ordner: `skills/translation-task/`, ohne stillen Trigger — die Auslösung geht vom Nutzer aus („übersetze mir das") und wird von der regulären Description erreicht.

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

## 3.2 `parallel-sessions`

Ordner: `skills/parallel-sessions/`, **mit** stillem Trigger. Ohne ihn bliebe der Skill wirkungslos: Dass eine zweite Instanz arbeitet, spricht niemand als Anfrage aus.

**Zweck.** Klärt die Zusammenarbeit, wenn mehrere Claude-Code-Instanzen gleichzeitig im selben Repository arbeiten. Zwei Schritte in fester Reihenfolge — erst die Schreibhoheit für Git klären (und bis zur Antwort keine schreibenden Kommandos ausführen), dann das Worktree-Modell als saubere Trennung anbieten und beide Einrichtungswege erklären.

**Der Trigger** nennt die Anzeichen als Ereignisse (ein zweiter offener Chat, Änderungen fremder Herkunft im Arbeitsbaum, eine Ankündigung des Nutzers) und bindet die Prüfung zusätzlich an eine Handlung: vor dem ersten schreibenden Git-Kommando der Sitzung. Der Anker ist inhaltlich der kritische Moment — vorher kann eine zweite Instanz keinen Schaden anrichten.

**Gemessen** (14. August 2026, nicht-interaktiv nach 1.6): Mit der jetzigen Description feuert der Trigger auf Sonnet im ersten Turn, und zwar sowohl in dieser Fassung als auch in einer reinen Überwachungsfassung ohne Anker — geprüft mit sechszeiliger und mit vollständiger realer `CLAUDE.md`, mit und ohne konkurrierende Handlungsanweisung im selben Prompt. Dass eine frühere Handmessung hier nicht auslöste, lag an der damaligen Test-Description, nicht am Trigger-Text (1.5). Der Anker bleibt trotzdem, weil die Überwachungsfassung allein keine eigene Tragfähigkeit hat (2.1, Punkt 4).

**Belegtes Verhalten des Worktree-Werkzeugs** (Beobachtung an der Werkzeugbeschreibung von `EnterWorktree`, 14. August 2026): Es legt den Worktree unter `.claude/worktrees/` an und erzeugt dabei **immer einen neuen Branch**, nie den bereits ausgecheckten. Basis ist standardmäßig `origin/<default-branch>`; die Einstellung `worktree.baseRef` mit dem Wert `head` zweigt stattdessen vom aktuellen lokalen HEAD ab. Ein Branch kann ohnehin nie in zwei Worktrees gleichzeitig ausgecheckt sein — das erzwingt Git.

**Offene Punkte, bewusst nicht im Skill entschieden.** Sie sind Vorwissen für die Weiterentwicklung, nicht Versäumnis:

- **Branch-Benennung im Worktree-Modus.** Arbeitet ein Projekt mit einem festen Branch-Namen für Claudes Arbeitsstand (`claude-workbench`), kollidiert das mit mehreren gleichzeitigen Worktrees: Sie brauchen mehrere Namen. Denkbare Wege sind ein festes Schema mit Zusatz (`claude-workbench-<aufgabe>`), die freie Vergabe durch das Werkzeug, oder der Verzicht auf den festen Namen im Worktree-Fall. Hinzu kommt, dass die Werkbank per Konvention vom **Hauptpfad** abgeleitet wird, das Werkzeug aber standardmäßig vom Default-Branch — die Einstellung `worktree.baseRef` oder ein manuelles `git worktree add` wären die Auswege.
- **Projekteigene Zustandsdateien mit Branch-Bezug.** Wo eine versionierte Datei den Namen der Werkbank festhält (etwa `arbeitsdaten.json`), trägt jeder Branch seine eigene Fassung — ein gemeinsamer Zustand entsteht also nicht. Offen ist, ob ein abweichender Werkbank-Name beim Zusammenführen in den Hauptpfad mitwandern soll oder dort ausgenommen wird, und ob die Datei ein eigenes Feld für den aktuellen Worktree-Namen braucht.

Beides sind Festlegungen des jeweiligen Projekts und gehören in dessen `CLAUDE.md`, nicht in den Skill. Der Skill benennt den Konflikt und überlässt die Entscheidung dem Nutzer.

## 3.3 `software-dev-doc-fh`

Ordner: `skills/software-dev-doc-fh/`, **mit** stillem Trigger.

**Zweck.** Ein Dokumentationsstandard für die Planung vor der Kodierung und für die laufende Mitschrift des Implementierten: was umgesetzt wird, welche Festlegungen getroffen wurden und, wo es nicht selbstverständlich ist, warum so und nicht anders. Ausdrücklich nicht gemeint sind Quelltextkommentare und Anwenderdokumentation.

**Inhalt.** Vier Phasen (Findung, Fixierung, Segmentierung, Implementierung), die Prosa-Code-Grenze samt bindender Begründung, die Dokumentstruktur mit numerischen Präfixen, die drei Segmente mit dem Aufnahmetest für Segment 2, die Trennung von Fahrplan und Status, die Regel „wo ein Plan steht", die Arbeitsschleife der Implementierung und die Behandlung von Review-Befunden im Doku-Anhang.

**Warum das Kürzel `-fh`.** Der Standard ist die Arbeitsweise eines bestimmten Entwicklers, nicht der einzig mögliche. Das Kürzel macht das im Namen sichtbar und lädt dazu ein, für eine andere Arbeitsweise einen eigenen Skill zu schreiben, statt diesen zu verbiegen.

**Der Trigger** ist die geankerte Fassung aus der Testreihe: „Bevor du in einer Sitzung zum ersten Mal einen Lösungsweg vorschlägst oder zum ersten Mal eine Datei änderst, halte kurz inne und prüfe: …". Die eigenschaftsförmige Ausgangsfassung („behalte im Blick, ob die Änderung über eine lokale Korrektur hinausgeht") wurde gemessen und feuerte in keinem Szenario; die geankerte Fassung feuerte bei identischem Prompt sofort (1.5). Beim Anpassen an ein Projekt darf der Anker verschoben, aber nicht weggelassen werden.

**Verhältnis zu den vorhandenen Skills.** `konzept-segmentierung` führt Phase 3 durch, `konsistenzpruefung` prüft deren Ergebnis vor Implementierungsbeginn. Beide sind Werkzeuge innerhalb dieses Standards. Ob sie langfristig in dieses Vorhaben überführt und mit `-fh` benannt werden, ist offen.

**Abgrenzung zur Schutzregel.** Die Pflicht, vor einer Dateiänderung einen Plan vorzulegen und Zustimmung abzuwarten, bleibt in der `CLAUDE.md` stehen und wandert **nicht** in diesen Skill. Grund: Skill-Trigger sind probabilistisch (1.5) — feuert der Trigger einmal nicht, fiele die Schutzwirkung genau dann aus, wenn sie gebraucht wird. Im Skill steht das ausführliche Wie, in der `CLAUDE.md` die knappe Pflicht.

## 3.4 Softwareaufgabe erkennen — noch nicht umgesetzt

Kein Ordner, keine `SKILL.md`. Festgehalten ist bisher nur die Idee samt dem, was die Testreihe darüber ergeben hat.

**Idee.** Ein Skill, der erkennt, dass die Anfrage des Nutzers auf eine zu schreibende oder zu ändernde Software hinausläuft — auch wenn sie das nicht mit Wörtern wie „Code", „programmieren" oder „Software" ausdrückt —, und daraufhin die einschlägigen Entwicklungsregeln nachlädt.

**Messergebnis der Testreihe.** Erprobt wurde eine eigenschaftsförmige Trigger-Fassung („behalte im Blick, ob die Anfrage auf zu schreibende oder zu ändernde Software hinausläuft", mit Beispielen für Anzeichen). Sie feuerte auf Sonnet in keiner von drei Eskalationsstufen — von der reinen Verständnisfrage zu einem vorhandenen Skript über die Schilderung eines Fehlverhaltens bis zur konkreten Vermutung über eine Programmierlücke. Dieselbe Fassung feuerte sofort, als statt einer knappen Frage ein Quelltextausschnitt mit einem vagen Unmut geschickt wurde: der erzwungene Einordnungsmoment aus 1.5. Auf Opus und Fable genügte bereits die mittlere Stufe.

**Was daraus für die Umsetzung folgt.** Der Trigger muss nach Vorgabe 2.1 umformuliert werden — geankert, nicht als Hintergrund-Beobachtung. Offen ist außerdem der Inhalt: Welche Entwicklungsregeln der Skill tragen soll und wie er sich gegen `software-dev-doc-fh` abgrenzt, ist noch nicht entschieden. Möglicherweise ist er dessen Vorstufe (erkennt überhaupt eine Softwareaufgabe) und nicht ein eigenständiger zweiter Skill.

**Teilweise überholt durch 3.5.** Der dort beschriebene Skill trägt inzwischen einen Teil dessen, was hier als Idee steht: Er wird ausgelöst, wenn Code entsteht, auch ohne dass die Anfrage von Code spricht. Die offene Entscheidung bleibt, ist aber enger geworden — zu klären ist nur noch, ob darüber hinaus ein eigener Erkenner gebraucht wird.

## 3.5 `common-code-generation-de`

Ordner: `skills/common-code-generation-de/`, **mit** stillem Trigger.

**Zweck.** Allgemeine Regeln für das Erzeugen und Ändern von Code: was in welcher Sprache benannt wird, wie viel Code überhaupt entstehen darf, welche Ressourcen zählen und wie eine Bedienoberfläche entworfen wird. Der Text stammt aus einer `CLAUDE.md` des Nutzers und wurde für dieses Vorhaben in einen Skill überführt; einige Eigenheiten erklären sich aus dieser Herkunft.

**Inhalt.** Sechs Abschnitte: Geltung und Abgrenzung, Sprache und Benennung im Quelltext, kein ungefragt erweiterter Funktionsumfang, die Rangfolge der Ressourcen, der Mensch als Ressource (Ergonomie für den Anwender, Umgangston gegenüber dem Entwickler) und technische Optimierungen mit dem Sonderfall Vorwissen in Schleifen.

**Zwei Rollen, zwei Wörter.** Der Skill hält `Entwickler` (der Mensch im Chat) und `Anwender` (der Mensch vor der fertigen Software) streng auseinander und legt das im Abschnitt „Geltung und Abgrenzung" ausdrücklich fest. Grund: In der Ausgangsfassung stand „Nutzer" für beide, teils in benachbarten Absätzen — eine Anweisung wie „frage den Nutzer nach der Priorität" war damit als „frage den Endanwender" lesbar. Prüfbar im Sinne des Aufnahmetests: Jede Stelle, an der „Nutzer" allein steht, verletzt die Festlegung; Komposita wie „Nutzungserlebnis" sind unbedenklich.

**Warum der Trigger ganz vorn ansetzt.** Der Skill ist kein Ablauf mit einem Startmoment, sondern ein Regelwerk, das ab der ersten Zeile Code durchgehend gilt. Weil sein Körper nach dem Laden für den Rest der Sitzung im Kontext bleibt (1.3), zählt allein der früheste Treffer — ein später Treffer rettet die Entscheidungen nicht mehr, die vorher gefallen sind. Die im Skilltext selbst genannten Momente (Benennen, Optimierungsvorschlag, Designentscheidung) taugen deshalb nicht als Auslöser, obwohl einer davon bereits geankert formuliert ist.

**Der Trigger.** Die Description nennt den Anwendungsfall vorn und bindet ihn an die erste Codeberührung der Sitzung. Der stille Trigger trägt zwei Bedingungen: den Anker („bevor du in einer Sitzung zum ersten Mal Quelltext schreibst oder änderst") und ein davon unabhängiges Ereignis (an der Applikation wird ein eigenes Frontend oder eine Schnittstelle zu einem externen Frontend erkennbar). Sieben ursprünglich gesammelte Auslösesituationen ließen sich darauf zusammenziehen, weil fünf davon derselbe Moment sind. Die zwei Beispielfragen im Wortlaut des Absatzes sind Absicht: Wörtliche Nähe zur Nutzerformulierung senkt die Auslöseschwelle (1.5), und vorzeitiges Laden dadurch ist widerlegt.

**Noch nicht gemessen.** Anders als bei 3.2 und 3.3 steht die Prüfung nach 1.6 aus; der Trigger ist bisher nur nach Vorgabe 2.1 konstruiert, nicht bestätigt. Bei 3.3 hat genau diese Messung die erste Fassung widerlegt. Der Schritt steht im Fahrplan.

**Die Witz-Regel hängt an einer Beobachtung.** Der Skill erlaubt einen Witz je Chat, sobald dieser mindestens drei Stunden läuft. Die ursprüngliche Fassung („einmal am Tag") war nicht befolgbar: Über Sitzungsgrenzen hinweg gibt es kein Gedächtnis, drei Chats an einem Tag hätten drei Witze ergeben. Die Sitzungsdauer ist dagegen ermittelbar — Claude Code legt je Sitzung eine JSONL-Datei unter `~/.claude/projects/<projektpfad>/` an, deren Einträge einen ISO-Zeitstempel tragen; der erste Eintrag ist der Sitzungsbeginn (Beobachtung am laufenden System, 16. August 2026). Der Skill bindet das Nachsehen daran, dass ohne Rückfrage gelesen werden darf.

**Abgrenzung zu 3.3.** `software-dev-doc-fh` regelt die Dokumentation und greift erst, wenn eine Änderung über eine lokal begrenzte Korrektur hinausgeht; dieser Skill regelt den Code selbst und gilt ab der ersten geänderten Zeile. Beide stille Trigger benutzen fast denselben Ankermoment. Das ist hingenommen: Mehrfachauslösung ist möglich und unschädlich (1.5), und keiner der beiden Absätze erwähnt den anderen Skill, damit sie einzeln installierbar bleiben.
