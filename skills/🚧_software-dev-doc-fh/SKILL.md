---
name: software-dev-doc-fh
description: Dokumentationsstandard für Planung vor der Kodierung und für die laufende Mitschrift des Implementierten — was umgesetzt wird, welche Festlegungen getroffen wurden und warum so und nicht anders. Vier Phasen von der Findung bis zur Implementierung, dreigeteilte Segmentstruktur, Fahrplan und Status. Verwenden, sobald eine Software-Änderung über eine lokal begrenzte Korrektur hinausgeht, oder wenn der Nutzer /software-dev-doc-fh aufruft.
license: CC0-1.0
---

# Dokumentationsstandard für Planung und Implementierung

## Was dieser Standard ist — und was nicht

Dieser Skill beschreibt **einen** Dokumentationsstandard, nicht den einzigen möglichen. Das Kürzel `-fh` im Namen sagt genau das: Es ist die Arbeitsweise eines bestimmten Entwicklers, bewährt in mehreren Projekten, aber ohne Anspruch, für jeden zu passen. Wer anders arbeitet, schreibt sich einen anderen Skill.

**Gegenstand ist die entwicklungsbegleitende Dokumentation**: alles, was vor der Kodierung geplant und während der Umsetzung mitgeschrieben wird — was implementiert werden soll, was implementiert wurde, welche Festlegungen getroffen wurden und, wo es nicht selbstverständlich ist, warum so und nicht anders.

**Nicht Gegenstand** sind die Dokumentation im Quelltext (Kommentare, Docstrings) und die Anwenderdokumentation des fertigen Produkts. Beide haben andere Adressaten und andere Regeln. Die Anwenderdokumentation entsteht später aus Segment 1 dieses Standards, ist aber nicht dasselbe.

## Die vier Phasen

1. **Findungsphase** — offenes Konzipieren in Prosa. Es wird gesammelt und verworfen; nichts ist Festlegung. Die Prosa-Code-Grenze gilt hier abgemildert, die Segmentstruktur noch gar nicht.
2. **Fixierung** — Ideen wechseln schrittweise zu Vorgaben. Erste endgültige API-Beschreibungen entstehen. Ab hier gilt die Prosa-Code-Grenze strikt.
3. **Segmentierung** — Das Konzeptdokument wird als neues, dreigeteiltes Dokument **neu geschrieben**, nicht umgebaut. Dabei entsteht erstmals der Fahrplan. Werkzeug dafür: der Skill `konzept-segmentierung`.
4. **Implementierung** — Das segmentierte Dokument ist jetzt die Implementierungsdoku und wird parallel zum Code gepflegt.

Zwischen Phase 3 und 4 gehört die Konsistenzprüfung des frisch segmentierten Dokuments; Werkzeug dafür ist der Skill `konsistenzpruefung`.

## Die Prosa-Code-Grenze

Konzept- und Implementierungsdokumente enthalten **keinen Implementierungscode**. Genau zwei Ausnahmen: endgültig beschlossene API-Signaturen und Nutzungsbeispiele.

Die Begründung ist bindend, nicht schmückend:

- Code im Konzept macht die spätere Prüfung von Code gegen Konzept wertlos — man vergliche den Code mit sich selbst.
- Prosa hält den mitgedachten Kontext fest, den Code nicht abbilden kann: Absicht, Abwägung, verworfene Alternative.
- Aus der Prosa entsteht später die Anwenderdokumentation.

Lässt sich eine geplante Änderung ohne Kontrollfluss nicht beschreiben, ist der Schritt zu groß gewählt: zerlegen, nicht Code ins Dokument aufnehmen.

## Dokumentstruktur

- **Ordner:** `running_implementation_doc/` — der Name ist pro Projekt anpassbar.
- **Dateien:** je eine für Segment 1 und 2, dann eine je Hauptkapitel von Segment 3; dazu `fahrplan.md` und `status.md`. Die Dokumentdateien tragen numerische Präfixe in Leseordnung (`1_zusammenhaenge.md`, `2_vorgaben.md`, `3_1_orchestrator.md`, `3_2_pipeline.md`, …), Fahrplan und Status nicht.
- **Überschriften:** Die Segmente sind Überschriften erster Ordnung, nummeriert 1 bis 3. Die Überschrift „3 …" steht nur in der ersten Kapiteldatei von Segment 3; jede weitere beginnt direkt mit ihrer Kapitelüberschrift zweiter Ordnung. So ergibt das Verketten aller Dokumentdateien in Dateireihenfolge ein gültiges Gesamtdokument.

Ob ein Segment auf eine Datei oder mehrere verteilt wird, entscheidet das Projekt. Verlangt ist nur, dass die Verkettung in Dateireihenfolge lesbar bleibt.

## Die drei Segmente

**Segment 1 — Zusammenhänge.** Beschreibt das System entlang der Funktionen im Arbeitsablauf des Benutzers. Verweist reichlich auf die Kapitel von Segment 3; diese Verweise sind die explizite Abbildung der logischen Querbezüge und zugleich der Suchweg jeder Auswirkungsanalyse. Segment 1 ist die Quelle der späteren Anwenderdokumentation.

**Segment 2 — Vorgaben.** Projektweite Festlegungen, die quer über den gesamten Code gelten: die Vereinheitlichung wiederkehrender Kodierungsaufgaben, Strukturen gemeinsam genutzter Daten, Rollenschnitte zwischen Prozessen. **Aufnahmetest:** Man muss auf eine Datei zeigen und sagen können „das verletzt diese Vorgabe". Was so nicht prüfbar ist, gehört als Begründung nach Segment 1 oder als Detail nach Segment 3.

**Segment 3 — Einheiten.** Je Hauptkapitel eine in sich geschlossene Einheit: Klasse, Modul, Ausführungsmodell samt Interprozesskommunikation, Pipeline mit Kernel-Unterkapiteln, Frontend.

**Übergreifend:** Jede Aussage hat genau ein normatives Zuhause; überall sonst stehen Querverweise. Nie zwei gleichrangige Fassungen derselben Festlegung — sie driften auseinander, und niemand merkt, welche gilt.

## Fahrplan und Status

- **Fahrplan** — die nächsten Schritte in aufgabenangemessener Detaillierung. Erledigtes fliegt vollständig heraus, es wird nicht abgehakt. Die Nummern der verbleibenden Schritte werden dabei **nicht** neu vergeben; neue Schritte zählen hoch, damit ein Rückblick auf „Schritt n" eindeutig bleibt.
- **Status** — ausschließlich abgearbeitete Fahrplaneinträge, in der Reihenfolge des Abschlusses. Hier stehen **keine** Entscheidungen; die gehören sofort in das zuständige Segment.

**Wo ein Plan steht.** Für alles, was keine winzige Änderung ist, wird zuerst ein Plan geschrieben — nicht nur im Chat vorgetragen, sondern an einem Ort, den eine neue Sitzung von selbst findet. Es gibt genau zwei solche Orte und **keine eigenen Plan-Dateien**: die Bearbeitung eines Review-Befundes gehört in den Review-Anhang beim betreffenden Befund, alles andere in den Fahrplan beim betreffenden Schritt. Es steht höchstens ein noch nicht ausgeführter Plan gleichzeitig da, deutlich als solcher gekennzeichnet. Nach der Ausführung wird er **ersetzt**, nicht ergänzt.

## Arbeitsschleife der Implementierung

- Die Tagesaufgabe kommt aus dem Fahrplan.
- In den Kontext geladen wird die betroffene Sektion aus Segment 3 vollständig. Segment 1 wird bei Bedarf gezielt durchsucht, nicht pauschal geladen; Segment 2 gilt ohnehin parallel.
- Reicht eine Entscheidung über die aktuelle Codestelle hinaus: über Segment 1 suchen, welche weiteren Sektionen betroffen sind, diese lesen, die Entscheidung überdenken, die Auswirkungen rückwärts in die betroffenen Sektionen einpflegen und die Zusammenhänge in Segment 1 ergänzen.
- Zu jedem Kodierungsschritt gehört im Plan auch der Vorschlag, was dazu in die Doku aufzunehmen oder dort anzupassen ist. Doku und Code entstehen im Wechsel, nicht nacheinander.

## Reviews und ihr Anhang

Review-Befunde werden nicht im Chat abgehandelt und dann vergessen. Die Befundliste des Reviewers wird mit ihrem Erstellungsdatum als **Anhang in die Doku** übernommen, das Original danach entfernt, damit keine zweite Fassung entsteht.

Jeder Befund bekommt einen Eintrag — behoben, abgelehnt oder zurückgestellt. Der Eintrag ist zunächst der Plan des Schritts und wird nach der Ausführung durch den Bericht ersetzt: warum der Punkt genau so gelöst wurde. Die Länge des Eintrags ist selbst eine Aussage: „erledigt" heißt geradeheraus, ein begründeter Absatz steht dort, wenn die Lösung anders aussah als vorgeschlagen oder der Befund abgelehnt wurde. **Der abgelehnte Befund ist der wichtigste** — ohne festgehaltene Begründung meldet ihn der nächste Review wieder, und zwar zu Recht.

**Die Grenze zwischen Kapiteln und Anhang:** In die Kapitel gehört, was man zum **Ändern** des Codes braucht, einschließlich der Messwerte, an denen eine Festlegung hängt. In den Anhang gehört, was man zum **Beurteilen der Bearbeitung** braucht: verworfene Wege, Bewertungen, der Verlauf.

## Zusammenspiel mit anderen Skills

- `konzept-segmentierung` — führt Phase 3 durch und erzwingt echtes Neuschreiben statt Umsortieren.
- `konsistenzpruefung` — prüft das segmentierte Dokument vor Implementierungsbeginn auf innere Widerspruchsfreiheit und Kodierbarkeit.

Beide sind Werkzeuge innerhalb dieses Standards, keine Alternativen dazu.
