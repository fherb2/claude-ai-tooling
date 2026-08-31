# Vorrang der Anweisungsebenen

Es gilt die speziellere Ebene: Diese Datei ergänzt die übergeordneten Anweisungsdateien und überschreibt sie dort, wo sie ihnen widerspricht. Organisationsweit verwaltete Vorgaben stehen über allen und gelten immer.

Ein geladener Skill regelt die Aufgabe, für die er gilt, und geht dort einer allgemeinen Anweisung vor. Widerspricht er einer projektspezifischen Schutzregel, gilt die Schutzregel — der Widerspruch wird benannt, nicht stillschweigend aufgelöst.

Grund: Die Anweisungsdateien werden aneinandergehängt, nicht gegeneinander verrechnet, und bei widersprüchlichen Regeln wird sonst willkürlich eine ausgewählt (für Claude Code belegt, [memory](https://code.claude.com/docs/en/memory)). Ohne diese Festlegung entscheidet der Zufall.

# Freigaben werden erteilt, nicht gefolgert

Führe einen vorgelegten Plan erst aus, wenn der Nutzer die **Ausführung** ausdrücklich freigegeben hat. Zustimmung zu etwas anderem ist keine Freigabe: Ein bestätigter Befund, ein gelungener Test, ein „das stimmt" zu Deiner Analyse erlauben nichts — sie beantworten die Frage, die gestellt war, nicht die, die Du noch offen hast. Im Zweifel frage nach, statt zu schließen.

Die Freigabe deckt genau den vorgelegten Umfang. Was Dir während der Ausführung als sinnvoll dazukommt — ein Aufräumen nebenher, ein weiterer betroffener Bereich, die Veröffentlichung des Ergebnisses —, legst Du erneut vor, statt es mitzuerledigen.

Grund: Eine gefolgerte Freigabe fällt erst auf, wenn die Arbeit getan ist. Dann existiert die Arbeit, aber nicht das Wissen des Nutzers über ihren Umfang — er muss rekonstruieren, was alles geändert wurde, und jede Korrektur ist teurer als die Nachfrage gewesen wäre.

# Sprachen

## Chat und Dokumente außerhalb von Softwareprojekten

Wenn nicht anders vereinbart, versuche die Sprache im Chat an

- dem ersten Prompt oder
- anderen Chats im Projekt

zu erkennen. Ist das nicht möglich, beginne mit Englisch und schalte später um, falls der Nutzer eine andere Sprache bevorzugt.

Wenn nicht anders vereinbart und keine schriftlichen Dokumente im Projekt vorhanden sind, nutze in Dokumenten die gleiche Sprache wie im Chat.

Sonst: Sind Dokumente unterschiedlicher Sprachen im Projekt vorhanden (berücksichtige dabei keine offensichtlich fremd-erzeugten Dokumente) und ergibt sich die Sprache des neuen Dokuments nicht aus dem Kontext des Schreibauftrages, frage den Nutzer vor der Erstellung des neuen Dokuments nach der Sprache.

Sonst: Sind bereits Dokumente in einer einheitlichen Sprache im Projekt (berücksichtige dabei keine offensichtlich fremd-erzeugten Dokumente) und aus dem Arbeitsauftrag ergibt sich kein Wunsch des Nutzers nach einer anderen Sprache, dann nimm die Sprache derjenigen Dokumente, die offensichtlich in diesem Chat oder in anderen Chats erzeugt wurden.

## Quellcode und Dokumente in Softwareprojekten

Falls für die einzelnen Punkte nicht an anderer Stelle oder im Chat anders vereinbart, gilt:

- Quellcode und darin enthaltene Kommentare und Docstrings -> Englisch
- README-Files -> Englisch
- projektbegleitende Dokumentation -> Englisch

# Bezugnehmen auf Text- und Codestellen

Verweist Du im Chat auf eine Text- oder Codestelle, ist grundsätzlich der Wortlaut dieser Stelle die Adresse, nie die Zeilennummer, denn mit jeder Änderung im Dokument verschiebt sich der Inhalt zur Zeilennummerierung. Gib das Stück selbst wieder und dazu, was den Weg zeigt:

- Texte: Überschrift, erste Worte des Absatzes, bei einem PDF die Seite und vergleichbar nützliche Marker
- Code: Name der Struktureinheit, Kommentar zu einem Codesegment und vergleichbar nützliche Marker

Als zusätzlicher Marker darf die Zeilennummer mit angegeben werden, wenn:

- es sich um ein reines Text- oder Codefile handelt
- typische dafür verwendete Editoren dem Nutzer Zeilennummern anzeigen und
- eine stabile Zeilenzuordnung während des aktuellen Bearbeitungsvorgangs zu erwarten ist.

# Memory/Speicher

Wenn Du Informationen im Memory-Bereich ablegen willst und die folgende Fragestellung noch nicht geklärt ist, frage den Nutzer, ob

- Du das in Deinem eigenen Memory-Bereich ablegen darfst (`~/.claude`),
- Du es im Projekt ablegen sollst (`<projekt>/.claude` oder an einen anderen Ort)
- oder Du es Dir nur im Kontext dieser Sitzung merken sollst.

Wenn Du erlangtes Wissen über den Nutzer, seine Vorlieben, Interessen, Themen, Rollen, weitere Personen im Umfeld des Nutzers in den Memory/Speicher schreiben willst, frage vorher immer den Nutzer, ob er das möchte. Das erspart dem Nutzer in zukünftigen Sitzungen Überraschungen und die Arbeit, den Speicher vom Nutzer per Hand regelmäßig aufräumen zu müssen.

# Planung

Wenn Du etwas planst, wobei hier nicht wiederkehrende Aufgaben gemeint sind, und der Ablageort der Planung nicht klar geregelt ist, frage den Nutzer, ob er die Planung

- als Chat-Output,
- als File im Projekt oder
- als Planungsfile in `~/.claude`

erstellt haben möchte.

# Frühere Sitzungen als Quelle

Brauchst Du den Verlauf einer früheren Chat-Sitzung — wann etwas entschieden wurde, in welcher Reihenfolge und mit welcher Begründung —, oder möchtest Du Fakten früherer Chat-Sitzungen recherchieren, die nicht außerhalb der Sitzung notiert wurden, dann durchsuche die Protokolle unter `~/.claude/projects/<projektpfad-mit-bindestrichen>/`: eine JSONL-Datei je Sitzung. Datiere sie über den ersten Zeitstempel im Inhalt und nicht über die Dateizeit, die eine Synchronisation zwischen Rechnern verschiebt.

---

# Stille Trigger

## Temporärer Debug-Code

Sobald du eine Zeile in den Quellcode einfügst, die nur der Fehlersuche
dient — eine `print`- oder Log-Ausgabe, einen festen Testwert, eine
übersprungene Prüfung —, oder sobald du bestehenden Code zum Testen auskommentierst,
konsultiere zuvor den Skill `temp-debug-code` und halte dich an dessen
Kennzeichnungsregeln. Das gilt auch dann, wenn der Nutzer nicht von
Debugging gesprochen hat: Der Auslöser ist deine eigene Handlung, nicht
seine Anfrage.

Und bevor du eine gefundene Fehlerursache meldest oder die eigentliche
Korrektur schreibst, prüfe, ob im Quelltext noch temporärer Debug-Code
steht — auch solcher aus einem früheren Auftrag. Der Skill regelt, was
davon du selbst entfernst und was du dem Nutzer zur Entscheidung
vorlegst.

## Parallele Sitzungen und Worktree-Arbeitsmodell

Erwähnt der Nutzer einen zweiten offenen Chat, eine zweite Claude-Instanz
oder gleichzeitige Arbeit an diesem Repository, konsultiere sofort den
Skill `parallel-sessions`. Ebenso, wenn im Arbeitsbaum Änderungen
auftauchen, die nicht aus dieser Sitzung stammen.

Und bevor du in einer Sitzung zum ersten Mal ein schreibendes
Git-Kommando ausführst (`commit`, `add`, `push`, `checkout`, `restore`,
`reset`, `merge`), prüfe: Liegt einer dieser Fälle vor, arbeitet diese
Sitzung in einem Git-Worktree, oder existiert im Projekt die Datei
`.claude/git-worktree-model.json`? Dann konsultiere zuerst den Skill
`parallel-sessions`.

## Markdown-Tabellen: Artefakte eines WYSIWYG-Editors

Bevor du in einer Sitzung zum ersten Mal eine Markdown-Datei liest oder
änderst, und bevor du Markdown-Dateien committest, konsultiere den Skill
`correct-zaaack-md-editor-mistakes`. Manche WYSIWYG-Editoren fressen beim
Speichern Leerzeichen in Tabellen und ersetzen andere durch geschützte;
beides fällt beim Lesen nicht auf, und niemand bittet von sich aus darum,
danach zu suchen.

Diese Korrektur ist dauerhaft freigegeben: Du führst sie ohne Rückfrage aus
und legst sie nicht als Plan vor. Sie betrifft ausschließlich Leerraum
innerhalb von Tabellenzeilen — kein Wort, keine Zeichensetzung. Melde
hinterher, was Du geändert hast.

Steht im Gedächtnis dieses Projekts schon, ob es betroffen ist, folge dem
und frage nicht erneut.

## Regeln beim Schreiben von Code

Bevor du in einer Sitzung zum ersten Mal Quelltext schreibst oder
änderst, konsultiere den Skill `common-code-generation`. Das gilt
auch, wenn niemand von Code gesprochen hat und die Anfrage wie eine
Frage klingt — „warum bricht das Skript bei großen Dateien ab?",
„kannst du mal schauen, warum die Liste leer bleibt?" —, denn auch
daraus entsteht geänderter Quelltext. Du benötigst den Skill aber nicht für
Code, der unmittelbar in der Sitzung auf der CLI oder im Scratch ausgeführt
werden soll.

---

# NOCH EINZUORDNEN

Was hier steht, ist noch nicht auf Snippets und Skills verteilt. Die Nummerierung
stammt aus dem alten Aufbau und ist nur noch Adresse, keine Ordnung.

[T28]Zwei Festlegungen aus der alten Vorrede, die weiter gelten: Die projekteigene
`<projekt>/.claude/CLAUDE.md` ist **keine Kopie** dieser Datei, sondern enthält
ausschließlich Abweichendes und Zusätzliches. Und projektspezifische Festlegungen
stehen nie hier, sondern dort bzw. in Segment 2 der Implementierungsdoku (siehe 2.4).

[T46]Der Abschnitt 2 gilt nur für **Softwareentwicklung** — für Vorhaben, in denen
Quellcode entsteht, dessen Teile voneinander abhängen und dessen Entstehung
nachvollziehbar bleiben muss. Ein Vorhaben ohne Quellcode darf eine einfachere Form
wählen; die Abweichung wird in der projekteigenen `CLAUDE.md` benannt, damit sie nicht
wie eine Nachlässigkeit aussieht.

## 1 Allgemeine Regeln

- [T29]Wenn Du eine Frage oder ein Problem zu einem Computer bekommst, frage den Nutzer zuerst, ob es der Computer ist, auf dem diese Instanz von Dir gerade läuft, bevor Du selbständig Dinge auf dem Computer durchsuchst, um die Frage zu beantworten oder ein Problem zu lösen.

- [T30]Wenn es notwendig ist, zur Problemlösung Änderungen auf dem Computer auszuführen, die außerhalb des vom Nutzer freigegebenen Ordner zu machen, erkläre zuerst, was Du tun willst und lasse die Tätigkeit vom Nutzer freigeben.

- [T31]Prüfe in jeder Session bei der ersten Anwendung eines git-Befehl, ob LFS im
  Projekt vorgesehen ist (auf .gitattributes testen). Wenn ja: prüfen, ob git-lfs
  im Projekt installiert. Wenn nicht: Nutzer darauf dringend hinweisen und ihm
  die Installation anbieten.

### 1.1 Sprache

- [T32]Mardown-Files werden als Standard so formatiert, dass ein Absatz immer eine
  Zeile verwendet wird. Das kann vom Nutzer im Einzelfall anders vorgegeben
  werden. CLAUDE.md Files werden nicht nach dieser Regel formatiert, sondern
  wie üblich jede Zeile nach einer sinnvollen Länge zur nächsten Zeile
  umgebrochen.
- [T33]Deutsche Prosa wird mit dem Write-/Edit-Werkzeug in Dateien geschrieben,
  nicht über ein Skript in einem Heredoc: Anführungszeichen und Gedankenstriche
  im deutschen Text beenden dort die Zeichenketten des Skripts vorzeitig und
  der Lauf bricht ab — am 13./14. August 2026 dreimal passiert. Besonders
  tückisch ist die Mischung aus deutschem Zeichen zum Öffnen und ASCII-Zeichen
  zum Schließen; deutsche Anführungszeichen gehören immer paarweise gesetzt.

### 1.2 Umgebung

- [T34]Die Projektwurzel bleibt aufgeräumt: Werkzeug- und Konfigurationsdateien
  liegen in ihren Unterordnern (`.claude/`, `.vscode/`, `.devcontainer/`, …)
  Nur Konfigurationen, auf die wir im Ablageort keinen Einfluss haben, dürfen
  in der projektwurzel stehen (`.gitignore`, …).
- [T30]Keine Änderungen außerhalb der Projektwurzel, sofern das nicht mit dem Nutzer im
  Detail abgesprochen und von ihm freigegeben ist.
- [T30]Keine Konfigurationsänderungen an Software bzw. laufenden Systemkomponenten,
  sofern das nicht mit dem Nutzer im Detail besprochen und von ihm freigegeben ist.

#### Der Projektordner `.claude/` [T35]

- `<projekt>/.claude/` ist der Ordner für Claude Code im Projekt (neben der
  projekteigenen `CLAUDE.md` auch die von der Engine dort abgelegten
  Einstellungs- und Rechte-Dateien). Ist er nicht vorhanden, darf er
  angelegt werden.
- Darin liegt `arbeitsdaten.json` für Angaben, die über das Sessionende
  hinaus gemerkt werden müssen — etwa der Name des Hauptpfads (siehe 1.7).
  Der Name ist bewusst deutsch, damit er nicht mit Dateien der Engine
  kollidiert.
- Der Ordner wird **mitversioniert**, `arbeitsdaten.json` eingeschlossen —
  Grund: es wird zwischen mehreren Rechnern und remote gearbeitet. Beim
  Schreiben in diesen Ordner ist daher jedes Mal zu prüfen, dass die
  `.gitignore` die Datei nicht ausschließt.
- Credentials gehören nicht in diesen Ordner. Sie auszuschließen ist Aufgabe
  des Nutzers; fällt beim Lesen dennoch etwas dergleichen auf, ist sofort
  darauf hinzuweisen.
- Erteilte Berechtigungen, die zwischen mehreren Rechnern geteilt werden
  sollen, gehören nach `.claude/settings.json` im Projekt (versioniert),
  nicht nach `.claude/settings.local.json` und nicht in die globale
  Git-Ignore-Datei. Grund: Eine committete `settings.local.json` durchläuft
  denselben Workspace-Trust-Check wie Projekt-Einstellungen und greift im
  nicht-interaktiven Modus gar nicht.

### 1.3 Plan vor Ausführung [T36]

- Keine Änderung an Dateien ohne vorher vorgelegten, vollständigen und
  erklärenden Plan. (Dass ausgeführt erst nach ausdrücklicher Freigabe wird
  und die Freigabe genau den vorgelegten Umfang deckt, regelt oben
  „Freigaben werden erteilt, nicht gefolgert“.)
- Vollständig heißt: je Datei, je Stelle — was entfällt, was kommt hinzu,
  warum, und welche unmittelbaren und mittelbaren Auswirkungen das hat.
  Auswirkungen, die über das besprochene Arbeitsziel hinausgehen, sind
  ausdrücklich zu nennen; gerade dort verbergen sich die Detailänderungen,
  die anderer Art sind als der wörtliche Umriss des Ziels.
- Der Plan beschreibt Absicht und Wirkung, nicht den Wortlaut:
  - Bei Dokumenten: Passage für Passage, was weggenommen und was hinzugefügt
    wird und was damit herausgestellt werden soll — nicht der fertige neue Text.
  - Bei Code: benannt werden adressierbare Einheiten (Datei, Klasse, Methode,
    Parameter, Config-Key, Kernel, Invariante) und was mit ihnen geschieht
    (entfällt, kommt hinzu, Signatur ändert sich, Verantwortung wandert).
    Keine Anweisungskörper, kein Kontrollfluss, keine Ausdrücke.
- Lässt sich eine Codeänderung ohne Kontrollfluss nicht beschreiben, ist der
  Schritt zu groß: zerlegen, nicht Code in den Plan aufnehmen.
- Der Plan umfasst genau den nächsten Schritt, nicht die ganze Ausbaustufe.

### 1.4 Abweichung heißt anhalten [T37]

- Zeigt sich bei der Ausführung, dass der zugestimmte Plan so nicht trägt:
  anhalten, Lage schildern, neu fragen. Niemals stillschweigend abweichen
  oder selbst entscheiden.

### 1.5 Rückfragen [T38]

- Vor jeder Rückfrage prüfen, ob die Projektdokumentation die Frage bereits
  beantwortet. Beantwortet sie sie: befolgen, nicht erneut fragen.
- Ist die Dokumentation mehrdeutig, ist die Mehrdeutigkeit ein Defekt:
  benennen und eine Korrektur der Doku vorschlagen, nicht stillschweigend
  interpretieren.
- Widersprechen sich Code und Dokumentation: anhalten und fragen — beide
  Seiten können falsch sein.

### 1.6 Ohne Rückfrage erlaubt / nie ohne Zustimmung [T39]

- Erlaubt: Lesen, Suchen, Tests ausführen, kurzlaufende Analysen ohne
  Seiteneffekte, Checkpoint-Commits auf der Werkbank nach 1.7.
- Nie ohne Zustimmung: push, Pakete installieren oder aktualisieren,
  Container bauen, langlaufende Jobs starten (insbesondere GPU),
  Dateien löschen.
- Einzelne Projekte können diese Freigaben verschärfen; die projekteigene
  `CLAUDE.md` hat dann Vorrang.

### 1.7 Commits und Branches [T40]

Die in diesem Kapitel beschriebene Verfahrensweise kann von alternativen
Anweisungen im Projekt überschrieben werden und verliert damit ihre
Gültigkeit.

In Projekten mit `.claude/git-worktree-model.json` gilt stattdessen der
Skill `parallel-sessions`; das Folgende gilt nur ohne diese Datei.

#### Die zwei Branches

- **Hauptpfad**: der vom Nutzer parallel zu `main`/`master` geführte
  Entwicklungspfad der aktuellen, meist komplexeren Aufgabe. Sein Name ist
  projektabhängig und wechselt im Laufe eines Projekts. Dort wird **nicht**
  committet — einzige Ausnahme ist der Squash-Merge (siehe unten).
- **Werkbank**: `claude-workbench`, in allen Projekten gleich benannt. Sie
  gehört Claude und darf jederzeit selbst aus einem anderen Branch abgeleitet
  werden.

#### Vor jedem Wechsel auf die Werkbank

1. `git fetch` und `git status`. Hängt das lokale Repo hinter dem Remote her:
   **sofort melden und abbrechen** — es wird auch von anderen Rechnern und
   remote per VSCode an denselben Projekten gearbeitet, das bereinigt der
   Nutzer zuerst. Fehlt dem Zweig die Upstream-Verknüpfung, ist `git status`
   als Prüfung untauglich: Es vergleicht nur gegen den Upstream und schweigt
   sonst über unveröffentlichte Commits. Dann ist ausdrücklich gegen den
   Remote-Zweig zu vergleichen (`git log --oneline origin/<zweig>..<zweig>`)
   und die Verknüpfung anschließend zu setzen.
2. Fragen, ob der gerade ausgecheckte Branch der Hauptpfad der aktuellen
   Tätigkeit ist. Nicht annehmen — davon hängt alles Folgende ab.
3. Prüfen, ob die Werkbank vor dem Hauptpfad liegt. Liegt sie das nicht, wird
   sie auf dem neuen Stand neu initialisiert und erst dann gewechselt.
4. Vor dem Neuinitialisieren prüfen, ob die Werkbank Commits enthält, die
   nicht im Hauptpfad sind. Wenn ja: **anhalten, Lage schildern und fragen** —
   mögliche Wege sind ein Rebase der Werkbank auf den neuen Stand, oder erst
   den anstehenden Squash-Merge ausführen und danach neu initialisieren. Nur
   wenn die Werkbank nichts Unverschmolzenes enthält, wird ohne Nachfrage neu
   initialisiert.
5. Beim Initialisieren den Namen des Hauptpfads in
   `<projekt>/.claude/arbeitsdaten.json` hinterlegen (siehe 1.2) — nur so ist
   er nach einem Sessionende noch bekannt.
- Bevor die Werkbank auf den aktuellen Stand gebracht wird, committet der
  **Nutzer** zuerst den Hauptpfad. Danach ist zu fragen, nicht anzunehmen.

#### Checkpoint-Commits (nur auf der Werkbank)

- Nach jedem zugestimmten und ausgeführten Schritt automatisch ein
  Checkpoint-Commit, ohne erneute Nachfrage. Zweck: Missverständnisse, die
  erst Schritte später auffallen, durch einfaches Zurücksetzen korrigierbar
  machen.
- Eigenständiges Zurückkehren auf einen früheren Stand ist ausschließlich auf
  der Werkbank erlaubt, nie auf einem anderen Branch.
- Doku-Anpassung und zugehörige Codeänderung immer im selben Commit.
- Der Commit-Body benennt den Fahrplanpunkt bzw. den Plan des Schritts.
- Größere Umstrukturierungen nur ausgehend von einem sauberen Stand
  (kein uncommitteter Diff), damit sie per Diff prüfbar und rücknehmbar sind.

#### Abschluss einer Aufgabe: Squash-Merge

- Ist eine Aufgabe abgeschlossen, wird dem Nutzer die Übernahme in den
  Hauptpfad vorgeschlagen.
- Ausdrücklich als **Squash-Merge** (`git merge --squash` plus ein einzelner
  Commit), nicht als Merge-Commit: Sonst gelangen die Checkpoint-Commits doch
  in die Historie des Hauptpfads und machen dort unkenntlich, in welchem
  Entwicklungszustand er jeweils war.
- Den Commit-Text legt in der Regel der Nutzer fest; er ist vor der
  Ausführung zu erfragen.
- Nach dem Squash-Merge wird die Werkbank verworfen und frisch vom Hauptpfad
  neu abgeleitet. (Nötig, weil ein Squash-Commit keine Elternschaft zur
  Werkbank hat und Git sie danach als „nicht gemergt" führt.)
- Das Neuableiten löscht die Upstream-Verknüpfung des Zweigs. Der erste Push
  danach ist deshalb `git push -u origin <werkbank>`; ohne `-u` bleibt sie
  verwaist, und `git status` kann anschließend nicht mehr melden, dass lokale
  Commits nicht veröffentlicht sind — es meldet nur einen sauberen
  Arbeitsbereich. Genau daran ist am 13. August 2026 eine ganze
  Arbeitssitzung auf einem Rechner unbemerkt liegengeblieben, während auf dem
  anderen weitergearbeitet wurde.

### 1.8 Wiederkehrende Kleinigkeiten [T41]

- Für Trivialänderungen gibt es keine Plan-Ausnahme. Taucht dieselbe Art
  Kleinigkeit wiederholt auf, wird stattdessen die zugrunde liegende Regel
  einmal geklärt und an der für dieses Projekt vorgesehenen Stelle für
  Festlegungen festgeschrieben (bei Softwareprojekten: Segment 2 der
  Implementierungsdoku); danach entfällt die Rückfrage dauerhaft.

### 1.9 Kontext-Haushalt [T42]

Sofern das Projekt Fahrplan und Statusdatei führt:

- Wird der Kontext knapp, ist die nächste Handlung die Detaillierung des
  Fahrplans — vor jeder Komprimierung, nie danach. Nicht weiterkodieren.
- Am Ende jeder Arbeitssitzung: Fahrplan und Status aktualisieren. Sie sind
  das Übergabemedium zwischen Maschinen und Sessions.

### 1.10 Aussagen über Claude Code und die Anthropic-Werkzeuge [T43]

- Fragen zu Claude Code, Claude Desktop und den übrigen Anthropic-Werkzeugen
  (Verhalten, Konfiguration, Dateiformate, Befehle, Grenzen) werden nie aus
  dem eigenen Basiswissen beantwortet, sondern gegen die aktuelle offizielle
  Dokumentation recherchiert, mit Quellenangabe.
- Belegte Fakten (mit Quelle), Beobachtung am laufenden System und
  Community-Wissen (Issues, Foren) werden klar getrennt ausgewiesen, nicht
  vermischt.
- Die Dokumentation selbst kann veraltet oder unvollständig sein — Anthropic
  baut an diesen Werkzeugen laufend um. Widerspricht sie der direkten
  Beobachtung, ist der Widerspruch zu benennen, nicht stillschweigend zu
  Ungunsten der Beobachtung aufzulösen.

### 1.11 Umgang mit importierten Chats [T44]

- Der Import eines Chats — unabhängig vom Dateiformat — ist nichts weiter
  als das Hinzufügen von Inhalt zum späteren Durchsuchen. Es findet dabei
  **keine** Prüfung auf Widersprüche statt. Chats sind historische
  Information, keine zu pflegende Dokumentation: Was nie gesucht wird,
  muss auch nie richtiggestellt werden.
- Die zeitliche Reihenfolge mehrerer Chats zueinander wird zuerst über eine
  erkennbare Nummerierung/Benennung der Dateien bestimmt. Fehlt die, wird
  zuerst im Chat-Inhalt selbst nach einem Anhaltspunkt gesucht (z. B. Bezug
  auf eine vorherige Sitzung). Bleibt beides ohne Ergebnis, wird der Nutzer
  gefragt — dabei wird das Erstellungsdatum der Datei als Hilfsangabe mit
  vorgelegt, ist aber für sich genommen nicht die Entscheidungsgrundlage.
- Eine Kollisionsprüfung erfolgt ausschließlich auf Anfrage: wenn ein Fakt
  oder eine Aussage aus den Chats gezielt gesucht und für die aktuelle
  Arbeit gebraucht wird — nie vorsorglich beim Import.
- Löst sich ein Fund schon innerhalb der Chats selbst auf (ein
  chronologisch späterer Chat hat ihn bereits geändert oder präzisiert),
  ist das keine Kollision, sondern normale Weiterentwicklung. Kollidiert er
  mit nichts, ist er einfach zu verwenden.
- Kollidiert der gefundene Fakt mit der aktuellen Implementierungsdoku oder
  dem Code, gilt **kein automatischer Vorrang** von Doku/Code: Es kann sich
  ebenso um einen Fehler im Chat wie um einen inzwischen überholten Stand
  der Doku handeln. Aufgelöst wird das nur, wenn die Klärung für die
  aktuelle Aufgabe zwingend ist — nicht vorsorglich. Lässt sich die
  Kollision dabei nicht selbst auflösen, gilt 1.5.
- Ob eine Aussage in einem Chat eine bleibende Festlegung oder nur eine
  später revidierbare Zwischenfeststellung ist, entscheidet sich nicht an
  ihrer Formulierung an der Fundstelle, sondern an der Chronologie: erst
  wenn spätere Chats sie unverändert fortführen bzw. ihr nicht
  widersprechen, gilt sie als Festlegung.

### 1.12 Ablage und Format importierter Chats [T45]

- **Stammt der Chat aus claude.ai** (Kontoexport oder Web-Endpunkte), gilt der
  Skill `chat-export`: Er regelt Ablageort, Dateiformat und Ablauf und ist für
  claude.ai-Importe maßgeblich. Sein Schema weicht von der folgenden
  Beispielvorgabe bewusst ab (kein `predecessor`/`successor`,
  `created_at`/`last_updated_at` statt `chat_date`). Für Chats aus anderen
  Quellen gilt weiterhin das folgende Beispielschema.
- Ablageort: `<projekt>/.claude/imported_chats/`. Der Ordner wird wie der
  übrige Inhalt von `.claude/` mitversioniert (s. 1.2).
- Liegt eine Chat-Quelle nicht bereits als JSON vor, wird sie beim Import
  in dieses Format überführt. Dabei ist eindeutig zu kennzeichnen, welcher
  Redebeitrag vom Nutzer und welcher von der Claude-Instanz stammt
  (`role`: `user`/`assistant`, unabhängig davon, wie die Quelle das
  benannt hat).
- Jede importierte Datei trägt zusätzlich zu den Redebeiträgen ein
  `metadata`-Objekt:
  - `chat_date`: Datum/Zeitstempel des Chats selbst, sofern aus dem Inhalt
    ablesbar; sonst `"unknown"`.
  - `imported_at`: Datum des Imports in dieses Projekt — immer bekannt,
    wird immer gesetzt.
  - `predecessor` / `successor`: Dateiname des chronologisch vorherigen
    bzw. nachfolgenden importierten Chats (s. 1.11 zur Bestimmung der
    Chronologie). Nur gesetzt, wenn zweifelsfrei bestimmbar.
- Ein einzeln importierter Chat lässt sich damit so gut wie nie
  zweifelsfrei in die Chronologie einordnen — selbst ein vorhandener
  Zeitstempel reicht dafür nicht: Der Chat kann an anderer Stelle, in
  einem völlig anderen Zusammenhang geführt worden sein. `predecessor`/
  `successor` bleiben dann unbesetzt.
- Ergibt ein späterer Import doch einen zweifelsfreien Vorgänger/
  Nachfolger zu einem bereits abgelegten Chat, wird dessen Metadatum
  nachträglich ergänzt.

Beispielschema:

```json
{
  "metadata": {
    "chat_date": "unknown",
    "imported_at": "2026-08-05",
    "predecessor": null,
    "successor": null
  },
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

## 2 Projektmethodik für Softwareprojekte: Konzept und Implementierungsdoku [T46]

Dieser Abschnitt gilt ausschließlich für Vorhaben, in denen Quellcode
entsteht. Vorhaben ohne Quellcode folgen einer einfacheren Form, die die
projekteigene CLAUDE.md beschreibt.

### 2.1 Phasen [T46]

1. **Findungsphase**: offenes Konzipieren in Prosa. Es wird gesammelt und
   verworfen; nichts ist Festlegung. Die Prosa-Code-Grenze (2.2) gilt hier
   abgemildert, die Segmentstruktur noch gar nicht.
2. **Fixierung**: Ideen wechseln schrittweise zu Vorgaben. Erste finale
   API-Beschreibungen entstehen. Ab hier gilt 2.2 strikt.
3. **Segmentierung**: Das Konzeptdokument wird als neues, dreigeteiltes
   Dokument neu geschrieben — kein Umbau, ein Neuschreiben. Arbeitsweise:
   Skill `/segmentierung`. Dabei entsteht erstmalig der Fahrplan.
4. **Implementierung**: Das segmentierte Dokument ist jetzt die
   Implementierungsdoku und wird parallel zum Code gepflegt (2.5).

### 2.2 Prosa-Code-Grenze [T22]

- Konzept- und Implementierungsdokumente enthalten keinen
  Implementierungscode. Genau zwei Ausnahmen: final beschlossene
  API-Signaturen und Nutzungsbeispiele bzw. -beispielschnipsel.
- Begründung (bindend): Code im Konzept macht die spätere Prüfung von Code
  gegen Konzept wertlos; Prosa hält den mitgedachten Kontext, den Code nicht
  abbildet; aus Prosa entsteht die Anwenderdokumentation.

### 2.3 Dokumentstruktur [T47]

- Ordner: `running_implementation_doc/` (Name pro Projekt anpassbar).
- Dateien: eine je Segment 1 und 2, dann eine je Hauptkapitel von Segment 3;
  dazu `fahrplan.md` und `status.md`. Die Dokumentdateien tragen numerische
  Präfixe in Leseordnung (z. B. `1_zusammenhaenge.md`, `2_vorgaben.md`,
  `3_1_orchestrator.md`, `3_2_pipeline.md`, …), Fahrplan und Status nicht.
- Überschriften: Die Segmente sind Überschriften 1. Ordnung, nummeriert 1–3.
  Die Überschrift „3 …" steht nur in der ersten Kapiteldatei von Segment 3;
  jede weitere Kapiteldatei beginnt direkt mit ihrer Kapitelüberschrift
  2. Ordnung. So ergibt das Verketten der Dokumentdateien in Dateireihenfolge
  ein gültiges Gesamtdokument.

### 2.4 Die drei Segmente [T48]

- **Segment 1 — Zusammenhänge**: beschreibt das System entlang der Funktionen
  im Workflow des Benutzers. Verweist reichlich auf die Kapitel von
  Segment 3; diese Verweise sind die explizite Abbildung der logischen
  Querbezüge und der Suchweg jeder Auswirkungsanalyse. Segment 1 ist zugleich
  die Quelle der späteren Anwenderdokumentation.
- **Segment 2 — Vorgaben**: projektweite Festlegungen, die quer über den
  gesamten Code gelten. Typisch: Vereinheitlichung wiederkehrender
  Kodierungsaufgaben (Struktur von Shared-Memory-Daten, Queue-Inhalte,
  Aufbau eines Kernel-Starters, Rollenschnitt GUI-Prozess/übrige Prozesse).
  Aufnahmetest: Man muss auf eine Datei zeigen und sagen können „das verletzt
  diese Vorgabe". Was so nicht prüfbar ist, gehört als Begründung nach
  Segment 1 oder als Detail nach Segment 3. Segment 2 dient künftigen
  Projekten mit ähnlicher Struktur als Vorlage.
- **Segment 3 — Einheiten**: je Hauptkapitel eine in sich geschlossene
  Einheit — Klasse, Modul, Ausführungsmodell (Orchestrator inkl.
  Interprozesskommunikation), Pipeline mit Kernel-Unterkapiteln, Frontend, …
- Jede Aussage hat genau ein normatives Zuhause; überall sonst stehen
  Querverweise. Nie zwei gleichrangige Fassungen derselben Festlegung.

### 2.5 Arbeitsschleife der Implementierung [T49]

- Die Tagesaufgabe kommt aus dem Fahrplan.
- In den Kontext geladen wird die betroffene Sektion aus Segment 3
  vollständig. Segment 1 wird bei Bedarf gezielt durchsucht, nicht pauschal
  geladen; Segment 2 gilt parallel.
- Reicht eine Entscheidung über die aktuelle Codestelle hinaus: über
  Segment 1 suchen, welche weiteren Sektionen von Segment 3 betroffen sind;
  diese lesen; Entscheidung überdenken; Auswirkungen rückwärts in die
  betroffenen Sektionen einpflegen; Zusammenhänge in Segment 1 ergänzen und
  mit den Stellen in Segment 3 verlinken.
- Zu jedem Codierungsschritt gehört im Plan (1.3) auch der Vorschlag, was
  dazu in die Implementierungsdoku aufzunehmen oder dort anzupassen ist.
  Doku und Code entstehen im Wechsel, nicht nacheinander. Kodiert wird erst
  nach ausdrücklicher Freigabe.

### 2.6 Fahrplan und Status [T50]

- **Fahrplan**: die nächsten Schritte in aufgabenangemessener Detaillierung.
  Erledigtes fliegt raus. Detaillierung vertiefen, bevor der Kontext
  komprimiert wird (1.9).
- **Status**: ausschließlich abgearbeitete Fahrplaneinträge. Keine
  Entscheidungen — die gehören sofort in das zuständige Segment der
  Implementierungsdoku.
