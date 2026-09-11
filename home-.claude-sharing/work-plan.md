# Fahrplan: Syncthing-Sync für `~/.claude`

Reine Abfolge der Arbeitsschritte, keine Inhalte. Details stehen in `implementation-doc.md`.

Der Mechanismus ist fertig und im Betrieb, in Deutsch und Englisch. Offen ist ein Ausbauschritt — die Portierung nach Windows —, dazu eine Nachtragung, sobald der vierte Rechner läuft. Nummern erledigter Schritte werden nicht neu vergeben; die Lücken davor sind gewollt.

## Schritte

14. **Den vierten Rechner nachtragen — und was der erste Vollzug der neuen Anleitung gezeigt hat.**

    Am 10. September 2026 hat der Entwickler den vierten Rechner angebunden: Syncthing zuerst, der Wächter danach. **Das war der erste Vollzug des Verfahrens aus 3.6 in der Form, die seit demselben Tag in der README steht** — mit Werkzeugpaket statt Kopiervorgang und mit dem Handstart der Konfliktsitzung. Der Ausgang lag bei Abschluss der Sitzung noch nicht vor.

    Nachzutragen ist zweierlei, und das zweite ist das Wertvollere:

    - **Die Rechnerzahl** steht an vier Stellen auf „drei": `README.md` und `README.en.md` dieses Ordners („inzwischen auf drei Rechnern; auf allen drei läuft der Wächter als Dienst") sowie die Standzeile in den beiden Wurzel-READMEs („Im Betrieb auf drei Rechnern beim Entwickler seit dem 11. August 2026"). Erst ändern, wenn der Dienst dort wirklich läuft — eine Zahl in einer Statuszeile, die niemand belegen kann, ist schlechter als eine veraltete.
    - **Was die Anleitung offengelassen hat.** Hat der Erstabgleich Konfliktkopien erzeugt, und ließen sie sich mit dem beschriebenen Handstart auflösen? Hat eine Voraussetzung gefehlt, die die Tabelle nicht nennt? War ein Schritt in der falschen Reihenfolge? Jeder solche Fund gehört in die README und in 3.6 — nicht ins Gedächtnis. Eine Anleitung, die einmal gegen die Wirklichkeit gelaufen ist, ist mehr wert als jede Prüfung am Schreibtisch.

15. **Ein Packwerkzeug für dieses Vorhaben — zu entscheiden, nicht beschlossen.**

    2.7 verlangt: Wer in `files/` etwas ändert, packt im selben Arbeitsgang neu, und geprüft wird das über Prüfsummen. Ein Werkzeug dafür gibt es hier nicht — die Skills haben eines (`skill-dev-doc.md`, Anhang A.1), dieses Vorhaben nicht. Bei der Mehrsprachigkeit hat sich das gezeigt: Der Dateisatz je Paket ist jetzt eine Regel mit Ausnahmen (ein Katalog, eine Anweisung, README umbenannt, `tools/` und `zustand.json` draußen), und die von Hand einzuhalten ist genau die Sorte Arbeit, die beim dritten Mal schiefgeht. Am 11. September 2026 ist das mit einem Einmal-Skript im Sitzungsordner erledigt worden, samt Prüfung jeder Datei gegen ihre Quelle und je Sprache drei Gegenproben gegen die Pflichtdateien-Strecke des Installskripts. **Zu entscheiden:** ob dieses Skript als `files/pack_packages.sh` (oder unter `tools/`) ins Repo kommt. Dafür spricht, dass die Regel sonst nur in Prosa steht; dagegen, dass es ein weiteres Artefakt ist, das gepflegt werden muss.

6. **Windows-Pendant** entwickeln (Kap. 3.7). Die Zuordnung der plattformabhängigen Bausteine für die Kapselstelle ist dort bereits festgehalten, ebenso die Grenze: Gekapselt sind Dialoge, Terminalstart, Prozessprüfung, der Ablageort der Syncthing-Konfiguration und der Start des Dauerdienstes — alles andere ist plattformneutral (2.4).
