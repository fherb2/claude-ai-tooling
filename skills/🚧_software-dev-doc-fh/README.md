# 🚧 software-dev-doc-fh — Dokumentationsstandard für Planung und laufende Mitschrift

*Stand: 2026-08-25*

**🚧 In Arbeit.** Einsetzbar, aber noch nicht abgenommen: Offen ist, wie die beiden Werkzeug-Skills dieses Standards eingebunden werden (siehe „Stand und Offenes" am Ende).

**Gibt einen Standard für die entwicklungsbegleitende Dokumentation vor** — für alles, was vor der Kodierung geplant und während der Umsetzung mitgeschrieben wird: was umgesetzt wird, welche Festlegungen getroffen wurden und, wo es nicht selbstverständlich ist, warum so und nicht anders.

**Nicht** Gegenstand sind die Dokumentation im Quelltext (Kommentare, Docstrings) und die Anwenderdokumentation des fertigen Produkts. Beide haben andere Adressaten und andere Regeln; die Anwenderdokumentation entsteht später aus Segment 1 dieses Standards, ist aber nicht dasselbe.

Das Kürzel `-fh` ist Absicht: Das ist die Arbeitsweise eines bestimmten Entwicklers, bewährt in mehreren Projekten, aber ohne Anspruch, für jeden zu passen. Wer anders arbeitet, schreibt einen eigenen Skill, statt diesen zu verbiegen.

## Installation

1. **Zielort wählen.** Der Skill gilt entweder für alle Projekte des Nutzers oder nur für eines:

   | Ort         | Pfad                                      | Gilt für                  |
   | ----------- | ----------------------------------------- | ------------------------- |
   | Persönlich  | `~/.claude/skills/software-dev-doc-fh/`   | alle Projekte des Nutzers |
   | Projekt     | `.claude/skills/software-dev-doc-fh/`     | nur dieses Projekt        |

2. **Ordner `software-dev-doc-fh/` unter seinem unveränderten Namen kopieren.** Er enthält `SKILL.md`, `CLAUDE-snippet.md` und diese `README.md`. Ein Sprachkürzel trägt bisher keine der Dateien, weil es nur die deutsche Fassung gibt.

3. **Stillen Trigger übernehmen.** Der Inhalt der `CLAUDE-snippet.md` **unterhalb der Trennlinie** kommt in die `CLAUDE.md` des Zielorts; die Snippet-Datei bleibt am Zielort liegen, wirksam ist allein die `CLAUDE.md`. Sein Wortlaut ist an eine Handlung gebunden („Bevor du in einer Sitzung zum ersten Mal einen Lösungsweg vorschlägst oder zum ersten Mal eine Datei änderst …") — dieser Anker darf beim Anpassen an ein Projekt verschoben, aber nicht weggelassen werden, sonst löst der Trigger nicht mehr aus.

## Details

**Vier Phasen.** Findung (offenes Konzipieren in Prosa), Fixierung (Ideen werden zu Vorgaben), Segmentierung (das Konzeptdokument wird als dreigeteiltes Dokument **neu geschrieben**, nicht umgebaut — dabei entsteht der Fahrplan), Implementierung (das segmentierte Dokument wird parallel zum Code gepflegt).

**Drei Segmente.** Segment 1 beschreibt die Zusammenhänge entlang des Arbeitsablaufs und ist zugleich der Suchweg jeder Auswirkungsanalyse; Segment 2 trägt die projektweiten Vorgaben; Segment 3 je Hauptkapitel eine geschlossene Einheit. Übergreifend gilt: Jede Aussage hat genau ein normatives Zuhause, überall sonst stehen Querverweise.

**Die Prosa-Code-Grenze.** Konzept- und Implementierungsdokumente enthalten keinen Implementierungscode; genau zwei Ausnahmen sind endgültig beschlossene API-Signaturen und Nutzungsbeispiele. Lässt sich eine geplante Änderung ohne Kontrollfluss nicht beschreiben, ist der Schritt zu groß gewählt.

**Fahrplan und Status.** Der Fahrplan trägt die nächsten Schritte, Erledigtes fliegt heraus statt abgehakt zu werden, und die Nummern der übrigen bleiben stehen. Der Status trägt ausschließlich abgearbeitete Fahrplaneinträge und **keine** Entscheidungen — die gehören sofort in das zuständige Segment.

**Reviews und ihr Anhang.** Die Befundliste wandert als Anhang in die Doku, das Original wird entfernt. Jeder Befund bekommt einen Eintrag, auch der abgelehnte — ohne festgehaltene Begründung meldet ihn der nächste Review wieder, und zwar zu Recht.

**Erweitern.** Zwei Festlegungen tragen die übrigen und sollten beim Anpassen nicht fallen: die Prosa-Code-Grenze (sonst prüft man später Code gegen Code) und die Regel vom einen normativen Zuhause (sonst entstehen zwei Fassungen derselben Festlegung, die auseinanderdriften). Der Aufnahmetest für Segment 2 — „man muss auf eine Datei zeigen und sagen können, das verletzt diese Vorgabe" — ist das Werkzeug, mit dem sich entscheiden lässt, wohin eine neue Aussage gehört.

**Zur Trigger-Fassung.** Die eigenschaftsförmige Ausgangsfassung feuerte in keinem Szenario, die geankerte bei identischem Prompt sofort (Vorgaben, Kapitel 3). Das ist der Grund für den Anker in Installationsschritt 3.

## Stand und Offenes

**Status:** Anweisungen vollständig, Frontmatter gesetzt, stiller Trigger vorhanden. Die Erprobung am Zielort findet statt, wenn der Skill dort gebraucht wird.

**Offen:** Ob die Werkzeug-Skills `konzept-segmentierung` und `konsistenzpruefung` in dieses Vorhaben gehören, ist nicht entschieden. Der Schritt dazu steht im [Fahrplan](../fahrplan.md).

**Geplant, aber noch nicht auf der Tagesordnung.** Bei der nächsten Arbeit an diesem Skill ist mitzuentscheiden, ob er nach Kapitel 5.2 der Vorgaben zweigeteilt wird — dünne `SKILL.md` mit einer Klärung, ob der Standard hier überhaupt gilt, und ein nachgeladener Regelteil. Der Trigger ist eigenschaftsförmig („sobald eine Software-Änderung über eine lokal begrenzte Korrektur hinausgeht"), eine Abwahl also realistisch, und der Regelteil ist lang genug. Anders als bei anderen Kandidaten wäre hier aber kein Klärungsschritt umzubauen, sondern erst einer zu entwerfen — deshalb keine eigene Runde, sondern eine Entscheidung im Zuge der inhaltlichen Arbeit (Durchsicht vom 25. August 2026).
