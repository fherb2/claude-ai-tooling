# Skills für Claude Code

Wiederverwendbare Skills für Claude Code, samt der Trigger, die sie auslösen. Dieses Verzeichnis ist die Quelle — hier werden die Skills entwickelt und gepflegt. Wirksam werden sie erst, wenn sie an ihren Zielort kopiert wurden (Kapitel 2).

## 1 Zweck

Anweisungen an Claude sammeln sich in `CLAUDE.md`-Dateien an, und jede Zeile darin liegt in **jeder** Sitzung im Kontext — auch wenn sie nur selten gebraucht wird. Ein umfangreicher Dokumentationsstandard oder eine seitenlange Verfahrensbeschreibung kostet so dauerhaft Platz, damit sie in dem einen Prozent der Sitzungen verfügbar ist, in dem es darauf ankommt.

Skills lösen das: Der Inhalt liegt in einer eigenen Datei und wird erst geladen, wenn er gebraucht wird. In der `CLAUDE.md` bleibt höchstens ein kurzer Absatz stehen, der sagt, *wann* nachzuladen ist — nicht *was* dort steht.

Dieses Vorhaben entwickelt solche Skills und dokumentiert dabei, wie ihre Auslösung tatsächlich funktioniert. Die Erkenntnisse aus den zugehörigen Messreihen stehen in `skill_vorgaben.md`; diese README beschreibt nur das Ergebnis: was es gibt und wie man es benutzt.

## 2 Skills beschaffen und installieren

Was Skills sind, wie sie aufgebaut sind und wie Claude Code sie lädt, beschreibt die offizielle Dokumentation: **[Extend Claude with skills](https://code.claude.com/docs/en/skills)**. Diese README setzt das als bekannt voraus und beschreibt nur, was hier hinzukommt.

**Was hier hinzukommt, sind stille Trigger.** Die von Anthropic vorgesehene Technik löst einen Skill über seine `description` aus: Passt sie zur Anfrage, wird der Skill geladen. Das funktioniert gut, wenn der Nutzer etwas verlangt, das dem Skill offensichtlich entspricht. Es funktioniert nicht, wenn der Auslöser eine Beobachtung ist, die niemand ausspricht — etwa dass gerade eine zweite Claude-Instanz im selben Repository arbeitet. Für solche Fälle liegt ein zusätzlicher Absatz in der `CLAUDE.md` des Zielorts, der die Bedingung benennt und auf den Skill verweist. Er heißt **stiller Trigger**, weil ihn niemand aufruft und niemand sieht: Er wirkt aus dem Hintergrund, ohne dass der Nutzer etwas davon merkt.

Skills, die einen solchen Trigger brauchen, bringen dafür eine Datei `CLAUDE-snippet.md` in ihrem Ordner mit.

**Jeder Skill liegt in zwei Sprachfassungen vor,** einer deutschen und einer englischen. Beide liegen im selben Ordner und unterscheiden sich durch ein Sprachkürzel vor der Endung: `SKILL.de.md` und `SKILL.en.md`, ebenso `README.de.md`/`README.en.md` und `CLAUDE-snippet.de.md`/`CLAUDE-snippet.en.md`. Installiert wird genau **eine** der beiden Fassungen, und dabei entfällt das Kürzel — Claude Code erkennt ausschließlich den Namen `SKILL.md`. Der Ordnername ist in beiden Fassungen derselbe und trägt nie ein Kürzel; dasselbe gilt für den Skill-Namen im Frontmatter und damit für den Aufruf `/<skill-name>`.

### Installation

1. **Zielort wählen.** Ein Skill gilt entweder für alle Projekte des Nutzers oder nur für eines:

   | Ort        | Pfad                                     | Gilt für                  |
   | ---------- | ---------------------------------------- | ------------------------- |
   | Persönlich | `~/.claude/skills/<skill-name>/SKILL.md` | alle Projekte des Nutzers |
   | Projekt    | `.claude/skills/<skill-name>/SKILL.md`   | nur dieses Projekt        |

2. **Skill-Ordner kopieren, Sprachfassung wählen.** Der Ordner hier hat bereits genau die Struktur des Zielorts. Kopiert wird er unter seinem unveränderten Namen; von jeder Datei kommt nur die gewünschte Sprachfassung mit, und ihr Sprachkürzel entfällt dabei: Aus `SKILL.de.md` wird am Zielort `SKILL.md`. Bleibt das Kürzel stehen, findet Claude Code den Skill nicht.

3. **Stillen Trigger übernehmen, falls vorhanden.** Liegt im Ordner eine `CLAUDE-snippet.md`, wird ihr Inhalt **unterhalb der Trennlinie** in die `CLAUDE.md` des Zielorts übernommen — bei einem persönlichen Skill in `~/.claude/CLAUDE.md`, bei einem Projekt-Skill in dessen `CLAUDE.md`. Der Text oberhalb der Trennlinie ist die Anleitung dazu und wird nicht mitkopiert.

4. **`CLAUDE-snippet.md` und `README.md` am Zielort löschen.** Beide haben ihren Zweck erfüllt. Beim Snippet ist das zwingend: Bliebe es liegen, entstünde eine zweite Fassung des Triggers, die beim nächsten Anpassen auseinanderdriftet. Die README beschreibt den Arbeitsstand in der Quelle, nicht das installierte Werkzeug — sie darf bleiben, nützt am Zielort aber nichts.

Ohne Schritt 3 und 4 funktioniert der Skill weiterhin — aber nur, wenn er ausdrücklich mit `/<skill-name>` aufgerufen wird.

### Beim Anpassen eines Triggers

Drei Regeln — zwei davon aus Messungen und nicht aus Geschmack, die dritte aus Anthropics eigener Vorgabe:

**Die `description` des Skills entscheidet zuerst.** Sie beginnt mit dem Hauptanwendungsfall und benutzt die Wörter, die ein Nutzer von sich aus sagen würde. Wer dort eine Einordnung voranstellt („Testskill…", „Interne Fassung…") oder projektinterne Fachbegriffe verwendet, die in keiner Anfrage vorkommen, kann den Trigger unwirksam machen — gemessen: derselbe Trigger-Text feuerte mit guter Beschreibung, mit schwacher nicht.

**Ein Trigger sollte an ein Ereignis oder eine Handlung gebunden sein,** nicht bloß an eine Eigenschaft der Aufgabe. „Behalte im Blick, ob diese Aufgabe komplex ist" trägt sich nicht selbst; „bevor du zum ersten Mal eine Datei änderst, prüfe …" oder „taucht eine Datei auf, die du nicht angefasst hast, dann …" lösen zuverlässig aus. Die Messreihen dazu stehen in `skill_vorgaben.md`, Kapitel 3.

**Die `description` steht in der dritten Person.** Sie beschreibt den Skill — „Übersetzt Dokumente …", „Verwenden, sobald …" — und spricht niemanden an, weder Claude noch den Nutzer. Das ist keine Stilfrage: Die Beschreibung wird in den Systemprompt eingefügt, und ein wechselnder Blickwinkel stört dort die Auswahl unter vielen Skills. Anthropic sagt das ausdrücklich — *„Always write in third person […] inconsistent point-of-view can cause discovery problems"* ([Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).

## 3 Die Skills im Einzelnen

### 3.1 `translation-task`

**Wozu.** Übersetzt Dokumente mit softwareentwicklungsnahem Inhalt — README-Dateien, Konzept- und Implementierungsdokumente, Anleitungen. Nicht auf eine Sprachrichtung festgelegt.

**Was er konkret tut.** Er klärt vorab Zielsprache und Fachjargon-Grad, legt vor der vollständigen Übersetzung eine Arbeitsprobe vor (höchstens ein Drittel des Dokuments und höchstens rund 1000 Wörter) und behandelt danach drei Dinge nach festen Regeln: Codeblöcke werden nur übersetzt, wenn sie erkennbar illustrativ sind und keine echte Quelle im Projekt haben; Eigennamen, Produktnamen und wörtliche Marker wie `@Claude:` bleiben immer unangetastet; Begriffsentscheidungen wandern in ein Glossar.

**Besonderheiten.** Der Skill erkennt selbst, ob er lokal in Claude Code oder in claude.ai läuft, und führt das Glossar nur lokal — in claude.ai erwähnt er es gar nicht erst, statt eine Datei zu versprechen, die niemand wiederfindet.

**Erweitern.** Das Glossar liegt als `glossar.md` im Skill-Ordner und ist der vorgesehene Ort für eigene Begriffsentscheidungen; es wächst im Betrieb. Wer die Regeln selbst ändert, sollte die Codeblock-Erkennung nicht vereinfachen: Die projektweite Suche nach einer echten Quelle ist der Grund, warum echter Werkzeug-Output nicht versehentlich übersetzt wird.

**Installation.** Wie in Kapitel 2, kein stiller Trigger nötig — die Auslösung kommt vom Nutzer selbst.

### 3.2 `parallel-sessions`

**Wozu.** Klärt die Zusammenarbeit, wenn mehrere Claude-Code-Instanzen gleichzeitig im selben Repository arbeiten.

**Was er konkret tut.** Zwei Schritte in fester Reihenfolge. Erstens: Er lässt klären, welche Instanz eigenständig schreibende Git-Kommandos ausführen darf, und führt bis zur Antwort selbst keine aus. Zweitens: Er bietet das Worktree-Modell als saubere Trennung an und erklärt beide Einrichtungswege — über das Werkzeug `EnterWorktree` und von Hand über `git worktree add`, samt der Unterschiede bei Ablageort und Basis-Branch.

**Besonderheiten.** Der Skill entscheidet bewusst nicht, wie ein projekteigenes Branch-Namensschema mit mehreren gleichzeitigen Worktrees zusammengeht — das ist eine Projektfestlegung. Er benennt den Konflikt und überlässt die Entscheidung dem Nutzer.

**Erweitern.** Wer den Skill um ein eigenes Namensschema ergänzt, sollte es im Projekt-`CLAUDE.md` verankern und hier nur darauf verweisen, statt es in den Skill zu schreiben — sonst gilt das Schema plötzlich für alle Projekte.

**Installation.** Wie in Kapitel 2, **mit** stillem Trigger (`CLAUDE-snippet.md`). Ohne ihn bemerkt der Skill die Situation nicht, denn niemand sagt von sich aus „hier arbeitet eine zweite Instanz".

### 3.3 `software-dev-doc-fh`

**Wozu.** Ein Dokumentationsstandard für Planung vor der Kodierung und für die laufende Mitschrift des Implementierten: was umgesetzt wird, welche Festlegungen getroffen wurden und warum so und nicht anders. **Nicht** gemeint sind Quelltextkommentare und Anwenderdokumentation.

**Was er konkret tut.** Er gibt vier Phasen vor (Findung, Fixierung, Segmentierung, Implementierung), eine dreigeteilte Dokumentstruktur (Zusammenhänge, Vorgaben, Einheiten), die Trennung von Fahrplan und Status sowie die Regel, dass Konzeptdokumente keinen Implementierungscode enthalten. Dazu die Arbeitsschleife, nach der Doku und Code im Wechsel entstehen, und die Behandlung von Review-Befunden im Doku-Anhang.

**Besonderheiten.** Das Kürzel `-fh` ist Absicht: Das ist die Arbeitsweise eines bestimmten Entwicklers, nicht der einzige mögliche Standard. Wer anders arbeitet, kopiert den Skill und schreibt ihn um, statt diesen zu verbiegen. Die Skills `konzept-segmentierung` und `konsistenzpruefung` sind Werkzeuge innerhalb dieses Standards.

**Erweitern.** Zwei Festlegungen tragen die übrigen und sollten beim Anpassen nicht fallen: die Prosa-Code-Grenze (sonst prüft man später Code gegen Code) und die Regel, dass jede Aussage genau ein normatives Zuhause hat (sonst entstehen zwei Fassungen derselben Festlegung, die auseinanderdriften). Der Aufnahmetest für Segment 2 — „man muss auf eine Datei zeigen und sagen können, das verletzt diese Vorgabe" — ist das Werkzeug, mit dem sich entscheiden lässt, wohin eine neue Aussage gehört.

**Installation.** Wie in Kapitel 2, **mit** stillem Trigger (`CLAUDE-snippet.md`). Dessen Wortlaut ist an eine Handlung gebunden („bevor du zum ersten Mal …") — dieser Anker darf verschoben, aber nicht weggelassen werden, sonst löst der Trigger nicht mehr aus.

### 3.4 `common-code-generation`

**Wozu.** Allgemeine Regeln für das Erzeugen und Ändern von Code — die Art Festlegungen, die sonst in jeder `CLAUDE.md` wiederholt stehen müsste. **Nicht** Gegenstand: die Pflicht, vor einer Dateiänderung einen Plan vorzulegen; die bleibt in der `CLAUDE.md`, weil ein Skill nur wahrscheinlich lädt, eine Schutzregel aber sicher greifen muss.

**Was er konkret tut.** Er legt fest, dass alles im Quelltext — Bezeichner, Kommentare, Docstrings — auf Englisch steht und dass selbst gewählte Namen dem Nutzer zur Entscheidung vorgelegt werden. Er verbietet ungefragte Erweiterungen des Funktionsumfangs. Er gibt eine Rangfolge der Ressourcen vor (Rechenzeit, Arbeitsspeicher, Massenspeicher) und verlangt, jeden Optimierungsvorschlag vorher gegen die Realität zu prüfen: ob er sich im tatsächlichen Anwendungsfall lohnt und ob sein Effekt über die Gesamtapplikation überhaupt messbar ist. Dazu ein Sonderfall — die Anordnung von Abbruchkriterien in Schleifen nach Vorwissen über die Daten, samt dem Hinweis, dass der Compiler die Reihenfolge im Maschinencode ohnehin ändert.

**Besonderheiten.** Der Anker des Triggers liegt am frühestmöglichen Moment der Sitzung, nicht bei der ersten Benennung oder dem ersten Optimierungsvorschlag. Grund: Der Skill ist kein Ablauf, sondern ein Regelwerk, das ab der ersten Zeile Code gilt — und weil sein Körper nach dem Laden im Kontext bleibt und nicht neu gelesen wird, rettet ein später Treffer die Entscheidungen nicht mehr, die vorher gefallen sind.

**Erweitern.** Der Anker darf beim Anpassen verschoben, aber nicht weggelassen werden. Und die Plan-Pflicht gehört nicht in den Skill geholt, so verlockend das aussieht: Ein Trigger ist probabilistisch, eine Schutzregel muss sicher greifen.

**Installation.** Wie in Kapitel 2, **mit** stillem Trigger (`CLAUDE-snippet.md`).

## 4 Offene Punkte des Vorhabens

Was an einem einzelnen Skill offen ist, steht in dessen eigener `README.md` im Skill-Ordner. Übergreifend offen ist:

- **Transport an den Zielort.** Ob das Kopieren eines fertigen Skills nach `.claude/skills/` bzw. `~/.claude/skills/` automatisiert wird, ist nicht entschieden. Derzeit bleibt es Handarbeit des Nutzers. Naheliegend wäre eine Anbindung an `home-.claude-sharing`, das bereits einen Sync-Mechanismus für `~/.claude` unterhält.

## Lizenz

Alle Skills in diesem Verzeichnis stehen unter **[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)** — der Verzicht auf alle Rechte, soweit gesetzlich möglich. Das bedeutet:

- **Nutzung ohne jede Bedingung** — privat, kommerziell, in geschlossenen wie in offenen Projekten.
- **Keine Namensnennung nötig.** Wer will, darf nennen; niemand muss.
- **Beliebig änderbar und weitergebbar**, auch in veränderter Form und unter anderem Namen.
- **Keine Pflicht, Änderungen offenzulegen** oder zurückzugeben.
- **Kein Lizenztext muss mitgegeben werden** — anders als bei MIT oder Apache-2.0, die beide Namensnennung und Mitgabe des Lizenztextes verlangen.
- **Keine Gewährleistung und keine Haftung.** Was diese Skills anrichten, verantwortet, wer sie einsetzt.

Anthropic macht keine Vorgaben zur Lizenzierung selbst geschriebener Skills, und das Skill-Format ist ein offener Standard ohne eigene Bedingungen. Anthropics eigenes Skills-Repository nutzt für die quelloffenen Skills Apache-2.0. CC0 ist hier also eine bewusste Wahl, keine Auflage — und die weitergehende: Apache-2.0 verlangt Namensnennung und Mitgabe des Lizenztextes, CC0 nicht.
