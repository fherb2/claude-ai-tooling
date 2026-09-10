# Fahrplan: Syncthing-Sync für `~/.claude`

Reine Abfolge der Arbeitsschritte, keine Inhalte. Details stehen in `implementation-doc.md`.

Der Mechanismus ist fertig und im Betrieb. Offen sind zwei Ausbauschritte: die Mehrsprachigkeit von Anzeige und Arbeitsanweisung und die Portierung nach Windows. Nummern erledigter Schritte werden nicht neu vergeben; die Lücken davor sind gewollt.

## Schritte

13. **Mehrsprachigkeit: Anzeige und Anweisung in Deutsch und Englisch.**

    **Das Ziel ist nicht „das Werkzeug kann auch Englisch", sondern dass die mitgegebene Arbeitsanweisung die Claude-Instanz nicht in eine Sprache zwingt, die der Nutzer nicht spricht.** Heute ist `conflict-resolution.md` durchgehend deutsche Prosa; die Konfliktsitzung fragt deshalb auf Deutsch, auch einen englischsprachigen Nutzer. Alles Übrige folgt daraus.

    **Entschieden (Entwickler, 10. September 2026):**

    - **Sprachfassungen tragen ihr Kürzel im Dateinamen — und behalten es im Archiv.** `conflict-resolution.de.md` / `.en.md`; für die Kataloge `messages_de.py` / `messages_en.py` mit **Unterstrich**, weil ein Punkt im Python-Modulnamen ein Paketpfad wäre und die Datei damit nicht importierbar. Keine Umbenennung beim Packen: `skill-dev-doc.md` 5.3 bleibt unberührt, Repo und Paket sind namensgleich, und der Wächter bleibt aus dem Repo heraus prüfbar (daran hängen die Prüffälle in 3.8).
    - **Ein Paket enthält genau einen Katalog und genau eine Arbeitsanweisung.** Der Wächter bestimmt seine Sprache daran, **welche Fassung vorliegt** — keine Einstellung, keine Umgebungserkennung. Grund, gemessen: Die Unit setzt keine Spracheinstellung, und ein Benutzerdienst startet mit karger Umgebung; `LANG` kann fehlen. Liegen beide vor — der Entwicklungszustand im Repo —, entscheidet der Schalter `--lang de|en` aus der Schalterfamilie in 3.1; fehlt auch der, gilt Deutsch, weil das Werkzeug ursprünglich lokal und deutsch gedacht war. `zustand.json` bleibt Merker und nimmt keine Konfiguration auf (3.2).
    - **Katalogform: ein Python-Modul je Sprache mit einem Wörterbuch.** Kein CSV und kein `gettext`. Gegen `gettext` steht der Kompilierschritt in einem Werkzeug, das als reiner Dateisatz ausgeliefert wird; gegen CSV und JSON steht, dass sie **keine Kommentare** kennen — die Wortlaute, die 1.8 zur Festlegung erklärt, verlieren dort die Begründung, die heute unmittelbar bei ihnen steht. Der Zugriff im Code erfolgt über sprechende Schlüssel, nicht über Sprachfetzen. Mehrzahl weiterhin über die Klammerform („Stunde(n)", „hour(s)") statt über eine Pluralmaschine.
    - **Die Journalzeilen folgen der Anzeigesprache**, aus demselben Katalog wie die Dialoge.
    - **`install_service.sh` und `uninstall_service.sh` sprechen künftig englisch**, einsprachig. Das ist eine **Ausnahme von 2.5** und dort als solche mit Grund einzutragen: Die Einrichtung ist der erste Kontakt, läuft einmal und richtet sich an jemanden, der das Werkzeug noch nicht kennt.

    **Zu ändern, nach adressierbaren Einheiten:** neues Modul `messages_de.py`/`messages_en.py` samt Auflösungsfunktion hinter **einer** Stelle (2.4); im Wächter jede Ausgabestelle auf Schlüsselzugriff; `conflict-resolution.md` in zwei Sprachfassungen; der Pfad der Arbeitsanweisung im Sitzungsaufruf wird sprachabhängig (3.3, dazu die neun Aufruf-Prüffälle in 3.8); die Pflichtdateien-Prüfung in `install_service.sh` akzeptiert die Sprachvariante; beide Shell-Skripte auf Englisch. **Doku:** 1.8 (Wortlaute je Sprache), 2.5 (Sprachregel und die Ausnahme), 2.7 (Ablageorte), 3.1 (`--lang`), 3.3, 3.4, 3.5, 3.8; README und README.en (Paketname, Handstart der Sitzung). **Prüfskript:** Meldungsprüfungen gegen den Katalog statt gegen Literale, dazu je Sprache eine Vollständigkeitsprobe — gleicher Schlüsselsatz, und jeder im Code benutzte Schlüssel vorhanden. Damit ist „halb übersetzt" ein fallender Prüffall.

    **Reihenfolge:** Katalog mit beiden Sprachen → Ausgabestellen im Wächter → Arbeitsanweisung teilen → Skripte auf Englisch → Prüfskript → Doku → Pakete neu packen. Je Etappe ein Checkpoint-Commit.

    **Zur englischen Fassung:** Übersetzt werden die **Festlegungen**, nicht die Wörter. Wo 1.8 zwei Wortlaute unterscheidet — die kurze und die lange Pausenfassung —, muss die englische Fassung diese Unterscheidung tragen, nicht bloß denselben Satz zweimal.

6. **Windows-Pendant** entwickeln (Kap. 3.7). Die Zuordnung der plattformabhängigen Bausteine für die Kapselstelle ist dort bereits festgehalten, ebenso die Grenze: Gekapselt sind Dialoge, Terminalstart, Prozessprüfung, der Ablageort der Syncthing-Konfiguration und der Start des Dauerdienstes — alles andere ist plattformneutral (2.4).
