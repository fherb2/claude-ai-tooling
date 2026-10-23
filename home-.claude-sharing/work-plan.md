# Fahrplan: Syncthing-Sync für `~/.claude`

Reine Abfolge der Arbeitsschritte, keine Inhalte. Details stehen in `implementation-doc.md`.

Der Mechanismus ist fertig und im Betrieb, in Deutsch und Englisch. Nummern erledigter Schritte werden nicht neu vergeben; die Lücken davor sind gewollt. Offen ist nur noch Schritt 6.

Am 15. September 2026 abgeschlossen: die Zweiteilung der Ausschlussliste in einen gemeinsamen und einen rechnerspezifischen Teil (`.stignore-local`), der Ausschluss von `backups/`, `plans/`, `debug/`, `image-cache/` und der toten Scratchpad-Projekte, die Entfernung des nie benutzten Werkzeugordners `tools/` samt Schalter `--add-dir`, und das Ausrollen auf die beteiligten Rechner. Der Abgleich läuft danach fehlerfrei; damit ist der Auslieferungsstand erreicht.

## Schritte

6. **Windows-Pendant** entwickeln (Kap. 3.7). Die Zuordnung der plattformabhängigen Bausteine für die Kapselstelle ist dort bereits festgehalten, ebenso die Grenze: Gekapselt sind Dialoge, Terminalstart, Prozessprüfung, der Ablageort der Syncthing-Konfiguration und der Start des Dauerdienstes — alles andere ist plattformneutral (2.4).
