# Review: Herleitung vom Ziel zur Umsetzung

*Arbeitsdokument, angelegt am 2026-10-05, neu geschrieben am selben Tag. Es ersetzt nichts und ist selbst keine Festlegung.*

## Wozu dieses Dokument da ist

Die Arbeit am Vorhaben bestand seit einiger Zeit aus dem Lösen von Diskrepanzen: Ein Befund zeigt, dass zwei Stellen nicht zusammenpassen; eine Regel löst es; die Regel erzeugt den nächsten Befund. Dieses Dokument prüft, ob dahinter ein Planungsfehler weiter oben steckt. Dafür wurde die Kette vom Ziel des Skills über seine Leistungen zu den Mechanismen und Vorgaben neu gezogen — ausschließlich in dieser Richtung. Gelesen wurden als Quelle Kapitel 1, Kapitel 2, `status.md` und der Fahrplan; Kapitel 3 und die Zieltexte wurden gelesen, aber nur als Umsetzungsversuch, nie als Quelle einer Vorgabe.

**Ergebnis der Prüfung von Ebene 0:** Ziel, Leitidee, Rollenverteilung und Größenschranke (Kapitel 1.2, 1.3, 1.3.4, 1.10, Vorgabe 2.2) sind vollständig, in sich geschlossen und vom Entwickler geprüft. Dort gibt es nichts zu beanstanden; dieses Dokument sagt dazu nichts weiter.

Alles Weitere sind Befunde. Jeder ist so aufgebaut, dass er ohne die Doku daneben verständlich ist: worum es sachlich geht, was dafür festgelegt wurde, was tatsächlich dasteht, welche Folge das hätte, und welche Wege es gibt. Die Wege sind Richtungen mit ihren Kosten, keine Entscheidungen. Die Reihenfolge: zuerst die Widersprüche zwischen Stellen, die beide festlegen wollen; dann, was versprochen ist, aber keinen Mechanismus hat; dann, was festgelegt ist, aber dessen Herleitung nicht trägt; dann Begründungen, die nicht mehr tragen; zuletzt der Anhang mit dem, was in der Umsetzung ohne Vorgabe entstanden ist. Eine gemeinsame Ursache für alle Befunde hat die Prüfung nicht ergeben; wo mehrere dieselbe Form haben, steht das beim Befund.

**Eine Korrektur am Dokument selbst.** Die erste Fassung dieses Reviews hat Kapitel 2 als den Ort für alles gelesen, was sich gegen eine Datei prüfen lässt — und daraus gefolgert, die funktionalen Festlegungen in Kapitel 1 seien fehlplatziert. Das war falsch: Kapitel 1 trägt, *was* der Skill tut, Kapitel 2 trägt, *wie* alles umgesetzt wird, was in diesem Vorhaben entsteht — Normative, die an keiner einzelnen Funktion hängen. Die Fehllesung hatte eine Quelle in der Doku, und die steht jetzt als L-15.

---

## Widersprüche zwischen Stellen, die beide festlegen

### L-15 — Die Abgrenzung von Kapitel 1 und 2 ist nicht formuliert, und fünf Festlegungen stehen in beiden

**Worum es geht.** Die Doku folgt dem Dreiersschema. Kapitel 1 trägt die Zusammenhänge und mit ihnen die funktionalen Festlegungen — *was* der Skill tut, wann er fragt, was ein Marker ist, wann eine Festlegung bindet. Kapitel 2 trägt die Normative, die nicht an einer Funktion hängen, sondern sagen, *wie* umgesetzt wird: Sprache der Schlüsselwörter, Größenschranke, Ausgabevertrag, Kosten, Hooks nur lesend, kein Zwang für den Entwickler. Der Vorläufer verlangte für jede Aussage genau ein normatives Zuhause (Anhang A.6): „Nie zwei gleichrangige Fassungen derselben Festlegung — sie driften auseinander, und niemand merkt, welche gilt."

**Was festgelegt ist.** Der Kopf von Kapitel 2, vollständig: „Projektweite Festlegungen für alles, was in diesem Vorhaben entsteht: Regelteile, Skript, Hooks, Dokumentation. Aufnahmetest: Auf eine Datei muss sich zeigen lassen ‚das verletzt diese Vorgabe'. Was so nicht prüfbar ist, gehört als Begründung nach Kapitel 1 oder als Detail nach Kapitel 3." Das ist alles, was die Doku über die Abgrenzung der beiden Kapitel sagt. Der Vorläufer hatte in A.6 davor noch „Projektweite Festlegungen, die quer über den gesamten Code galten" — der Querschnittscharakter stand dort vor dem Aufnahmetest; beim Übertragen ist er zu „für alles, was entsteht" geworden, was etwas anderes sagt.

**Was tatsächlich dasteht.** Zweierlei. Erstens: Der Kopf nennt den Aufnahmetest und nicht das Merkmal, das Kapitel 2 von Kapitel 1 trennt. Funktionale Festlegungen — die Prüfliste, „Marker werden vorgeschlagen, nicht verfügt", „gefragt wird am Anlass" — bestehen den Aufnahmetest ebenso: Man kann auf eine Datei zeigen und sagen, sie verletze das. Nach dem Kopf allein gehörten sie nach Kapitel 2, und genau so hat der Verfasser dieses Reviews ihn in der ersten Fassung gelesen.

Zweitens: Fünf Festlegungen stehen in beiden Kapiteln, ohne dass eine Stelle die andere als Zuhause nennt. „Gefragt wird am Anlass": 1.7, 1.7.7, 1.8, 2.9. „Fehlende Felder blockieren nie": 1.3.1, 2.10. „Marker pflichtig am Definitionsort und in `relate`": 1.3.3 Funktionstabelle, 2.2 Bedingung 1, 1.7.4. „Hooks sind nur lesend": 1.3.5, 2.8. Die erhöhte Reibungsschwelle für `global`: 1.3.1 R6, 1.3.3, 2.9. Zum Vergleich, wie es richtig aussieht: „Annahmen machen nie `fixed`" steht in 1.3.1 mit dem Zusatz „ist keine Einzelheit dieser Liste, sondern Vorgabe 2.11" — ein Verweis, der das Zuhause benennt.

**Warum das ein Problem ist.** Wo dieselbe Festlegung an zwei Orten steht, erreicht eine Änderung nur einen. L-12 ist der Fall, in dem das geschehen ist: Q-15 hat 1.7 geändert; 1.8 und 2.9 sagen noch das Alte. Die übrigen vier Doppelungen sind heute stimmig, aber jede nächste Änderung an ihnen hat dieselbe Chance. Und solange die Abgrenzung nicht formuliert ist, entscheidet jeder Schreibende nach Gefühl, wohin eine neue Festlegung gehört — sie landet dort, wo gerade gearbeitet wird, und beim nächsten Mal daneben. Dieses Review selbst ist der Beleg: Es hat die Abgrenzung aus dem Kopf von Kapitel 2 herausgelesen und falsch verstanden.

**Was zu tun wäre.** Drei Schritte. Erstens die Abgrenzung in den Kopf von Kapitel 2 schreiben — dass Kapitel 1 trägt, was der Skill tut, und Kapitel 2, wie alles umgesetzt wird, was in diesem Vorhaben entsteht, unabhängig von einer einzelnen Funktion; der Aufnahmetest bleibt als zweite Bedingung dahinter. Zweitens für die fünf Doppelungen je ein Zuhause bestimmen — nach der Abgrenzung: funktional nach Kapitel 1, Normativ nach Kapitel 2 — und an der anderen Stelle einen Verweis setzen, wie 1.3.1 es für 2.11 schon tut. Drittens: Der Standard des Vorläufers wird mit Fahrplanschritt 7 zu `standard.de.md` und bringt seinen Aufnahmetest aus A.6 mit. Kapitel 1.11 zählt drei Anpassungen auf, die er dabei erfährt; die Abgrenzung von Segment 1 und 2 müsste die vierte sein — sonst erbt jedes Projekt, das den Standard über den Skill führt, dieselbe Lücke, aus der dieses Missverständnis entstanden ist.

### L-02 — `mode` bedeutet zweierlei

**Worum es geht.** Der Skill kennt zwei Dinge, die sich auf den Betrieb beziehen. Das eine ist die **Lage** einer Sitzung: Führt die Instanz einen beschlossenen Schritt aus, oder denkt sie mit dem Entwickler über etwas neu nach? Davon hängt ab, wie sie mit einer Festlegung umgeht, an die eine Idee stößt — im ersten Fall hält sie an und fragt, im zweiten parkt sie die Kollision und denkt weiter. Das andere ist die **Abwahl** des Skills für ein Projekt: ob er hier überhaupt etwas tun soll.

**Was festgelegt ist.** Vorgabe 2.1: „Ein Schlüsselwort ist ein Name, keine Beschreibung: Wer `decided` schreibt, meint genau diesen Zustand, und niemand darf `fixed`, `decided` und ein drittes Wort als persönliche Ausdrucksformen desselben Zustands lesen." Aus demselben Grund wurde die Ereigniszeile `confirmed` zu `upheld` umbenannt (Q-02): `confirmed` war schon ein Statuswert, und dasselbe Wort hätte im selben Register zwei Bedeutungen getragen.

**Was tatsächlich dasteht.** Kapitel 1.4 nennt die Lage „**Lage** (`mode`)" mit den Werten `execute` und `design`; `rules-core.de.md` Abschnitt 2 führt sie ebenso. Vorgabe 2.9 und `rules-startup.de.md` nennen den Skill-Parameter für die Abwahl `mode` mit den Werten `on`, `off`, `null`. `SKILL.de.md` Schritt 2 liest „Steht dort `mode: off`", Schritt 4 heißt „Lage bestimmen". Dasselbe Schlüsselwort, zwei Bedeutungen, zwei Wertemengen.

**Warum das ein Problem ist.** Das Skript wird einen Parameter `mode` lesen und muss wissen, welcher gemeint ist. Die Instanz liest in der Parameterdatei `mode: on` und im Regelteil, dass `mode` `execute` oder `design` ist, und bekommt keine Regel, wie das zusammenpasst. Das ist genau die Lage, die 2.1 ausschließen will — und sie ist nicht aufgefallen, weil beide Stellen für sich stimmig sind.

**Was zu tun wäre.** Eines der beiden umbenennen. Der Skill-Parameter ist in der Parameterdatei das einzige Feld, das über Ein und Aus entscheidet; `enabled` oder `active` sagen das ohne Verwechslung. Die Lage ist der ältere Begriff und steht mit `execute`/`design` an mehr Stellen; sie zu belassen ist billiger. Umgekehrt ginge auch `stance` oder `reading` für die Lage und `mode` bliebe dem Schalter — aber dann wandert die Änderung durch die Härtetabelle, das Verhalten und die Szenen in Kapitel 1.6. Die Entscheidung kostet in beiden Fällen eine Stunde; der Fehler, sie nicht zu treffen, kostet beim Bauen des Skripts einen Sonderfall, der in jeder Zeile mitläuft.

### L-04 — Wer schreibt die Marker in die Prosa?

**Worum es geht.** Eine Festlegung bekommt in der Prosa des Entwicklers einen Marker, `[D-0042]`, und im Register ihre Zeilen. Beides entsteht, wenn ein freigegebener Plan ausgeführt wird. Für das Register ist klar, dass das Skript schreibt — es gibt dafür das Kommando `apply`. Für den Marker in der Prosa ist die Frage heikler: Die Prosa gehört dem Entwickler, und Bedingung 6 der Größenschranke verbietet dem Skript, sie zu ändern.

**Was festgelegt ist.** Bedingung 6 in Vorgabe 2.2: „Kein automatisches Umschreiben von Prosa. Das Skript listet, die Instanz schlägt im Plan vor, der Entwickler gibt frei." Kapitel 1.3.4: „Marker und Registerzeilen schreibt die Instanz mit der Ausführung eines freigegebenen Plans." Kapitel 3.6.2: „Kein Kommando ändert Prosa des Entwicklers. Geschrieben werden dürfen: das Register […] und Arbeitsdokumente."

**Was tatsächlich dasteht.** Die Ergänzung zu Vorgabe 2.6 vom 4. Oktober sagt: „Die Markerformen `[D-0042]` und `[>D-0042]` schreibt zwar `apply` in die Prosa." Das ist eine dritte Antwort, und sie widerspricht den beiden anderen. Sie steht in einem Vorgabentext und ist dort als Begründung gebaut — warum die Markerform im Regelteil bleiben darf —, aber die Begründung stützt sich auf eine Behauptung über die Umsetzung, die nirgends sonst gilt.

**Warum das ein Problem ist.** Wer `apply` baut, liest 3.6.2 und schreibt keine Prosa. Wer die Regelteile liest, liest 2.6 und erwartet, dass `apply` Marker setzt. Die Instanz steht dann vor einem Plan mit zehn Markervorschlägen und weiß nicht, ob sie zehn Edits macht oder einen Aufruf. Vorgabe 2.7 sagt, der Dateiedit sei der teuerste Vorgang überhaupt — die Frage ist also nicht nebensächlich, sondern entscheidet über die Kosten jeder Planausführung.

**Was zu tun wäre.** Erstens den Satz in 2.6 korrigieren; die Begründung dort trägt auch ohne ihn, denn die Instanz muss die Markerform im Plan vorschlagen und in fremder Prosa erkennen — unabhängig davon, wer sie am Ende schreibt. Zweitens die eigentliche Frage entscheiden, die bisher niemand gestellt hat: Bedingung 6 verbietet *Umschreiben*; ist das Einfügen von acht Zeichen am Satzende ein Umschreiben? Wenn nein, darf `apply` die Marker setzen, und die Planausführung wird ein einziger Aufruf statt zehn Edits — das wäre im Sinne von 2.7 und 1.3.6. Wenn ja, schreibt die Instanz jeden Marker selbst, und 1.3.4 bleibt wörtlich. Beides ist vertretbar; die Doku muss eines sagen, an einer Stelle.

### L-10 — H3 ist eingeplant und unentschieden zugleich

**Worum es geht.** Drei Hooks sichern, dass Marker und Register konsistent bleiben. H1 prüft nach jedem Edit, H2 vor jedem Commit — beide kommen mit dem Skill und wirken ohne Einrichtung im Projekt. H3 ist anders: Er läuft am Sitzungsstart und fängt zwei Lücken auf, die H1 und H2 nicht sehen — wenn der Entwickler die Doku zwischen zwei Sitzungen selbst bearbeitet hat, und wenn nach einer Kompaktierung der Kontext weg ist. Dafür muss er je Projekt in die Konfiguration eingetragen werden, und das bricht die Zusage aus 1.3.5, dass die Absicherung ohne Einrichtung wirkt.

**Was festgelegt ist.** Kapitel 1.7.6: „Zu entscheiden ist deshalb zweierlei: ob die beiden Lücken diese eine Ausnahme wert sind, und ob man das jetzt entscheidet oder erst, wenn die Probe zeigt, wie oft sie in der Praxis auftreten."

**Was tatsächlich dasteht.** Fahrplanschritt 6: „H1 bis H3 nach Kapitel 3.7: Frontmatter-Einbindung, Pfadauflösung prüfen, Zeitlimits messen, H3 als Angebot des Skillstarts." Das Entscheidungstor der Probe (3.8.5): „Über H3 wird vorher entschieden, nicht hier." Kapitel 3.7 beschreibt H3 vollständig und sagt selbst, der Fahrplan enthalte „an zwei Stellen Widersprüchliches". Der Zustand ist seit dem 25. September bekannt und unverändert.

**Warum das ein Problem ist.** Solange die Frage offen ist, ist nicht nur H3 offen, sondern eine Zusage aus Kapitel 1.3.5 steht unter Vorbehalt. Und 1.7.6 nennt als mögliche Antwort, die Probe entscheiden zu lassen — die Probe kann aber nur messen, was gebaut ist. Wird H3 nicht gebaut, misst sie nichts; wird er gebaut, ist die Frage „ob" durch Tatsachen beantwortet.

**Was zu tun wäre.** Die Frage ist kleiner, als sie aussieht, wenn man sie als zwei Fragen stellt. Erstens: Wird H3 **gebaut**? Das kostet laut Fahrplan eine Sitzung, und ohne ihn lässt sich die Lücke „Entwickler bearbeitet zwischen Sitzungen" gar nicht beobachten. Zweitens: Wird er **standardmäßig angeboten**? Das ist die Frage, die 1.3.5 berührt, und sie kann die Probe beantworten, wenn H3 existiert. Die Doku müsste dann sagen: H3 wird gebaut; ob der Skillstart ihn anbietet oder nur auf Nachfrage einrichtet, entscheidet die Probe. Damit sind Fahrplan und Probe-Tor wieder einig.

### L-12 — Zwei Stellen sagen noch, der Skillstart frage

**Worum es geht.** Am 2. Oktober wurde entschieden (Q-15), dass der Skill beim Laden keine Frage stellt. Er liest, bestimmt die Lage, parkt Kollisionen — und fragt erst in dem Moment, in dem er zum ersten Mal etwas vorschlagen oder schreiben will, weil die Antwort erst dann etwas bewirkt. Die Begründung in Kapitel 1.7: Die frühere Fassung fragte zweimal, einmal beim Laden als Methodikfrage, einmal später am Anlass, und der Entwickler konnte beim ersten Mal nicht beurteilen, worum es geht.

**Was festgelegt ist.** Kapitel 1.7: „Gefragt wird, wenn die Antwort etwas bewirkt — vorher nie." Kapitel 1.7.7: „Gefragt wird aber nicht beim Laden, sondern am ersten Anlass."

**Was tatsächlich dasteht.** Kapitel 1.8, Schritt 1 „Skillstart": „Die Instanz liest die Skill-Parameterdatei oder erhebt aus dem Projekt, was sich ablesen lässt, und **fragt** nur, was sich nicht ablesen lässt." Vorgabe 2.9: „Der Skillstart **erfragt** nur, was sich aus dem Projekt nicht ablesen lässt." Beide Sätze beschreiben eine Frage beim Start. Der Prüfvermerk „Ok" an 1.8 stammt vom 24. September, acht Tage vor Q-15.

**Warum das ein Problem ist.** Das ist ein Fall von L-15 in Reinform: Dieselbe Regel steht an drei Orten — 1.7, 1.8, 2.9 —, und die Änderung hat nur einen erreicht. Wer den Skillstart baut und 1.8 oder 2.9 liest, baut die Frage ein, die Q-15 abgeschafft hat.

**Was zu tun wäre.** Die beiden Sätze auf den Stand von Q-15 bringen — in 1.8 „fragt nur, was sich nicht ablesen lässt" durch „fragt nichts; was sich nicht ablesen lässt, bleibt offen bis zum ersten Anlass", in 2.9 den Satz streichen oder auf 1.7 verweisen. Das ist in fünf Minuten getan. Was länger dauert und wichtiger ist: nachsehen, ob Q-15 noch weitere Stellen nicht erreicht hat. Kapitel 1.7.1 („Was sich aus dem Projekt nicht ablesen lässt […] wird besprochen") und 1.7.7 („Die Instanz fragt einmal je Sitzung") sind Kandidaten.

### L-14 — Kapitel 1.7.1 widerspricht sich selbst

**Worum es geht.** Die Erstanlage ist der Fall, in dem ein Projekt noch keine Doku hat und der Entwickler eine haben will. Kapitel 1.7.1 legt fest, wie das abläuft: Die Instanz liest das Projekt, bildet Annahmen, legt einen vollständigen Vorschlag im Plan vor, und der Entwickler korrigiert in Prosa. Der Abschnitt grenzt sich ausdrücklich von einem Fragebogen ab.

**Was festgelegt ist.** Kapitel 1.7.1, Absatz „Klärung im Gespräch, kein Formular": „Sie arbeitet also keine Fragenliste ab, sondern liest zuerst das Projekt und legt dann einen vollständigen Vorschlag vor, in dem jede Annahme sichtbar ist." Und Vorgabe 2.13: „Alles, was der Entwickler über das Schreiben von Prosa, das Lesen von Plänen und das Antworten in Prosa hinaus tun müsste, ist ein Verstoß."

**Was tatsächlich dasteht.** Vier Absätze weiter, unter „Planungen und Arbeitsschritte": „Mit dem Entwickler ist zu klären, wie der Projektfortschritt […] geplant werden soll:" — und dann drei Fragen als Aufzählung: ob es einen Fahrplan geben soll und wo, ob die Planung im Chat bleibt oder in Dateien, ob abgearbeitete Schritte aufgezeichnet werden und wo. Das ist eine Fragenliste. Der Entwickler hat den Widerspruch am 18. September benannt („Der Planungsblock widerspricht zwei Absätzen weiter oben"); der Abschnitt trägt dennoch den Prüfvermerk „Ok" und ist seither unverändert.

**Warum das ein Problem ist.** Der Abschnitt ist die Vorlage für das, was die Instanz bei der Erstanlage tut. Steht dort eine Fragenliste, wird sie abgearbeitet — und der Entwickler bekommt bei der ersten Begegnung mit dem Skill genau den Fragebogen, den 1.3.4, 1.7.1 und 2.13 ausschließen. Die Erstanlage ist laut 1.7.1 „folgenreich: Was hier entsteht, prägt die Arbeit der nächsten Monate"; der erste Eindruck prägt auch, ob der Entwickler den Skill weiter benutzt.

**Was zu tun wäre.** Die drei Fragen in Annahmen umschreiben, die der Vorschlag mitbringt: Die Instanz liest, ob es eine Fahrplandatei gibt, ob Planungen bisher im Chat oder in Dateien liegen, ob eine Statusdatei existiert — und schlägt entsprechend vor, mit der Begründung aus dem Projekt. Nur was sich nicht ablesen lässt, steht als offener Punkt im Plan, so wie der Abschnitt es für den Ordner schon vormacht („Ein Punkt bleibt zu klären, weil er sich nicht ablesen lässt"). Danach den Prüfvermerk auf „offen" setzen, bis der Entwickler den Abschnitt erneut gelesen hat.

---

## Versprochen, aber ohne Mechanismus

### L-03 — Der lageabhängige Abbruchwert hat keinen Weg zum Skript

**Worum es geht.** Die Auswirkungsrechnung sammelt zu einer geänderten Festlegung Kandidaten ein, die betroffen sein könnten. Wie weit sie dabei sucht, bestimmt ein Abbruchwert. Kapitel 1.7.4 beschreibt die Spannung: Die Liste soll kurz sein, weil jeder Kandidat die Instanz eine Entscheidung kostet, und vollständig, weil ein übersehener Kandidat genau der Fehler ist, den das Verfahren verhindern soll.

**Was festgelegt ist.** Kapitel 1.7.4: „Aufgelöst wird das durch einen Abbruchwert: Wie weit die Suche reicht, ist einstellbar — **eng in der Lage `execute`, weiter in der Lage `design`**."

**Was tatsächlich dasteht.** Es gibt einen Skill-Parameter `impact_cutoff` mit einem Wert („1 bei `hops`, 0,40 bei `weighted`", `rules-startup.de.md`). Kapitel 3.6.5 beschreibt Graphenparameter und Kostenfunktionen ohne Bezug zur Lage. Das Kommando `impact` nimmt `--chapter` oder `--ids`, keine Lage. Nirgends steht, wie die Lage — die ja die Instanz bestimmt, nicht das Skript — den Abbruchwert verändert.

**Warum das ein Problem ist.** Die Lageabhängigkeit ist nicht Beiwerk, sondern die Auflösung der Spannung, die 1.7.4 selbst aufmacht: Beim Ausführen eines Schritts darf die Liste kurz sein, weil der Rahmen feststeht; beim Entwerfen muss sie weit sein, weil gerade gesucht wird, was alles betroffen ist. Ohne den Mechanismus gilt ein Wert für beides, und die Probe misst dann nicht das, was Kapitel 1 beschreibt.

**Was zu tun wäre.** Drei Wege. Erstens: `impact` bekommt ein Argument `--mode execute|design` (oder wie die Lage nach L-02 dann heißt), und das Skript wählt den Abbruchwert daraus — dann braucht die Parameterdatei zwei Werte oder einen Faktor. Zweitens: Die Instanz übergibt den Abbruchwert selbst, je nach Lage, und der Regelteil sagt ihr, welchen — das ist einfacher im Skript, aber eine Rechenvorschrift im Regelteil, gegen Vorgabe 2.6. Drittens: Die Lageabhängigkeit wird gestrichen und 1.7.4 entsprechend geändert; die Probe prüft dann, ob ein Wert für beide Lagen reicht. Der dritte Weg ist der billigste und möglicherweise richtig — aber er muss entschieden werden, nicht durch Vergessen eintreten.

### L-05 — `[register: pfad]` ist weder Adresse noch Feld

**Worum es geht.** Ein Repository kann mehrere Vorhaben mit je eigener Doku tragen; dieses Repository ist so gebaut. Jedes Vorhaben hat sein eigenes Register. Die Skill-Parameterdatei gibt es aber nur einmal je Repository (Q-19). Damit der Skill weiß, zu welchem Register eine Dokudatei gehört, trägt die Datei eine Zeile `[register: pfad]`.

**Was festgelegt ist.** Vorgabe 2.3: „Im Dokument des Entwicklers stehen vom Skill nur Adressen: Marker an Festlegungen und Rollen an Überschriften oder Absätzen. Keine Skill-Logik, kein Attribut, kein Zustand steht dort." Vorgabe 2.10 kennt vier Feldsorten: Marker-Feld, Registerfeld, Skill-Parameter, Ausgabefeld — „jede wird beim Namen genannt, wo sie vorkommt".

**Was tatsächlich dasteht.** Kapitel 3.5.4 und `rules-startup.de.md`: „Ein Vorhaben mit eigener Doku weicht ab, indem seine Dateien Rollenmarker und eine `[register: pfad]`-Zeile tragen." `rules-core.de.md` Abschnitt 14 führt sie als dritte Stufe der Registersuche. Sie ist kein Marker (sie adressiert keine Festlegung), keine Rolle, kein Registerfeld, kein Skill-Parameter — und sie steht im Dokument des Entwicklers. 2.3 kennt sie nicht; 2.10 kennt sie nicht.

**Warum das ein Problem ist.** Die Zeile ist sachlich sinnvoll und war die Antwort auf Q-19. Aber sie ist eine Ausnahme von 2.3, die nirgends als Ausnahme benannt ist — anders als der Registerpfad-Qualifier im Umbauziel, für den 2.3 ausdrücklich sagt: „Eine benannte Ausnahme gibt es doch, und sie steht hier, damit sie nicht stillschweigend bleibt." Eine stillschweigende zweite Ausnahme neben einer ausdrücklich benannten ersten untergräbt die Vorgabe.

**Was zu tun wäre.** Zwei Wege. Erstens: Die Zeile als Adresse einordnen — sie adressiert das Register, so wie ein Marker eine Festlegung adressiert — und in 2.3 und 2.10 beim Namen nennen, mit derselben Begründung wie beim Qualifier: Ein Register wird selten verschoben, ein Bruch trifft die Zuordnung, nicht die Identität. Zweitens: Die Zeile aus dem Dokument nehmen und die Zuordnung Vorhaben → Register in die Skill-Parameterdatei legen, etwa als Liste von Ordner-Register-Paaren. Das hält 2.3 ausnahmslos, kostet aber die Einfachheit von Q-19 („die Zeile im Dokument reicht") und macht die Parameterdatei zum Ort, der jedes Vorhaben kennen muss.

### L-08 — Die Suchschlüssel haben keinen Weg vom Urteil zum Kommando

**Worum es geht.** Jede Festlegung bekommt im Register zwei bis vier Suchschlüssel — Begriffe, mit denen das Skript Erwähnungen findet, die keinen Marker tragen. Sie sind die zweite Quelle der Auswirkungsrechnung neben dem Graphen und laut 1.7.4 der Maßstab, an dem sich der Graph überhaupt rechtfertigen muss.

**Was festgelegt ist.** Q-05 (Kapitel 1.7.4): „Wer die Suchschlüssel wählt und pflegt: die Instanz, beim Anlegen der Festlegung — sichtbar im Planabschnitt, damit der Entwickler sie korrigieren kann." B-03 (3. Oktober) hat festgelegt, dass sie als Block unter der Tabelle des Planabschnitts stehen, nur für neu angelegte Festlegungen.

**Was tatsächlich dasteht.** Kapitel 3.6.4 bei `plan-section`: Das Kommando gibt „den fertigen Abschnitt ‚Berührte Festlegungen'" aus, „darunter der Suchschlüsselblock für die neu angelegten IDs". Bei `apply`: schreibt „Suchschlüssel" ins Register. Zwischen „die Instanz wählt" und „das Skript gibt aus und schreibt" steht nichts: kein Argument, mit dem die Instanz ihre Wahl an `plan-section` übergibt, kein Weg, auf dem `apply` sie aus dem Plan liest. Dazu kommt, dass neue Festlegungen zum Planzeitpunkt noch keine ID haben — IDs vergibt `next-id`, geschrieben wird mit `apply` —, der Block in 3.6.4 aber „für die neu angelegten IDs" gilt.

**Warum das ein Problem ist.** Entweder wählt die Instanz die Schlüssel und schreibt sie von Hand in den Plan — dann ist der Block nicht Teil der Kommandoausgabe, und `apply` muss ihn aus dem Plan parsen. Oder das Skript schlägt sie vor — dann widerspricht das Q-05, und es braucht eine Heuristik, die aus einem Satz Begriffe zieht. Beides ist baubar; die Doku sagt nicht, welches. Wer `plan-section` baut, muss raten.

**Was zu tun wäre.** Die Frage ist, wer die Schlüssel vorschlägt. Wenn die Instanz: `plan-section` nimmt sie als Argument entgegen, zum Beispiel `--keys "Wortlaut=Begriff;Begriff"`, und schreibt sie in den Block; `apply` liest den Block aus dem Plan wie alles andere. Wenn das Skript: Q-05 wird geändert, und 3.6.4 beschreibt die Heuristik — die wäre einfach (Substantive und Zahlen aus dem Definitionssatz), aber eine weitere Rechenvorschrift. Für den Block gilt in beiden Fällen: Er adressiert neue Festlegungen über den Wortlaut, nicht über eine ID, wie B-03 es festgelegt hat; 3.6.4 ist entsprechend zu korrigieren (siehe F-08).

---

## Festgelegt, aber die Herleitung trägt nicht

### L-01 — Die Gründungsleistung ist die am dünnsten festgelegte

**Worum es geht.** Kapitel 1.2 nennt zwei Fehlbilder des Vorläufers. Das zweite, das Fehlbild Gesetz, ist das schwerere: Die Instanz liest jede Festlegung als bindend, jede Idee stößt an eine und wird verworfen, mit wachsender Doku wird sie unkreativ. Kapitel 1.7.5 nennt die Leistung, die das behebt, „die Leistung, um derentwillen das Vorhaben begonnen wurde". Kapitel 1.9 sagt, dass sich an ihr das Design entscheidet: Schießt die Instanz Ideen weiterhin ab, „ist nicht ein Wert falsch eingestellt, sondern das Design gescheitert".

**Was festgelegt ist.** Kapitel 1.7.5, vollständig: „Bittet der Entwickler um Alternativen oder bringt eine Idee, liest die Instanz die Doku als Stand, nicht als Vorgabe, führt den Gedanken zu Ende und parkt jede Kollision in einem Satz, statt sie als Ablehnung zu formulieren. Welche Festlegung dabei wie schwer wiegt, sagt ihre Härte (Kapitel 3.1)." Drei Sätze. Dazu die Messgröße der Probe (3.8.4): „jede Kollision mit `decided` wird geparkt, keine als Ablehnung formuliert."

**Was tatsächlich dasteht.** In Kapitel 2 nichts. Keine Vorgabe sagt, was Parken ist, wie ein geparkter Satz gebaut ist, was „zu Ende führen" heißt, oder wann die Instanz die Lage `design` wählt. Das alles steht nur in der Umsetzung: `rules-core.de.md` Abschnitt 6 mit der Härte-mal-Lage-Tabelle, dem Parken („Ein Satz je Festlegung: was sie festlegt, ihr Grund, die Umbaukosten […] Formulierung: ‚Das berührt X, weil …' — nie ‚Das geht nicht wegen X'") und der Auswirkungsliste mit drei Bewertungen. Für die Auswirkungsliste gibt es nicht einmal in Kapitel 1 eine Quelle (F-02).

Zum Vergleich: Die Erstanlage (Leistung 1) hat in Kapitel 1.7.1 den längsten Abschnitt des Kapitels, mit sechs Planpunkten, drei Gliederungsformen, einer Liste von Ordnernamen und einem Absatz über Umkehrbarkeit.

**Warum das ein Problem ist.** Die Probe misst „Parken statt Abschuss" und erklärt das Design bei Verfehlen für gescheitert. Gemessen wird dann gegen eine Verhaltensbeschreibung, die nur in der Umsetzung existiert — und wenn sie verfehlt wird, gibt es keine Vorgabe, zu der man zurückgeht, sondern nur den Regeltext, der gerade versagt hat. Die Doku weiß nicht, was sie von dieser Leistung verlangt; sie weiß nur, wie sie sie gebaut hat.

**Was zu tun wäre.** Kapitel 1.7.5 so ausarbeiten, dass es die Leistung festlegt und nicht nur benennt — das ist funktional und gehört deshalb nach Kapitel 1, nicht nach Kapitel 2. Festzulegen wäre, was in der Lage `design` prüfbar gilt: dass keine Kollision mit einer `decided`-Festlegung als Ablehnung formuliert wird; dass jeder geparkte Satz die Festlegung, ihren Grund und die Umbaukosten nennt; dass der Gedanke bis zu einem Vorschlag mit Kosten geführt wird, bevor der Entwickler entscheidet. Diese drei Sätze stehen inhaltlich schon in Abschnitt 6 des Regelteils — sie müssen nur in Kapitel 1 zur Festlegung werden, damit der Regelteil ihre Umsetzung ist und nicht ihre einzige Quelle. Daneben wäre zu prüfen, ob 1.7.5 nicht auch die Erzählung verdient, die 1.7.1 hat: Szene 5 in Kapitel 1.6 zeigt den Fall, aber der Abschnitt, der die Leistung beschreibt, verweist nicht einmal auf sie.

### L-07 — Die Planungsort-Regel folgt aus einem lokalen Konflikt

**Worum es geht.** Kapitel 1.7.3 legt fest, wo eine Planung steht: bis zehn Sätze im Schritt selbst, mit Festlegungen über das System in der Doku, als bloßer Arbeitsweg in einer eigenen Datei, die nach der Ausführung gelöscht wird. Die Regel ist ausgearbeitet, in `rules-planning.de.md` umgesetzt und mit Q-12 entschieden.

**Was festgelegt ist.** Kapitel 1.7.3 begründet, warum der Skill das regeln muss: „Dass der Skill das regeln **muss**, hat einen zweiten Grund: Die bestehenden Anweisungen widersprechen sich. Die globale Regel nennt drei mögliche Orte und fragt, wenn keiner geregelt ist; die Projektregel dieses Repositories verbietet eigene Plan-Dateien. Solange beides nebeneinandersteht, hängt die Antwort davon ab, welche Datei zuerst gelesen wird."

**Was tatsächlich dasteht.** Der Skill ist für jeden Entwickler mit ähnlicher Arbeitsweise gedacht (Kapitel 1.1). Die „globale Regel" und die „Projektregel" sind die `CLAUDE.md`-Dateien eines bestimmten Entwicklers. Der Konflikt zwischen ihnen ist real, aber er ist ein Konflikt in dessen Anweisungen, nicht im Ziel des Skills. Der erste Grund in 1.7.3 — der Fahrplan trägt was, nicht wie — stammt aus einem Vorfall vom 22. August (Anhang A.7, Anmerkung), also ebenfalls aus der Praxis dieses Entwicklers mit dem Vorläufer.

**Warum das ein Problem ist.** Nicht, dass die Regel falsch wäre. Sondern dass sie im Skill an einer Stelle steht, die aus dem Ziel folgen soll, und dort mit einem Grund begründet ist, der außerhalb des Skills liegt. Was aus dem Ziel folgt, ist nur ein Teil: Geplante Schritte müssen ein Umbauziel tragen, weil sonst nichts öffnet (1.7.3, erster Absatz). Wo eine Planung steht und wie lang sie sein darf, ist Methodik — dieselbe Sorte Regel wie Phasen, Segmente und Arbeitsschleife, die Kapitel 1.11 in den Regelteil `standard.de.md` verweist.

**Was zu tun wäre.** Die Regel teilen. Was der Mechanismus braucht — ein geplanter Schritt ist ein Text unter einer Überschrift, er trägt ein Umbauziel, er steht in einem Abschnitt mit der Rolle `plan` oder in einer Datei aus `planned_steps` — bleibt in `rules-planning.de.md`; seine Festlegung steht in Kapitel 1.7.3 bereits, sie wäre nur vom Methodikteil zu trennen. Was Methodik ist — die drei Orte, die zehn Sätze, das Löschen der Planungsdatei — wandert nach `standard.de.md` zu den übrigen Anpassungen des Vorläufers, die Kapitel 1.11 schon aufzählt („die Regel, wo ein Plan steht, wird durch Kapitel 3.4 ersetzt"). Dann lädt ein Projekt, das den Standard des Vorläufers nicht führt, diese Regel auch nicht — und der Skill zwingt niemandem eine Methodik auf, die aus einem fremden Vorfall stammt.

### L-16 — Eine Vorgabe wird angewendet, die nirgends steht

**Worum es geht.** Die Skills dieses Repositories sollen unabhängig voneinander installierbar sein. Ein Regelteil, der einen Nachbar-Skill nennt, setzt voraus, dass dieser am Zielort existiert — und er tut es möglicherweise nicht.

**Was festgelegt ist.** Kapitel 3.9.2 sagt: Der Abschnitt „Zusammenspiel mit anderen Skills" der bisherigen `SKILL.md` „verstößt gegen die Vorgabe, dass kein Skill-Körper auf einen anderen Skill dieses Verzeichnisses verweist, und wird beim Zusammensetzen aufgelöst." Diese Vorgabe steht nicht in Kapitel 2. Sie steht in keinem Kapitel dieser Doku. Vermutlich steht sie in `skill-dev-doc.md` des Repositories; geprüft wurde das hier nicht, weil diese Datei nicht Quelle dieses Reviews ist.

**Was tatsächlich dasteht.** `rules-core.de.md` Abschnitt 17: „die Fähigkeit dazu trägt der Skill `konzept-segmentierung`". Abschnitt 20: „Letzteres ist Gegenstand des Skills `konsistenzpruefung`." `rules-startup.de.md`: „wie `git-workbench.json` und `git-branch-model.json`". Drei Zieltexte, vier Nachbar-Skills. Kapitel 1.7.2 nennt `konzept-segmentierung` ebenfalls.

**Warum das ein Problem ist.** Wenn die Vorgabe gilt, verstoßen drei Zieltexte dagegen, und niemand hat es gemeldet, weil die Vorgabe nicht in der Doku steht, gegen die geprüft wird. Wenn sie nicht gilt, ist 3.9.2 falsch begründet. In beiden Fällen fehlt der Doku eine Festlegung, die sie anwendet.

**Was zu tun wäre.** Die Vorgabe in Kapitel 2 aufnehmen — ein Satz, mit Verweis auf ihre Quelle im Repository, falls es eine gibt — und die drei Stellen bereinigen. Bei `konzept-segmentierung` und `konsistenzpruefung` genügt es, die Fähigkeit zu benennen statt den Skill („bleibt ein eigener Projektschritt auf ausdrücklichen Auftrag" trägt den Satz auch ohne den Namen). Bei den beiden JSON-Dateien ist der Vergleich entbehrlich; die Begründung „Projektwerte gehören ins Projekt" steht daneben und reicht.

---

## Begründungen, die nicht mehr tragen oder nie aufgegriffen wurden

### L-06 — „Die Tabelle kostet nichts" ist gemessen falsch

**Worum es geht.** Jeder Abschnitt einer Doku trägt eine Rolle, die sagt, worum es in ihm geht; der Skill ordnet der Rolle eine Funktion zu. Die Namen der Rollen folgen arc42, dem Gliederungsschema für Architekturdokumentation. Am 20. September wurde entschieden (Q-08), alle zwölf arc42-Rollen und fünf weitere anzubieten.

**Was festgelegt ist.** Kapitel 1.3.3: „Der Skill bietet alle zwölf arc42-Rollen an und die fünf der Projektarbeit — **die Tabelle kostet nichts**, und ein Projekt benutzt, was es braucht."

**Was tatsächlich dasteht.** Am 4. Oktober gemessen: Die vollständige Tabelle mit drei Spalten kostet rund 725 Token, die zweispaltige Fassung mit Rolle und Funktion rund 161 — und sie wird bei jedem Skillstart geladen, weil die Regeln an den Funktionen hängen. Der Neuschnitt hat deshalb nur die zweispaltige Fassung in den Regelteil übernommen; wo die dritte Spalte hingehört, steht als offener Rest im Fahrplan.

**Warum das ein Problem ist.** Die Entscheidung Q-08 ist vermutlich richtig — siebzehn Rollen sind nicht zu viel, und ein Projekt benutzt tatsächlich nur einige. Aber ihre Begründung ist durch eine Messung widerlegt, und eine Entscheidung mit widerlegter Begründung ist beim nächsten Review wieder offen. Das ist der Zustand, den der Vorläufer für abgelehnte Befunde beschreibt: „ohne festgehaltene Begründung meldet ihn der nächste Review wieder, und zwar zu Recht."

**Was zu tun wäre.** Die Begründung ersetzen, nicht die Entscheidung. Was trägt: Der Entwickler muss eine Rolle an seinen Überschriften erkennen können, und ein unvollständiger Rollensatz zwingt ihn, fremde Inhalte unter eine passende Rolle zu biegen; die Kosten der Tabelle sind bekannt und werden durch die Trennung in eine immer geladene Zuordnung (161 Token) und eine nur bei Bedarf geladene Beschreibung (564 Token) begrenzt. Und den offenen Rest aus dem Fahrplan entscheiden: Die Beschreibungsspalte wird gebraucht, wenn die Instanz eine Rolle vorschlägt — bei der Erstanlage (`rules-startup.de.md`) und im Plan (`rules-planning.de.md`); da der Vorschlag im Plan der häufigere Fall ist, spricht mehr für die Planungsdatei.

### L-13 — Der Trigger wiederholt die Schwäche, die der Vorläufer selbst benannt hat

**Worum es geht.** Der Skill wird nicht in jeder Sitzung geladen, sondern durch einen Satz in der `CLAUDE.md`, der an eine Handlung gebunden ist. Das ist die Antwort auf die gemessene Eigenschaft aus 1.2: Haltungsbeschreibende Anweisungen feuern nicht zuverlässig, handlungsgebundene feuern.

**Was festgelegt ist.** Kapitel 3.11.2: „Der Wortlaut ist bewusst an eine Ankerhandlung gebunden (‚bevor du zum ersten Mal …'), nicht als Haltungsbeschreibung formuliert." Anhang A.13 hält über den Vorläufer fest: „mit der Beobachtung, dass der damalige Trigger eigenschaftsförmig war (‚sobald eine Software-Änderung über eine lokal begrenzte Korrektur hinausgeht') und eine Abwahl damit realistisch."

**Was tatsächlich dasteht.** `CLAUDE-snippet.de.md`: „Bevor du in einer Sitzung zum ersten Mal einen Lösungsweg vorschlägst oder zum ersten Mal eine Datei änderst, halte kurz inne und prüfe: Geht die besprochene Software-Änderung über eine einzelne, lokal begrenzte Korrektur hinaus — sind mehrere Stellen betroffen, müssen mehrere Vorgehensweisen gegeneinander abgewogen werden, oder müssen erst Zusammenhänge im bestehenden Code erarbeitet werden, bevor klar ist, was zu ändern ist? Wenn ja, konsultiere sofort den Skill." Das ist, bis auf den Skillnamen, der Wortlaut des Vorläufers aus A.11. Der Anker — „bevor du zum ersten Mal" — ist handlungsgebunden. Die Bedingung dahinter — „geht über eine lokal begrenzte Korrektur hinaus" — ist genau das Urteil, das A.13 als Schwäche benennt.

**Warum das ein Problem ist.** Der Vorläufer wurde nie installiert und nie unter seinem Trigger erprobt (A.1). Die Beobachtung in A.13 war eine Vermutung, keine Messung. Aber sie ist die eigene Beobachtung dieses Vorhabens, sie steht in seinem Anhang, und weder Kapitel 1 noch Kapitel 2 noch Kapitel 3.11 greift sie auf. Wenn die Bedingung nicht zuverlässig feuert, lädt der Skill nicht — und alles, was er leisten soll, findet nicht statt, ohne dass jemand es merkt. Das Fehlbild Intensität wäre dann nicht behoben, sondern durch sein Gegenteil ersetzt.

**Was zu tun wäre.** Die Frage ist, ob die Bedingung überhaupt nötig ist. Seit Q-15 fragt der Skill beim Laden nichts, und seit dem 2. Oktober prüft er selbst, ob ein Vorhaben Software ist, und endet sonst still. Ein Skill, der beim Laden nichts kostet außer der Wurzel, braucht keine Vorbedingung im Trigger; der Trigger kann lauten „Bevor du zum ersten Mal einen Lösungsweg vorschlägst oder eine Datei änderst, konsultiere den Skill" — und der Skill entscheidet selbst, ob er etwas zu tun hat. Das verlagert das Urteil von der Anweisung, wo es nicht zuverlässig fällt, in das Skript, wo es mechanisch fällt. Es kostet die Wurzel in jeder Sitzung, in der eine Datei geändert wird — rund tausend Token heute, weniger nach dem dritten Teil von Fahrplanschritt 10. Ob das zu viel ist, lässt sich in der Probe messen; die Alternative — ein Trigger, der nicht feuert — lässt sich dort nicht messen, weil nichts stattfindet.

---

## Offen und vertagt

Zwei Punkte sind keine Lücken in der Herleitung, aber die Kette macht sichtbar, was an ihnen hängt.

### L-09 — Ein Drittel der Konfiguration dient einer unbewiesenen Leistung

**Worum es geht.** Die Auswirkungsrechnung (Leistung 4) findet Kandidaten über ein Geflecht aus Markern. Kapitel 1.7.4 sagt, woran sie sich rechtfertigt: an den Kandidaten, die eine Textsuche über die Suchschlüssel **nicht** gefunden hätte. „Stellt die Probe fest, dass es keine solchen Funde gibt, ist die Rechnung überflüssig und der Skill behält nur die Erwähnungssuche. Diese eine Zahl entscheidet über den Bestand des ganzen Teils."

**Was daran hängt.** Drei der elf Skill-Parameter (`impact_model`, `impact_cutoff`, `impact_lib`), ein eigenes Modul `impact.py`, drei Kostenfunktionen, die alle gebaut werden, eine optionale Bibliothek mit eigener Frage an den Entwickler, ein Rechenmodell in Anhang B, der Abschnitt 3.6.5, Szene 8 in Kapitel 1.6, und ein Gutteil der Probe. Zusammen ist das die am weitesten ausgearbeitete Leistung des Skills — und die einzige, deren Existenz die Doku selbst unter Vorbehalt stellt.

**Warum das zählt.** Nicht, weil die Ausarbeitung falsch wäre; jede dieser Festlegungen folgt aus 1.7.4. Sondern weil die Reihenfolge des Fahrplans — Stufe 1 des Skripts, Stufe 2 mit der gewichteten Rechnung, dann Probe — bedeutet, dass die Rechnung vollständig gebaut ist, bevor die eine Zahl gemessen wird, die über sie entscheidet.

**Was zu tun wäre.** Die Messung vorziehen. Die Frage „findet das Geflecht Kandidaten, die die Suchschlüssel verfehlen?" braucht keine drei Kostenfunktionen; sie braucht eine Fixture-Doku mit einem `relate`-Text und die einfachste Variante (`hops`, Tiefe 1). Das ist ein Teil von Stufe 1 und ein Nachmittag Probe. Fällt die Antwort nein aus, entfällt Stufe 2 zur Hälfte, und die Parameterdatei schrumpft um ein Drittel. Fällt sie ja aus, hat Stufe 2 ihre Berechtigung, bevor sie gebaut wird.

### L-11 — Die Ausgabeform ist offen, und beide Formen werden gebaut

**Worum es geht.** Jede Ausgabe des Skripts ist eine Aussage mit Kopfzeile und Einzelzeilen (Vorgabe 2.5). Ob sie als Zeile mit Trennzeichen oder als JSON erscheint, ist seit dem 25. September offen; Kapitel 3.6.3 spezifiziert die Zeilenform vollständig und führt `--json` daneben, weil die Hooks es brauchen.

**Was daran hängt.** Laut Fahrplan blockiert die Frage Schritt 4. Tatsächlich blockiert sie ihn nicht: Beide Formen werden ohnehin gebaut, und die Frage ist nur, welche ohne Argument erscheint. Das lässt sich nach dem Bauen messen — Lesekosten der Instanz je Form — und braucht vorher keine Entscheidung.

**Was zu tun wäre.** Die Zeile in der Tabelle der offenen Entscheidungen im Fahrplan ändern: Sie blockiert nicht Schritt 4, sondern wird in Schritt 8 gemessen. Damit ist eine der drei offenen Entscheidungen keine Blockade mehr.

---

## Die Befunde gesammelt

| | Befund | Art |
|---|---|---|
| L-15 | Die Abgrenzung von Kapitel 1 und 2 ist nicht formuliert; fünf Festlegungen stehen in beiden | Lücke in der Doku; Doppelung |
| L-02 | `mode` bedeutet Lage und Abwahl zugleich | Widerspruch zu 2.1 |
| L-04 | Wer Marker in die Prosa schreibt: drei Antworten | Widerspruch |
| L-10 | H3 eingeplant und unentschieden zugleich | Widerspruch Fahrplan / Probe-Tor |
| L-12 | 1.8 und 2.9 sagen noch, der Skillstart frage | veraltet gegen Q-15 |
| L-14 | 1.7.1: „kein Formular" neben einer Fragenliste | Widerspruch im Abschnitt |
| L-03 | Lageabhängiger Abbruchwert versprochen, kein Weg zum Skript | Vorgabe ohne Mechanismus |
| L-05 | `[register: pfad]` weder Adresse nach 2.3 noch Feld nach 2.10 | Mechanismus ohne Vorgabe |
| L-08 | Suchschlüssel: Instanz wählt, Skript gibt aus — keine Übergabe | Mechanismus ohne Mitte |
| L-01 | Die Gründungsleistung hat keine Vorgabe, nur drei Sätze und eine Messgröße | Leistung ohne Vorgabe |
| L-07 | Planungsort-Regel aus lokalem Anweisungskonflikt, nicht aus dem Ziel | Herleitung trägt nicht |
| L-16 | Vorgabe gegen Skill-Querverweise wird angewendet, steht aber nirgends | Vorgabe fehlt |
| L-06 | „Tabelle kostet nichts" als Begründung für siebzehn Rollen | Begründung widerlegt |
| L-13 | Trigger wiederholt die in A.13 benannte Schwäche des Vorläufers | eigene Beobachtung nicht aufgegriffen |
| L-09 | Ein Drittel der Konfiguration hängt an einer unbewiesenen Leistung | Risikokonzentration |
| L-11 | Ausgabeform offen, beide gebaut | vertagt, blockiert nicht |

---

## Anhang — Fehlumsetzungen

Hier steht, was in Kapitel 3 oder in den Zieltexten steht und von keiner Vorgabe her erreicht wird. Das sind keine Fehler im Sinne von falsch; es sind Inhalte, deren Quelle die Umsetzung selbst ist. Solange ihnen keine Vorgabe vorausgeht, sind sie aus Sicht der Aufgabe nicht zu halten — entweder bekommen sie eine, oder sie entfallen. Jeder Eintrag erklärt, was dort steht, warum es keine Vorgabe hat, und was daraus folgen könnte.

**F-01 — Die Wurzel lädt `standard.de.md` mit einer Bedingung, die 2.15 als unzulässig vorführt.** `SKILL.de.md`, Schritt 5: „`standard.de.md`, wenn eine Frage zur Methodik ansteht, die nicht die Härte- oder Registerregeln selbst betrifft." Vorgabe 2.15 sagt: „Ein Zweig lohnt sich nur, wenn seine Ladebedingung an einem benennbaren Anlass hängt, nicht an einer Einschätzung. Eine weiche Bedingung — ‚wenn eine Frage zur Methodik ansteht' — führt dazu, dass im Zweifel geladen wird und die Ersparnis entfällt, oder dass nicht geladen wird und eine Regel fehlt." Die Vorgabe zitiert wörtlich die Formulierung, die in der Wurzel steht. Was zu tun wäre: einen Anlass finden. `standard.de.md` trägt die Methodik des Vorläufers — Phasen, Segmente, Arbeitsschleife. Der Anlass, an dem sie gebraucht wird, ist die Erstanlage (Wahl der Gliederungsform) und das Zusammenspiel mit dem Fahrplan; beides sind benennbare Handlungen. Oder die Datei wird gar nicht nachgeladen, sondern ist Teil der Installation des Entwicklers, der den Standard des Vorläufers führt — dann ist sie kein Zweig des Skills.

**F-02 — Die Auswirkungsliste mit drei Bewertungen hat keine Quelle.** `rules-core.de.md`, Abschnitt 6: „Auswirkungsliste (bei `open` in `design`): je berührter Festlegung ihr Grund und eine von drei Bewertungen — Grund fällt mit der Idee · Grund trägt weiter · Grund nicht dokumentiert." Kapitel 1.7.5 kennt die Auswirkungsliste nicht; Kapitel 1.3.1 nennt sie einmal im Vorbeigehen („in der Auswirkungsliste der aktuellen Idee"). Die drei Bewertungen stehen nirgends in Kapitel 1 oder 2. Sie sind plausibel — sie strukturieren, was mit einer geparkten Festlegung geschieht —, aber sie sind eine Erfindung der Umsetzung. Wird L-01 behoben und bekommt die Lage `design` eine Vorgabe, gehören die drei Bewertungen dorthin oder entfallen.

**F-03 — „Fünfzehn Festlegungen" ist eine Zahl aus einer Erzählung.** `rules-core.de.md`, Abschnitt 7: „Nennt ein Plan mehr als etwa fünfzehn Festlegungen, ist der Schritt zu groß — zerlegen." Die Zahl stammt aus Szene 8 in Kapitel 1.6: „Der Abschnitt wird lang — über fünfzehn Einträge —, und das ist selbst die Aussage." Eine Szene ist eine Erzählung, keine Vorgabe; die Zahl dort illustriert, sie legt nicht fest. Der Gedanke dahinter — die Länge des Planabschnitts ist ein Maß für die Schrittgröße — ist richtig und folgt aus der Prosa-Code-Grenze des Vorläufers (A.4: „Ließ sich eine Änderung ohne Kontrollfluss nicht beschreiben, galt der Schritt als zu groß"). Was zu tun wäre: entweder die Regel ohne Zahl („wird der Abschnitt länger als eine Bildschirmseite") oder die Zahl als Vorgabe mit Begründung — dann aber nicht aus der Szene abgeschrieben, sondern begründet.

**F-04 — Ein siebter Anker, den Kapitel 1.8 nicht kennt.** `rules-core.de.md`, Abschnitt 10, letzte Zeile der Ankertabelle: „Neue Einheit wird gegen eine Festlegung gebaut — Härte lesen; nur bei `open` oder vorhandener Reibung ein Satz, sonst Schweigen." Kapitel 1.8 nennt sechs Anker: Skillstart, Bereich öffnen, Lage bestimmen, Plan schreiben, Ausführen, Hooks. „Neue Einheit bauen" ist keiner davon; es ist ein Fall von „Ausführen". Die Zeile ist vermutlich eine Vorsichtsregel, die während der Ausarbeitung dazukam. Entweder gehört sie als Unterfall zu „Ausführen", oder sie entfällt — als eigener Anker ist sie nicht hergeleitet.

**F-05 — Drei Antwortformen auf eine Frage.** `rules-core.de.md`, Abschnitt 4, Regel 3: „Drei Antwortformen: Antwort → Attribute werden `confirmed`. ‚Später' → `pending` bleibt […]. ‚Lass uns das durchgehen' → Gespräch über so viele Turns wie nötig." Vorgabe 2.13 regelt, wie gefragt wird: mit Anlass und Wortlaut, ohne Skill-Vokabular. Was mit der Antwort geschieht, regelt niemand. Die drei Formen sind sinnvoll — sie decken Antwort, Vertagung und Vertiefung ab —, aber sie sind ein Protokoll ohne Vorgabe. Milder Fall; bei einer Vorgabe zur Frage (L-01, 2.13) ließe sich die Antwort mit einem Satz aufnehmen.

**F-06 — Ein Vorgabentext behauptet etwas über die Umsetzung, das sonst nirgends gilt.** Vorgabe 2.6, Ergänzung vom 4. Oktober: „Die Markerformen schreibt zwar `apply` in die Prosa." Siehe L-04. Der Satz ist vom Verfasser dieses Reviews am Vortag geschrieben worden, als Begründung dafür, dass die Markerform im Regelteil bleiben darf. Die Begründung trägt ohne ihn; er ist zu streichen.

**F-07 — Zieltexte nennen Nachbar-Skills.** Siehe L-16. Drei Stellen: `rules-core.de.md` Abschnitte 17 und 20, `rules-startup.de.md` Absatz nach der Parametertabelle.

**F-08 — `plan-section` kennt IDs, die es noch nicht gibt.** Kapitel 3.6.4: „darunter der Suchschlüsselblock für die neu angelegten IDs". Zum Planzeitpunkt hat eine neue Festlegung keine ID; B-03 hat den Block deshalb mit dem Wortlaut als Adresse angelegt, und Szene 2 in Kapitel 1.6 zeigt ihn so. Der Satz in 3.6.4 ist am 3. Oktober vom Verfasser dieses Reviews geschrieben worden und widerspricht dem, was er am selben Tag in Kapitel 1.6 eingebaut hat. Zu korrigieren auf „für die Festlegungen, die der Plan neu anlegt, adressiert über ihren Wortlaut". Siehe L-08.

**F-09 — `notes` läuft mit `open`, aber `open` weiß nichts davon.** Kapitel 3.6.4 bei `notes`: „Wann es läuft: beim Öffnen eines Bereichs zusammen mit dem Abgleich, der dort ohnehin stattfindet." Die Spezifikation von `open` nennt in ihrer Ausgabe `ITEM` je Festlegung und `FINDING` je Abweichung — keine Notizen. Entweder gibt `open` die Notizen des Bereichs mit aus (dann gehört das in seine Zeile der Tabelle), oder die Instanz ruft `notes` getrennt auf (dann ist es nicht „zusammen", und Vorgabe 2.7 fragt, warum zwei Aufrufe). Das ist eine Unstimmigkeit innerhalb von Kapitel 3; sie zeigt, dass die Kommandotabelle und die Prosa darunter nicht gegeneinander geprüft wurden.

**F-10 — Die Projektart-Listen stehen im Regelteil, sollen aber von einem Kommando gelesen werden.** `rules-startup.de.md`, „Erkennung der Projektart": Listen von Manifestdateien und Quelldateiendungen, mit der Begründung in Kapitel 3.5.5: „Die Listen altern — deshalb stehen sie hier im Regelteil und nicht als Konstante im Skript: So lassen sie sich erweitern, ohne Code anzufassen." Fahrplanschritt 10, dritter Teil, macht die Prüfung zu einem Kommando. Dann liest das Kommando die Listen — und nach Vorgabe 2.6 ist das, was ein Kommando auswertet, Spezifikation, nicht Regeltext. Die Begründung „ohne Code anzufassen" und die Vorgabe 2.6 ziehen in verschiedene Richtungen. Der Ausweg, der beiden gerecht wird: Die Listen werden ein Skill-Parameter mit eingebautem Standard, wie `lint_signals` es schon ist — erweiterbar je Projekt, gelesen vom Skript, nicht im Regeltext.

**F-11 — Kapitel 3.9 hat nach eigener Aussage keine Quelle in Kapitel 1.** Kapitel 3.9, Kopf: „Was hier steht, hat keine Quelle in Kapitel 1 und beschreibt überwiegend Handlungen am System des Entwicklers statt einer Einheit des Skills." Das Kapitel benennt das Problem selbst und lässt die Entscheidung bis Fahrplanschritt 9 offen. Was zur Entwicklung gehört — dass Abschnitt 2 der globalen Anweisungsdatei die Quelle von `standard.de.md` ist —, ist ein Satz in Kapitel 1.11 und steht dort schon. Der Rest ist Installationsanleitung für einen bestimmten Entwickler; er gehört in dessen Notizen oder in die README des Skills, nicht in die Doku des Vorhabens.

**F-12 — Kapitelnummern dieser Doku im Zieltext.** `rules-startup.de.md`, „Die Doku wächst": „Wird eine Festlegung aus Kapitel 1 oder 2 durch eine aktuelle Anwender- oder Programmdokumentation redundant". Gemeint sind die Kapitel dieser Doku — Zusammenhänge und Vorgaben. In der Doku eines beliebigen Projekts gibt es diese Nummern nicht, und Vorgabe 2.3 verbietet, eine Wirkung an eine Kapitelnummer zu binden. Bekannt als Befund B-09 seit dem 25. September, offen. Was zu tun wäre, steht dort: die drei Fälle über Rollen ausdrücken — Zusammenhänge sind die Rollen mit Funktion `relate`, Vorgaben sind `crosscutting` und `constraints`, ausgenommen bleibt `building-blocks`.

**F-13 — `mode` mit `execute`/`design` im Regelteil.** `rules-core.de.md`, Abschnitt 2, Zeile `mode`. Siehe L-02.

Dreizehn Einträge. Sechs davon — F-01, F-06, F-08, F-10, F-12, F-13 — verstoßen gegen eine Vorgabe, die es gibt. Zwei davon, F-06 und F-08, stammen vom Verfasser dieses Reviews aus den beiden Tagen davor. Die übrigen sieben sind Inhalte ohne Vorgabe darüber: Ausarbeitungen, die plausibel sind und vielleicht richtig, deren Herkunft aber die Umsetzung selbst ist.

---

## Was dieses Dokument nicht tut

Es trifft keine Entscheidung. Wo es Wege nennt, nennt es ihre Kosten, nicht ihre Wahl. Es bewertet nicht, ob das Vorhaben in seiner Größe richtig ist; die Zahlen dazu — rund 10 000 Token Zieltext, rund 70 000 Token Entwicklungsdoku, 1 278 Token in dem Abschnitt der globalen Anweisungsdatei, den der Skill ersetzt — stehen in der Sitzung vom 4. Oktober und sind hier nur genannt, damit sie nicht verloren gehen.
