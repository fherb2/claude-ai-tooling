# 1 Zusammenhänge

Dieses Dokument ist die Implementierungsdoku des Vorhabens `software-design-doc` — eines Skills für die projektbegleitende Softwaredokumentation: Ziel, Randbedingungen, allgemeine und spezielle Festlegungen bis zur Detailbeschreibung der Ausführung. Es folgt dem Schema des Vorläufers (drei Segmente, Fahrplan, Status; Anhang A) und wendet die neuen Ideen des Vorhabens — Marken, Register, Rollen — auf sich selbst **nicht** an; das geschieht frühestens nach der Probe (Kapitel 3.8).

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

Stünden Art, Grund, Status und Ereignisse als Metainformation im Text, wäre die Doku unlesbar und der Entwickler in ein formales Konzept gezwungen, das ihn einschränkt und mit Zusatzaufgaben belastet — inakzeptabel. Stünde umgekehrt gar nichts Maschinenlesbares im Text, müsste die Instanz jede Aussage interpretieren, und das Fehlbild Gesetz wäre zurück. Der Mittelweg: **Die Felder sind normiert, aber sie liegen in einem Register neben der Doku; die Prosa trägt je Festlegung nur eine kurze Marke — eine Adresse, nichts sonst** (Kapitel 3.2). So bleibt der rote Faden eines Absatzes für den Leser erhalten, ein Absatz mit drei Festlegungen bleibt ein Absatz, und `grep` findet trotzdem alles zu einer Festlegung.

### 1.3.3 Abschnitte haben eine Rolle — und das Dokument trägt keine Bedeutung

Eine Doku besteht nicht nur aus Festlegungen. Es gibt Abschnitte, in denen der Entwickler Festlegungen aus verschiedenen Teilen zueinander in Beziehung setzt — die Übersicht, ein Ablauf, die Lösungsstrategie —, Abschnitte mit Vorgaben, die im ganzen Projekt gelten, Abschnitte, die eine einzelne Einheit beschreiben, und Abschnitte, in denen nur konzipiert wird und nichts bindet. Der Skill muss diese Arten unterscheiden, denn er tut in ihnen Verschiedenes. Er darf sie aber nicht an Kapitelnummern oder Überschriften erkennen: Nummern ändern sich beim Umsortieren, Überschriften sind frei formuliert und in jeder Sprache. Deshalb trägt ein Abschnitt ein kurzes Etikett an der Überschrift — seine **Rolle**, etwa „Laufzeitsicht" oder „Randbedingungen". Auch das ist keine Formalie für den Entwickler: Die Instanz erkennt aus dem Inhalt, welche Rolle ein Abschnitt hat, schlägt sie im Plan vor und schreibt sie mit dessen Ausführung, wie die Marken; der Entwickler bestätigt oder korrigiert in Prosa. Die Rollen sind nach einem etablierten Gliederungsschema benannt, damit der Entwickler versteht, was er da bestätigt; was der Skill in einem Abschnitt mit einer bestimmten Rolle tut, steht im Skill selbst (Kapitel 3.3). Rollen gelten je Abschnitt; je Aussage gibt es nur die Marke aus 1.3.2.

Damit steht im Dokument des Entwicklers genau zweierlei vom Skill: Marken an Festlegungen und Rollen an Überschriften. Beides sind Adressen. Aus einer Marke folgt nichts, ohne das Register zu lesen; aus einer Rolle folgt nichts, ohne den Skill zu lesen. **Keine Skill-Logik, kein Attribut, kein Zustand steht im Dokument des Entwicklers** — die Bedeutung liegt immer außerhalb. Das ist der Grundsatz, der die Doku lesbar hält und den Entwickler frei lässt, und Kapitel 2 macht ihn zur Vorgabe.

### 1.3.4 Was dem Entwickler gehört und was er trägt

Ihm gehört die Doku: Gliederung, Reihenfolge, Nummerierung, Sprache der Überschriften, Layout, ob Dreiersschema des Vorläufers (Anhang A) oder freiere Form, wo das Register liegt, wo geplante Schritte stehen. Der Skill bindet nichts an Nummern, Dateinamen oder Titel — nur an Rollen (Kapitel 3.3) —, und er fordert keine Struktur, die nichts zu halten hat; die Doku wächst an Festlegungen, nicht an Pflichten (Kapitel 3.5). Der Entwickler muss weder die Grammatik der Marken noch die des Registers noch die Namen der Härtewerte kennen.

Was er tut: Prosa schreiben, den Planabschnitt „Berührte Festlegungen" lesen und in Prosa antworten. Was er hinnimmt — das ist der ehrliche Preis: Klammern im Text, eine Registerdatei neben der Doku und einen Abschnitt in jedem Plan. Marken und Registerzeilen schreibt die Instanz mit der Ausführung eines freigegebenen Plans; schreibt der Entwickler selbst Prosa, findet der Lint unmarkierte Festlegungen, und die Instanz schlägt die Marken im nächsten Plan vor. Die Buchführung trägt die Instanz, die Kontrolle tragen Skript und Hooks — nie der Entwickler.

### 1.3.5 Was die Einhaltung sichert

Dass die Instanz Marken und Registerzeilen tatsächlich schreibt, sichern nicht Anweisungen, sondern **ein Skript und Hooks**, die nach jedem Doku-Edit und vor jedem Commit lesend prüfen (Kapitel 3.6 und 3.7). Anweisungen, die eine Haltung beschreiben, feuern nicht zuverlässig (1.2); ein Hook feuert immer.

## 1.4 Bild des fertigen Systems

Ein Projekt, das den Skill führt, hat seine Doku in Prosa — nach dem Dreiersschema des Vorläufers (Anhang A) oder in freierer Form —, in der bindende Sätze eine Marke tragen; je Doku eine Registerdatei mit Attributen, Ereignissen und Lebenszyklus je Festlegung; eine Skill-Parameterdatei in `.claude/`; geplante Schritte, wo immer sie stehen, die ihr Umbauziel nennen. Der Skill selbst besteht aus einer dünnen `SKILL.md`, die Lage und die Skill-Parameter bestimmt und die passenden Regelteile nachlädt, aus dem angepassten Regeltext des Vorläufers als eigenem Regelteil (Anhang A, Anpassungen in 1.8), aus einem Skript mit einem Modul für die Auswirkungsrechnung, und aus zwei Hooks, die mit dem Skill kommen, sowie einem dritten, den das Projekt einrichten kann.

## 1.5 Der Arbeitsablauf entlang der Anker

Der Skill greift nicht kontinuierlich ein, sondern an benannten Handlungen. Die Reihenfolge in einer Sitzung:

1. **Skillstart.** Die Instanz liest die Skill-Parameterdatei oder erhebt aus dem Projekt, was sich ablesen lässt, und fragt nur, was sich nicht ablesen lässt (Kapitel 3.5). Ist der Skill für das Projekt abgewählt, endet er hier.
2. **Bereich öffnen.** Für den anstehenden Schritt oder die besprochene Idee listet das Skript die Festlegungen des berührten Bereichs mit ihrer Härte und meldet Abweichungen zwischen Prosa und Register (Kapitel 3.6).
3. **Lage bestimmen.** Aus dem Auftrag folgt, ob die Sitzung ausführt oder entwirft; im Zweifel eine Frage (Kapitel 3.1).
4. **Plan schreiben.** Jeder Plan trägt den Abschnitt „Berührte Festlegungen": Welche Festlegungen der Schritt berührt, welche Attribute die Instanz annimmt, welche Härte folgt, welche Kollisionen geparkt werden. Das Skript liefert das Gerüst; die Auswirkungskandidaten kommen aus dem Graphen der Marken (Kapitel 3.6). Der Entwickler liest, korrigiert in Prosa oder gibt frei (Kapitel 3.1 und 3.4).
5. **Ausführen.** Doku und Code entstehen im Wechsel; mit der Ausführung schreibt die Instanz Marken und Registerzeilen. Ein Sonderfall im Plan, der nur wegen einer Festlegung existiert, hinterlässt eine Reibungszeile; eine verworfene Idee oder ein abgelehnter Befund hinterlässt eine Bestätigungszeile (Kapitel 3.2).
6. **Hooks.** Nach jedem Doku-Edit meldet ein Lint normative Sätze ohne Marke; vor jedem Commit blockiert ein Abgleich strukturelle Inkonsistenzen; am Sitzungsstart meldet ein Zustandsbericht, was seit der letzten Sitzung geschah (Kapitel 3.7).

Ein Projekt, dessen Doku noch keine Marke trägt, kommt am Berührungspunkt in das Schema: Nur die Festlegungen, die ein Schritt tatsächlich berührt, werden markiert — über den Plan, nie als Gesamtmigration. Eine völlig unmarkierte Doku erhält den wichtigsten Gewinn sofort, weil das Auffangergebnis der Härteliste zusammen mit der Lage „entwerfend" das Parken von Kollisionen statt ihres Abschusses bedeutet.

## 1.6 Der Weg zur Fertigstellung

Der Fahrplan (`work-plan.md`) führt neun Arbeitspakete: die Regelteile für Register und Marken, Planung und Skillstart; das Skript in zwei Stufen; die Hooks; das Zusammensetzen des Skills; die Probe; die Migration aus den bisherigen Anweisungsdateien. Die **Probe** (Kapitel 3.8) ist das Tor: Erst wenn sie zeigt, dass die Instanz die Marken setzt und Kollisionen parkt, werden die globalen Anweisungen umgezogen und der Skill installiert (Kapitel 3.9). Scheitert die Probe an diesen beiden Punkten, ist das Design falsch, nicht ein Skill-Parameter.

## 1.7 Was dieses Vorhaben nicht ist

Keine Oberfläche, keine Editor-Erweiterung. Keine Einbettung fremder Werkzeuge (Anforderungs-Tracing, Entscheidungsverwaltung); ihre Ideen — Fingerabdruck, kaskadierende Meldung bei Änderung, Lebenszyklus mit Nachfolger — werden übernommen, nicht ihre Programme. Keine semantische Suche; Zusammenhänge kommen aus Marken, Nähe im Text und Suchschlüsseln. Kein automatisches Umschreiben von Prosa; das Skript listet, die Instanz schlägt im Plan vor, der Entwickler gibt frei. Kein Lesen fremder ID-Systeme; das ist eine spätere Ausbaustufe.

## 1.8 Verhältnis zum Vorläufer

**Der Vorläufer ist vollständig in Anhang A archiviert** — vier Phasen, dreigeteilte Segmentstruktur, Prosa-Code-Grenze, ein normatives Zuhause je Aussage, Arbeitsschleife, Fahrplan und Status, Reviews und ihr Anhang, dazu der stille Trigger und die Begründungen der README. Wo diese Doku Begriffe wie „Dreiersschema", „Arbeitsschleife" oder „Prosa-Code-Grenze" benutzt, ist dort nachzulesen, was sie bedeuten. Der Anhang ist nötig, weil die drei Dateien des Vorläufers mit Fahrplanschritt 7 verschwinden; danach gäbe es außerhalb der Git-Historie keine Quelle mehr.

Sein Regeltext bleibt der Sache nach erhalten und wird zum Regelteil `standard.md`, mit drei Anpassungen: Die drei Segmente werden zu empfohlenen Rollen (Kapitel 3.3), nicht zu verlangter Struktur. Die Phasen gelten je Bereich, nicht je Projekt — ein Bereich kann in die Findung zurück, während der Rest in der Implementierung bleibt; die Lage „entwerfend" ist die Findungs- und Fixierungsphase für diesen Bereich. Und die Regel, wo ein Plan steht, wird durch Kapitel 3.4 ersetzt.

Was der Vorläufer nicht leisten konnte und was dieses Vorhaben deshalb hinzufügt: Abweichungen und Vereinfachungen der Struktur mussten bei kleineren Projekten immer wieder neu ausgehandelt und zusätzlich in Anweisungen gebacken werden; Umstrukturierungen und Kapitelneunummerierungen waren aufwändig und fehleranfällig. An die Stelle beider Mühen treten Rollen statt Nummern, Marken statt Struktur und das Register.
