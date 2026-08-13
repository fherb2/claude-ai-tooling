# Status: abgearbeitete Fahrplanschritte

Ausschließlich erledigte Fahrplaneinträge, in der Reihenfolge des Abschlusses. Hier stehen **keine** Entscheidungen — die gehören sofort in das zuständige Kapitel von `implementierungs_doku.md`.

- **Abgleich von `~/.claude` eingerichtet** — über einen dauerhaft laufenden Vermittlungsknoten, ohne dass die beteiligten Rechner sich sehen oder gleichzeitig eingeschaltet sein müssen. Einrichtung des Knotens und der Clients in `Syncthing-Synology-Konfigurationsanleitung-allgemein.md`.

- **Ausschlussliste `.stignore` erstellt und wirksam belegt** — Zugangsdaten sind im Index von Syncthing nachweislich nicht vorhanden, die Gegenprobe an derselben Freigabe zeigt reguläre Dateien als abgeglichen (Belege in 3.8, T5).

- **Konflikt-Wächter gebaut** — Dateiüberwachung, Konflikterkennung, stündliche Betriebsmeldung, dreistufige Eskalation bis zur geführten Claude-Code-Sitzung. Dateien in `files/`, Beschreibung in 3.1 bis 3.5.

- **Prüfskript für die Stellen ohne Bildschirm** — `tests/test_dialog_and_naming.py`, ohne Anzeige, Zenity, Syncthing oder Netz lauffähig; einmal mit absichtlich verfälschter Erwartung gegengeprüft, damit es nicht stumm durchläuft (3.8).

- **Testreihe T1 bis T8 abgeschlossen** — einschließlich der Handproben, die einen Bildschirm und einen Menschen brauchten: Pause-Meldung im Vollzug am 12. August 2026, Selbstschließen des Dialogs, Ausschlussmechanik, Weitergabe einer Löschung. Belege in 3.8.

- **Dienst auf beiden Rechnern installiert und in Betrieb** — bestätigt am 11. August 2026. Damit ist die Zwei-Wächter-Lage aus 1.6 Betriebszustand, nicht mehr Entwurf. Der eigens angelegte Testordner ist auf beiden Rechnern gelöscht und seine Freigabe entfernt.

- **Echte Konflikte behandelt** — die Kette vom Erkennen über die Eskalation bis zur geführten Sitzung ist an nicht herbeigeführten Konflikten auf beiden Rechnern durchlaufen, ein Fall vollständig verlustfrei aufgelöst.

- **Selbstschließzeit für die gesamte Eskalationsstrecke umgesetzt** — vorher trug nur der Frage-Dialog eine Frist; Auswahldialog und Freitexteingabe konnten unbegrenzt stehen und die Laufsperre halten. Vom Prüfskript abgedeckt, einschließlich der Aufrufstellen (Doku 3.3).

- **Doku-Review abgeschlossen** — 13. August 2026, die Implementierungsdoku vollständig gegen sich selbst geprüft: 22 Befunde, alle abgearbeitet, sieben davon mit einer anderen Lösung als vorgeschlagen. Was inhaltlich blieb, steht in den Kapiteln 1 bis 3; die Befundliste selbst ist verworfen (Begründung in Anhang B.2, „Vorgeschichte").

- **Abgleich der Doku gegen den Code durchgeführt** — 13. August 2026, von einer getrennten, rein lesenden Sitzung gegen den Stand `192fede`. Ergebnis: 33 Befunde, im Wortlaut des Reviewers in Anhang B der Doku übernommen. Ihre Abarbeitung ist Fahrplanschritt 1 und damit noch offen.
