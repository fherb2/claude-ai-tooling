# Fahrplan: Syncthing-Sync für `~/.claude`

Reine Abfolge der Arbeitsschritte, keine Inhalte. Details stehen in `implementation-doc.md`.

Der Mechanismus ist fertig und im Betrieb, in Deutsch und Englisch. Offen ist ein Ausbauschritt — die Portierung nach Windows —, dazu eine Nachtragung, sobald der vierte Rechner läuft. Nummern erledigter Schritte werden nicht neu vergeben; die Lücken davor sind gewollt.

## Schritte

14. **Den vierten Rechner nachtragen — und was der erste Vollzug der neuen Anleitung gezeigt hat.**

    Am 10. September 2026 hat der Entwickler den vierten Rechner angebunden: Syncthing zuerst, der Wächter danach. **Das war der erste Vollzug des Verfahrens aus 3.6 in der Form, die seit demselben Tag in der README steht** — mit Werkzeugpaket statt Kopiervorgang und mit dem Handstart der Konfliktsitzung. Der Ausgang lag bei Abschluss der Sitzung noch nicht vor.

    Nachzutragen ist zweierlei, und das zweite ist das Wertvollere:

    - **Die Rechnerzahl** steht an vier Stellen auf „drei": `README.md` und `README.en.md` dieses Ordners („inzwischen auf drei Rechnern; auf allen drei läuft der Wächter als Dienst") sowie die Standzeile in den beiden Wurzel-READMEs („Im Betrieb auf drei Rechnern beim Entwickler seit dem 11. August 2026"). Erst ändern, wenn der Dienst dort wirklich läuft — eine Zahl in einer Statuszeile, die niemand belegen kann, ist schlechter als eine veraltete.
    - **Was die Anleitung offengelassen hat.** Hat der Erstabgleich Konfliktkopien erzeugt, und ließen sie sich mit dem beschriebenen Handstart auflösen? Hat eine Voraussetzung gefehlt, die die Tabelle nicht nennt? War ein Schritt in der falschen Reihenfolge? Jeder solche Fund gehört in die README und in 3.6 — nicht ins Gedächtnis. Eine Anleitung, die einmal gegen die Wirklichkeit gelaufen ist, ist mehr wert als jede Prüfung am Schreibtisch.

6. **Windows-Pendant** entwickeln (Kap. 3.7). Die Zuordnung der plattformabhängigen Bausteine für die Kapselstelle ist dort bereits festgehalten, ebenso die Grenze: Gekapselt sind Dialoge, Terminalstart, Prozessprüfung, der Ablageort der Syncthing-Konfiguration und der Start des Dauerdienstes — alles andere ist plattformneutral (2.4).
