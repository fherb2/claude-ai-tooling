# Arbeitsanweisungen für dieses Repo

Ergänzung zu `~/.claude/CLAUDE.md` (im Folgenden „Arbeitsanweisungen"),
**keine Kopie**: Hier steht nur, was dort nicht steht — und nur, was für
**alle Vorhaben** dieses Repos gilt. Was nur eines betrifft, gehört in
dessen eigene Doku oder README — nicht hierher.

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

## Zuerst lesen: `.claude/arbeitsdaten.json`

Diese Datei wird **nicht** automatisch in den Kontext geladen — anders als
diese CLAUDE.md. Sie trägt den Namen des Hauptpfads, den der Werkbank und
den vereinbarten Commit-Umfang (Arbeitsanweisungen §1.2, §1.7). Wer sie
nicht liest, kennt den Hauptpfad nicht. Die Rückfrage aus §1.7 Punkt 2
entfällt dadurch nicht, hat aber einen dokumentierten Ausgangspunkt.

Weil Adds und Commits immer das **Gesamtprojekt** umfassen, wandert
parallele Arbeit des Entwicklers regelmäßig mit — er arbeitet an anderen
Ordnern des Repos weiter, während hier committet wird, und hält das für
den besseren Weg als einen eigenen Worktree. Das ist so gewollt und
**nicht** zu melden. Ein **kurzer Satz** am Ende des Commit-Texts, dass fremde
Änderungen mitgewandert sind, genügt — ohne Ordner oder Dateien aufzuzählen.
Mehr wäre verschenkte Mühe: Die Checkpoint-Nachrichten der Werkbank
verschwinden beim Squash in den Hauptpfad ohnehin, der Vermerk hilft also nur
im Ausnahmefall, in dem jemand die Historie der Werkbank selbst durchsucht.

## Mehrere Instanzen, Schreibrechte für Git

Weil mehrere Vorhaben in einem Repo gebündelt sind, kann es vorkommen, dass
mehrere Claude-Instanzen und der Nutzer gleichzeitig arbeiten. Jede Instanz
klärt **vorab** mit dem Nutzer, welche Instanz eigenständig mit
schreibenden Git-Kommandos (`commit`, `push`, …) arbeiten darf. Ist das
einmal entschieden, kann der Nutzer die Rechte im weiteren Verlauf eines
Chats umverteilen — dann meldet er sich **aktiv**. Hat eine Instanz die
Rechte einmal vom Nutzer erhalten, muss sie nicht bei jedem Commit erneut
nachfragen.

## Jedes Vorhaben ist eigenständig aufgebaut

Die Vorhaben dieses Repos unterscheiden sich in Doku-Aufbau, Benennung und
Begleitdateien. Das ist Absicht und keine Nachlässigkeit: **Vereinheitliche
nichts über Ordnergrenzen hinweg**, und leite aus dem Aufbau eines Vorhabens
nichts für ein anderes ab. Welche Struktur eines hat, sagt seine eigene
README; welche Regeln darin gelten, sein eigener Vorgabenteil (siehe nächster
Abschnitt).

**Nicht zur Weitergabe freigegeben ist `home-.claude-sharing`** — die README
trägt den Hinweis „Nicht benutzen!“. Bei jedem anderen Vorhaben entscheidet
seine README.

## `fahrplan.md`, `status.md` und die Implementierungsdoku sind entwicklungszeitlich

Diese drei Dateien tragen die Entwicklung eines Vorhabens. Sie sind
**keine Pflichtausstattung** eines Ordners, und ihr Fehlen ist kein Mangel,
den man beheben müsste.

- **Während der Entwicklung** gelten die Arbeitsanweisungen §2.3 und §2.6:
  Fahrplan und Status werden geführt, die Doku wächst mit dem Code.
- **Ist ein Vorhaben fertig**, können `fahrplan.md` und `status.md`
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
sondern nur gegen `skills/implementation_doku.md`. Wer die Vorgaben nicht kennt,
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
