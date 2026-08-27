# Syncthing-Sync für `~/.claude`

*Stand: 2026-08-14*

**Hält den Arbeitszustand von Claude Desktop und Claude Code — Konfiguration, Sitzungsprotokolle, Projektgedächtnis — automatisch zwischen mehreren Rechnern synchron, damit derselbe Kontext überall zur Verfügung steht.**

# Stand: Noch in Überarbeitung. Nicht benutzen!

Status: **Im Betrieb beim Entwickler, nicht zur Weitergabe freigegeben.** Der Abgleich läuft seit dem 11. August 2026 auf zwei Rechnern, der Wächter ist auf beiden als Dienst eingerichtet und hat echte Konflikte behandelt. Die Doku (`implementation-doc.md`) ist in sich geprüft und gegen den Code abgeglichen; die Befunde dieses Abgleichs werden gerade abgearbeitet (Anhang B der Doku). Der Warnhinweis oben bleibt stehen, solange das Werkzeug ausschließlich beim Entwickler im Quasi-Testbetrieb läuft — er entfällt erst, wenn es auch Kollegen benutzen dürfen. Offene Fragen (F3, F7, F11) stehen im Anhang der Doku.

## Ziel

Wer an mehreren Rechnern mit Claude Code arbeitet, hat ohne dieses Werkzeug mehrere unabhängige Gedächtnisse: Was auf dem Laptop erarbeitet wurde, existiert auf dem Arbeitsplatzrechner nicht. Den Abgleich von `~/.claude` übernimmt Syncthing über einen dauerhaft laufenden Vermittlungsknoten auf einer eigenen NAS — die beteiligten Rechner müssen sich dafür weder sehen noch gleichzeitig eingeschaltet sein.

Syncthing führt Dateien, die auf zwei Rechnern gleichzeitig geändert wurden, bewusst **nicht** zusammen, sondern legt die unterlegene Fassung als Konfliktkopie daneben. Genau dort setzt dieses Projekt an: Es entdeckt solche Kopien, meldet sie und führt den Nutzer gemeinsam mit Claude durch die inhaltliche Auflösung.

## Einrichtung auf einem Rechner

Voraussetzungen: Syncthing läuft und gleicht `~/.claude` ab, Claude Code ist unter `/usr/bin/claude` erreichbar, `zenity` und `python3-watchdog` sind installiert. Das Installationsskript prüft alles und bricht mit dem passenden Befehl ab, wenn etwas fehlt — es installiert nichts von selbst nach.

1. **Ordner anlegen:** `mkdir ~/.claude-sync-watch`
2. **Dateien hineinkopieren:** den vollständigen Inhalt von `files/` aus diesem Repo dorthin. Der Ort ist **Vorschrift**, keine Empfehlung: Die Dienstdefinition verweist fest darauf, und das Installationsskript verweigert den Dienst an jedem anderen Ort.
3. **Einrichten:** `~/.claude-sync-watch/install_service.sh` starten. Das Skript ermittelt selbst, in welchem Ordner es liegt — es darf also aus jedem Arbeitsverzeichnis heraus aufgerufen werden.

Der Dienst startet danach bei jeder Anmeldung an der grafischen Sitzung von selbst und endet mit ihr. Mitlesen: `journalctl --user -u claude-sync-watch.service -f`. Wieder abmelden: `~/.claude-sync-watch/uninstall_service.sh` — das entfernt den Dienst, nicht den Ordner.

**Wichtig zum Remote-Arbeiten:** Der Wächter meldet sich immer auf **dem** Rechner, an dessen grafischer Sitzung er hängt — nicht dort, wo gerade gearbeitet wird. Wer über VSCode Remote-SSH auf einem anderen Rechner arbeitet, sieht dessen Meldungen erst, wenn er wieder an einem tatsächlich synchronisierten Rechner mit grafischer Sitzung sitzt. Ein Rechner, der selbst nicht am Abgleich teilnimmt, meldet nie etwas.

## Anwendung (grob)

- Der Abgleich selbst läuft ereignisgesteuert im Hintergrund und braucht im Alltag kein Zutun — Änderungen sind meist binnen Sekunden auf dem Vermittlungsknoten, ausgeschaltete Rechner holen beim nächsten Start selbsttätig nach.
- Zwei Gewohnheiten helfen, Konflikte gar nicht erst entstehen zu lassen: nach dem Einschalten erst den Abgleich ankommen lassen und dann mit Claude arbeiten; und einen Rechner nicht ausschalten, solange der Abgleich sichtbar offen ist.
- Bei einem Konflikt: ein Dialog fragt, ob jetzt gelöst werden soll; bei Zustimmung öffnet sich ein Terminal mit einer Claude-Code-Sitzung, die die betroffenen Dateien einzeln mit dem Nutzer durchgeht und erst nach dessen ausdrücklicher Zustimmung schreibt oder löscht.
- Ein neuer Rechner bringt in der Regel ein eigenständig gewachsenes `~/.claude` mit, das nicht überschrieben werden darf. Er wird deshalb geführt angebunden: Bestand sichern, `.stignore` **vor** dem Teilen anlegen, den Erstabgleich abwarten und die dabei entstehenden Konfliktkopien in einer Sitzung zusammenführen. Dieser Zusammenführungsschritt ist der geplante Teil des Verfahrens, keine Störung.

## Weiterführendes

- `implementation-doc.md` — vollständiges Konzept (Zusammenhänge, Vorgaben, Einheiten) samt Fragenkatalog
- `work-plan.md` — nächste Schritte; `status.md` — was davon schon abgearbeitet ist
- `syncthing-synology-setup-guide.md` — Einrichtung des Vermittlungsknotens und der Clients
