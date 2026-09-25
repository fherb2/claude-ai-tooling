# 1 Zusammenhänge

Dieses Dokument ist die Implementierungsdoku des Vorhabens `software-design-doc` — eines Skills für die projektbegleitende Softwaredokumentation: Ziel, Randbedingungen, allgemeine und spezielle Festlegungen bis zur Detailbeschreibung der Ausführung. Es folgt dem Schema des Vorläufers (drei Segmente, Fahrplan, Status; Anhang A) und wendet die neuen Ideen des Vorhabens — Marker, Register, Rollen — auf sich selbst **nicht** an; das geschieht frühestens nach der Probe (Kapitel 3.8).

Die Segmente sind: dieses Kapitel 1 mit den Zusammenhängen, Kapitel 2 mit den projektweiten Vorgaben, Kapitel 3 mit den Einheiten. Daneben `work-plan.md` (Fahrplan) und `status.md`. Zwei Anhänge: **Anhang A** archiviert den Vorläufer — das Dokumentationsschema, auf dessen Erfahrungen dieses Vorhaben aufbaut und auf das die Kapitel mehrfach verweisen; **Anhang B** trägt den Verlauf der Recherchen und das Rechenmodell.

Noch nicht entschiedene Punkte stehen dort, wo die Entscheidung hingehört, und sind in den laufenden Text eingearbeitet: Der Gedankengang führt bis zu der Stelle, an der es mehrere Wege gibt, nennt sie mit ihren Kosten und sagt, dass die Wahl aussteht. Eine offene Frage in Kapitel 3 wäre fast immer ein Zeichen dafür, dass etwas Funktionales oder eine Vorgabe noch nicht entschieden ist — sie gehört dann nach Kapitel 1 oder 2 (Festlegung des Entwicklers vom 2026-09-25). Welche Punkte offen sind und welchen Fahrplanschritt sie blockieren, sagt `work-plan.md`. Was nicht als offen gekennzeichnet ist, gilt als geplant.

> Geprüft: offen

## 1.1 Name des Skills

Der Skill hieß `software-dev-doc-fh`. Das Kürzel `-fh` bezeichnete die Arbeitsweise eines bestimmten Entwicklers; mit der Verallgemeinerung auf Rollen, Register und Härteregeln ist der Skill für jeden mit einem ähnlichen Ansatz nutzbar, und das Kürzel entfällt. Der neue Name ist `software-design-doc`: Was der Skill pflegt, ist im Fachjargon ein Design Doc — Kontext und Ziel, Randbedingungen, Entscheidungen mit Alternativen, Detail bis zur Ausführung. Das Präfix `software-` vermeidet die Verwechslung mit Produkt- oder Oberflächendesign, die `design-doc` allein hätte. Erwogen wurden außerdem `solution-design-doc` und `living-design-doc` (das die parallele Pflege zum Code betont, aber mit dem etablierten Begriff „Living Documentation" für generierte Doku kollidiert). Die Entscheidung ist bis zur Installation ohne Kosten umkehrbar; Skill-Parameterdatei und Skript folgen dem Namen (Kapitel 3.5 und 3.6).

Der Skill ist auf Softwareentwicklung zugeschnitten, aber nicht durchgehend: Softwarespezifisch sind der Regeltext des Vorläufers als Regelteil (Phasen, Segmente, Arbeitsschleife; Anhang A), die Signalwörter des Lints und die Suche nach Erwähnungen im Code. Der Kern — Festlegungen mit Härte, Register, Rollen, geplante Schritte — kennt keinen Code und könnte andere Entwicklungsaufgaben ebenso tragen. **Entschieden am 2026-09-18:** Beim Zusammensetzen des Skills wird geprüft, ob die softwarespezifischen Teile in einem eigenen Regelteil isoliert sind. Sind sie es, wird der Skill vor der Installation in `solution-design-doc` umbenannt; die Prüfung kostet nichts, solange nicht installiert ist (Fahrplanschritt 9).

> Geprüft: Ok

## 1.2 Ausgangslage: zwei Fehlbilder

Der Vorläufer beschreibt die entwicklungsbegleitende Doku als dreigeteiltes Dokument mit Fahrplan und Status und eine Arbeitsschleife, in der Code und Doku im Wechsel entstehen (vollständig in Anhang A). Für größere Projekte hat sich das bewährt. In der Praxis zeigten sich zwei Fehlbilder, die beide auf denselben Ursachen beruhen.

**Fehlbild Intensität.** Bei kleinen Vorhaben, bei kurzen Eingriffen in ein laufendes Projekt und bei Projekten, deren Doku anders aufgebaut ist, verweist die Instanz beharrlich auf Segmente, Fahrplan und Statusdatei und verlangt Struktur, die nichts zu halten hat. Ursache: Der Standard war als Abschnitt der globalen Anweisungsdatei in jeder Sitzung geladen und kannte keine Frage, ob und in welcher Ausbaustufe ein Projekt ihn führt.

**Fehlbild Gesetz.** Sobald eine Doku steht, liest die Instanz jede Festlegung darin als bindend. Will der Entwickler einen Bereich neu denken, stößt jede Idee an eine bestehende Festlegung und wird verworfen, statt zu Ende gedacht zu werden; mit wachsender Doku wird die Instanz unkreativ. Ursache: Der Standard kannte nur eine Lesart der Doku — Doku als Vorgabe — und keine Regel dafür, wann eine Festlegung bindet und wann sie zur Disposition steht.

Hinter beiden liegt eine Eigenschaft der Instanz, die in diesem Repository gemessen wurde: Anweisungen, die eine Haltung beschreiben („behalte im Blick, ob …"), feuern nicht zuverlässig; Anweisungen, die an eine Handlung gebunden sind („bevor du zum ersten Mal …"), feuern. Und eine Instanz wägt mehrere Dimensionen nicht zuverlässig gegeneinander ab — sie läuft gegen Extrema. Jedes Verfahren, das von ihr Abwägung verlangt, scheitert an dieser Stelle.

> Geprüft: Ok

## 1.3 Leitidee

Drei Sätze tragen das Vorhaben. Die Instanz wägt nicht, sie schlägt nach. Alles, was sie zum Nachschlagen braucht, steht außerhalb der Prosa des Entwicklers. Und der Entwickler schreibt seine Doku so, wie sie für Menschen am nützlichsten ist — der Skill fügt ihr Adressen hinzu, keine Logik.

### 1.3.1 Nachschlagen statt abwägen

Ob eine Festlegung in der aktuellen Arbeit bindet oder zur Disposition steht, ergibt sich aus wenigen Feldern, die zu ihr gehören — Art (von außen gegeben oder von uns gewählt), Grund, Status, Ereigniszeilen —, und aus den Umbauzielen der geplanten Schritte des Projekts. Eine geordnete Liste einzelner Prüfungen macht daraus die **Härte** der Festlegung; aus Härte und **Lage** der Sitzung (Beschlossenes umsetzen oder etwas neu denken) folgt das Verhalten — sechs Zellen, eine Handlung je Zelle (Kapitel 3.1). Nichts davon wird kombiniert oder gewichtet; die Instanz führt Prüfungen aus, sie bildet kein Urteil.

**Was bewusst nicht einfließt.** Vier Größen, die man erwarten könnte, bleiben draußen, und jede aus einem Grund. Das **Alter** einer Entscheidung: Zeitregeln sind fragil, weil Projekte verschieden schnell laufen; eine Festlegung gilt als frisch, bis sich zum ersten Mal Arbeit an ihr gerieben hat — das ist ein Ereignis und kein Datum. Die **Umbaukosten**: Sie entscheiden nicht, ob ein Gedanke verfolgt wird, sondern sie sind eine Zahl, die der Entwickler zur Entscheidung braucht; sie stehen im geparkten Satz und nicht in der Ableitung. Jede Form von **Gewichtung**: Die Prüfungen werden gelesen, nicht verrechnet — genau daran scheitert eine Instanz (1.2). Und **neues Wissen, das einen Grund hinfällig macht**: Dass eine Annahme von gestern heute nicht mehr trägt, ist beim Vorbeigehen nicht erkennbar; das braucht einen eigenen Durchgang durch die Doku und gehört deshalb in die Konsistenzprüfung, nicht in die laufende Arbeit.

Die Felder **gehören** zur Festlegung, aber sie **stehen** nicht bei ihr im Text. Das ist der Punkt, an dem die folgenden Abschnitte ansetzen.

> Geprüft: Ok

### 1.3.2 Der Mittelweg: normierte Felder, aber getrennt von der Prosa

Stünden Art, Grund, Status und Ereignisse als Metainformation im Text, wäre die Doku unlesbar und der Entwickler in ein formales Konzept gezwungen, das ihn einschränkt und mit Zusatzaufgaben belastet — inakzeptabel. Stünde umgekehrt gar nichts Maschinenlesbares im Text, müsste die Instanz jede Aussage interpretieren, und das Fehlbild Gesetz wäre zurück. Der Mittelweg: **Die Felder sind normiert, aber sie liegen in einem Register neben der Doku; die Prosa trägt je Festlegung nur einen kurzen Marker — eine Adresse, nichts sonst** (Kapitel 3.2). So bleibt der rote Faden eines Absatzes für den Leser erhalten, ein Absatz mit drei Festlegungen bleibt ein Absatz, und `grep` findet trotzdem alles zu einer Festlegung.

> Geprüft: Ok

### 1.3.3 Abschnitte haben eine Rolle — im Dokument steht ihr Name, im Skill ihre Wirkung

**Das Problem: Der Skill muss wissen, in welcher Art Text er gerade steht.** Eine Doku besteht nicht nur aus Festlegungen, und nicht jede Stelle verlangt vom Skill dasselbe. Sechs Arten von Text kommen in einer entwicklungsbegleitenden Doku vor, und in jeder verhält sich der Skill anders:

- **Text, der eine Einheit beschreibt** — ein Modul, eine Klasse, einen Prozess. Hier entstehen die Festlegungen; hier gehören die Definitionsmarker hin (1.3.2).
- **Text, der Festlegungen aus verschiedenen Teilen zueinander in Beziehung setzt** — eine Übersicht, ein Ablauf, die Lösungsstrategie. Hier steht der rote Faden der Doku, und hier lernt der Skill, was womit zusammenhängt: Wird eine Festlegung geändert, findet er über solche Texte die anderen, die stillschweigend von ihr abhängen (1.7.4). Dafür müssen die herangezogenen Festlegungen hier als Zitat markiert sein — anderswo ist das freiwillig.
- **Text mit Vorgaben, die im ganzen Projekt gelten.** Festlegungen hier wiegen schwerer: Sie zu öffnen verlangt mehr Reibung, und eine Kollision mit ihnen betrifft nicht ein Kapitel, sondern alles.
- **Text, in dem nichts bindet** — Findungstext, Risikoliste, Glossar, Anhang, erledigte Schritte. Sähe der Skill hier Festlegungen, wäre das Fehlbild Gesetz (1.2) an genau dieser Stelle zurück; deshalb übergehen ihn Lint und Auswirkungsrechnung.
- **Text mit geplanten Schritten.** Hier liest der Skill die Umbauziele, die Festlegungen für die Dauer eines Umbaus öffnen (1.3.1).
- **Das Register selbst**, das seiner eigenen Grammatik folgt (Kapitel 3.2).

Diese sechs Verhaltensweisen heißen im Skill **Funktionen**, und sie tragen dort englische Namen — der Entwickler wird ihnen nie begegnen, sie stehen hier nur, damit Kapitel 3 sie benutzen kann (Namen entschieden am 2026-09-20):

| Funktion     | Die Textart                                                  | Was der Skill dort tut                                                                                                           |
| ------------ | ------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| `define`     | eine Einheit wird beschrieben                                | Definitionsmarker sind Pflicht; Standard für alles, was keine Rolle trägt                                                      |
| `relate`     | Festlegungen verschiedener Teile werden in Beziehung gesetzt | Zitatmarker sind Pflicht; aus dem gemeinsamen Zitieren entstehen die Kanten der Auswirkungsrechnung (1.7.4)                      |
| `global`     | Vorgaben für das ganze Projekt                              | die Schwelle, ab der Reibung eine Festlegung öffnet, liegt eine Stufe höher; Kollisionen werden als projektweit gekennzeichnet |
| `nonbinding` | nichts bindet                                                | Lint und Auswirkungsrechnung übergehen den Text                                                                                 |
| `plan`       | geplante Schritte                                            | Umbauziele werden gelesen (Kapitel 3.4)                                                                                          |
| `register`   | das Register                                                 | die Registergrammatik gilt (Kapitel 3.2)                                                                                         |

**Woran der Skill die Textart erkennt: an einem Etikett.** Er darf sie nicht an Kapitelnummern oder Überschriften erkennen — Nummern ändern sich beim Umsortieren, Überschriften sind frei formuliert und in jeder Sprache. Deshalb trägt ein Abschnitt ein kurzes Etikett, seine **Rolle**. Ein Abschnitt ist dabei der Text unter einer Überschrift bis zur nächsten Überschrift gleicher oder höherer Ordnung. Auch die Rolle ist keine Formalie für den Entwickler: Die Instanz erkennt aus dem Inhalt, welche Rolle ein Abschnitt hat, schlägt sie im Plan vor und schreibt sie mit dessen Ausführung, wie die Marker; der Entwickler bestätigt oder korrigiert in Prosa.

**Warum das Etikett den Inhalt nennt und nicht das Verhalten des Skills.** Man könnte die sechs Funktionsnamen selbst als Etikett nehmen. Aber der Entwickler muss das Etikett bestätigen und liest es an seinen eigenen Überschriften — und `relate` sagt ihm nichts über sein Kapitel, während „Laufzeitsicht" es trifft. Deshalb benennt die Rolle, **worum es in einem Abschnitt geht**, und der Skill ordnet jeder Rolle intern ihre Funktion zu. Die Namen folgen [arc42](https://arc42.org), dem etablierten Gliederungsschema für Architekturdokumentation; es ist die einzige der geprüften Quellen mit einem festen, benannten Abschnittssatz in beiden Sprachen und ohne Lizenzhürde (Anhang B, Abschnitt B.3). Dazu kommen fünf Rollen der Projektarbeit, die arc42 nicht kennt, weil es Architektur beschreibt und nicht Projektarbeit. **Entschieden am 2026-09-20:** Der Skill bietet alle zwölf arc42-Rollen an und die fünf der Projektarbeit — die Tabelle kostet nichts, und ein Projekt benutzt, was es braucht.


| Rolle             | Ein Abschnitt dieser Rolle beschreibt                                                       | Funktion            |
| ----------------- | ------------------------------------------------------------------------------------------- | ------------------- |
| `goals`           | Aufgabe und Ziele: was das Vorhaben erreichen soll und woran sich das misst                 | `define`, `relate`  |
| `constraints`     | Randbedingungen, die von außen gesetzt sind: Technik, Organisation, Normen                 | `define`, `global`  |
| `context`         | die Abgrenzung: Nachbarsysteme, Schnittstellen nach außen, Benutzer                        | `relate`            |
| `strategy`        | die Lösungsstrategie: die Grundsatzentscheidungen, die das Ganze prägen                   | `relate`            |
| `building-blocks` | eine Einheit des Systems — Modul, Klasse, Prozess — mit ihren Festlegungen                | `define` (Standard) |
| `runtime`         | Abläufe: wie die Einheiten im Betrieb zusammenspielen                                      | `relate`            |
| `deployment`      | die Verteilung: Hardware, Zielumgebungen, Installation                                      | `define`            |
| `crosscutting`    | Konzepte, die quer über das System gelten: Fehlerbehandlung, Protokollierung, Konventionen | `define`, `global`  |
| `decisions`       | die Begründungen großer, kapitelübergreifender Entscheidungen in Prosa                   | `define`            |
| `quality`         | Qualitätsanforderungen: was messbar gut sein muss und wie gut                              | `define`, `relate`  |
| `risks`           | Risiken und technische Schulden: bekannt und benannt, aber nicht bindend                    | `nonbinding`        |
| `glossary`        | die Begriffe des Vorhabens und ihre Bedeutung                                               | `nonbinding`        |
| `plan`            | geplante Schritte, wo immer sie stehen                                                      | `plan`              |
| `status`          | erledigte Schritte                                                                          | `nonbinding`        |
| `concept`         | Findungstext: hier wird gedacht, nichts bindet                                              | `nonbinding`        |
| `appendix`        | Verlauf, Reviews, verworfene Wege — Beurteilungsmaterial                                   | `nonbinding`        |
| `register`        | das Register selbst                                                                         | `register`          |

Zwei Rollen verdienen einen eigenen Satz. **`decisions` bleibt neben dem Register bestehen** (entschieden am 2026-09-20) und doppelt es nicht: Das Register hält die Attribute jeder Festlegung, ein `decisions`-Abschnitt hält die Begründung einer großen Entscheidung in Prosa — einer, die kein einzelnes Kapitel besitzt. Und **`concept` löst ein Problem, das der Vorläufer nicht adressierte**: Findungstexte neben der bindenden Doku las die Instanz genauso als Gesetz; ein Abschnitt mit dieser Rolle ist ausdrücklich Denkraum.

**Wo eine Rolle gilt und wo sie endet.** Im Regelfall steht die Rolle an der Überschrift und gilt für den ganzen Abschnitt, Unterabschnitte eingeschlossen, soweit die keine eigene tragen. Das allein reicht aber nicht: Ein Entwickler fügt in ein erklärendes Kapitel einen Absatz „Hinweis: Wenn …" ein, der eine Festlegung ausspricht, oder in ein Bausteinkapitel einen Absatz, in dem er nur laut denkt. Deshalb kann die Rolle auch **an einem Absatz** wechseln: Der Absatz trägt seinen eigenen Rollenmarker, die Rolle gilt für diesen Absatz, und danach gilt wieder die des Abschnitts. Feiner als der Absatz wird nicht gewechselt (entschieden am 2026-09-21), weil es dafür kein Bedürfnis gibt — die Ebene darunter ist der Satz, und für den Satz gibt es bereits den Marker: Ein einzelner Satz, der in nichtbindendem Umfeld eine Festlegung ausspricht, trägt seinen Definitionsmarker, und **der Definitionsmarker geht der Rolle vor**; ein erläuternder Satz in bindendem Umfeld braucht gar nichts, er bekommt schlicht keinen Marker (Aufnahmetest: Kann Code das verletzen?). Trägt nichts eine Rolle, gilt alles als `building-blocks`; der Skill schlägt beim ersten Kontakt vor, den Text mit den Zusammenhängen zu kennzeichnen — schlägt vor, verlangt nicht. Die Form des Rollenmarkers steht in Kapitel 3.3.1.

**Marker werden vorgeschlagen, nicht verfügt** (entschieden am 2026-09-21). Bevor in einer Doku zum ersten Mal Marker entstehen, legt die Instanz vor, was sie einbauen will und wozu — was die Klammern leisten und was ohne sie nicht geht —, und der Entwickler entscheidet daraufhin. Er kann sie abwählen: Seine Doku bleibt dann unmarkiert, und das ist kein Fehlerzustand, sondern der Anfangszustand jedes Projekts (1.7.2). Der Skill arbeitet weiter — er liest die Doku, bestimmt die Lage und parkt Kollisionen, statt sie abzuschießen; das ist der wichtigste Gewinn, und den gibt es ohne jeden Marker (1.8). Was entfällt, ist die Buchführung: ohne Adresse kein Registereintrag zu einer Festlegung, keine Ereigniszeilen, keine Auswirkungsrechnung. Das ist etwas anderes als die Abwahl des Skills insgesamt (`mode: off`, 1.7.7) — dort tut er nichts, hier tut er, was ohne Adressen geht.

**Ein dritter Weg ist erwogen und zurückgestellt** (entschieden am 2026-09-21): Das Register könnte eine Festlegung statt über einen Marker über Datei und Wortlaut eines Kernsatzes ansprechen und die Prosa ganz unberührt lassen. Er ist fragiler — ein umformulierter Satz bricht die Adresse, und das Verfahren muss es melden, statt es zu bemerken —, und er kostet einen zweiten Ankermechanismus im Skript. Der Regeltext nennt ihn als Möglichkeit; gebaut wird er erst, wenn ein Projekt ihn braucht (Kapitel 3.2.9).

Damit steht im Dokument des Entwicklers genau zweierlei vom Skill: Marker an Festlegungen und Rollen an Überschriften oder Absätzen. Beides sind Adressen. Aus einem Marker folgt nichts, ohne das Register zu lesen; aus einer Rolle folgt nichts, ohne den Skill zu lesen. **Keine Skill-Logik, kein Attribut, kein Zustand steht im Dokument des Entwicklers.** Das ist der Grundsatz, der die Doku lesbar hält und den Entwickler frei lässt, und Kapitel 2 macht ihn zur Vorgabe.

> Geprüft: Ok

### 1.3.4 Was dem Entwickler gehört und was er trägt

Ihm gehört die Doku: Gliederung, Reihenfolge, Nummerierung, Sprache der Überschriften, Layout, ob Dreiersschema des Vorläufers (Anhang A) oder freiere Form, wo das Register liegt, wo geplante Schritte stehen. Der Skill bindet nichts an Nummern, Dateinamen oder Titel — nur an Rollen (1.3.3) —, und er fordert keine Struktur, die nichts zu halten hat; die Doku wächst an Festlegungen, nicht an Pflichten (Kapitel 3.5). Der Entwickler muss weder die Grammatik der Marker noch die des Registers noch die Namen der Härtewerte kennen.

Was er tut: Prosa schreiben, den Planabschnitt „Berührte Festlegungen" lesen und in Prosa antworten. Was er hinnimmt — das ist der ehrliche Preis: Klammern im Text, eine Registerdatei neben der Doku und einen Abschnitt in jedem Plan. Marker und Registerzeilen schreibt die Instanz mit der Ausführung eines freigegebenen Plans; schreibt der Entwickler selbst Prosa, findet der Lint unmarkierte Festlegungen, und die Instanz schlägt die Marker im nächsten Plan vor. Die Buchführung trägt die Instanz, die Kontrolle tragen Skript und Hooks — nie der Entwickler.

**Und er wird nicht ausgefragt — Annahmen statt Fragen.** Fehlt zu einer Festlegung ein Attribut — ihre Art, ihr Grund, ihre Quelle —, bildet die Instanz aus der Prosa eine Annahme und legt sie im Planabschnitt sichtbar vor, statt eine Frage zu stellen; im Regelfall bestätigt die Freigabe des Plans die gelisteten Annahmen, soweit der Entwickler nichts anderes sagt (Skill-Parameter `assumptions_on_approval`). Gefragt wird nur, wo keine tragfähige Annahme möglich ist — und dann ohne das Vokabular des Skills, mit dem Wortlaut der Festlegung und dem Anlass. Eine Annahme bleibt als solche gekennzeichnet und macht eine Festlegung nie unantastbar (Vorgabe 2.11); die Regeln im Einzelnen stehen in Kapitel 3.1.3.

> Geprüft: Ok

### 1.3.5 Was die Einhaltung sichert

Dass die Instanz Marker und Registerzeilen tatsächlich schreibt, sichern nicht Anweisungen, sondern **ein Skript und Hooks**: Der Hook H1 prüft nach jedem Doku-Edit, der Hook H2 vor jedem Commit — beide lesend (Kapitel 3.6 und 3.7). Anweisungen, die eine Haltung beschreiben, feuern nicht zuverlässig (1.2); ein Hook feuert immer. Diese Absicherung kommt mit dem Skill und wirkt in jedem Projekt, das ihn führt, ohne dass dort etwas einzurichten wäre; nur der Zustandsbericht am Sitzungsstart (Hook H3) ist ein Angebot je Projekt (Kapitel 3.7).

**H2 blockiert, und der Entwickler kann das im Einzelfall aufheben** (entschieden am 2026-09-24, vormals Q-26): H2 blockiert den Commit bei struktureller Inkonsistenz — das ist der einzige blockierende Eingriff des Skills. Der Entwickler kann diese Blockade für einen einzelnen Commit ausdrücklich aufheben, statt den Hook im Projekt insgesamt abzuschalten; wie er das Wort dafür ausspricht, ist eine technische Einzelheit (Kapitel 3.7.4).

> Geprüft: Ok.

### 1.3.6 Wozu das Skript da ist und wie es aufgerufen wird

**Was es übernimmt.** Vier Arbeiten, die eine Instanz zwar ausführen könnte, bei denen sie aber Urteil vortäuschen würde, wo Mechanik gefragt ist: **zählen** — wie viele Reibungszeilen seit der letzten Bestätigung; **ableiten** — welche Prüfung der Härteliste als erste zutrifft; **einsammeln** — welche Festlegungen als von einer Änderung berührt in Frage kommen; **abgleichen** — wo Prosa und Register auseinanderlaufen. Alle vier sind aus den Feldern eindeutig bestimmt. Was eindeutig bestimmt ist, gehört nicht ins Modell, sondern in ein Programm; eine Instanz, die es „im Kopf" täte, käme manchmal zum richtigen Ergebnis und niemand wüsste, wann.

**Was es nie tut.** Es schreibt keine Prosa des Entwicklers um. Es entscheidet nicht, ob ein Satz eine Festlegung ist. Es beurteilt nicht, ob ein Kandidat wirklich betroffen ist. Diese drei sind Urteil und bleiben bei der Instanz; das Skript legt ihr die Grundlage vor.

**Wie seine Kommandos geschnitten sind.** Nicht entlang des Datenmodells — eine ID, eine Zeile —, sondern **entlang der Anker**: Ein Kommando je Handlung, die im Ablauf ohnehin vorkommt. Bereich öffnen ist ein Aufruf, Plan schreiben ist ein Aufruf, Plan ausführen ist ein Aufruf, jede Hook-Prüfung ist ein Aufruf. Daneben gibt es feinkörnige Auskunftskommandos für eine einzelne Festlegung, aber die dienen der Nachfrage des Entwicklers („warum steht das zur Disposition?") und nicht dem Ablauf.

**Warum dieser Schnitt.** Jeder Aufruf kostet die Instanz dreierlei: ihn zu starten, auf ihn zu warten und seine Antwort zu deuten — und das unabhängig davon, wie wenig er tut. Eine Schnittstelle, bei der fünfzehn berührte Festlegungen fünfzehn Aufrufe bedeuten, ist deshalb nicht bloß unschön, sondern sie macht den Skill an der teuersten Stelle teuer (Vorgabe 2.7). Daraus zwei Regeln: **Was mehrere Festlegungen betrifft, nimmt eine Liste** und nicht eine ID. Und **was die Instanz zu entscheiden hat, kommt in einem Bündel** — alle Entscheidungen eines Ankers auf einmal, nicht eine je Aufruf.

**Wie das Ergebnis zurückkommt.** Drei Wege, und die Wahl richtet sich nach einer einzigen Frage: *Muss die Instanz das lesen, um zu entscheiden?*


| Antwort                 | Weg                                                                                    | Wofür                                                                                                                            |
| ----------------------- | -------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Ja, vollständig        | **inline** in der Antwort des Aufrufs                                                  | alles, worüber entschieden wird: Kandidatenlisten, Befunde, Härten. Richtwert bis etwa vierzig Zeilen                           |
| Ja, aber nur einen Teil | **Datei, dazu inline eine Kurzfassung** mit Zahlen, den ersten Einträgen und dem Pfad | lange Listen, von denen meist die Zahl genügt — etwa alle Erwähnungen einer Festlegung im Code. Die Instanz liest gezielt nach |
| Nein                    | **Das Skript schreibt selbst**, inline kommt nur die Quittung                          | Erzeugnisse statt Entscheidungsgrundlagen: der Planabschnitt, die Registerzeilen einer Ausführung                                |

Der dritte Weg ist der wichtigste, weil er die teuerste Handlung überhaupt einspart: den Dateiedit durch die Instanz. Er gilt ausdrücklich **nicht** für die Prosa des Entwicklers — die ändert das Skript nie (Bedingung 6 in Kapitel 2.2) —, sondern für das Register und für Arbeitsdokumente, die der Ablauf ohnehin erzeugt.

**Was daraus für die Ausgabeform folgt.** Weil die Instanz die Antwort deuten muss, ist jede Ausgabe eine Aussage und keine Rohdatenhalde: eine Zeile je Gegenstand, entscheidungsfertig, und im Fehlerfall Schritt, Ursache, Zustand und Abhilfe statt eines Protokolls. Die Vorgaben dazu stehen in Kapitel 2.5 bis 2.7, die Ausführung in Kapitel 3.6.

> Geprüft: offen

### 1.3.7 Was die Prosa festhält — und was sie anderswo überlässt

**Ergänzt am 2026-09-24** (Anstoß aus einem Parallelprojekt): Kann Code eine Aussage verletzen, ist sie eine Festlegung — aber nicht jede Festlegung braucht deshalb einen Platz in der Prosa des Entwicklers. Eine vollständige Programmdokumentation besteht aus mehreren, sich ergänzenden Teilen: der begleitenden Doku, den Docstrings von Modulen, Klassen und Funktionen, den Kommentaren an den Parametrierungsstellen im Code, und dem Code selbst. Die begleitende Doku trägt nur, was die anderen Teile nicht tragen. Aufzunehmen ist der Grund einer wesentlichen Detailentscheidung, wo das Ergebnis ihn nicht zeigt; die Prinzipbeschreibung einer Logik, die sich aus Code und Kommentaren nicht erschließt — einschließlich dessen, was ein Abschnitt ausdrücklich nicht leistet; und die Begründung, warum eine Vorgabe aus Kapitel 1 oder 2 gerade durch diese Umsetzung erfüllt wird und nicht durch eine naheliegende andere. Nicht aufzunehmen ist, was der Docstring einer Klasse, Methode oder eines Moduls ohnehin sagt — Schnittstelle, Parameter, Grundfunktion —, was sich beim Lesen von selbst ergibt, und eine Aufzählung dessen, was ins Programm eingetragen wurde: Die begleitende Doku ist kein Änderungsspeicher — anders als ihre Ereigniszeilen (3.1.2), die nicht festhalten, *was* geändert wurde, sondern *ob sich eine Festlegung bewährt hat*. Maßstab: so viel, dass sich im Nachhinein aus Code und Doku alles erarbeiten lässt, was an echtem Wissen in den Entwurf eingegangen ist — und nicht mehr.

**Neben Code, Docstrings und Kommentaren kann es weitere, unabhängige Dokumentation geben — und die zählt mit.** Ein fortgeschrittenes Projekt führt oft schon eine Anwenderdokumentation (und sei es nur eine README) oder eine zentrale, eigenständige Programmdokumentation. Beide haben mit der laufenden, projektbegleitenden Doku dieses Skills zunächst nichts zu tun — sie entstehen unabhängig und für ein anderes Publikum. Existiert eine solche Dokumentation aber bereits und ist sie aktuell genug, gehört sie zur gesamten Dokumentationslage dazu, und die begleitende Doku darf sich daran messen: Was dort bereits vollständig und aktuell steht, muss die begleitende Doku nicht doppelt tragen. Das erlaubt, Inhalte zu entfernen, sobald sie dort nur noch redundant sind und für die weitere Implementierung keine Funktion mehr haben — vorzugsweise aus Kapitel 1, seltener aus Kapitel 2; solange eine Festlegung noch eine solche Funktion trägt, bleibt sie, auch wenn dieselbe Aussage anderswo ebenfalls steht. **Kapitel 3 ist davon ausgenommen.** Ob sein Detailwissen adäquat in eine finale Projektdokumentation übernommen wurde, lässt sich von hier aus nie sicher beurteilen — und fehlt es dort, fehlt es im Servicefall ganz. Entfernt wird eine so redundant gewordene Festlegung nie stillschweigend, sondern über den Lebenszyklus wie jede andere auch: mit einer `retired`-Zeile, die den Grund nennt (Kapitel 1.7.6).

> Geprüft: Ok.

## 1.4 Die Begriffe im Überblick

Alles, was der Skill kennt, steht hier auf einer Seite. Die Werte sind vollständig aufgezählt: Ein nicht aufgeführter Wert ist ein Fehler, den das Skript meldet (Vorgabe 2.1). Ausführlich beschrieben wird jeder Begriff dort, wo die letzte Spalte hinweist.

**Was in der Prosa des Entwicklers steht**

| Begriff        | Bedeutung                                                                                                                                                                                                                                                                        | Werte                                                                                                                                                                                                       | Ausführlich |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| **Festlegung** | eine Aussage, die etwas bindend festhält. Aufnahmetest: Kann Code sie verletzen?                                                                                                                                                                                                | —                                                                                                                                                                                                          | 3.2          |
| **Marker**     | ein Feld in der Prosa, gefüllt mit einer Adresse und nichts sonst. Drei Arten: Definitionsmarker `[D-0042]` am Satz, der die Festlegung ausspricht; Zitatmarker `[>D-0042]` an Stellen, die sie heranziehen; Rollenmarker `[DS:runtime]` an einer Überschrift oder einem Absatz | —                                                                                                                                                                                                          | 3.2.2, 3.3   |
| **ID**         | der stabile Schlüssel einer Festlegung; global je Register, wird nie neu vergeben, trägt kein Kapitel                                                                                                                                                                          | `D-0042`                                                                                                                                                                                                    | 3.2.3        |
| **Rolle**      | sagt, worum es in einem Abschnitt geht; daraus folgt, was der Skill dort tut                                                                                                                                                                                                     | `goals`, `constraints`, `context`, `strategy`, `building-blocks`, `runtime`, `deployment`, `crosscutting`, `decisions`, `quality`, `risks`, `glossary`, `plan`, `status`, `concept`, `appendix`, `register` | 1.3.3        |
| **Funktion**   | was der Skill in einem Abschnitt mit dieser Rolle tut                                                                                                                                                                                                                            | `define`, `relate`, `global`, `nonbinding`, `plan`, `register`                                                                                                                                              | 1.3.3        |

**Was im Register steht** — je Festlegung eine Gruppe von Zeilen

| Begriff                                     | Bedeutung                                                                                                                                                                                     | Werte                                                                                                                                                                                                              | Ausführlich |
| ------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------ |
| **Art** (`kind`)                            | woher die Festlegung kommt                                                                                                                                                                    | `given` — von außen vorgegeben (Physik, Hardware, Fremdschnittstelle, Norm) · `chosen` — von uns entschieden                                                                                                   | 3.1.2        |
| **Grund** (`reason`), **Quelle** (`source`) | warum so, beziehungsweise woher                                                                                                                                                               | Freitext ·`in prose` — steht in der Doku selbst · `unknown` — nicht mehr bekannt                                                                                                                               | 3.2.5        |
| **Alternative** (`instead`)                 | die stärkste verworfene Alternative, mit dem Grund der Ablehnung; eine Zeile                                                                                                                 | Freitext ·`in prose`                                                                                                                                                                                              | 3.2.5        |
| **Status** (`status`)                       | wie die Attribute zustande kamen — der Fußabdruck                                                                                                                                           | `assumed` — Lesart der Instanz, nicht bestätigt · `accepted` — stand in einem freigegebenen Plan, nicht einzeln angesprochen · `confirmed` — vom Entwickler selbst bestätigt oder korrigiert                | 3.1.2        |
| **Festgeschrieben** (`pinned`)              | ausdrückliche Entscheidung, eine gewählte Festlegung nicht wieder aufzumachen                                                                                                               | ja/nein                                                                                                                                                                                                            | 3.1.2        |
| **Suchschlüssel** (`keys`)                 | zwei bis vier markante Begriffe; finden unmarkierte Erwähnungen                                                                                                                              | Freitext                                                                                                                                                                                                           | 3.2.5        |
| **Fingerabdruck** (`fp`)                    | Kurzhash des Definitionssatzes; erkennt, dass die Definition sich geändert hat                                                                                                               | Hexzeichen                                                                                                                                                                                                         | 3.6.7        |
| **Ereigniszeile**                           | eine **datierte Zeile, die festhält, dass der Festlegung etwas widerfahren ist.** Sie ändert die Festlegung nicht, sondern sammelt Erfahrung mit ihr — und daraus folgt später ihre Härte | `friction` — Arbeit musste um die Festlegung herum gebaut werden · `upheld` — sie wurde gegen eine Idee oder einen Befund geprüft und hat standgehalten · `pending` — eine Frage an den Entwickler ist offen | 3.1.2, 3.2.5 |
| **Lebenszyklus**                            | was am Ende mit ihr geschieht                                                                                                                                                                 | `superseded … by <ID>` — durch eine neue ersetzt · `retired` — entfällt ersatzlos                                                                                                                             | 3.2.6        |

**Was die Sitzung bestimmt**


| Begriff                 | Bedeutung                                                                                                                   | Werte                                                                                                            | Ausführlich |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | ------------ |
| **Härte** (`hardness`) | wie bindend eine Festlegung **jetzt** ist; wird bei jedem Kontakt neu abgeleitet und **nie gespeichert**                     | `fixed` — nicht zur Diskussion · `decided` — gilt, darf hinterfragt werden · `open` — steht zur Disposition | 3.1.4        |
| **Lage** (`mode`)       | wie die Sitzung die Doku liest                                                                                              | `execute` — Beschlossenes umsetzen · `design` — etwas neu denken                                              | 3.1.5        |
| **Kontakt**             | eine Festlegung ist kontaktiert, wenn sie im Plan des Schritts oder in der Auswirkungsliste der Idee genannt werden müsste | —                                                                                                               | 3.1.3        |
| **Parken**              | eine Kollision in der Lage `design` in einem Satz festhalten, statt den Gedanken abzubrechen                                 | —                                                                                                               | 3.1.5        |

**Was die Planung trägt**


| Begriff                   | Bedeutung                                                                                        | Werte                      | Ausführlich |
| ------------------------- | ------------------------------------------------------------------------------------------------ | -------------------------- | ------------ |
| **Geplanter Schritt**     | ein noch offener Schritt der Projektplanung, wo immer er steht                                   | —                         | 3.4.1        |
| **Umbauziel** (`target:`) | die Zeile, mit der ein Schritt sagt, was er umbauen will                                         | IDs oder eine Kapiteldatei | 3.4.2        |
| **Planabschnitt**         | „Berührte Festlegungen" — der Abschnitt jedes Plans, in dem der Entwickler die Annahmen sieht | —                         | 3.1.6        |

**Was das Projekt einstellt** — Skill-Parameter in der Skill-Parameterdatei, jeder mit Standardwert (2.9): `mode`, `doc_dir`, `register`, `planned_steps`, `marking`, `friction_threshold`, `assumptions_on_approval`, `impact_model`, `impact_lib`, `impact_cutoff`, `lint_signals` (3.5.2). Davon zu unterscheiden sind die **Script-Argumente** je Aufruf (2.4) und die **Graphenparameter** der Auswirkungsrechnung, die im Skill stehen und nicht projektkonfigurierbar sind (3.6.5). Kein Skill-Parameter ist das Absatzlayout der Prosa: Es wird aus der vorhandenen Doku abgelesen, und nur wenn es keine gibt oder sie uneindeutig ist, wird einmal gefragt (entschieden am 2026-09-25, vormals Q-17; Kapitel 3.2.8).

> Geprüft: offen

## 1.5 Bild des fertigen Systems

Ein Projekt, das den Skill führt, hat seine Doku in Prosa — nach dem Dreiersschema des Vorläufers (Anhang A) oder in freierer Form —, in der bindende Sätze einen Marker und Abschnitte ihre Rolle an der Überschrift tragen; je Doku eine Registerdatei mit Attributen, Ereignissen und Lebenszyklus je Festlegung; eine Skill-Parameterdatei in `.claude/`; geplante Schritte, wo immer sie stehen, die ihr Umbauziel nennen.

**„Je Doku", nicht „je Projekt" — das ist Absicht.** Ein Repository kann mehrere Vorhaben tragen, jedes mit eigener Doku, eigener Gliederung und eigenem Register; in diesem Repository ist genau das der Fall. Der Skill darf deshalb nicht von einer Doku je Projekt ausgehen und keine über Ordnergrenzen hinweg vereinheitlichen. Er folgt dem Vorhaben, in dem die berührten Dateien liegen: Register, Rollen und geplante Schritte bestimmen sich aus dessen Umgebung, nicht aus einer Einstellung am Repository. Wie er das Vorhaben findet, steht in Kapitel 3.5.4.

**Der Skill selbst** besteht aus einer dünnen `SKILL.md` (Kapitel 3.10), die Lage und die Skill-Parameter bestimmt und die passenden Regelteile nachlädt, aus dem angepassten Regeltext des Vorläufers als eigenem Regelteil (Anhang A, Anpassungen in 1.11), aus einem Skript mit einem Modul für die Auswirkungsrechnung, und aus zwei Hooks, die mit dem Skill kommen, sowie einem dritten, den das Projekt einrichten kann; geladen wird er über einen Trigger in der `CLAUDE.md` (Kapitel 3.11).

> Geprüft: Ok.

## 1.6 Ein Beispiel von Anfang bis Ende

Acht Szenen an einem erfundenen Vorhaben: Ein Werkzeug liest Messwerte von einem Sensor und schreibt sie in eine Datei. Die ersten sieben sind ausgeführt und zeigen jeden Begriff aus 1.4 im Gebrauch; die achte springt ein Jahr weiter und beschreibt — ohne Ausführung — einen Umbau an einem gewachsenen Vorhaben, weil erst dort die Auswirkungsrechnung etwas beiträgt. Wer das gelesen hat, findet in Kapitel 2 und 3 nur noch Einzelheiten.

### 1.6.1 Szene 1 — Der Entwickler lässt eine Doku anlegen

> **Entwickler:** „Leg mir eine begleitende Doku an."

Die Instanz liest das Projekt — eine Python-Datei, eine README, kein Doku-Ordner, keine Liste offener Schritte — und legt einen **Plan** vor: Einstiegsform, weil es ein Modul ist; Ordner `dev-doc/` mit der einen Datei `accompanying-doc.md`; Register `dev-doc/decisions.md`; geplante Schritte vorerst als Abschnitt in der README; Layout ein Absatz je Zeile, aus der README abgelesen. Dreiteilung und Sichtenform nennt sie mit je einem Satz, warum sie hier zu groß wären. Ein Punkt bleibt zu klären, weil er sich nicht ablesen lässt: ob es überhaupt einen eigenen Ordner geben soll.

> **Entwickler:** „Ja, mit Ordner."

Nach der Freigabe entstehen zwei Dateien und die Skill-Parameterdatei. Sonst nichts — keine leeren Kapitel.

### 1.6.2 Szene 2 — Die ersten Festlegungen entstehen

Der Entwickler schreibt in `accompanying-doc.md`:

> ## Erfassung
>
> Der Sensor liefert Messwerte mit 100 Hz; schneller kann er nicht. Das Werkzeug liest sie in einer eigenen Schleife und schreibt sie blockweise zu je 1000 Werten, weil ein Schreibzugriff je Einzelwert das Dateisystem ausbremst. Das Format ist CSV.

Der Hook H1 läuft nach dem Edit und meldet in den Kontext: drei Sätze mit Normativsignal ohne Marker, und die Überschrift hat keine Rolle. Die Instanz **fragt nicht**, sondern bildet Annahmen und legt sie im Plan vor:

> **Berührte Festlegungen**
>
>
> | Wortlaut                        | Art      | Grund/Quelle                                                            | Status    | Härte    |
> | ------------------------------- | -------- | ----------------------------------------------------------------------- | --------- | --------- |
> | „liefert Messwerte mit 100 Hz" | `given`  | Grenze des Sensors — Quelle vermutet, Datenblatt?                      | `assumed` | `decided` |
> | „blockweise zu je 1000 Werten" | `chosen` | steht in der Prosa: Schreibzugriff je Einzelwert bremst das Dateisystem | `assumed` | `decided` |
> | „Das Format ist CSV"           | `chosen` | kein Grund genannt —`pending`: Warum CSV?                              | `assumed` | `decided` |
>
> Rolle für „Erfassung": `building-blocks`.
> Die Freigabe dieses Plans bestätigt die gelisteten Annahmen, soweit Du nichts anderes sagst.

> **Entwickler:** „Die 100 Hz stehen im Datenblatt. CSV, weil der Auswerter es direkt liest — binär wäre kleiner, aber dann braucht es ein eigenes Lesewerkzeug."

Die Instanz zeigt, wie sie das einträgt, und schreibt nach der Freigabe. Die Prosa bekommt drei Marker und einen Halbsatz, den der Entwickler geliefert hat:

> ## Erfassung [DS:building-blocks]
>
> Der Sensor liefert Messwerte mit 100 Hz [D-0001]; schneller kann er nicht. Das Werkzeug liest sie in einer eigenen Schleife und schreibt sie blockweise zu je 1000 Werten [D-0002], weil ein Schreibzugriff je Einzelwert das Dateisystem ausbremst. Das Format ist CSV [D-0003], weil der Auswerter es direkt liest.

Und `dev-doc/decisions.md` bekommt seine ersten Einträge:

```
[D-0001 given confirmed] Abtastrate des Sensors
[D-0001 source] Datenblatt des Sensors: 100 Hz sind das Maximum
[D-0001 keys] Abtastrate; 100 Hz; Sensor

[D-0002 chosen accepted] Blockgröße beim Schreiben
[D-0002 reason] in prose
[D-0002 keys] Blockgröße; blockweise; 1000

[D-0003 chosen confirmed] Dateiformat
[D-0003 reason] in prose
[D-0003 instead] Binärformat — kleiner, braucht aber ein eigenes Lesewerkzeug
[D-0003 keys] CSV; Dateiformat; Auswerter
```

Der Unterschied zwischen `confirmed` und `accepted` ist der Fußabdruck: D-0001 und D-0003 hat der Entwickler selbst angesprochen, D-0002 lief im freigegebenen Plan mit. Später ist ablesbar, was nachgeprüft wurde und was nur mitlief.

### 1.6.3 Szene 3 — Ein Schritt wird umgesetzt

Lage `execute`. Der Plan für „Schreiben implementieren" berührt D-0002 und D-0003; beide sind `decided`, es gibt keine Kollision. Der Planabschnitt listet sie, sonst geschieht nichts. **Der Entwickler sieht zwei Zeilen und liest weiter.** Das ist der Normalfall, und der Skill schweigt darin.

### 1.6.4 Szene 4 — Reibung entsteht

Wochen später soll eine Live-Anzeige dazukommen. Sie braucht einzelne Werte und greift sie vor dem Blockpuffer ab — ein Sonderweg, den es nur wegen D-0002 gibt. Die Instanz erkennt das beim Schreiben des Plans und trägt mit dessen Ausführung eine Ereigniszeile ein:

```
[D-0002 friction 2026-10-02] Live-Anzeige umgeht den Blockpuffer, weil sie einzelne Werte braucht
```

Der Entwickler hat dazu nichts getan und nichts entschieden. Die Zeile ändert nichts an D-0002 — sie sammelt Erfahrung.

### 1.6.5 Szene 5 — Eine Idee, die nicht abgeschossen wird

> **Entwickler:** „Könnten wir nicht binär schreiben? Die Dateien werden riesig."

Das ist keine Aufgabe, sondern eine Idee. Die Instanz wechselt in die Lage `design` und sagt es: „Ich lese die Doku hier als Stand, nicht als Vorgabe." Die Härte von D-0003 ist `decided` — Kollision, aber kein Abbruch. Sie **parkt** in einem Satz:

> „Das berührt D-0003 (CSV, weil der Auswerter es direkt liest). Verworfen wurde Binär damals, weil ein eigenes Lesewerkzeug gefehlt hätte — das wäre neu zu bewerten, seit es den Auswerter als eigenes Programm gibt. Umbaukosten: zwei Stellen in der Doku, drei im Code."

Und führt den Gedanken dann zu Ende: Blockformat mit Kopfsatz, CSV-Ausgabe als eigenes Kommando, Abschätzung der Dateigröße. **Genau das leistete der Vorläufer nicht** — dort wäre die Idee an D-0003 gescheitert, bevor sie ausformuliert war.

> **Entwickler:** „Interessant, aber nicht jetzt."

```
[D-0003 upheld 2026-10-05] Gegen die Idee Binärformat geprüft; der Grund trägt weiter
```

Die Zeile ist wichtiger, als sie aussieht: Sie verhindert, dass dieselbe Idee in drei Monaten erneut aufgemacht wird, und sie setzt den Reibungszähler für D-0003 zurück.

### 1.6.6 Szene 6 — Die zweite Reibung öffnet eine Festlegung

Noch später soll ein Netzwerk-Streaming dazukommen, das ebenfalls Einzelwerte braucht — der zweite Umweg um denselben Blockpuffer:

```
[D-0002 friction 2026-11-13] Netzwerk-Streaming braucht Einzelwerte; zweiter Umweg am Blockpuffer
```

Beim nächsten Plan, der D-0002 berührt, rechnet das Skript die Härte neu: zwei `friction`-Zeilen seit der letzten `upheld`-Zeile, Schwelle ist 2 — Prüfung R6 greift, die Härte ist **`open`**. Die Instanz sagt einen Satz:

> „Die feste Blockgröße steht inzwischen zur Disposition: Zweimal musste Arbeit um sie herum gebaut werden. Soll ich Alternativen ausarbeiten?"

Niemand hat sich das gemerkt, niemand hat es gezählt. Es steht im Register, und ein Kommando liest es ab.

### 1.6.7 Szene 7 — Ablösung, und warum alte Verweise trotzdem auflösen

> **Entwickler:** „Ja, mach die Blockgröße einstellbar."

Die neue Festlegung bekommt eine neue ID; die alte bleibt im Register stehen und zeigt auf ihre Nachfolgerin:

```
[D-0002 superseded 2026-11-20 by D-0007] Blockgröße ist jetzt einstellbar

[D-0007 chosen confirmed] Blockgröße einstellbar, Standard 1000
[D-0007 reason] in prose
[D-0007 instead] feste Blockgröße — zwei Verbraucher brauchten Einzelwerte
[D-0007 keys] Blockgröße; einstellbar; Standard 1000
```

In der Prosa wird der Satz umgeschrieben und trägt jetzt `[D-0007]`. Und die alten Verweise? Ein Commit-Text von letztem Monat nennt D-0002, ein älterer Absatz zitiert sie — beide lösen weiterhin auf, denn das Register kennt die Nachfolgerin und `show D-0002` nennt sie. **Niemand muss vor dem Weiterarbeiten das Projekt nach alten Verweisen absuchen.**

### 1.6.8 Szene 8 — Ein Jahr später: der Umbau, und wozu die Auswirkungsrechnung da ist

Die sieben Szenen zeigen alles außer einem: Wozu die Kantenrechnung über den Graphen gut ist. Sie zeigen es nicht, weil sie es nicht können — das Vorhaben hat einen Abschnitt und einen Absatz, in dem jede Festlegung neben jeder anderen steht. Der Graph gäbe dort alle zurück, und alle wären unerheblich. **Die Auswirkungsrechnung verdient sich erst, wenn eine Doku mehrere Kapitel hat und es einen Text mit der Funktion `relate` gibt.** Diese Szene beschreibt einen solchen Fall in seinen Schritten, ohne ihn auszuführen.

**Die Lage.** Aus dem Testwerkzeug ist die Software eines Geräts geworden. Mehrere Sensoren hängen über I2C am Controller, jeder mit eigenem Treiber; geschrieben wird nicht mehr in eine Datei, sondern in eine SQLite-Datenbank; die Doku hat Kapitel für Hardware und Treiber, für die Speicherung und für die Auswertung, dazu einen Übersichtstext mit der Funktion `relate`. Jetzt sollen Statuswerte per LoRaWAN übertragen werden. Der Transceiver bringt einen eigenen Temperatursensor mit — der bisher verbaute kann entfallen. Programm und Doku sind zu überarbeiten.

**Warum das ein schwieriger Umbau ist.** Nicht die Frage „was ändert sich am Temperatursensor" ist das Problem, sondern „was hat stillschweigend vorausgesetzt, dass es ihn gibt". Solche Voraussetzungen nennen ihren Gegenstand oft nicht beim Namen. Eine Festlegung in der Auswertung — etwa, dass über eine bestimmte Zahl von Messwerten gemittelt wird, weil sonst das Rauschen durchschlägt — hängt an der Rauschcharakteristik des alten Sensors, ohne ihn zu erwähnen. Der neue hat andere Werte. Eine Textsuche findet diesen Satz nicht; der Graph findet ihn, weil er im Übersichtstext im selben Absatz zitiert wird wie die Temperaturmessung.

**Die Schritte:**

**1. Erst die Idee prüfen, dann umbauen.** Der Entwickler bringt den Vorschlag: Der mitgelieferte Sensor macht den verbauten überflüssig. Das ist noch keine Aufgabe, sondern eine Idee, und die Instanz arbeitet zunächst in der Lage `design` — sie liest die Doku als Stand, nicht als Vorgabe, und sagt das. Sie trägt zusammen, was für den Ersatz spricht und was dagegen: Der neue Sensor sitzt im Transceiver, also an einer anderen Stelle im Gehäuse und misst eine andere Temperatur; seine Genauigkeit steht im Datenblatt des Transceivers und ist eine andere. Kollisionen mit bestehenden Festlegungen werden **geparkt**, nicht als Ablehnung formuliert. Am Ende steht ein Vorschlag mit Kosten, und der Entwickler entscheidet. Erst dann wechselt die Sitzung nach `execute`.

**2. Den Bereich öffnen.** Bevor irgendetwas geplant wird, listet das Skript die Festlegungen der berührten Kapitel — Hardware und Treiber, Speicherung, Auswertung — mit ihrer abgeleiteten Härte und dem Grund dafür. Das ist keine Suche, sondern ein Abzug aus dem Register, und er zeigt nebenbei, was seit der letzten Sitzung nicht zusammenpasst: Marker ohne Registereintrag, geänderte Definitionssätze, unlesbare Zeilen. Die Instanz weiß an dieser Stelle noch nicht, was der Umbau berührt; sie weiß nur, was es in der Gegend gibt.

**3. Kandidaten einsammeln.** Jetzt kommt die Auswirkungsrechnung. Ausgangspunkt sind die Festlegungen, die entfallen oder sich ändern: die über den verbauten Temperatursensor, die über seinen Treiber, die über seine I2C-Adresse. Von ihnen aus sammelt das Skript Kandidaten ein — jede Festlegung, die mit einer von ihnen im selben Absatz steht, im selben Abschnitt, oder die im Übersichtstext gemeinsam mit ihr zitiert wird; dazu, als eigene Quelle, jede, deren Suchschlüssel im geänderten Bereich vorkommen. Je Kandidat nennt die Ausgabe, **warum** er einer ist und wie weit er entfernt liegt. **Hier ist der Punkt, an dem das Verfahren sich beweisen muss:** Die Festlegungen, die „Temperatursensor" wörtlich enthalten, hätte auch eine Textsuche gefunden. Der Mittelungssatz in der Auswertung enthält das Wort nicht — er taucht in der Liste auf, weil er im Übersichtstext im selben Absatz zitiert wird wie die Temperaturmessung.

**4. Je Kandidat entscheiden.** Die Liste ist eine Vorlage, kein Ergebnis. Die Instanz geht sie durch und beantwortet für jeden Eintrag, ob er wirklich berührt ist — beim Mittelungssatz: ja, weil die neue Rauschcharakteristik eine andere Mittelungsbreite verlangt; bei der Festlegung über das Abtastintervall der Feuchtemessung, die zufällig im selben Absatz steht: nein. Für die bestätigten nennt sie die gemessenen Umbaukosten, also die Zahl der Stellen, an denen die Festlegung erwähnt wird — in der Doku und im Code. **Verworfene Kandidaten verschwinden aus dem Plan**; was der Entwickler zu lesen bekommt, ist die geprüfte Liste, nicht die rohe.

**5. Die Härten ansehen — und den Sonderfall der hinfälligen Quelle.** Für jede bestätigte Festlegung steht jetzt die Härte fest. Die meisten sind `decided` und werden im Plan mitgeführt. Die Festlegungen über die alte Hardware — I2C-Adresse, Genauigkeit, Abtastrate — sind `given` und damit nach Prüfung R3 `fixed`: Sie wären nicht zu diskutieren. Aber ihre Quelle ist hinfällig geworden, denn das Datenblatt beschreibt ein Bauteil, das nicht mehr verbaut wird. Genau für diesen Fall sagt die Instanz einen Satz — „Die Genauigkeit stammt aus dem Datenblatt des alten Sensors; gilt die Quelle noch?" — und der Entwickler öffnet sie mit einem Wort. **Das ist der einzige Weg, auf dem eine `given`-Festlegung weich wird**, und er ist bewusst an eine ausdrückliche Äußerung gebunden.

**6. Den Planabschnitt füllen — und merken, dass der Schritt zu groß ist.** Alles Bestätigte wandert in den Abschnitt „Berührte Festlegungen": je Eintrag die ID, das Kapitel, Art und Grund, der Status, die Härte mit ihrer Bedingung, bei Kollisionen der geparkte Satz. Der Abschnitt wird lang — über fünfzehn Einträge —, und **das ist selbst die Aussage**: Ein Plan dieser Länge beschreibt keinen Schritt mehr, sondern ein Vorhaben. Er wird zerlegt, etwa in „Treiber und Hardware", „Schema und Speicherung", „Auswertung anpassen". Jeder Teilschritt bekommt ein eigenes Umbauziel, und damit werden die dort genannten Festlegungen für die Dauer des Umbaus `open` — nach Prüfung R2, ohne dass jemand das eigens verfügen müsste.

**7. Ausführen, und dabei den Lebenszyklus schreiben.** Doku und Code entstehen im Wechsel. Die Festlegung über die I2C-Adresse des alten Sensors entfällt ersatzlos und bekommt eine `retired`-Zeile; die über die Temperaturmessung hat eine Nachfolgerin und bekommt `superseded … by`. Für LoRaWAN entstehen neue Festlegungen mit neuen IDs — Übertragungsintervall, Nutzlast, Sendeleistung —, jede mit Art, Grund und verworfener Alternative. Der Mittelungssatz in der Auswertung wird geändert; weil sein Grund sich verschoben hat, ist das eine neue Festlegung und nicht dieselbe mit neuem Wert. Zuletzt bekommt der Übersichtstext seine neuen Zitatmarker — **damit hat das Geflecht beim nächsten Umbau wieder Kanten.** Wer diesen Schritt auslässt, spart zehn Minuten und verliert die Auswirkungsrechnung für alles, was danach kommt.

**8. Abrechnen.** Nach dem Umbau lässt sich sagen, was die Rechnung geleistet hat: wie viele Kandidaten sie vorgelegt hat, wie viele davon wirklich betroffen waren, und — die einzige Zahl, auf die es ankommt — wie viele der bestätigten eine Textsuche über die Suchschlüssel **nicht** gefunden hätte. Wäre diese Zahl null, wäre das Geflecht überflüssig und der Skill behielte die Erwähnungssuche (1.7.4). Sie zu messen ist Gegenstand der Probe (Kapitel 3.8).

**Keine Zahlen in dieser Szene**, weil die Gewichte der Kanten nicht zu ihrem Gegenstand gehören: Was eine Kante ist, steht seit dem 2026-09-24 fest (1.7.4), wie schwer sie wiegt und nach welcher Formel gerechnet wird, ist eine Sache der Messung und nicht der Erzählung (Kapitel 3.6.5 und 3.8).

### 1.6.9 Was der Entwickler in diesen Szenen getan hat

In den ersten sieben Szenen hat er Prosa geschrieben, Pläne gelesen und **viermal in Prosa geantwortet**: einmal zum Ordner, einmal zu Datenblatt und CSV, einmal zur Idee, einmal zur Blockgröße. In Szene 8 kommen zwei Entscheidungen dazu — ob der Ersatz überhaupt trägt, und das Wort, das die hinfällig gewordene Hardware-Festlegung öffnet.

Was er **nie** getan hat: einen Marker gesetzt, eine Registerzeile geschrieben, ein Schlüsselwort gelernt, eine Härte bestimmt, gezählt, wie oft etwas gerieben hat. Und was der Skill nie getan hat: seine Prosa umgeschrieben, ohne dass er es freigegeben hat.

> 1.6 geprüft: Ok.

## 1.7 Welche Arten der Unterstützung es gibt

Der Skill erbringt sieben unterscheidbare Leistungen. Sie sind nicht alle gleich häufig und nicht alle gleich eingreifend; was sie verbindet, ist die Rollenverteilung aus 1.3.4 — der Entwickler schreibt Prosa und entscheidet, die Instanz führt Buch, Skript und Hooks kontrollieren.

**Über allen steht ein Grundsatz: Die Doku wächst an Festlegungen, nicht an Pflichten.** Keine Struktur wird gefordert, die nichts zu halten hat, und keine Leistung wird erbracht, für die es keinen Anlass gibt. Die Ausbaustufe eines Projekts ist, was es hat — nicht, was eine Einstellung behauptet. Daraus folgt die Zurückhaltung, die allen sieben Leistungen gemeinsam ist: Die Erstanlage geschieht nur auf Auftrag, der Einstieg nur am Berührungspunkt, die Prüfung nur an benannten Handlungen. Was daraus im Einzelnen folgt — wann die erste Datei, der erste Registereintrag, die erste Rolle entsteht —, steht in Kapitel 3.5.3. Wann genau die erste Frage überhaupt kommt, ist damit ebenfalls entschieden (2026-09-24, vormals Q-15): erst, wenn im Plan eine Festlegung entsteht, die den Code überdauert — der Aufnahmetest „kann Code das verletzen?" ist der Auslöser.

|   | Leistung                                       | Auslöser                              | Ergebnis                                                   |
| - | ---------------------------------------------- | -------------------------------------- | ---------------------------------------------------------- |
| 1 | **Erstanlage** einer begleitenden Doku (1.7.1) | ausdrücklicher Auftrag                | Gerüst aus Dateien, Rollen und leerem Register            |
| 2 | **Einstieg** in eine vorhandene Doku (1.7.2)   | Berührungspunkt                       | Marker und Registerzeilen für die berührten Festlegungen |
| 3 | **Laufende Pflege** (1.7.3)                    | Plan und seine Ausführung             | Doku und Code im Wechsel; Ereigniszeilen                   |
| 4 | **Auswirkungen finden** (1.7.4)                | Änderung an einer Festlegung          | Kandidatenliste, gemessene Umbaukosten                     |
| 5 | **Einen Bereich neu denken** (1.7.5)           | Idee, Bitte um Alternativen            | zu Ende gedachte Vorschläge, geparkte Kollisionen         |
| 6 | **Prüfen und Aufräumen** (1.7.6)             | Bereich öffnen, Commit, Sitzungsstart | Befunde; Lebenszyklus abgelöster Festlegungen             |
| 7 | **Nichts tun** (1.7.7)                         | `mode: off`                            | keine Wirkung                                              |

### 1.7.1 Erstanlage einer begleitenden Doku

Das ist der Fall, in dem ein Projekt noch keine begleitende Doku hat und der Entwickler eine haben will. Er ist folgenreich: Was hier entsteht, prägt die Arbeit der nächsten Monate.

**Auslöser.** Nur ein ausdrücklicher Auftrag des Entwicklers. Der Skill bietet die Erstanlage **nie von sich aus an** — von selbst wächst die Doku an Festlegungen und nicht an Pflichten (Leistung 2 und 3). Ein Projekt, das nur einen Schritt zu erledigen hat, bekommt kein Gerüst, sondern eine Festlegung mit einem Zuhause.

**Klärung im Gespräch, kein Formular.** Die Erstanlage folgt derselben Regel wie alles andere: Die Instanz bildet Annahmen, legt sie im Plan vor, der Entwickler korrigiert in Prosa (1.3.4). Sie arbeitet also keine Fragenliste ab, sondern liest zuerst das Projekt und legt dann **einen vollständigen Vorschlag** vor, in dem jede Annahme sichtbar ist und die verworfenen Alternativen benannt sind.

Ganz ohne Klärung geht es dennoch nicht: Was sich aus dem Projekt nicht ablesen lässt und wofür es keine tragfähige Annahme gibt, wird besprochen — so wenige Punkte wie möglich, jeder mit einem Vorschlag, und die Antworten wandern in die Skill-Parameterdatei, damit sie nie zweimal erfragt werden. Dazu gehört regelmäßig die Frage, ob die Einstiegsform einen eigenen Ordner bekommt oder ihre eine Datei ohne Ordner im Projekt liegt.

**Was die Instanz vorher liest** — alles im Projekt ohne Rückfrage, alles nur lesend: Gibt es schon Text, der als Doku gemeint ist (README, `docs/`, Konzeptdateien)? Wie groß ist der Code, wie viele Module? Gibt es eine Liste offener Schritte? Führt das Repository mehrere Vorhaben? Wie schreibt der Entwickler Prosa — ein Absatz je Zeile oder umbrochen? Daraus folgt der Vorschlag; was sich nicht ablesen lässt, wird angenommen und als Annahme gekennzeichnet.

**Der Vorschlag im Plan** nennt sechs Dinge, jedes mit Begründung in einem Satz:

1. **Ort der Doku** — ein Ordner, Vorschlag der im Projekt übliche (falls das klar aus den Informationen über die bestehende Projektstruktur hervorgeht) oder `dev-doc/`, `design-doc/`, `accompanying-doc/`, `accomp-doc/`, `accomp-dev-doc/` oder `accomp-design-doc/`. Beachte: Dieser Skill dient einer projektbegleitenden Dokumentation der Entwicklung und nicht einer in sich abgeschlossenen Projektdokumentation oder Anwenderdokumentation. Der übliche Ordner `doc/` für die Dokumentation des fertigen Projektvorhabens ist deshalb meist nicht der richtige Platz. Das sollte dem Entwickler gesagt werden, wenn er `doc/` unter der Projektwurzel vorschlägt. Letztlich ist aber jede finale Vorgabe des Entwicklers als Platz dieser Dokumentation zu akzeptieren.
2. **Gliederung** — eine der drei Formen unten, mit Begründung, warum diese zur Größe des Vorhabens passt.
3. **Rollen der Abschnitte** — welcher Abschnitt welche Rolle trägt (1.3.3). Besonders: ob es einen Abschnitt gibt, der Festlegungen zueinander in Beziehung setzt (Funktion `relate`). Das ist die folgenreichste Einzelheit der Erstanlage, denn ohne einen solchen Text hat die Auswirkungsrechnung keine Kanten über Kapitelgrenzen hinweg (1.7.4).
4. **Ort des Registers** — Standard ist `decisions.md` im Doku-Ordner. Dem Entwickler kann aber angeboten werden, die Metainformationen stattdessen in einem Ordner unterhalb von `.claude/` abzulegen.
5. **Ort der geplanten Schritte** — eigene Datei oder Abschnitt mit der Rolle `plan` in einer vorhandenen Datei. Bei einer eigenen Datei für diesen Zweck wird dem Entwickler angeboten, diese ebenfalls im Doku-Ordner anzulegen oder alternativ unterhalb von `.claude/`.
6. **Layout der Prosa** — ein Absatz je Zeile oder Umbruch mit Leerzeilen; abgelesen, wo möglich.

**Die drei Gliederungsformen**, die der Skill anbietet:


| Form              | Woraus sie besteht                                                                                                                                                                                                                                                                                                                                                                                                           | Wofür                                                              |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| **Einstiegsform** | eine einzige Datei als `accompanying-doc` mit der Rolle `building-blocks`, dazu das Register                                                                                                                                                                                                                                                                                                                                  | kleine Vorhaben; ein Modul; alles, was eine Person überblickt      |
| **Dreiteilung**   | Funktionale Aufgabenbeschreibung und Zusammenhänge (`relate`), Grundsätzliche Vorgaben (`global`), Details in Planung und Ausführung der zum Projekt gehörigen Module bzw. Einheiten (`building-blocks`), dazu Zusatzinformationen in Form von Anhängen zur Doku oder eigenen Dateien (auch an anderen Orten des Projekts, wie z.B. `research/`, `datasheets/` und Ähnliche.) — das Schema des Vorläufers (Anhang A) | der bewährte Mittelweg; wächst mit                                |
| **Sichtenform**   | ein Kern nach arc42: Ziele, Randbedingungen, Kontext, Lösungsstrategie, Bausteine, Laufzeit, Querschnitt                                                                                                                                                                                                                                                                                                                    | große oder langlebige Systeme; Projekte, die arc42 ohnehin führen |

Der Vorschlag wählt eine Form und nennt die anderen beiden mit einem Satz, warum sie hier nicht passen oder alternativ auch sinnvoll wären. Der Entwickler kann in Prosa widersprechen („nimm die Sichtenform"), und die Instanz baut den Plan um — nicht die Dateien.

**Planungen und Arbeitsschritte:** Mit dem Entwickler ist zu klären, wie der Projektfortschritt im Ganzen bzw. in großen Abschnitten sowie im Detail geplant werden soll:

- Soll es eine Art "Fahrplan" über mehrere Entwicklungsschritte hinaus geben? Wenn ja, in einer eigenen Datei (`work-plan.md`) oder innerhalb eines anderen Dokuments?
- Soll die detaillierte Planung eines oder weniger aufeinanderfolgenden Schritte nur im Chat bleiben, immer in einer eigenen Datei angelegt werden (`plan-<bezeichnung>.md`, wohin?) oder in voller Detaillierung in den `work-plan` oder einer vergleichbaren Datei des Projekts?
- Werden abgearbeitete Schritte aufgezeichnet? Wenn ja: In einer eigenen Datei (`status.md` oder `history.md`), die die abgearbeiteten Schritte als Liste aus dem `work-plan` übernimmt (der Text wandert dorthin), oder in einer entsprechenden Sektion des `work-plan` oder der Doku selbst?

**Was nach der Freigabe entsteht:** die Dateien der gewählten Form, jede mit Überschriften und Rollenmarkern, aber **ohne leere Kapitelhüllen**; das Register als leere Datei mit ihrer Rolle; die Skill-Parameterdatei mit den Werten, die aus dem Plan folgen — damit sie in keiner späteren Sitzung erneut erfragt werden. Ein Gerüst ist eine Ordnung, kein Vorrat: Ein Abschnitt entsteht, wenn er etwas zu halten hat.

**Was nicht entsteht:** kein Inhalt, den der Entwickler nicht geliefert hat. Die Instanz füllt keine Ziele, keine Randbedingungen und keine Vorgaben aus eigener Vermutung — sie legt Überschriften an und sagt, was dort hingehört.

**Grenze zur Leistung 2.** Hat das Projekt bereits eine Doku, gibt es keine Erstanlage. Dann gilt der Einstieg (1.7.2): Die vorhandene Struktur bleibt, wie sie ist, und bekommt am Berührungspunkt Rollen und Marker. Eine vorhandene Doku wird nie umgebaut, um zu einer der drei Formen zu passen.

**Umkehrbarkeit.** Alles, was die Erstanlage erzeugt, ist gewöhnlicher Text und eine Konfigurationsdatei. Die Form ist keine Festlegung auf Dauer: Wer später von der Einstiegsform zur Dreiteilung wechselt, verschiebt Prosa und ändert Rollenmarker; IDs, Register und Ereigniszeilen bleiben davon unberührt, weil keine von ihnen an einer Datei oder einem Kapitel hängt (Bedingung 2 in Kapitel 2.2).

> Geprüft: Ok.

### 1.7.2 Einstieg in eine vorhandene Doku

Ein typischer Fall, denn die meisten Projekte haben schon etwas Text. Der Einstieg geschieht **am Berührungspunkt und nie als Gesamtmigration** — außer der Entwickler fordert eine ausdrücklich; abgefragt wird das nie (Kapitel 3.2.7, die Fähigkeit dazu trägt der Skill `konzept-segmentierung`): Nur die Festlegungen, die ein Schritt tatsächlich berührt, bekommen Marker und Registerzeilen — über den Plan, mit Annahmen, die der Entwickler korrigieren kann (Kapitel 3.1). Rollen bekommen die Abschnitte ebenso: vorgeschlagen, wenn ein Abschnitt berührt wird, nicht vorab für das ganze Dokument. Eine Doku ohne einen einzigen Marker ist deshalb kein Fehlerzustand; sie ist der Anfangszustand, und der Skill liefert in ihr bereits das Wichtigste — Kollisionen werden geparkt statt abgeschossen (1.7.5).

> Geprüft: kleiner Ergänzung -> bitte gegenprüfen. Sonst ok.

### 1.7.3 Laufende Pflege während der Implementierung

Was der Vorläufer die Arbeitsschleife nannte (Anhang A, Abschnitt A.8), bleibt: Doku und Code entstehen im Wechsel, nicht nacheinander. Neu ist die Buchführung, die dabei mitläuft — Marker und Registerzeilen werden mit der Ausführung eines freigegebenen Plans geschrieben, Reibung wird vermerkt, wenn ein Sonderfall nur wegen einer Festlegung existiert, und eine verworfene Idee hinterlässt eine Bestätigungszeile. Der Entwickler sieht davon den Planabschnitt „Berührte Festlegungen" und sonst nichts. Was dabei überhaupt in die Prosa aufgenommen wird, statt dem Code oder einer anderen Dokumentation überlassen zu bleiben, steht in Kapitel 1.3.7.

**Dazu gehört eine Festlegung darüber, wo eine Planung liegt — und die muss der Skill treffen.** Der Vorläufer verlangte, jede Planung in den Fahrplan zu schreiben, beim betreffenden Schritt ausdetailliert. Das hat sich für viele Fälle als ungünstig erwiesen: Der Fahrplan trägt, **was** zu tun ist und in welcher Dringlichkeit, nicht **wie** — er ist keine Dokumentation und keine Planungsablage, sofern der Nutzer das nicht explizit einfordert (entschieden am 2026-09-24). Warum das so ist und woran es sich zeigte, steht in Kapitel 3.4.3.

Dass der Skill das regeln **muss**, hat einen zweiten Grund: Die bestehenden Anweisungen widersprechen sich. Die globale Regel nennt drei mögliche Orte und fragt, wenn keiner geregelt ist; die Projektregel dieses Repositories verbietet eigene Plan-Dateien. Solange beides nebeneinandersteht, hängt die Antwort davon ab, welche Datei zuerst gelesen wird. Der Skill entscheidet die Frage einmal für alle Projekte, und die globale Regel tritt dann von selbst zurück — sie gilt nur, „wenn der Ablageort nicht klar geregelt ist".

**Wo eine Planung steht und was ein Schritt im Fahrplan davon zeigt, ist entschieden** (2026-09-24, vormals Q-12; Einzelheiten in Kapitel 3.4.3):

1. Ein Schritt im Fahrplan beschreibt nur Ziel, Grund der Dringlichkeit, Umbauziel und — falls vorhanden — einen Verweis auf die Planung; nicht den Weg dorthin, außer der Entwickler fordert das für einen Schritt ausdrücklich ein (1.7.3 oben).
2. Die eigentliche Planung steht an einem von drei Orten, je nach Länge und Haltbarkeit: bis etwa zehn Sätze direkt im Schritt; trägt sie Festlegungen über das System, die den Code überdauern, in der Doku beim zuständigen Kapitel; beschreibt sie nur den Arbeitsweg und ist danach wertlos, in einer eigenen Planungsdatei im Projekt.
3. Nach der Ausführung wandert, was zur Beurteilung nötig bleibt, in die Doku; die Planungsdatei wird gelöscht, die Statusdatei nennt sie.
4. Der Kontext-Haushalt heißt seitdem „Planung an ihrem Ort vertiefen", nicht „Fahrplan detaillieren".

Damit tritt die bisherige globale Regel — drei mögliche Orte, Nachfrage wenn keiner geregelt ist — für dieses Vorhaben zurück; welche Anweisungen das im Einzelnen betrifft, steht in Kapitel 3.9.1.

**Wie genau ein Schritt sein Umbauziel benennt, ist noch offen.** Das Umbauziel ist der einzige Weg, auf dem eine Planung eine Festlegung öffnet: Ohne es bindet alles, was einmal entschieden wurde, und der Skill wäre an dieser Stelle wieder das Fehlbild Gesetz aus 1.2. Ein Schritt, der etwas umbauen will, muss also sagen können, was — und dafür gibt es zwei Größenordnungen. Die eine ist die einzelne Festlegung: Sie hat eine ID, die nie neu vergeben wird und kein Kapitel trägt, also eine Adresse, die jede Umsortierung überlebt. Die andere ist der ganze Bereich — „die Pipeline-Sektion wird ersetzt" —, und für den gibt es keine solche Adresse. Ein Bereich ist nur über seinen Ort greifbar, über Datei und Überschrift; Gliederung, Reihenfolge und Nummerierung aber gehören ausdrücklich dem Entwickler (1.3.4). Wer einen Bereich benennt, adressiert damit über etwas, das sich jederzeit ändern darf.

Die Entscheidung steht deshalb noch aus, und jeder der drei Wege verlangt dem Entwickler etwas anderes ab. **Den Bruch hinnehmen:** Der Schritt nennt Datei und Kapitel; wird die Datei umbenannt, meldet die Prüfung das zerbrochene Ziel, und repariert wird es über den nächsten Plan. Das ist billig und selten, steht aber gegen die Vorgabe, dass nichts an einem Dateinamen hängt (Vorgabe 2.3). **Dem Bereich eine eigene Kennung geben:** Ein Kapitel trüge neben seiner Rolle eine stabile Kennung, die das Umbauziel nennt; das überlebt jede Umbenennung, führt aber eine zweite Art von Kennung neben den IDs ein, die der Entwickler im Text mitführt. **Auf Bereichsziele verzichten:** Wer einen Bereich umbaut, zählt die betroffenen Festlegungen einzeln auf; keine neue Kennung und keine Ausnahme, dafür bei einem großen Umbau eine lange Aufzählung, die nachgeführt werden muss, sobald eine Festlegung hinzukommt. Was die Antwort für die Vorgaben bedeutet, steht in Vorgabe 2.3; die Schreibweise, die daraus folgt, in Kapitel 3.4.2.

### 1.7.4 Auswirkungen einer Änderung finden

**Das Bedürfnis.** Soll eine Festlegung geändert werden oder entfallen, muss vorher feststehen, welche anderen Festlegungen davon berührt sind. Wer das übersieht, merkt es erst, wenn etwas nicht mehr zusammenpasst — und dann ist die Ursache schwer zu finden, weil ein Übersehen keine Spur hinterlässt.

**Warum es schwer ist.** Die gefährlichen Fälle sind nicht die, die den geänderten Gegenstand beim Namen nennen; die findet jede Suche. Gefährlich sind die, die ihn stillschweigend voraussetzen — eine Festlegung über die Mittelung von Messwerten, die an der Rauschcharakteristik eines Sensors hängt, ohne den Sensor zu erwähnen. Sie ist nur über den Zusammenhang erreichbar, in dem beide einmal gemeinsam genannt wurden.

**Wie der Vorläufer es löste und warum das nicht reicht.** Er verlangte Handarbeit: Segment 1 war „der Suchweg jeder Auswirkungsanalyse", und die Arbeitsschleife forderte, dort zu suchen, welche weiteren Sektionen betroffen sind (Anhang A, Abschnitte A.6 und A.8). Das setzt voraus, dass jemand vollständig sucht — bei jeder Änderung, auch bei der zwanzigsten in einer langen Sitzung.

**Was der Skill stattdessen tut.** Aus dem Text lässt sich ablesen, welche Festlegungen miteinander in Beziehung stehen: Sie werden im selben Absatz genannt, im selben Abschnitt, oder sie werden in einem Text mit der Funktion `relate` gemeinsam zitiert. Daraus entsteht ein Geflecht, über das sich von einer geänderten Festlegung aus **Kandidaten** einsammeln lassen — dazu Treffer der Suchschlüssel als eigene Quelle. Das Skript liefert diese Kandidaten mit der Angabe, **warum** jeder einer ist. Die Instanz entscheidet je Kandidat, ob er wirklich betroffen ist, und nennt bei den bestätigten die gemessenen Umbaukosten. Die Entscheidung bleibt also beim Urteil, die Vollständigkeit der Vorlage bei der Mechanik.

**Wer die Suchschlüssel wählt und pflegt** (entschieden am 2026-09-24, vormals Q-05): die Instanz, beim Anlegen der Festlegung — sichtbar im Planabschnitt, damit der Entwickler sie korrigieren kann, ohne dass sie eine eigene Frage kosten. Gepflegt werden sie nur bei Reibung oder wenn `mentions` sichtbar Erwähnungen verfehlt.

**Die Spannung, die das Verfahren aushalten muss.** Zwei Anforderungen ziehen gegeneinander. Die Liste soll **kurz** sein, denn jeder Kandidat kostet eine Entscheidung der Instanz, und eine lange Liste bei jedem Schritt macht den Skill teuer. Die Liste soll **vollständig** sein, denn ein übersehener Kandidat ist genau der Fehler, den das Verfahren verhindern soll. Aufgelöst wird das durch einen Abbruchwert: Wie weit die Suche reicht, ist einstellbar — eng in der Lage `execute`, weiter in der Lage `design`. Wo die richtige Weite liegt, ist nicht auszurechnen, sondern zu messen; deshalb prüft die Probe beides, die Länge der Liste **und** wie viel davon die Instanz nicht als unerheblich verwirft (Kapitel 3.8).

**Woran sich das Verfahren rechtfertigt.** Für Festlegungen, die den geänderten Gegenstand nennen, genügen die Suchschlüssel. Das Geflecht verdient sich allein an den anderen. Stellt die Probe fest, dass es keine solchen Funde gibt, ist die Rechnung überflüssig und der Skill behält nur die Erwähnungssuche. Diese eine Zahl entscheidet über den Bestand des ganzen Teils.

**Was es voraussetzt.** Beziehungen über Kapitelgrenzen hinweg entstehen nur dort, wo ein Text Festlegungen aus verschiedenen Kapiteln gemeinsam nennt — also in einem Abschnitt mit der Funktion `relate`. Fehlt er, bleiben nur Nähe innerhalb eines Kapitels und die Suchschlüssel. Deshalb ist die Frage nach einem solchen Text die folgenreichste Einzelheit der Erstanlage (1.7.1), und deshalb zeigt Szene 8 den Nutzen erst am gewachsenen Vorhaben (1.6.8).

**Was ausgeschlossen bleibt.** Keine semantische Suche, keine Einbettungen, kein Index — das wäre eine eigene Infrastruktur je Projekt und damit das große Softwareprojekt, das dieses Vorhaben nicht sein will (Bedingung 3 in Kapitel 2.2). Alles, was der Skill über Zusammenhänge weiß, steht sichtbar im Text des Entwicklers.

**Eine Wahl, die der Entwickler bewusst treffen können muss.** Die Rechnung läuft ohne jede fremde Bibliothek; sie kann aber eine benutzen, wenn eine vorhanden ist, und rechnet dann schneller und in mehr Varianten. Es ist genau eine, und sie heißt `networkx` — eine Graphenbibliothek, die kürzeste Wege in gewichteten Graphen fertig mitbringt; was der Skill ohne sie leistet, rechnet ein eingebauter Weg von etwa dreißig Zeilen (Kapitel 3.6.1). Der Name steht hier und nicht erst in Kapitel 3, weil die Entscheidung dem Entwickler gehört: Wer gefragt wird, ob etwas auf seinem Rechner installiert werden soll, muss wissen, worum es geht. Vorhanden ist so etwas auf einem Entwicklungsrechner meist nur zufällig — und **was niemand kennt, installiert niemand.** Deshalb gilt: Braucht der Skill die Rechnung zum ersten Mal und die Bibliothek fehlt, erklärt die Instanz dem Entwickler in zwei Sätzen, was sie besser machen würde, und fragt. Er kann sie installieren lassen, selbst installieren oder ablehnen — und **seine Antwort wird festgehalten**, damit die Frage nie zweimal kommt. Drei Zustände sind zu unterscheiden: noch nicht geprüft und nicht gefragt (der Anfangszustand), benutzen, nicht benutzen. Ohne die Bibliothek arbeitet der Skill vollständig weiter; sie ist Beschleunigung, nicht Voraussetzung. Die Einzelheiten stehen in Kapitel 3.5.2 und 3.6.1.

**Zitatmarker außerhalb der Funktion `relate` bleiben optional** (entschieden am 2026-09-24, vormals Q-06): Ob `mentions` ohne sie zu viel übersieht, entscheidet die Probe (Kapitel 1.9, 3.8) — ein einmaliger Test in der Entwicklung dieses Skills, nicht ein Mechanismus, der mit dem Skill ausgeliefert wird. Verfehlt die Kandidatenliste dort ihre Schwelle, wird `marking: full` zum Standard nachgezogen.

**Was eine Kante im Graphen bedeutet, ist entschieden** (2026-09-24, vormals Q-20): „Steht im Text nahe" — mechanisch, wie in Kapitel 3.6.5 beschrieben (gleicher Absatz, gleicher Abschnitt, Nachbarabschnitt, gleiches Kapitel, mit abnehmenden Gewichten). „Hängt inhaltlich zusammen" wäre das bessere Kriterium, aber unbezahlbar, wenn es für jede Festlegung im Dokument berechnet würde. Nötig ist das nicht: Der Graph liefert nur günstig eine kurze Kandidatenliste; die inhaltliche Beurteilung geschieht ohnehin nachgelagert, je Kandidat, durch die Instanz (Schritt 4 in Szene 8, Kapitel 1.6.8) — dort kostet sie nur einmal je Kandidat der Vorauswahl, nicht einmal je Fakt im Dokument.

### 1.7.5 Einen Bereich neu denken

Die Leistung, um derentwillen das Vorhaben begonnen wurde (1.2, Fehlbild Gesetz). Bittet der Entwickler um Alternativen oder bringt eine Idee, liest die Instanz die Doku als **Stand, nicht als Vorgabe**, führt den Gedanken zu Ende und parkt jede Kollision in einem Satz, statt sie als Ablehnung zu formulieren. Welche Festlegung dabei wie schwer wiegt, sagt ihre Härte (Kapitel 3.1).

> Geprüft: Ok.

### 1.7.6 Prüfen und Aufräumen

Beim Öffnen eines Bereichs, vor jedem Commit und am Sitzungsstart läuft eine nur lesende Prüfung: Marker ohne Registereintrag, Einträge ohne Marker, unlesbare Zeilen, zerbrochene Umbauziele, geänderte Definitionssätze — Letztere erkannt über einen gespeicherten Fingerabdruck je Definitionssatz (entschieden am 2026-09-24, vormals Q-04). Bevor eine Abweichung der Instanz gemeldet wird, prüft das Skript rein mechanisch, ob nur wenige Einzelzeichen abweichen — ein Hinweis auf reine Formatierung oder Rechtschreibung: Dann ist das keine Entscheidungsgrundlage, sondern löst nur eine stille Neuberechnung des Fingerabdrucks aus (Kapitel 3.6 und 3.7).

**Die drei Anlässe reichen verschieden weit — und ob der dritte bleibt, ist offen.** Die Prüfung beim Öffnen eines Bereichs sieht diesen Bereich; die Prüfung vor dem Commit sieht, was zum Commit ansteht. Zwei Lücken bleiben. Die eine: Der Entwickler bearbeitet seine Doku zwischen zwei Sitzungen selbst — kein Edit der Instanz, kein Commit, also kein Anlass, der davon etwas bemerkte. Die andere: Nach einer Verdichtung des Kontextes hat die Instanz ihren Stand verloren, ohne dass sich eine Datei geändert hätte. Der Sitzungsstart ist der einzige Anlass, der beides auffängt.

Er kostet dafür etwas, das keine andere Leistung des Skills kostet: **Er muss je Projekt eingerichtet werden.** Das steht gegen die Zusage aus 1.3.5 — die Absicherung kommt mit dem Skill und wirkt in jedem Projekt, das ihn führt, ohne dass dort etwas einzurichten wäre. Zu entscheiden ist deshalb zweierlei: ob die beiden Lücken diese eine Ausnahme wert sind, und ob man das jetzt entscheidet oder erst, wenn die Probe zeigt, wie oft sie in der Praxis auftreten (1.9). Wie der Hook gebaut wäre, steht in Kapitel 3.7.

**Der Lebenszyklus einer Festlegung ist Teil dieser Leistung, und er hat einen eigenen Grund.** Eine Festlegung, die überholt ist, verschwindet nicht einfach. Bliebe ihr Satz unmarkiert in der Prosa stehen, läse die Instanz ihn beim nächsten Mal als gültig — und das Fehlbild Gesetz wäre an genau dieser Stelle zurück, mit einer Festlegung, die niemand mehr vertritt. Deshalb gilt: **Was überholt ist, darf nicht unmarkiert dastehen.** Es bekommt entweder eine Nachfolgerin (`superseded … by`) oder entfällt ersatzlos (`retired`); der Eintrag im Register bleibt in beiden Fällen mit Datum bestehen.

Das hat einen zweiten Nutzen, der im Alltag mehr wiegt als der erste: **Alte Verweise lösen weiter auf.** Ein Commit-Text, ein älterer Absatz, ein Code-Kommentar, der eine abgelöste ID nennt, führt nicht ins Leere — das Register kennt die Nachfolgerin. Niemand muss vor dem Weiterarbeiten das Projekt nach alten Verweisen absuchen und sie geradeziehen.

Ob ein überholter Absatz in der Prosa stehen bleibt, entscheidet der Entwickler im Einzelfall — weil er als Begründung der Änderung noch wirkt, weil er Kontext verwässert, oder weil gerade keine Zeit ist. Der Mechanismus verlangt nur den Marker. Die drei Fälle und ihre Behandlung stehen in Kapitel 3.2.6.

### 1.7.7 Keine Unterstützung

**Fehlt die Skill-Parameterdatei oder das Feld `mode`, wird nicht stillschweigend `on` angenommen** (entschieden am 2026-09-24, vormals Q-16): Die Instanz fragt einmal je Sitzung, ob der Skill hier geführt werden soll — wie `git-workbench` es tut —, und bietet an, die Skill-Parameterdatei anzulegen. Lehnt der Entwickler ab, fragt sie zusätzlich, ob `mode: off` trotzdem in einer Skill-Parameterdatei festgehalten werden soll, damit die Frage nicht wiederkehrt. Sagt er zu, folgt danach — nicht gleichzeitig — die eigentliche Erstanlage- oder Einstiegsfrage (Kapitel 1.7.1/1.7.2, Kapitel 3.10.2).

Ein Projekt kann den Skill auch ausdrücklich abwählen (`mode: off`). Dann fordert er nichts, schlägt nichts vor und zitiert keine Regel; vorhandene Doku wird vor Änderungen gelesen und dort gepflegt, wo das Projekt sie selbst pflegt (Kapitel 3.10.2). Das ist eine gültige Betriebsart, keine Nachlässigkeit.

**Der Trigger, der den Skill überhaupt lädt, bleibt davon unberührt** (entschieden am 2026-09-24, vormals Q-31): Ein Ladevorgang mit sofortigem Ende — der Skill endet bei `mode: off` sofort wieder — ist billiger als zwei Stellen, die zusammenpassen müssten.

> Geprüft: Ok.

## 1.8 Der Arbeitsablauf entlang der Anker

Abschnitt 1.7 sagt, **welche** Leistungen der Skill erbringt; dieser Abschnitt sagt, **an welchen Handlungen** sie ausgelöst werden. Der Skill greift nicht kontinuierlich ein, sondern an benannten Handlungen. Die Reihenfolge in einer Sitzung:

1. **Skillstart.** Geladen wird der Skill durch den geankerten Trigger in der Anweisungsdatei (Kapitel 3.11) — sobald eine Software-Änderung über eine lokal begrenzte Korrektur hinausgeht — oder durch Aufruf. Die Instanz liest die Skill-Parameterdatei oder erhebt aus dem Projekt, was sich ablesen lässt, und fragt nur, was sich nicht ablesen lässt (Kapitel 3.5 und 3.10). Ist der Skill für das Projekt abgewählt, endet er hier.
2. **Bereich öffnen.** Für den anstehenden Schritt oder die besprochene Idee listet das Skript die Festlegungen des berührten Bereichs mit ihrer Härte und meldet Abweichungen zwischen Prosa und Register (Kapitel 3.6).
3. **Lage bestimmen.** Aus dem Auftrag folgt, ob die Sitzung ausführt oder entwirft; im Zweifel eine Frage (Kapitel 3.1).
4. **Plan schreiben.** Jeder Plan trägt den Abschnitt „Berührte Festlegungen": Welche Festlegungen der Schritt berührt, welche Attribute die Instanz annimmt, welche Härte folgt, welche Kollisionen geparkt werden. Das Skript liefert das Gerüst; die Auswirkungskandidaten kommen aus dem Graphen der Marker (Kapitel 3.6). Der Entwickler liest, korrigiert in Prosa oder gibt frei (Kapitel 3.1 und 3.4).
5. **Ausführen.** Doku und Code entstehen im Wechsel; mit der Ausführung schreibt die Instanz Marker und Registerzeilen. Ein Sonderfall im Plan, der nur wegen einer Festlegung existiert, hinterlässt eine Reibungszeile; eine verworfene Idee oder ein abgelehnter Befund hinterlässt eine Bestätigungszeile (Kapitel 3.2).
6. **Hooks.** Nach jedem Doku-Edit meldet ein Lint normative Sätze ohne Marker; vor jedem Commit blockiert ein Abgleich strukturelle Inkonsistenzen; am Sitzungsstart meldet ein Zustandsbericht, was seit der letzten Sitzung geschah (Kapitel 3.7).

Ein Projekt, dessen Doku noch keinen Marker trägt, kommt am Berührungspunkt in das Schema: Nur die Festlegungen, die ein Schritt tatsächlich berührt, werden markiert — über den Plan, nie als Gesamtmigration. Eine völlig unmarkierte Doku erhält den wichtigsten Gewinn sofort, weil das Auffangergebnis der Härteliste zusammen mit der Lage „entwerfend" das Parken von Kollisionen statt ihres Abschusses bedeutet.

> Geprüft: Ok.

## 1.9 Der Weg zur Fertigstellung

Der Fahrplan (`work-plan.md`) führt neun Arbeitspakete: die Regelteile für Register und Marker, Planung und Skillstart; das Skript in zwei Stufen; die Hooks; das Zusammensetzen des Skills; die Probe; die Migration aus den bisherigen Anweisungsdateien.

**Die Probe ist das Tor, und sie ist nötig, weil der Rest nicht zu erdenken ist.** Die logische und codetechnische Seite dieses Vorhabens lässt sich am Schreibtisch klären — ob die Härteliste widerspruchsfrei ist, ob die Grammatik parsbar bleibt, ob die Hooks feuern. Geklärt heißt dabei belegt, nicht behauptet: Das Skript trägt Prüffälle, deren Fixture auch absichtlich beschädigte Eingaben enthält — „keine Befunde" zählt erst, wenn die Beschädigungen gefunden werden (Kapitel 3.6.8). Fünf Dinge lassen sich so nicht klären, weil sie vom Verhalten der Instanz und vom Zuschnitt einer echten Doku abhängen: ob die Instanz die Marker in der Praxis wirklich setzt; ob sie Kollisionen parkt statt sie abzuschießen; wie oft der Lint falschen Alarm schlägt; wie lang die Kandidatenlisten werden und wie viel davon brauchbar ist; und was der Skill an Kontext kostet. Über all das entscheidet eine Messung, nicht ein Argument.

**Die beiden ersten Punkte sind von anderer Art als die übrigen drei.** Setzt die Instanz die Marker nicht oder schießt sie Ideen weiterhin ab, ist nicht ein Wert falsch eingestellt, sondern das Design gescheitert — dann geht es zurück zu den Härteregeln und zum Register, nicht weiter zur Migration. Bleiben dagegen Kandidatenlisten zu lang oder meldet der Lint zu viel, sind Werte zu justieren und die Probe zu wiederholen. Erst wenn alle Schwellen erreicht sind, werden die globalen Anweisungen umgezogen und der Skill installiert (Kapitel 3.9). Der Aufbau der Probe, ihre Messgrößen und Schwellen stehen in Kapitel 3.8.

**Die Messgrößen und Schwellen der Probe sind bestätigt** (entschieden am 2026-09-24, vormals Q-28, Tabelle in Kapitel 3.8.4): Verfehlt „Marker gesetzt" oder „Parken statt Abschuss" ihre Schwelle, ist das Design gescheitert — zurück zu Kapitel 3.1/3.2. Verfehlen Kandidatenliste oder Fehlalarme ihre Schwelle, werden nur Werte nachjustiert und die Probe wiederholt (Kapitel 3.8.5). Am unsichersten bleibt „Kontext-Mehraufwand", weil nur grob messbar.

> Geprüft: Ok.

## 1.10 Was dieses Vorhaben nicht ist

Keine Oberfläche, keine Editor-Erweiterung. Keine Einbettung fremder Werkzeuge (Anforderungs-Tracing, Entscheidungsverwaltung); ihre Ideen — Fingerabdruck, kaskadierende Meldung bei Änderung, Lebenszyklus mit Nachfolger — werden übernommen, nicht ihre Programme. Keine semantische Suche; Zusammenhänge kommen aus Markern, Nähe im Text und Suchschlüsseln. Kein automatisches Umschreiben von Prosa; das Skript listet, die Instanz schlägt im Plan vor, der Entwickler gibt frei. Kein Lesen fremder ID-Systeme; das ist eine spätere Ausbaustufe.

> Geprüft: Ok.

## 1.11 Verhältnis zum Vorläufer

**Der Vorläufer ist vollständig in Anhang A archiviert** — vier Phasen, dreigeteilte Segmentstruktur, Prosa-Code-Grenze, ein normatives Zuhause je Aussage, Arbeitsschleife, Fahrplan und Status, Reviews und ihr Anhang, dazu der stille Trigger und die Begründungen der README. Wo diese Doku Begriffe wie „Dreiersschema", „Arbeitsschleife" oder „Prosa-Code-Grenze" benutzt, ist dort nachzulesen, was sie bedeuten. Der Anhang ist nötig, weil die drei Dateien des Vorläufers mit Fahrplanschritt 7 verschwinden; danach gäbe es außerhalb der Git-Historie keine Quelle mehr.

Sein Regeltext bleibt der Sache nach erhalten und wird zum Regelteil `standard.md`, mit drei Anpassungen: Die drei Segmente werden zu empfohlenen Rollen (Kapitel 3.3), nicht zu verlangter Struktur. Die Phasen gelten je Bereich, nicht je Projekt — ein Bereich kann in die Findung zurück, während der Rest in der Implementierung bleibt; die Lage „entwerfend" ist die Findungs- und Fixierungsphase für diesen Bereich. Und die Regel, wo ein Plan steht, wird durch Kapitel 3.4 ersetzt.

Was der Vorläufer nicht leisten konnte und was dieses Vorhaben deshalb hinzufügt: Abweichungen und Vereinfachungen der Struktur mussten bei kleineren Projekten immer wieder neu ausgehandelt und zusätzlich in Anweisungen gebacken werden; Umstrukturierungen und Kapitelneunummerierungen waren aufwändig und fehleranfällig. An die Stelle beider Mühen treten Rollen statt Nummern, Marker statt Struktur und das Register.

> Geprüft: Ok.