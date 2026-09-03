# Arbeitsanweisungen für dieses Repo

Ergänzung zu `~/.claude/CLAUDE.md` (im Folgenden „Arbeitsanweisungen"),
**keine Kopie**: Hier steht nur, was dort nicht steht oder dazu in diesem
Projekt abändernd wirken soll — und nur, was für
**alle Vorhaben** dieses Repos gilt. Was nur eines betrifft, gehört in
dessen eigene Doku oder README — nicht hierher.

# Sprachen

Abweichend zum sonst üblichen Verfahren, die README-Files in englisch
anzulegen, wird in diesem Projekt vorgegeben: Die README.md eines Ordners ist
in deutscher Sprache und zusätzlich wird eine README.en.md angelegt, auf die
die deutschsprachige README ganz oben verweist. **In der Projektwurzel ist es
umgekehrt**: Dort trägt die README.md die englische Fassung und die deutsche
liegt als README.de.md daneben; beide verweisen oben aufeinander. Grund ist
die Sichtbarkeit — GitHub zeigt beim Öffnen des Repositories die Datei namens
exakt README.md, und dies ist das einzige international gehostete Repository
des Entwicklers (Festlegung des Entwicklers vom 4. September 2026). Wer
dagegen einen Ordner öffnet, steckt schon im Vorhaben, dessen Arbeitssprache
Deutsch ist.

Bei Änderungen an READMEs ist die andere Sprachversion nachzuziehen. Welche
die "vorgebende" Version ist, ergibt sich aus dem Zeitpunkt der Änderungen:
Die neusten Änderungen ergänzen / ersetzen / entfernen Bereiche in der
anderen Sprache. Ausnahme: Fälle, wo beim Übersetzen bewusst ein Begriff
weggelassen oder nicht oder anders übersetzt wurde, um keine linguistischen
Probleme zu erzeugen, sind keine Änderungen, die in die andere Sprache
rückübertragen werden müssen.

**Und es bleibt bei diesen zwei Ebenen.** Eine dritte — eine `CLAUDE.md` in
einem Unterordner oder eine pfadgebundene Regel unter `.claude/rules/` — ist
möglich, aber für unsere Arbeitsweise untauglich: Beide laden erst, wenn
Claude eine Datei aus dem betreffenden Ordner liest, und beide werden nach
einer Kompaktierung **nicht** wieder eingespielt, anders als die Projekt-
CLAUDE.md (belegt, [memory](https://code.claude.com/docs/en/memory)). Bei
einem Kontexthaushalt, der Kompaktierung als Normalfall einplant
(Arbeitsanweisungen §1.9), wären solche Regeln nach der ersten Verdichtung
verschwunden. Was ein einzelnes Vorhaben dauerhaft binden soll, steht
deshalb in seiner Doku oder README — nicht in einer Datei, die mit dem Ende
der Entwicklung entfällt (siehe unten).

# Dateinamen sind englisch

Was für den Nutzer da ist, trägt englische Dateinamen; die Arbeitssprache
der Inhalte bleibt davon unberührt Deutsch. Ein Sprachkürzel wie `.de.md`
kennzeichnet eine Sprachfassung und ist kein Verstoß. Ausgenommen sind
Entwicklungs- und Verwaltungsdateien (`status.md`, `noch-geplant.md`
u. Ä.) — international sein muss, was für den Nutzer da ist, nicht die
Projektverwaltung (Festlegung des Entwicklers vom 26. August 2026,
Abschluss von Fahrplanschritt 11).

**Eine Ausnahme von dieser Ausnahme, bewusst abweichend von
Arbeitsanweisungen §2.3:** Der Fahrplan heißt in diesem Repository
`work-plan.md`, nicht `fahrplan.md`. Grund ist der Ort — dies ist das
einzige international gehostete Repository des Entwicklers, und der
Fahrplan liegt hier in der Projektwurzel, also im ersten Blickfeld jedes
Besuchers. Der Begriff „Fahrplan" bleibt in der deutschen Prosa
unverändert; nur der Dateiname folgt der Sichtbarkeit (Festlegung des
Entwicklers vom 27. August 2026). Betroffen sind alle drei: die
repository-weite `work-plan.md` in der Wurzel,
`home-.claude-sharing/work-plan.md` und `skills/chat-export/work-plan-v2.md`.

Zwei Präzisierungen: Bei Skill-Ordnern ist der Name die Schnittstelle —
Ordnername, Frontmatter-Feld `name` und Slash-Aufruf sind dasselbe; eine
Umbenennung ändert das Verhalten jeder installierten Kopie und wird
einzeln entschieden. Und Laufzeitmeldungen an den Entwickler dürfen
deutsch bleiben, wo der Bereich das mit Begründung festgelegt hat
(belegt: home-sharing, Sprachfestlegung 2.5, suchbare Journal-Anlässe).

# Datumszeilen in READMEs und CLAUDE-Snippets

Jede README dieses Repos (deutsch wie englisch, von der Top-Level-README
bis in jeden Unterordner) und jede Datei, deren Inhalt zum Übernehmen in
eine CLAUDE.md bestimmt ist (die `CLAUDE-snippet.md` der Skills ebenso wie
die Sammlungen unter `CLAUDE.md-Snippets/`), trägt ganz oben eine
Datumszeile mit dem Datum der letzten inhaltlichen Bearbeitung: in READMEs
kursiv unmittelbar unter der Hauptüberschrift (`*Stand: JJJJ-MM-TT*`,
englisch `*Last updated: JJJJ-MM-TT*`), in Snippet-Dateien als erste Zeile
— bei Skill-Snippets damit oberhalb der Trennlinie, sie wandert also nie in
eine CLAUDE.md mit. Wer eine dieser Dateien inhaltlich ändert, zieht die
Zeile im selben Arbeitsgang nach.

Zweck: Diese Dateien werden an andere Orte kopiert (etwa nach
`~/.claude/skills/` oder in fremde CLAUDE.md-Dateien). Ohne Datumszeile ist
einer installierten Kopie nicht anzusehen, ob sie dem Stand des Repos
entspricht; das Datum ist hier die Versionsangabe (Festlegung des
Entwicklers vom 24. August 2026).

## Arbeitsmodell: Git-Worktrees

Dieses Repo arbeitet nach dem Worktree-Modell: Jede Claude-Sitzung
arbeitet auf einer eigenen Werkbank (`claude-wb/<topic>`) in einem eigenen
Worktree; die Vereinbarungen stehen in `.claude/git-worktree-model.json`.
Verfahren und Regeln: Skill `parallel-sessions` (Quelle:
`skills/parallel-sessions/`).

## Jedes Vorhaben ist eigenständig aufgebaut

Die Vorhaben dieses Repos unterscheiden sich in Doku-Aufbau, Benennung und
Begleitdateien. Das ist Absicht und keine Nachlässigkeit: **Vereinheitliche
nichts über Ordnergrenzen hinweg**, und leite aus dem Aufbau eines Vorhabens
nichts für ein anderes ab. Welche Struktur eines hat, sagt seine eigene
README; welche Regeln darin gelten, sein eigener Vorgabenteil (siehe nächster
Abschnitt).

## `work-plan.md`, `status.md` und die Implementierungsdoku sind entwicklungszeitlich

Diese drei Dateien tragen die Entwicklung eines Vorhabens. Sie sind
**keine Pflichtausstattung** eines Ordners, und ihr Fehlen ist kein Mangel,
den man beheben müsste.

- **Während der Entwicklung** gelten die Arbeitsanweisungen §2.3 und §2.6:
  Fahrplan und Status werden geführt, die Doku wächst mit dem Code.
- **Ist ein Vorhaben fertig**, können `work-plan.md` und `status.md`
  **entfallen** — ohne offene Schritte wären sie leere Hüllen. Bevor sie
  gelöscht werden, wandert ihr dauerhaft geltender Teil in die Doku oder die
  README; was dort schon steht, entfällt ersatzlos.
- **Über die Implementierungsdoku entscheidet der Nutzer**, nicht Claude.
  Frage nach, wenn ihr Verbleib zur Frage steht.
- **Wo es keinen Fahrplan gibt**, benennt die README das Offene und trägt den
  Plan des nächsten Schritts. Steht wieder ein größerer Schritt an, kann der
  Fahrplan zurückkommen.

Prüfbar: Auf jede Stelle, die eine dieser Dateien in einem fertigen Vorhaben
verlangt oder ihr Fehlen als Defekt meldet, lässt sich zeigen — das ist der
Verstoß.

## Die Vorgaben lesen, bevor eine Datei des Vorhabens entsteht oder sich ändert

Was für ein einzelnes Vorhaben gilt, steht in dessen eigenem Vorgabenteil —
bei Segmentstruktur in Segment 2 („Vorgaben"), sonst dort, wo die README des
Vorhabens hinzeigt. Diese Texte werden **nicht** automatisch in den Kontext
geladen, anders als diese Datei. Deshalb gilt hier ausdrücklich: Wer eine
Datei eines Vorhabens anlegt oder ändert, liest **vorher** dessen Vorgaben
vollständig — nicht nur die Sektion, die zur Aufgabe gehört.

Der Grund steckt in der Natur dieser Vorgaben: Sie halten fest, was man der
einzelnen Datei nicht ansieht. Dass etwa die `description` eines Skills
gegen eine Vorgabe verstößt, erkennt man nicht beim Lesen der `SKILL.md`,
sondern nur gegen `skill-dev-doc.md`. Wer die Vorgaben nicht kennt,
schreibt den Verstoß gutgläubig hin — und der nächste Review meldet ihn zu
Recht.

## Fahrplan-Nummerierung

Erledigte Schritte fliegen aus dem Fahrplan; die Nummern der übrigen werden
dabei **nicht** neu vergeben, neue Schritte zählen hoch. Grund: Ein
Rückblick im Chat auf „Schritt n“ muss eindeutig bleiben. Gilt für jedes
Vorhaben mit eigenem Fahrplan und für den Fragenkatalog einer Doku genauso.

## Befundlisten abarbeiten

Gilt für jede Befundliste in diesem Repo — Doku-Review, Code-Review,
Docstring-Review. Welche derzeit offen sind, sagt der Fahrplan des
jeweiligen Vorhabens — wo es keinen gibt, die zugehörige `README.md`.

- Jeder Befund wird **einzeln vorgelegt und besprochen**, nicht selbständig
  ausgeführt. Die Entscheidung liegt beim Entwickler.
- **Nicht voraussetzen, dass die dem Befund gegenüberstehende Stelle recht
  hat.** Mehrfach lag der Fehler auf der anderen Seite, oder die Lösung sah
  anders aus als vorgeschlagen.
- Kleinkram wird gesammelt und am Ende in einem Zug erledigt, nicht
  zwischendurch.
- Eine Befundliste ist selbst keine Autorität: Auch ihre
  Tatsachenbehauptungen werden geprüft. Belegt am 13. August 2026, als ein
  Review die Zahl der Prüffälle mit 60 angab, während es 70 sind.
- Treffen wir auf einen überholten Verweis, wird er mitbereinigt — immer,
  nicht nur wenn er zum Befund gehört.

## Pläne aus dem Planmodus

Planmodus-Dateien liegen unter `~/.claude/plans/`, also **außerhalb** dieses
Repos. Zwei Folgen: Der Entwickler sieht nicht, dass es sie gibt, und ein
längst umgesetzter Plan wird einer neuen Sitzung trotzdem eingespielt — mit
dem Zusatz, die Arbeit daran fortzusetzen. So geschehen am 13. August 2026
mit einem vollständig umgesetzten Plan vom 6. August.

Deshalb: Ein eingespielter Plan wird **zuerst gegen den Code geprüft**, bevor
er als Auftrag gilt. Erweist er sich als umgesetzt oder überholt, wird das
gemeldet, damit der Entwickler ihn löscht — in `~/.claude/` zu schreiben oder
zu löschen ist nicht unsere Sache (§1.2). Ob die Ablage per `plansDirectory`
ins Projekt wandert, ist offene Entscheidung im Fahrplan von
`home-.claude-sharing`.

## Wo ein Plan steht

Für alles, was keine winzige Codeänderung ist, wird zuerst ein Plan
geschrieben — nicht nur im Chat vorgetragen, sondern an einem Ort, den eine
neue Sitzung von selbst findet. Für Code gilt dabei §1.3: adressierbare
Einheiten statt Kontrollfluss. Es gibt genau zwei Orte, und **keine eigenen
Plan-Dateien**:

- **Bearbeitung eines Review-Befundes** → im Review-Anhang der Doku, beim
  betreffenden Befund (siehe nächster Abschnitt).
- **Alles andere** → im **Fahrplan**, im betreffenden Schritt ausdetailliert.
  §2.6 beschreibt den Fahrplan ohnehin als „die nächsten Schritte in
  aufgabenangemessener Detaillierung", und §1.9 verlangt, diese Detaillierung
  vor einer Komprimierung zu vertiefen — das ist genau ein Plan. Wo es keinen
  Fahrplan gibt, steht der Plan unter „Offen" bzw. „Stand" in der `README.md`
  des Vorhabens. Bringt es seinen Fahrplan zurück, wandert der Plan dorthin.

In beiden Fällen steht **höchstens ein** noch nicht ausgeführter Plan
gleichzeitig da, deutlich als solcher gekennzeichnet. Sein Zweck ist die
Wiederaufnahme: Eine neue Sitzung soll dort weiterarbeiten können, ohne den
Chat zu kennen. Nach der Ausführung wird er **ersetzt** — nicht ergänzt.

## Reviews und ihre Bearbeitung

Gilt für jede Art Review in diesem Repo: Code, Doku, Docstrings.

**Ablauf.** Der Reviewer schreibt seine Befunde in eine **eigene Datei**. Die
Nachbearbeitung beginnt damit, diese Datei mit ihrem Erstellungsdatum als
**Anhang in die Doku** zu kopieren; danach wird das Original entfernt, damit
keine zweite Fassung entsteht, die auseinanderdriften kann. Im Anhang folgt ein
Berichtsteil, der in der Reihenfolge der Abarbeitung gefüllt wird.

**Der Eintrag zu einem Befund hat zwei Zustände.** Zuerst ist er der Plan des
laufenden Schritts. Nach der Ausführung wird er ersetzt durch den **Bericht:
warum der Punkt genau so gelöst wurde** — geradeheraus oder anders als
vorgeschlagen. Der Plan selbst und alles, was zur Beschreibung der Reaktion
nicht nötig ist, entfällt dabei.

**Die Länge des Eintrags ist selbst eine Aussage.** Steht dort nur
„erledigt", war es geradeheraus: Code korrigiert, vielleicht ein Satz in einem
Kapitel, sonst nichts Erwähnenswertes. Ein begründeter Absatz steht dort, wenn
die Lösung anders aussah als vorgeschlagen, wenn der Befund **abgelehnt** wurde
oder wenn eine Annahme des Reviews sich als falsch erwies.

**Jeder Befund bekommt einen Eintrag** — behoben, abgelehnt oder
zurückgestellt. Der abgelehnte ist der wichtigste: Ohne festgehaltene
Begründung meldet der nächste Review ihn wieder, und zwar zu Recht. Ein
Zustandsfeld („erledigt: ja/nein") gibt es nicht; der Stand ist ablesbar, weil
jeder Eintrag die Befundnummern nennt, die er erledigt.

**Die Grenze zwischen Kapiteln und Anhang.** In die Kapitel gehört, was man zum
**Ändern** des Codes braucht — einschließlich der Messwerte, an denen eine
Festlegung hängt, denn die schützen vor der nächsten gutgemeinten
Vereinfachung. In den Anhang gehört, was man zum **Beurteilen der Bearbeitung**
braucht: verworfene Wege, Bewertungen, der Verlauf. Für die Dokumentation ist
das uninteressant und für das Verständnis des Programms unnötig; für einen
Reviewer ist es die Wissensbasis, mit der er Eigenheiten im Code nachvollziehen
kann, statt sie erneut zu melden.

**Der nächste Review bekommt die Doku samt Anhang** und den Auftrag: Erledigtes
**nachprüfen** statt neu herleiten, und nur Neues melden. Meldet ein Review
etwas erneut, ist das zuerst ein Hinweis auf eine Lücke im Anhang und erst
danach auf einen Fehler im Code.

**Die Aufteilung in Dateien entscheidet das Vorhaben.** §2.3 lässt eine Datei
wie mehrere zu; verlangt ist nur, dass das Verketten in Dateireihenfolge ein
gültiges Gesamtdokument ergibt.

## Zurücknehmen nur gezielt, nie mit dem Vorschlaghammer

Weil im Repo parallel gearbeitet wird, darf eine Rücknahme nie mehr treffen als
den eigenen Ordner. Die Befehle, die das leisten:

- **Nur eigene Dateien wegsichern:** `git stash push -- <pfad>` — nimmt genau
  diese Pfade weg und lässt fremde Änderungen im Arbeitsbaum stehen.
- **Nur einen Teilbaum auf einen früheren Stand:** `git restore --source=<commit>
  -- <pfad>` und anschließend committen. Das korrigiert **vorwärts**, statt
  Historie umzuschreiben — und lässt alles außerhalb von `<pfad>` unberührt.
- **Niemals `git reset --hard`** und **niemals `git checkout -- <datei>`**, wenn
  in der Datei unversionierte Arbeit steckt: Beide setzen auf HEAD zurück und
  löschen sie ohne Rückfrage. Am 13. August 2026 hat genau das die neu
  geschriebenen Prüffälle vernichtet.
- **Für eine Leerprobe** (Erwartung absichtlich verfälschen, um zu sehen, ob der
  Test anschlägt) wird die Änderung **gezielt zurückgeschrieben** und über einen
  Prüfsummenvergleich bestätigt — nicht über Git.

## Aufbewahren gehört ins Projekt

`/tmp` als Arbeitsfläche ist richtig und kann sogar Teil eines
Prüfverfahrens sein. Der Sitzungsordner dort ist aber
sitzungsgebunden und beim nächsten Neustart weg. Was über die Sitzung
hinaus gebraucht wird, kommt deshalb **sofort** ins Repo. Was dort abgelegt
wurde und sich als entbehrlich erweist, wird bewusst gelöscht und das
gesagt, statt es liegenzulassen.

# Skills: dünne `SKILL.md`, nachgeladener Regelteil

Entsteht in `skills/` ein neuer Skill oder wächst ein bestehender, prüfe, ob
sein Regelteil aus der `SKILL.md` heraus in eine nachgeladene Datei desselben
Ordners gehört, und schlage die Teilung vor. Wann sie sich lohnt und wie sie
gebaut wird, steht in `skill-dev-doc.md`, Kapitel 5.2 — hier
absichtlich kein zweites Mal.

# Baustellenschilder in Ordnernamen

Die Baustellenschilder in den Ordnernamen erlauben dem Nutzer beim Start des
Projekts sofort zu erkennen, welche Skills noch unfertig sind. Nach der
Fertigstellung und vor dem ersten Einsatz (Kopie an das Installationsziel)
wird dieser Prä-Teil dann entfernt und bleibt entfernt. Somit kollidiert der
Ordnername nicht mit anderen Vorgaben und den Bedingungen an der
Installationsstelle.

# Nutzertexte

Wo der Nutzer Texte editiert und erstellt hat: Bitte prüfe vor einem Commit auf Rechtschreib- und Grammatikfehler und frage ihn, ob Du die sofort mit korrigieren darfst.