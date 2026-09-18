# 1 Zusammenhänge

Dieses Dokument ist die Implementierungsdoku des Vorhabens `software-design-doc` — eines Skills für die projektbegleitende Softwaredokumentation: Ziel, Randbedingungen, allgemeine und spezielle Festlegungen bis zur Detailbeschreibung der Ausführung. Es folgt dem Schema des Vorläufers (drei Segmente, Fahrplan, Status; Anhang A) und wendet die neuen Ideen des Vorhabens — Marker, Register, Rollen — auf sich selbst **nicht** an; das geschieht frühestens nach der Probe (Kapitel 3.8).

Die Segmente sind: dieses Kapitel 1 mit den Zusammenhängen, Kapitel 2 mit den projektweiten Vorgaben, Kapitel 3 mit den Einheiten. Daneben `work-plan.md` (Fahrplan) und `status.md`. Zwei Anhänge: **Anhang A** archiviert den Vorläufer — das Dokumentationsschema, auf dessen Erfahrungen dieses Vorhaben aufbaut und auf das die Kapitel mehrfach verweisen; **Anhang B** trägt den Verlauf der Recherchen und das Rechenmodell.

Noch nicht entschiedene Punkte stehen als Zitatblöcke `[Q-nn] Entscheidungsgrundlage` dort, wo ihr Kontext steht, mit Optionen, Vorschlag und einer Zeile **Antwort:** für den Entwickler; der Leseplan dazu steht am Anfang von `work-plan.md`. Was nicht so gekennzeichnet ist, gilt als geplant.

## 1.1 Name des Skills

Der Skill hieß `software-dev-doc-fh`. Das Kürzel `-fh` bezeichnete die Arbeitsweise eines bestimmten Entwicklers; mit der Verallgemeinerung auf Rollen, Register und Härteregeln ist der Skill für jeden mit einem ähnlichen Ansatz nutzbar, und das Kürzel entfällt. Der neue Name ist `software-design-doc`: Was der Skill pflegt, ist im Fachjargon ein Design Doc — Kontext und Ziel, Randbedingungen, Entscheidungen mit Alternativen, Detail bis zur Ausführung. Das Präfix `software-` vermeidet die Verwechslung mit Produkt- oder Oberflächendesign, die `design-doc` allein hätte. Erwogen wurden außerdem `solution-design-doc` und `living-design-doc` (das die parallele Pflege zum Code betont, aber mit dem etablierten Begriff „Living Documentation" für generierte Doku kollidiert). Die Entscheidung ist bis zur Installation ohne Kosten umkehrbar; Skill-Parameterdatei und Skript folgen dem Namen (Kapitel 3.5 und 3.6).

Der Skill ist auf Softwareentwicklung zugeschnitten, aber nicht durchgehend: Softwarespezifisch sind der Regeltext des Vorläufers als Regelteil (Phasen, Segmente, Arbeitsschleife; Anhang A), die Signalwörter des Lints und die Suche nach Erwähnungen im Code. Der Kern — Festlegungen mit Härte, Register, Rollen, geplante Schritte — kennt keinen Code und könnte andere Entwicklungsaufgaben ebenso tragen. Ob er das tut, zeigt sich erst, wenn die Regelteile geschrieben sind; dann wäre `solution-design-doc` der passendere Name.

> **[Q-32] Entscheidungsgrundlage — Name nach Abschluss der Regelteile prüfen**
> Kontext: `software-design-doc` ist akzeptiert. Der Kern des Skills ist domänenneutral, die Ränder sind es nicht. Sollte sich am Ende zeigen, dass die softwarespezifischen Teile abtrennbar sind (eigener Regelteil, eigener Skill-Parameter), trüge der Skill auch andere Entwicklungsaufgaben, und der Name wäre zu eng.
> Optionen: (a) beim Zusammensetzen (Schritt 7) prüfen, ob die softwarespezifischen Teile in einem Regelteil isoliert sind; wenn ja, Umbenennung in `solution-design-doc` vor der Installation; (b) Name beibehalten, Domänenneutralität nicht anstreben.
> Vorschlag: (a) — die Prüfung kostet nichts, solange nicht installiert ist.
> Gewicht: klein · Blockiert: Fahrplanschritt 9
> Antwort:(a), 18.9.2026

## 1.2 Ausgangslage: zwei Fehlbilder

Der Vorläufer beschreibt die entwicklungsbegleitende Doku als dreigeteiltes Dokument mit Fahrplan und Status und eine Arbeitsschleife, in der Code und Doku im Wechsel entstehen (vollständig in Anhang A). Für größere Projekte hat sich das bewährt. In der Praxis zeigten sich zwei Fehlbilder, die beide auf denselben Ursachen beruhen.

**Fehlbild Intensität.** Bei kleinen Vorhaben, bei kurzen Eingriffen in ein laufendes Projekt und bei Projekten, deren Doku anders aufgebaut ist, verweist die Instanz beharrlich auf Segmente, Fahrplan und Statusdatei und verlangt Struktur, die nichts zu halten hat. Ursache: Der Standard war als Abschnitt der globalen Anweisungsdatei in jeder Sitzung geladen und kannte keine Frage, ob und in welcher Ausbaustufe ein Projekt ihn führt.

**Fehlbild Gesetz.** Sobald eine Doku steht, liest die Instanz jede Festlegung darin als bindend. Will der Entwickler einen Bereich neu denken, stößt jede Idee an eine bestehende Festlegung und wird verworfen, statt zu Ende gedacht zu werden; mit wachsender Doku wird die Instanz unkreativ. Ursache: Der Standard kannte nur eine Lesart der Doku — Doku als Vorgabe — und keine Regel dafür, wann eine Festlegung bindet und wann sie zur Disposition steht.

Hinter beiden liegt eine Eigenschaft der Instanz, die in diesem Repository gemessen wurde: Anweisungen, die eine Haltung beschreiben („behalte im Blick, ob …"), feuern nicht zuverlässig; Anweisungen, die an eine Handlung gebunden sind („bevor du zum ersten Mal …"), feuern. Und eine Instanz wägt mehrere Dimensionen nicht zuverlässig gegeneinander ab — sie läuft gegen Extrema. Jedes Verfahren, das von ihr Abwägung verlangt, scheitert an dieser Stelle.

## 1.3 Leitidee

Drei Sätze tragen das Vorhaben. Die Instanz wägt nicht, sie schlägt nach. Alles, was sie zum Nachschlagen braucht, steht außerhalb der Prosa des Entwicklers. Und der Entwickler schreibt seine Doku so, wie sie für Menschen am nützlichsten ist — der Skill fügt ihr Adressen hinzu, keine Logik.

### 1.3.1 Nachschlagen statt abwägen

Ob eine Festlegung in der aktuellen Arbeit bindet oder zur Disposition steht, ergibt sich aus wenigen Feldern, die zu ihr gehören — Art (von außen gegeben oder von uns gewählt), Grund, Status, Ereigniszeilen —, und aus den Umbauzielen der geplanten Schritte des Projekts. Eine geordnete Liste einzelner Prüfungen macht daraus die **Härte** der Festlegung; aus Härte und **Lage** der Sitzung (Beschlossenes umsetzen oder etwas neu denken) folgt das Verhalten — sechs Zellen, eine Handlung je Zelle (Kapitel 3.1). Nichts davon wird kombiniert oder gewichtet; die Instanz führt Prüfungen aus, sie bildet kein Urteil.

Die Felder **gehören** zur Festlegung, aber sie **stehen** nicht bei ihr im Text. Das ist der Punkt, an dem die folgenden Abschnitte ansetzen.

### 1.3.2 Der Mittelweg: normierte Felder, aber getrennt von der Prosa

Stünden Art, Grund, Status und Ereignisse als Metainformation im Text, wäre die Doku unlesbar und der Entwickler in ein formales Konzept gezwungen, das ihn einschränkt und mit Zusatzaufgaben belastet — inakzeptabel. Stünde umgekehrt gar nichts Maschinenlesbares im Text, müsste die Instanz jede Aussage interpretieren, und das Fehlbild Gesetz wäre zurück. Der Mittelweg: **Die Felder sind normiert, aber sie liegen in einem Register neben der Doku; die Prosa trägt je Festlegung nur einen kurzen Marker — eine Adresse, nichts sonst** (Kapitel 3.2). So bleibt der rote Faden eines Absatzes für den Leser erhalten, ein Absatz mit drei Festlegungen bleibt ein Absatz, und `grep` findet trotzdem alles zu einer Festlegung.

### 1.3.3 Abschnitte haben eine Rolle — und das Dokument trägt keine Bedeutung

Eine Doku besteht nicht nur aus Festlegungen. Es gibt Abschnitte, in denen der Entwickler Festlegungen aus verschiedenen Teilen zueinander in Beziehung setzt — die Übersicht, ein Ablauf, die Lösungsstrategie —, Abschnitte mit Vorgaben, die im ganzen Projekt gelten, Abschnitte, die eine einzelne Einheit beschreiben, und Abschnitte, in denen nur konzipiert wird und nichts bindet. Der Skill muss diese Arten unterscheiden, denn er tut in ihnen Verschiedenes. Er darf sie aber nicht an Kapitelnummern oder Überschriften erkennen: Nummern ändern sich beim Umsortieren, Überschriften sind frei formuliert und in jeder Sprache. Deshalb trägt ein Abschnitt ein kurzes Etikett an der Überschrift — seine **Rolle**, etwa „Laufzeitsicht" oder „Randbedingungen". Auch das ist keine Formalie für den Entwickler: Die Instanz erkennt aus dem Inhalt, welche Rolle ein Abschnitt hat, schlägt sie im Plan vor und schreibt sie mit dessen Ausführung, wie die Marker; der Entwickler bestätigt oder korrigiert in Prosa. Die Rollen sind nach einem etablierten Gliederungsschema benannt, damit der Entwickler versteht, was er da bestätigt; was der Skill in einem Abschnitt mit einer bestimmten Rolle tut, steht im Skill selbst (Kapitel 3.3). Rollen gelten je Abschnitt; je Aussage gibt es nur den Marker aus 1.3.2.

Damit steht im Dokument des Entwicklers genau zweierlei vom Skill: Marker an Festlegungen und Rollen an Überschriften. Beides sind Adressen. Aus einem Marker folgt nichts, ohne das Register zu lesen; aus einer Rolle folgt nichts, ohne den Skill zu lesen. **Keine Skill-Logik, kein Attribut, kein Zustand steht im Dokument des Entwicklers** — die Bedeutung liegt immer außerhalb. Das ist der Grundsatz, der die Doku lesbar hält und den Entwickler frei lässt, und Kapitel 2 macht ihn zur Vorgabe.

### 1.3.4 Was dem Entwickler gehört und was er trägt

Ihm gehört die Doku: Gliederung, Reihenfolge, Nummerierung, Sprache der Überschriften, Layout, ob Dreiersschema des Vorläufers (Anhang A) oder freiere Form, wo das Register liegt, wo geplante Schritte stehen. Der Skill bindet nichts an Nummern, Dateinamen oder Titel — nur an Rollen (Kapitel 3.3) —, und er fordert keine Struktur, die nichts zu halten hat; die Doku wächst an Festlegungen, nicht an Pflichten (Kapitel 3.5). Der Entwickler muss weder die Grammatik der Marker noch die des Registers noch die Namen der Härtewerte kennen.

Was er tut: Prosa schreiben, den Planabschnitt „Berührte Festlegungen" lesen und in Prosa antworten. Was er hinnimmt — das ist der ehrliche Preis: Klammern im Text, eine Registerdatei neben der Doku und einen Abschnitt in jedem Plan. Marker und Registerzeilen schreibt die Instanz mit der Ausführung eines freigegebenen Plans; schreibt der Entwickler selbst Prosa, findet der Lint unmarkierte Festlegungen, und die Instanz schlägt die Marker im nächsten Plan vor. Die Buchführung trägt die Instanz, die Kontrolle tragen Skript und Hooks — nie der Entwickler.

### 1.3.5 Was die Einhaltung sichert

Dass die Instanz Marker und Registerzeilen tatsächlich schreibt, sichern nicht Anweisungen, sondern **ein Skript und Hooks**, die nach jedem Doku-Edit und vor jedem Commit lesend prüfen (Kapitel 3.6 und 3.7). Anweisungen, die eine Haltung beschreiben, feuern nicht zuverlässig (1.2); ein Hook feuert immer.

## 1.4 Bild des fertigen Systems

Ein Projekt, das den Skill führt, hat seine Doku in Prosa — nach dem Dreiersschema des Vorläufers (Anhang A) oder in freierer Form —, in der bindende Sätze einen Marker tragen; je Doku eine Registerdatei mit Attributen, Ereignissen und Lebenszyklus je Festlegung; eine Skill-Parameterdatei in `.claude/`; geplante Schritte, wo immer sie stehen, die ihr Umbauziel nennen. Der Skill selbst besteht aus einer dünnen `SKILL.md`, die Lage und die Skill-Parameter bestimmt und die passenden Regelteile nachlädt, aus dem angepassten Regeltext des Vorläufers als eigenem Regelteil (Anhang A, Anpassungen in 1.9), aus einem Skript mit einem Modul für die Auswirkungsrechnung, und aus zwei Hooks, die mit dem Skill kommen, sowie einem dritten, den das Projekt einrichten kann.

## 1.5 Welche Arten der Unterstützung es gibt

Der Skill erbringt sieben unterscheidbare Leistungen. Sie sind nicht alle gleich häufig und nicht alle gleich eingreifend; was sie verbindet, ist die Rollenverteilung aus 1.3.4 — der Entwickler schreibt Prosa und entscheidet, die Instanz führt Buch, Skript und Hooks kontrollieren.

| | Leistung | Auslöser | Ergebnis |
|---|---|---|---|
| 1 | **Erstanlage** einer begleitenden Doku (1.5.1) | ausdrücklicher Auftrag | Gerüst aus Dateien, Rollen und leerem Register |
| 2 | **Einstieg** in eine vorhandene Doku (1.5.2) | Berührungspunkt | Marker und Registerzeilen für die berührten Festlegungen |
| 3 | **Laufende Pflege** (1.5.3) | Plan und seine Ausführung | Doku und Code im Wechsel; Ereigniszeilen |
| 4 | **Auswirkungen finden** (1.5.4) | Änderung an einer Festlegung | Kandidatenliste, gemessene Umbaukosten |
| 5 | **Einen Bereich neu denken** (1.5.5) | Idee, Bitte um Alternativen | zu Ende gedachte Vorschläge, geparkte Kollisionen |
| 6 | **Prüfen und Aufräumen** (1.5.6) | Bereich öffnen, Commit, Sitzungsstart | Befunde; Lebenszyklus abgelöster Festlegungen |
| 7 | **Nichts tun** (1.5.7) | `mode: off` | keine Wirkung |

### 1.5.1 Erstanlage einer begleitenden Doku

Das ist der Fall, in dem ein Projekt noch keine begleitende Doku hat und der Entwickler eine haben will. Er ist selten, aber folgenreich: Was hier entsteht, prägt die Arbeit der nächsten Monate.

**Auslöser.** Nur ein ausdrücklicher Auftrag des Entwicklers. Der Skill bietet die Erstanlage **nie von sich aus an** — von selbst wächst die Doku an Festlegungen und nicht an Pflichten (Leistung 2 und 3). Ein Projekt, das nur einen Schritt zu erledigen hat, bekommt kein Gerüst, sondern eine Festlegung mit einem Zuhause.

**Kein Fragebogen.** Die Erstanlage folgt derselben Regel wie alles andere: Die Instanz bildet Annahmen, legt sie im Plan vor, der Entwickler korrigiert in Prosa (1.3.4). Sie stellt also **nicht** fünf Fragen nacheinander, sondern liest zuerst das Projekt und legt dann **einen vollständigen Vorschlag** vor, in dem jede Annahme sichtbar ist und die verworfenen Alternativen benannt sind.

**Was die Instanz vorher liest** — alles ohne Rückfrage, alles nur lesend: Gibt es schon Text, der als Doku gemeint ist (README, `docs/`, Konzeptdateien)? Wie groß ist der Code, wie viele Module? Gibt es eine Liste offener Schritte? Führt das Repository mehrere Vorhaben? Wie schreibt der Entwickler Prosa — ein Absatz je Zeile oder umbrochen? Daraus folgt der Vorschlag; was sich nicht ablesen lässt, wird angenommen und als Annahme gekennzeichnet.

**Der Vorschlag im Plan** nennt sechs Dinge, jedes mit Begründung in einem Satz:

1. **Ort der Doku** — ein Ordner, Vorschlag der im Projekt übliche oder `doc/`.
2. **Gliederung** — eine der drei Formen unten, mit Begründung, warum diese zur Größe des Vorhabens passt.
3. **Rollen der Abschnitte** — welcher Abschnitt welche Rolle trägt (Kapitel 3.3). Besonders: ob es einen Abschnitt gibt, der Festlegungen zueinander in Beziehung setzt (Funktion `relate`). Das ist die folgenreichste Einzelheit der Erstanlage, denn ohne einen solchen Text hat die Auswirkungsrechnung keine Kanten über Kapitelgrenzen hinweg (1.5.4).
4. **Ort des Registers** — Standard ist `decisions.md` im Doku-Ordner.
5. **Ort der geplanten Schritte** — eigene Datei oder Abschnitt mit der Rolle `plan` in einer vorhandenen Datei.
6. **Layout der Prosa** — ein Absatz je Zeile oder Umbruch mit Leerzeilen; abgelesen, wo möglich.

**Die drei Gliederungsformen**, die der Skill anbietet:

| Form | Woraus sie besteht | Wofür |
|---|---|---|
| **Einstiegsform** | eine Datei mit der Rolle `building-blocks`, dazu das Register | kleine Vorhaben; ein Modul; alles, was eine Person überblickt |
| **Dreiteilung** | Zusammenhänge (`relate`), Vorgaben (`global`), Einheiten (`building-blocks`) — das Schema des Vorläufers (Anhang A) | der bewährte Mittelweg; wächst mit |
| **Sichtenform** | ein Kern nach arc42: Ziele, Randbedingungen, Kontext, Lösungsstrategie, Bausteine, Laufzeit, Querschnitt | große oder langlebige Systeme; Projekte, die arc42 ohnehin führen |

Der Vorschlag wählt eine Form und nennt die anderen beiden mit einem Satz, warum sie hier nicht passen. Der Entwickler kann in Prosa widersprechen („nimm die Sichtenform"), und die Instanz baut den Plan um — nicht die Dateien.

**Was nach der Freigabe entsteht:** die Dateien der gewählten Form, jede mit Überschriften und Rollenmarkern, aber **ohne leere Kapitelhüllen**; das Register als leere Datei mit ihrer Rolle; die Skill-Parameterdatei mit den Werten, die aus dem Plan folgen — damit sie in keiner späteren Sitzung erneut erfragt werden. Ein Gerüst ist eine Ordnung, kein Vorrat: Ein Abschnitt entsteht, wenn er etwas zu halten hat.

**Was nicht entsteht:** kein Inhalt, den der Entwickler nicht geliefert hat. Die Instanz füllt keine Ziele, keine Randbedingungen und keine Vorgaben aus eigener Vermutung — sie legt Überschriften an und sagt, was dort hingehört.

**Grenze zur Leistung 2.** Hat das Projekt bereits eine Doku, gibt es keine Erstanlage. Dann gilt der Einstieg (1.5.2): Die vorhandene Struktur bleibt, wie sie ist, und bekommt am Berührungspunkt Rollen und Marker. Eine vorhandene Doku wird nie umgebaut, um zu einer der drei Formen zu passen.

**Umkehrbarkeit.** Alles, was die Erstanlage erzeugt, ist gewöhnlicher Text und eine Konfigurationsdatei. Die Form ist keine Festlegung auf Dauer: Wer später von der Einstiegsform zur Dreiteilung wechselt, verschiebt Prosa und ändert Rollenmarker; IDs, Register und Ereigniszeilen bleiben davon unberührt, weil keine von ihnen an einer Datei oder einem Kapitel hängt (Bedingung 2 in Kapitel 2.2).

### 1.5.2 Einstieg in eine vorhandene Doku

Der Regelfall, denn die meisten Projekte haben schon Text. Der Einstieg geschieht **am Berührungspunkt und nie als Gesamtmigration**: Nur die Festlegungen, die ein Schritt tatsächlich berührt, bekommen Marker und Registerzeilen — über den Plan, mit Annahmen, die der Entwickler korrigieren kann (Kapitel 3.1 und 3.2.7). Rollen bekommen die Abschnitte ebenso: vorgeschlagen, wenn ein Abschnitt berührt wird, nicht vorab für das ganze Dokument. Eine Doku ohne einen einzigen Marker ist deshalb kein Fehlerzustand; sie ist der Anfangszustand, und der Skill liefert in ihr bereits das Wichtigste — Kollisionen werden geparkt statt abgeschossen (1.5.5).

### 1.5.3 Laufende Pflege während der Implementierung

Was der Vorläufer die Arbeitsschleife nannte (Anhang A, Abschnitt A.8), bleibt: Doku und Code entstehen im Wechsel, nicht nacheinander. Neu ist die Buchführung, die dabei mitläuft — Marker und Registerzeilen werden mit der Ausführung eines freigegebenen Plans geschrieben, Reibung wird vermerkt, wenn ein Sonderfall nur wegen einer Festlegung existiert, und eine verworfene Idee hinterlässt eine Bestätigungszeile. Der Entwickler sieht davon den Planabschnitt „Berührte Festlegungen" und sonst nichts.

### 1.5.4 Auswirkungen einer Änderung finden

Soll eine Festlegung geändert werden, liefert das Skript die Kandidaten, die davon berührt sein könnten: über den Graphen der Marker, über die Nähe im Text und über Suchschlüssel (Kapitel 3.6.5). Die Instanz entscheidet je Kandidat, ob er wirklich betroffen ist, und nennt die gemessenen Umbaukosten. Das ersetzt die Suche, die der Vorläufer über Segment 1 von Hand verlangte — und es ist der Grund, warum ein Text mit der Funktion `relate` so wertvoll ist.

### 1.5.5 Einen Bereich neu denken

Die Leistung, um derentwillen das Vorhaben begonnen wurde (1.2, Fehlbild Gesetz). Bittet der Entwickler um Alternativen oder bringt eine Idee, liest die Instanz die Doku als **Stand, nicht als Vorgabe**, führt den Gedanken zu Ende und parkt jede Kollision in einem Satz, statt sie als Ablehnung zu formulieren. Welche Festlegung dabei wie schwer wiegt, sagt ihre Härte (Kapitel 3.1).

### 1.5.6 Prüfen und Aufräumen

Beim Öffnen eines Bereichs, vor jedem Commit und am Sitzungsstart läuft eine nur lesende Prüfung: Marker ohne Registereintrag, Einträge ohne Marker, unlesbare Zeilen, zerbrochene Umbauziele, geänderte Definitionssätze (Kapitel 3.6 und 3.7). Dazu gehört der Lebenszyklus: Eine abgelöste Festlegung behält ihren Eintrag mit Datum und Nachfolger, damit alte Verweise sich weiter auflösen (Kapitel 3.2.6).

### 1.5.7 Keine Unterstützung

Ein Projekt kann den Skill abwählen (`mode: off`). Dann fordert er nichts, schlägt nichts vor und zitiert keine Regel; vorhandene Doku wird vor Änderungen gelesen und dort gepflegt, wo das Projekt sie selbst pflegt (Kapitel 3.5.1). Das ist eine gültige Betriebsart, keine Nachlässigkeit.

## 1.6 Der Arbeitsablauf entlang der Anker

Abschnitt 1.5 sagt, **welche** Leistungen der Skill erbringt; dieser Abschnitt sagt, **an welchen Handlungen** sie ausgelöst werden. Der Skill greift nicht kontinuierlich ein, sondern an benannten Handlungen. Die Reihenfolge in einer Sitzung:

1. **Skillstart.** Die Instanz liest die Skill-Parameterdatei oder erhebt aus dem Projekt, was sich ablesen lässt, und fragt nur, was sich nicht ablesen lässt (Kapitel 3.5). Ist der Skill für das Projekt abgewählt, endet er hier.
2. **Bereich öffnen.** Für den anstehenden Schritt oder die besprochene Idee listet das Skript die Festlegungen des berührten Bereichs mit ihrer Härte und meldet Abweichungen zwischen Prosa und Register (Kapitel 3.6).
3. **Lage bestimmen.** Aus dem Auftrag folgt, ob die Sitzung ausführt oder entwirft; im Zweifel eine Frage (Kapitel 3.1).
4. **Plan schreiben.** Jeder Plan trägt den Abschnitt „Berührte Festlegungen": Welche Festlegungen der Schritt berührt, welche Attribute die Instanz annimmt, welche Härte folgt, welche Kollisionen geparkt werden. Das Skript liefert das Gerüst; die Auswirkungskandidaten kommen aus dem Graphen der Marker (Kapitel 3.6). Der Entwickler liest, korrigiert in Prosa oder gibt frei (Kapitel 3.1 und 3.4).
5. **Ausführen.** Doku und Code entstehen im Wechsel; mit der Ausführung schreibt die Instanz Marker und Registerzeilen. Ein Sonderfall im Plan, der nur wegen einer Festlegung existiert, hinterlässt eine Reibungszeile; eine verworfene Idee oder ein abgelehnter Befund hinterlässt eine Bestätigungszeile (Kapitel 3.2).
6. **Hooks.** Nach jedem Doku-Edit meldet ein Lint normative Sätze ohne Marker; vor jedem Commit blockiert ein Abgleich strukturelle Inkonsistenzen; am Sitzungsstart meldet ein Zustandsbericht, was seit der letzten Sitzung geschah (Kapitel 3.7).

Ein Projekt, dessen Doku noch keinen Marker trägt, kommt am Berührungspunkt in das Schema: Nur die Festlegungen, die ein Schritt tatsächlich berührt, werden markiert — über den Plan, nie als Gesamtmigration. Eine völlig unmarkierte Doku erhält den wichtigsten Gewinn sofort, weil das Auffangergebnis der Härteliste zusammen mit der Lage „entwerfend" das Parken von Kollisionen statt ihres Abschusses bedeutet.

## 1.7 Der Weg zur Fertigstellung

Der Fahrplan (`work-plan.md`) führt neun Arbeitspakete: die Regelteile für Register und Marker, Planung und Skillstart; das Skript in zwei Stufen; die Hooks; das Zusammensetzen des Skills; die Probe; die Migration aus den bisherigen Anweisungsdateien. Die **Probe** (Kapitel 3.8) ist das Tor: Erst wenn sie zeigt, dass die Instanz die Marker setzt und Kollisionen parkt, werden die globalen Anweisungen umgezogen und der Skill installiert (Kapitel 3.9). Scheitert die Probe an diesen beiden Punkten, ist das Design falsch, nicht ein Skill-Parameter.

## 1.8 Was dieses Vorhaben nicht ist

Keine Oberfläche, keine Editor-Erweiterung. Keine Einbettung fremder Werkzeuge (Anforderungs-Tracing, Entscheidungsverwaltung); ihre Ideen — Fingerabdruck, kaskadierende Meldung bei Änderung, Lebenszyklus mit Nachfolger — werden übernommen, nicht ihre Programme. Keine semantische Suche; Zusammenhänge kommen aus Markern, Nähe im Text und Suchschlüsseln. Kein automatisches Umschreiben von Prosa; das Skript listet, die Instanz schlägt im Plan vor, der Entwickler gibt frei. Kein Lesen fremder ID-Systeme; das ist eine spätere Ausbaustufe.

## 1.9 Verhältnis zum Vorläufer

**Der Vorläufer ist vollständig in Anhang A archiviert** — vier Phasen, dreigeteilte Segmentstruktur, Prosa-Code-Grenze, ein normatives Zuhause je Aussage, Arbeitsschleife, Fahrplan und Status, Reviews und ihr Anhang, dazu der stille Trigger und die Begründungen der README. Wo diese Doku Begriffe wie „Dreiersschema", „Arbeitsschleife" oder „Prosa-Code-Grenze" benutzt, ist dort nachzulesen, was sie bedeuten. Der Anhang ist nötig, weil die drei Dateien des Vorläufers mit Fahrplanschritt 7 verschwinden; danach gäbe es außerhalb der Git-Historie keine Quelle mehr.

Sein Regeltext bleibt der Sache nach erhalten und wird zum Regelteil `standard.md`, mit drei Anpassungen: Die drei Segmente werden zu empfohlenen Rollen (Kapitel 3.3), nicht zu verlangter Struktur. Die Phasen gelten je Bereich, nicht je Projekt — ein Bereich kann in die Findung zurück, während der Rest in der Implementierung bleibt; die Lage „entwerfend" ist die Findungs- und Fixierungsphase für diesen Bereich. Und die Regel, wo ein Plan steht, wird durch Kapitel 3.4 ersetzt.

Was der Vorläufer nicht leisten konnte und was dieses Vorhaben deshalb hinzufügt: Abweichungen und Vereinfachungen der Struktur mussten bei kleineren Projekten immer wieder neu ausgehandelt und zusätzlich in Anweisungen gebacken werden; Umstrukturierungen und Kapitelneunummerierungen waren aufwändig und fehleranfällig. An die Stelle beider Mühen treten Rollen statt Nummern, Marker statt Struktur und das Register.
