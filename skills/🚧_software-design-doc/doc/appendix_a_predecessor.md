# Anhang A — Der Vorläufer

In diesem Anhang wird das in den Monaten vor der Entstehung dieses Skills benutzte Dokumentationsschema beschrieben. Damit wurden wertvolle Erfahrungen gesammelt, insbesondere mit der hier beschriebenen Gliederung in drei Segmente (Hauptkapitel). Der neue Skill baut auf diesen Erfahrungen auf, erweitert sie aber in mehrfacher Hinsicht: Er lässt Abweichungen und Vereinfachungen in der Struktur der Dokumentation zu, und er formalisiert mit einer Reihe von Markern, einem Register und Regeln. Beim im Folgenden beschriebenen Modell mussten Abweichungen in der Dokumentation, vor allem bei kleineren Projekten zur Vereinfachung, immer wieder neu ausgehandelt und zusätzlich in Anweisungen gebacken werden. Umstrukturierungen oder Kapitelneunummerierungen der Doku waren außerdem eine recht aufwändige und fehleranfällige Aktion. Der neue Skill soll das nun für den Entwickler erheblich leichter machen. Da in der entwicklungsbegleitenden Doku aber mehrfach auf das bisherige Verfahren verwiesen wird, ist es im Folgenden als „historische Quelle" archiviert.

---

@CLAUDE: Der nachfolgende Abschnitt bis zum Marker „Anhang A — Ende" zitiert ein früheres Verfahren. Dabei werden auch Anweisungen formuliert. Beachte, dass diese Anweisungen für Dich hier im Projekt **KEINE** Anweisungen darstellen! Sie gehören auch nicht zum Bauplan des Skills dieses Vorhabens. Sie sind Vergleichsmaterial eines früher in Betrieb befindlichen Skills gewesen.

---

## A.1 Herkunft und Stand des zitierten Materials

Das Folgende gibt den Inhalt der drei Dateien wieder, aus denen der Vorläufer-Skill bestand: `SKILL.md` (Regeltext, Stand 2026-08-25), `CLAUDE-snippet.md` (stiller Trigger, Stand 2026-09-17) und `README.md` (Installation und Begründungen, Stand 2026-08-25). Der Skill hieß dort `software-dev-doc-fh`; das Kürzel `-fh` bezeichnete die Arbeitsweise eines bestimmten Entwicklers. Er war vollständig geschrieben, aber nie an einem Zielort installiert und daher nie unter dem eigenen Trigger erprobt.

Die Wiedergabe ist inhaltlich vollständig, aber nicht zeichengetreu; Reihenfolge und Wortlaut folgen der Quelle, wo es auf sie ankommt. Der unveränderte Wortlaut bleibt in der Git-Historie dieses Repositories erhalten.

## A.2 Was der Standard war — und was nicht

Der Vorläufer beschrieb **einen** Dokumentationsstandard, nicht den einzigen möglichen. Das Kürzel im Namen sagte das ausdrücklich: eine Arbeitsweise, bewährt in mehreren Projekten, aber ohne Anspruch, für jeden zu passen. Wer anders arbeitete, sollte sich einen anderen Skill schreiben.

Gegenstand war die **entwicklungsbegleitende Dokumentation**: alles, was vor der Kodierung geplant und während der Umsetzung mitgeschrieben wird — was implementiert werden soll, was implementiert wurde, welche Festlegungen getroffen wurden und, wo es nicht selbstverständlich ist, warum so und nicht anders.

**Nicht Gegenstand** waren die Dokumentation im Quelltext (Kommentare, Docstrings) und die Anwenderdokumentation des fertigen Produkts. Beide haben andere Adressaten und andere Regeln. Die Anwenderdokumentation sollte später aus Segment 1 entstehen, war aber nicht dasselbe.

## A.3 Die vier Phasen

1. **Findungsphase** — offenes Konzipieren in Prosa. Es wird gesammelt und verworfen; nichts ist Festlegung. Die Prosa-Code-Grenze galt hier abgemildert, die Segmentstruktur noch gar nicht.
2. **Fixierung** — Ideen wechseln schrittweise zu Vorgaben. Erste endgültige API-Beschreibungen entstehen. Ab hier galt die Prosa-Code-Grenze strikt.
3. **Segmentierung** — Das Konzeptdokument wird als neues, dreigeteiltes Dokument **neu geschrieben**, nicht umgebaut. Dabei entstand erstmals der Fahrplan. Werkzeug dafür: der Skill `konzept-segmentierung`.
4. **Implementierung** — Das segmentierte Dokument ist jetzt die Implementierungsdoku und wird parallel zum Code gepflegt.

Zwischen Phase 3 und 4 gehörte die Konsistenzprüfung des frisch segmentierten Dokuments; Werkzeug dafür war der Skill `konsistenzpruefung`.

## A.4 Die Prosa-Code-Grenze

Konzept- und Implementierungsdokumente enthielten **keinen Implementierungscode**. Genau zwei Ausnahmen: endgültig beschlossene API-Signaturen und Nutzungsbeispiele.

Die Begründung war als bindend gekennzeichnet, nicht als schmückend:

- Code im Konzept macht die spätere Prüfung von Code gegen Konzept wertlos — man vergliche den Code mit sich selbst.
- Prosa hält den mitgedachten Kontext fest, den Code nicht abbilden kann: Absicht, Abwägung, verworfene Alternative.
- Aus der Prosa entsteht später die Anwenderdokumentation.

Ließ sich eine geplante Änderung ohne Kontrollfluss nicht beschreiben, galt der Schritt als zu groß gewählt: zerlegen, nicht Code ins Dokument aufnehmen.

## A.5 Dokumentstruktur

- **Ordner:** `running_implementation_doc/` — der Name war pro Projekt anpassbar.
- **Dateien:** je eine für Segment 1 und 2, dann eine je Hauptkapitel von Segment 3; dazu `work-plan.md` und `status.md`. Die Dokumentdateien trugen numerische Präfixe in Leseordnung (`1_zusammenhaenge.md`, `2_vorgaben.md`, `3_1_orchestrator.md`, `3_2_pipeline.md`, …), Fahrplan und Status nicht.
- **Überschriften:** Die Segmente waren Überschriften erster Ordnung, nummeriert 1 bis 3. Die Überschrift „3 …" stand nur in der ersten Kapiteldatei von Segment 3; jede weitere begann direkt mit ihrer Kapitelüberschrift zweiter Ordnung. So ergab das Verketten aller Dokumentdateien in Dateireihenfolge ein gültiges Gesamtdokument.

Ob ein Segment auf eine Datei oder mehrere verteilt wurde, entschied das Projekt. Verlangt war nur, dass die Verkettung in Dateireihenfolge lesbar blieb.

## A.6 Die drei Segmente

**Segment 1 — Zusammenhänge.** Beschrieb das System entlang der Funktionen im Arbeitsablauf des Benutzers. Verwies reichlich auf die Kapitel von Segment 3; diese Verweise waren die explizite Abbildung der logischen Querbezüge und zugleich der Suchweg jeder Auswirkungsanalyse. Segment 1 war die Quelle der späteren Anwenderdokumentation.

**Segment 2 — Vorgaben.** Projektweite Festlegungen, die quer über den gesamten Code galten: die Vereinheitlichung wiederkehrender Kodierungsaufgaben, Strukturen gemeinsam genutzter Daten, Rollenschnitte zwischen Prozessen. **Aufnahmetest:** Man musste auf eine Datei zeigen und sagen können „das verletzt diese Vorgabe". Was so nicht prüfbar war, gehörte als Begründung nach Segment 1 oder als Detail nach Segment 3.

**Segment 3 — Einheiten.** Je Hauptkapitel eine in sich geschlossene Einheit: Klasse, Modul, Ausführungsmodell samt Interprozesskommunikation, Pipeline mit Kernel-Unterkapiteln, Frontend.

**Übergreifend:** Jede Aussage hatte genau ein normatives Zuhause; überall sonst standen Querverweise. Nie zwei gleichrangige Fassungen derselben Festlegung — sie driften auseinander, und niemand merkt, welche gilt.

## A.7 Fahrplan und Status

- **Fahrplan** — die nächsten Schritte in aufgabenangemessener Detaillierung. Erledigtes flog vollständig heraus, es wurde nicht abgehakt. Die Nummern der verbleibenden Schritte wurden dabei **nicht** neu vergeben; neue Schritte zählten hoch, damit ein Rückblick auf „Schritt n" eindeutig blieb.
- **Status** — ausschließlich abgearbeitete Fahrplaneinträge, in der Reihenfolge des Abschlusses. Dort standen **keine** Entscheidungen; die gehörten sofort in das zuständige Segment.

**Wo ein Plan steht.** Für alles, was keine winzige Änderung war, wurde zuerst ein Plan geschrieben — nicht nur im Chat vorgetragen, sondern an einem Ort, den eine neue Sitzung von selbst findet. Es gab genau zwei solche Orte und **keine eigenen Plan-Dateien**: die Bearbeitung eines Review-Befundes gehörte in den Review-Anhang beim betreffenden Befund, alles andere in den Fahrplan beim betreffenden Schritt. Es stand höchstens ein noch nicht ausgeführter Plan gleichzeitig da, deutlich als solcher gekennzeichnet. Nach der Ausführung wurde er **ersetzt**, nicht ergänzt.

*Anmerkung des laufenden Vorhabens, nicht Teil der Quelle:* Genau diese Regel hat am 22. August 2026 zu dem Vorfall geführt, aus dem Kapitel 3.4 entstanden ist — eine ausdetaillierte Arbeitsplanung wurde in den Fahrplan geschrieben, den der Entwickler ausdrücklich nicht als Planungsablage versteht.

## A.8 Arbeitsschleife der Implementierung

- Die Tagesaufgabe kam aus dem Fahrplan.
- In den Kontext geladen wurde die betroffene Sektion aus Segment 3 vollständig. Segment 1 wurde bei Bedarf gezielt durchsucht, nicht pauschal geladen; Segment 2 galt ohnehin parallel.
- Reichte eine Entscheidung über die aktuelle Codestelle hinaus: über Segment 1 suchen, welche weiteren Sektionen betroffen sind, diese lesen, die Entscheidung überdenken, die Auswirkungen rückwärts in die betroffenen Sektionen einpflegen und die Zusammenhänge in Segment 1 ergänzen.
- Zu jedem Kodierungsschritt gehörte im Plan auch der Vorschlag, was dazu in die Doku aufzunehmen oder dort anzupassen ist. Doku und Code entstanden im Wechsel, nicht nacheinander.

## A.9 Reviews und ihr Anhang

Review-Befunde wurden nicht im Chat abgehandelt und dann vergessen. Die Befundliste des Reviewers wurde mit ihrem Erstellungsdatum als **Anhang in die Doku** übernommen, das Original danach entfernt, damit keine zweite Fassung entstand.

Jeder Befund bekam einen Eintrag — behoben, abgelehnt oder zurückgestellt. Der Eintrag war zunächst der Plan des Schritts und wurde nach der Ausführung durch den Bericht ersetzt: warum der Punkt genau so gelöst wurde. Die Länge des Eintrags war selbst eine Aussage: „erledigt" hieß geradeheraus, ein begründeter Absatz stand dort, wenn die Lösung anders aussah als vorgeschlagen oder der Befund abgelehnt wurde. **Der abgelehnte Befund war der wichtigste** — ohne festgehaltene Begründung meldet ihn der nächste Review wieder, und zwar zu Recht.

**Die Grenze zwischen Kapiteln und Anhang:** In die Kapitel gehörte, was man zum **Ändern** des Codes braucht, einschließlich der Messwerte, an denen eine Festlegung hängt. In den Anhang gehörte, was man zum **Beurteilen der Bearbeitung** braucht: verworfene Wege, Bewertungen, der Verlauf.

## A.10 Zusammenspiel mit anderen Skills

- `konzept-segmentierung` — führte Phase 3 durch und erzwang echtes Neuschreiben statt Umsortieren.
- `konsistenzpruefung` — prüfte das segmentierte Dokument vor Implementierungsbeginn auf innere Widerspruchsfreiheit und Kodierbarkeit.

Beide galten als Werkzeuge innerhalb dieses Standards, nicht als Alternativen dazu.

## A.11 Der stille Trigger

Der Vorläufer trug seinen Auslöser in einer eigenen Datei, die nicht Teil des Skills war: Beim Installieren wurde alles unterhalb einer Trennlinie in die `CLAUDE.md` des Zielorts übernommen; die Datei blieb am Zielort liegen, wirksam war allein die `CLAUDE.md`. Ohne den Trigger lief der Skill nur bei ausdrücklichem Aufruf. Der Wortlaut:

> **Planung und Implementierungsdoku.** Bevor du in einer Sitzung zum ersten Mal einen Lösungsweg vorschlägst oder zum ersten Mal eine Datei änderst, halte kurz inne und prüfe: Geht die besprochene Software-Änderung über eine einzelne, lokal begrenzte Korrektur hinaus — sind mehrere Stellen betroffen, müssen mehrere Vorgehensweisen gegeneinander abgewogen werden, oder müssen erst Zusammenhänge im bestehenden Code erarbeitet werden, bevor klar ist, was zu ändern ist? Wenn ja, konsultiere sofort den Skill.

Die Begleitnotiz der Datei hielt fest, warum der Wortlaut so gebaut ist: Er ist an eine Ankerhandlung gebunden („bevor du zum ersten Mal …") und nicht als Hintergrund-Beobachtung formuliert. Das war keine Stilfrage — die eigenschaftsförmige Fassung war gemessen worden und feuerte nicht. Beim Anpassen an ein Projekt durfte der Anker verschoben, aber nicht weggelassen werden.

## A.12 Installation und Beschreibungstext

Der Skill war für zwei Zielorte vorgesehen: `~/.claude/skills/<name>/` für alle Projekte des Nutzers oder `.claude/skills/<name>/` für ein einzelnes. Der Ordner wurde unter seinem unveränderten Namen kopiert; er enthielt `SKILL.md`, `CLAUDE-snippet.md` und die README. Ein Sprachkürzel trug keine der Dateien, weil es nur die deutsche Fassung gab. Danach wurde der stille Trigger nach A.11 übernommen.

Der Beschreibungstext im Frontmatter, der über das Auslösen entscheidet, lautete sinngemäß: Dokumentationsstandard für Planung vor der Kodierung und für die laufende Mitschrift des Implementierten — was umgesetzt wird, welche Festlegungen getroffen wurden und warum so und nicht anders; vier Phasen von der Findung bis zur Implementierung, dreigeteilte Segmentstruktur, Fahrplan und Status; zu verwenden, sobald eine Software-Änderung über eine lokal begrenzte Korrektur hinausgeht. Lizenz: CC0-1.0.

## A.13 Was die README zusätzlich festhielt

**Zum Erweitern.** Zwei Festlegungen trugen nach eigener Aussage die übrigen und sollten beim Anpassen nicht fallen: die Prosa-Code-Grenze (sonst prüft man später Code gegen Code) und die Regel vom einen normativen Zuhause (sonst entstehen zwei Fassungen derselben Festlegung, die auseinanderdriften). Der Aufnahmetest für Segment 2 war das Werkzeug, mit dem sich entscheiden ließ, wohin eine neue Aussage gehört.

**Zum Stand.** Anweisungen vollständig, Frontmatter gesetzt, stiller Trigger vorhanden; die Erprobung am Zielort sollte stattfinden, wenn der Skill dort gebraucht würde. Offen war, ob die beiden Werkzeug-Skills in das Vorhaben gehören. Vorgemerkt, aber nicht auf der Tagesordnung war die Zweiteilung in eine dünne `SKILL.md` mit einer Klärung, ob der Standard überhaupt gilt, und einen nachgeladenen Regelteil — mit der Beobachtung, dass der damalige Trigger eigenschaftsförmig war („sobald eine Software-Änderung über eine lokal begrenzte Korrektur hinausgeht") und eine Abwahl damit realistisch.

---

**Anhang A — Ende**
