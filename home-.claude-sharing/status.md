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

- **Alle 33 Befunde des Code-Abgleichs sind abgearbeitet** — 22. August 2026. Erhoben am 13. August von einer getrennten, rein lesenden Sitzung gegen den Stand `192fede`; Bearbeitung samt Begründungen in Anhang B der Doku. In elf Fällen fiel die Lösung anders aus als vorgeschlagen, zweimal war der Vorschlag in seiner wörtlichen Form ein Rückschritt, und zwei Behauptungen des Reviews waren durch unsere eigene Arbeit überholt. Das Prüfskript wuchs dabei von 70 auf **216** Fälle und prüft seit Befund 30 auch die beiden Shell-Skripte.

- **Die Betriebsmeldung schweigt nicht mehr nach einer Neuverbindung** — 14. August 2026, im Betrieb aufgefallen und zwischen die Review-Befunde geschoben: Wo der Vergleichswert fehlt, steht jetzt ein Satz statt „0 B hoch, 0 B herunter". Ursache war der Wechsel zwischen VPN-WLAN und normalem WLAN, also Alltag und kein Sonderfall. Festlegung in 1.8 und 3.1 Punkt 1. Dabei geschlossen: Kein Prüffall hatte die Bytezahlen je angesehen — die Attrappe lieferte konstante Zählerstände, sodass die Differenz immer null war.

- **Der Aufruf der Konfliktsitzung ist im Prüfskript festgenagelt** — 22. August 2026, Fahrplanschritt 9. Neun Prüfungen an einem aufgezeichneten statt ausgeführten Aufruf: Argumentreihenfolge, Wert unmittelbar hinter seiner Option, Übergabetext an letzter Stelle, absoluter Programmpfad, Arbeitsverzeichnis. Zwei Leerproben bringen je genau die eine Prüfung zu Fall, für die sie gebaut sind — die historische Fehlform, die einmal eine Sitzung ohne jeden Prompt startete, und die naheliegende falsche Umsetzung. Das Skript zählt damit 227 Fälle. In 3.8 ist dabei die Grenze zu den Handproben geschärft worden: Die Zusammensetzung des Aufrufs ist maschinell gedeckt, das Aufgehen des Fensters nicht.

- **Das Installskript bietet die Ausschlussliste zum Übernehmen an** — 22. August 2026, Fahrplanschritt 8. Vorher nannte es nur den Kopierbefehl, und genau dieser Handschritt musste an einem Tag auf zwei Rechnern von Hand getan werden. Jetzt: Unterschiede vollständig anzeigen, dann fragen — mit Vorgabe **Ja**, auch dort, wo die wirksame Datei ganz fehlt und nichts ausgeschlossen ist. Kopiert wird nur nach Zustimmung; es ist die einzige Stelle, an der das Skript in den abgeglichenen Ordner schreibt (Begründung in 2.8). Nach einer tatsächlichen Übernahme empfiehlt es das Neueinlesen in Syncthing mit dessen dokumentierter Standardadresse — weil an keiner Stelle der Syncthing-Dokumentation steht, wann eine geänderte `.stignore` gelesen wird. Der Frage-Helfer ist aus `ensure_package` herausgelöst und wird von beiden Fragen benutzt; unterschiedlich ist allein die Vorgabe. Das Prüfskript zählt damit **254** Fälle und schneidet dafür zwei weitere markierte Strecken aus dem Shell-Skript. Drei Leerproben — Vorgabe gedreht, Empfehlung ohne Kopie, Vorgabe bei leerer Antwort weggelassen — schlagen je an ihrer eigenen Stelle an.
