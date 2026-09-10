# Syncthing-Sync für `~/.claude`

*Stand: 2026-09-10*

**Hält den Arbeitszustand von Claude Code und Claude Desktop — Konfiguration, Sitzungsprotokolle, Projektgedächtnis — automatisch zwischen mehreren Rechnern synchron, damit derselbe Kontext überall zur Verfügung steht. Und meldet den Ausnahmefall, den eine Synchronisation nicht selbst lösen kann: die beidseitig geänderte Datei.**

Der Abgleich läuft seit dem 11. August 2026, inzwischen auf drei Rechnern; der Wächter ist als Dienst eingerichtet und hat echte Konflikte behandelt. Die Implementierung ist abgeschlossen, offen ist allein ein Pendant für Windows (`work-plan.md`).

## Ziel

Claude Code, Claude Desktop und die VSCode-Erweiterung halten ihren gesamten Arbeitszustand im Verzeichnis `~/.claude` des jeweiligen Rechners. Wer an mehreren Rechnern arbeitet, hat damit mehrere voneinander unabhängige Gedächtnisse: Was auf dem Laptop erarbeitet wurde, existiert auf dem Arbeitsplatzrechner nicht.

Den Abgleich selbst leistet Syncthing vollständig, über einen dauerhaft laufenden Vermittlungsknoten auf einer eigenen NAS. Die beteiligten Rechner müssen sich dafür weder sehen noch gleichzeitig eingeschaltet sein — jeder kennt nur den Knoten. Deshalb gilt alles hier Beschriebene für **beliebig viele** Rechner, nicht nur für zwei.

Die Eigenleistung dieses Vorhabens liegt woanders: Syncthing führt Dateien, die auf zwei Rechnern gleichzeitig geändert wurden, bewusst **nicht** zusammen, sondern legt die unterlegene Fassung als Konfliktkopie daneben — und meldet das niemandem. Genau dort setzt dieses Werkzeug an: Ein Wächter entdeckt solche Kopien, meldet sie und führt den Nutzer gemeinsam mit Claude durch die inhaltliche Auflösung.

## Was mitwandert — und was nicht

Abgeglichen wird der gesamte Inhalt von `~/.claude`, einschließlich der Sitzungsprotokolle und Chats unter `projects/` — sie sind der eigentliche Zweck. Ausgenommen ist, was in der Ausschlussliste `.stignore` steht; welches Muster warum, sagt Kapitel 3.9 der Doku.

Vier Punkte, die man vorher wissen sollte:

- **Zugangsdaten wandern nie.** `.credentials.json` ist ausgeschlossen, und die Zeile muss auf **jedem** Rechner in `~/.claude/.stignore` stehen, **bevor** der Ordner dort erstmals verbunden wird. Diese Datei wandert selbst nicht mit — Syncthing synchronisiert sie prinzipiell nicht.
- **`/rewind` über Rechnergrenzen entfällt.** Die Momentaufnahmen unter `file-history/` sind ausgeschlossen: Sie hängen an absoluten Pfaden des Rechners, der sie angelegt hat, und ihr Schreibmuster ist für einen Abgleich das ungünstigste im ganzen Ordner. Wer eine Sitzung auf dem anderen Rechner fortsetzt, hat dort keine Prüfpunkte zum Zurückspielen. Dafür gibt es die Versionsverwaltung des Projekts.
- **MCP-Server im User- und Local-Scope bleiben örtlich.** Sie liegen in `~/.claude.json`, also **außerhalb** des abgeglichenen Ordners. Wer sich auf einem Rechner einen MCP-Server einrichtet, trägt ihn auf dem anderen erneut ein. Für den Project-Scope gilt das nicht: `.mcp.json` gehört ins Repo des Projekts und wandert mit ihm.
- **Anmeldung und Gerätezustand bleiben örtlich** — ebenfalls `~/.claude.json`. Ein Kontowechsel ist deshalb eine rein örtliche Angelegenheit und erzeugt keine Konflikte.

## Einrichtung auf einem Rechner

**Voraussetzungen**, die das Installationsskript einzeln prüft:

| Voraussetzung | Fehlt sie, dann … |
| --- | --- |
| Syncthing läuft und gleicht `~/.claude` ab | Warnung — der Wächter wird eingerichtet, findet aber nie etwas |
| `/usr/bin/claude` vorhanden **und angemeldet** | Abbruch. Abhilfe: `claude` von Hand starten und `/login` |
| `python3-watchdog`, `zenity`, `libnotify-bin` | Rückfrage je Paket, ob nachinstalliert werden soll |
| `systemctl` und ein steuerndes Terminal | Abbruch — ohne Terminal könnte keine Rückfrage gestellt werden |

Das Skript **installiert nichts stillschweigend**: Fehlt ein Paket, nennt es die Folge und fragt; die Vorgabe bei leerer Antwort ist **nein**. Ohne `zenity` fällt die gesamte Meldung aus, ohne die Beobachtungsbibliothek der Dienst — beides ist Voraussetzung. `libnotify-bin` ist dagegen Zubehör: Ohne es fehlt allein die stündliche Betriebsmeldung, Erkennung und Eskalation arbeiten vollständig.

Die Schritte:

1. **Ordner anlegen:** `mkdir ~/.claude-sync-watch`
2. **Dateien hineinkopieren:** den vollständigen Inhalt von `files/` aus diesem Repo dorthin. Der Ort ist **Vorschrift**, keine Empfehlung: Die Dienstdefinition verweist fest darauf, und das Installationsskript verweigert den Dienst an jedem anderen Ort.
3. **Einrichten:** `~/.claude-sync-watch/install_service.sh` starten. Das Skript ermittelt selbst, in welchem Ordner es liegt — es darf also aus jedem Arbeitsverzeichnis heraus aufgerufen werden.

Dabei vergleicht es `~/.claude/.stignore` mit der maßgeblichen Fassung im Werkzeugordner, zeigt jeden Unterschied vollständig an und **bietet die Übernahme an** — hier ist die Vorgabe **ja**, auch wenn die wirksame Datei ganz fehlt. Wurde tatsächlich kopiert, empfiehlt es, den Ordner in Syncthings Oberfläche (`http://127.0.0.1:8384`) einmal neu einlesen zu lassen.

Der Dienst startet danach bei jeder Anmeldung an der grafischen Sitzung von selbst und endet mit ihr. Mitlesen: `journalctl --user -u claude-sync-watch.service -f`. Wieder abmelden: `~/.claude-sync-watch/uninstall_service.sh` — das entfernt den Dienst, nicht den Ordner.

## Im Alltag

**Der Abgleich braucht kein Zutun.** Er läuft ereignisgesteuert; eine Änderung ist meist binnen Sekunden auf dem Vermittlungsknoten, und ein ausgeschalteter Rechner holt beim nächsten Start selbsttätig nach.

**Zwei Gewohnheiten verhindern Konflikte, statt sie zu lösen:** nach dem Einschalten erst den Abgleich ankommen lassen und dann mit Claude arbeiten; und einen Rechner nicht ausschalten, solange die Oberfläche noch „Syncing" zeigt. Das Konfliktfenster ist bei abwechselnd benutzten Rechnern nicht die Übertragungsdauer, sondern die Zeit zwischen der letzten Änderung hier und dem ersten Nachholen dort.

**Einmal je Stunde meldet sich der Wächter** — kurz eingeblendet, nicht anzuklicken. Sie ist das Lebenszeichen eines Dienstes, dem man sonst nicht ansieht, ob er arbeitet oder seit Tagen klemmt:

    abgeglichen: 0.8 MB hoch, 0.3 MB herunter
    kein Konflikt seit 74 Stunde(n)

Vier Formen dieser Meldung verlangen Aufmerksamkeit und bleiben deshalb länger stehen: `3 Konflikt(e) seit 9 Stunde(n) ungelöst` — eine vertagte Lösung gerät nicht in Vergessenheit; `Rückstand: 7 Datei(en)` — es klemmt etwas, und davon erfährt man sonst nie etwas; `Abgleich für diesen Ordner angehalten — Änderungen und Konfliktkopien bleiben liegen` — eine selbst gesetzte, vergessene Pause legt den Abgleich sonst unbemerkt still; und `keine Verbindung zum Abgleich seit …`. Steht dort statt einer Zahl `Zähler neu gesetzt` oder `Zählung neu begonnen`, fehlt schlicht der Vergleichswert — nach einer Neuverbindung etwa, wie sie ein Wechsel des WLAN mit sich bringt.

**Bleibt die stündliche Meldung dauerhaft aus, ist das selbst ein Befund** und im Journal nachzusehen.

**Bei einem Konflikt** fragt ein Dialog, ob jetzt gelöst werden soll („Jetzt lösen" / „Später"). Bei Zustimmung öffnet sich ein Terminal mit einer Claude-Code-Sitzung, die alle anstehenden Konfliktpaare **einzeln mit dem Nutzer** durchgeht: Sie vergleicht Original und Kopie, erklärt den Unterschied und holt die Entscheidung ein — Original behalten, Kopie übernehmen oder zusammenfügen. Geschrieben oder gelöscht wird **nichts** ohne ausdrückliche Zustimmung zur konkreten Datei; am Ende berichtet die Sitzung, was sie getan hat.

Zwei Dinge dazu:

- **Gelöst wird immer nur an einem Rechner.** Löschung der Kopie und Aktualisierung des Originals wandern als gewöhnliche Dateivorgänge mit — wer hier löst, räumt überall auf. Wird derselbe Konflikt an zwei Rechnern unterschiedlich entschieden, entsteht ein neuer.
- **Ein unbeantworteter Dialog schließt sich nach fünfzehn Minuten selbst** und fragt frühestens nach dreißig Minuten erneut. Die stündliche Meldung ist die leise Erinnerung dazwischen.

## Einen weiteren Rechner anschließen

Ein neuer Rechner bringt in der Regel ein eigenständig gewachsenes `~/.claude` mit, das nicht überschrieben werden darf — darin stecken alle Chats seiner lokalen Projekte. Er wird deshalb geführt angebunden:

1. **Bestand sichern** — Kopie oder Umbenennung; es ist die einzige Rückfalllinie dieses Schrittes.
2. **`.stignore` anlegen, bevor** der Ordner geteilt wird: aus der maßgeblichen Fassung kopieren, nicht neu schreiben.
3. **Ordner mit derselben Folder-ID teilen** und den Erstabgleich abwarten.
4. **Konfliktsitzung durchführen**, bis kein Fund mehr bleibt.
5. **Wächter einrichten**, die Wirksamkeit der Ausschlussliste prüfen, die Sicherung nach angemessener Beobachtungszeit auflösen.

Beim Erstabgleich zweier nicht-leerer Bestände vereinigt Syncthing auf Dateiebene: Was nur auf einer Seite existiert, wird verteilt; was auf beiden Seiten existiert und sich unterscheidet, erzeugt Konfliktkopien. **Die anschließende Konfliktlösung ist der geplante Zusammenführungsschritt, keine Störung.**

## Wenn etwas kaputt ist

**Kein Notfall** ist eine inhaltlich unschön aufgelöste Datei — die wird normal nachgearbeitet. Ein Notfall sieht so aus: Claude Code startet nicht mehr, verlangt eine erneute Anmeldung, findet ein Projekt nicht mehr, oder eine Einstellung ist verschwunden. Auch dann kann die Ursache eine andere sein als der Abgleich, und die Reihenfolge trennt beides:

1. **Alle Claude-Sitzungen ordentlich schließen** (`/exit`), im Terminal wie in VSCode. Die des **anderen** Rechners erst, wenn das hier nichts gebracht hat.
2. **Hängengebliebene Prozesse beenden:** `pkill -u $USER claude`. Der Wächter ist davon nicht betroffen; er beobachtet nur.
3. **Sitzung neu öffnen.** Läuft sie wieder, ist hier Schluss — es war kein Synchronisationsschaden, und es ist nichts zurückzuholen.
4. Erst wenn es weiter kaputt ist: **Sicherung anlegen** (`cp -a ~/.claude ~/.claude.kaputt-<Datum>`), **dann** den Abgleich für diesen Ordner pausieren. Die Sicherung steht bewusst vor dem Pausieren: Pausieren hält nur die Weiterverbreitung auf.
5. **Einzelne Dateien zurückholen**, im Regelfall aus dem „Staggered"-Bestand der NAS — sie empfängt von allen Rechnern und archiviert deshalb jeden übertragenen Stand. Das lokale `~/.claude/.stversions/` taugt nur, wenn der Schaden von der Gegenseite hereinkam; die eigene Zerschreibung archiviert es nicht.
6. **Auf beiden Rechnern prüfen**, gegebenenfalls neu anmelden, und erst dann den Abgleich wieder einschalten.
7. **Die Sicherung aufbewahren**, bis geklärt ist, was schiefging — sie ist die einzige Quelle dafür.

## Grenzen, die man kennen muss

- **Der Wächter braucht eine grafische Sitzung**, weil er Dialoge zeigt. Bei einer Anmeldung ohne Bildschirm — über SSH oder eine Konsole — läuft Syncthing, der Wächter nicht: Konfliktkopien können dann eintreffen, ohne dass jemand gefragt wird. Verloren geht dabei nichts; der Suchlauf bei der nächsten grafischen Anmeldung holt sie nach.
- **Gemeldet wird auf dem Rechner, an dessen grafischer Sitzung der Wächter hängt** — nicht dort, wo gerade gearbeitet wird. Wer über VSCode Remote-SSH auf einem anderen Rechner arbeitet, sieht dessen Meldungen erst, wenn er wieder an einem tatsächlich synchronisierten Rechner mit Bildschirm sitzt. Es genügt, dass **irgendein** beteiligter Rechner meldet.
- **Ein Rechner, der selbst nicht am Abgleich teilnimmt, meldet nie etwas.**
- **Die Anzeigedauer der stündlichen Meldung ist eine Bitte, keine Zusicherung:** Plasma befolgt sie, GNOME Shell übergeht sie.

## Weiterführendes

- `implementation-doc.md` — die vollständige Beschreibung (Zusammenhänge, Vorgaben, Einheiten), im Anhang der Code-Review vom 13. August 2026 samt Bearbeitung
- `work-plan.md` — der noch offene Schritt
- `syncthing-synology-setup-guide.md` — Einrichtung des Vermittlungsknotens und der Clients
- `offener_fall_chatprotokolle.md` — ein untersuchter, aber nicht abgeschlossener Sonderfall: Konflikte in Sitzungsprotokollen
