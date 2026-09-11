# Syncthing-Sync für `~/.claude`

*Stand: 2026-09-11*

*[English version](https://github.com/fherb2/claude-ai-tooling/blob/master/home-.claude-sharing/README.en.md)*

**Hält den Arbeitszustand von Claude Code und Claude Desktop — Konfiguration, Sitzungsprotokolle, Projektgedächtnis — automatisch zwischen mehreren Rechnern synchron, damit derselbe Kontext überall zur Verfügung steht. Und meldet den Ausnahmefall, den eine Synchronisation nicht selbst lösen kann: die beidseitig geänderte Datei.**

Der Abgleich läuft seit dem 11. August 2026, inzwischen auf drei Rechnern; auf allen drei läuft der Wächter als Dienst, und er hat echte Konflikte behandelt. Die Implementierung ist abgeschlossen, offen ist allein ein Pendant für Windows (`work-plan.md`).

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

## Voraussetzungen

### Ein Knoten, der immer läuft

Der Abgleich braucht eine Stelle, die **alle** beteiligten Rechner erreichen können und die dauerhaft läuft — hier eine Synology-NAS, geeignet ist aber jeder ständig erreichbare Rechner. Das ist keine Bequemlichkeit, sondern Bedingung: Syncthings öffentliche Relay-Server **speichern nichts**, sie leiten nur zwischen zwei Geräten weiter, die **gleichzeitig** verbunden sind. Zwei Rechner, die nie zusammen online sind, gleichen darüber nicht ab.

Auf dem Knoten läuft deshalb eine vollwertige Syncthing-Instanz mit einer **vollständigen Kopie** des Ordners. Der Datenfluss ist Rechner A → Knoten → Rechner B, ohne dass sich A und B je begegnen; der Ordner liegt damit dreimal vor, und auf dem Knoten kommt der Platz für die Versionierung hinzu.

Was dort einzurichten ist — die Handgriffe im Einzelnen stehen in `syncthing-synology-setup-guide.md`, hier nur, worauf es ankommt:

- **Gerätekopplung, beidseitig und sternförmig** (Abschnitt 6): Der Knoten kennt jeden Rechner, jeder Rechner kennt nur den Knoten. Die Rechner werden **nicht** miteinander gekoppelt.
- **„Introducer" bleibt überall aus** (6). Ist die Option gesetzt, reicht ein Gerät die ihm bekannten Geräte-IDs an seine Gegenstellen weiter — der Knoten würde die Rechner einander bekannt machen, und sie versuchten sich direkt zu verbinden.
- **Portfreigabe und Firewall nur am Knoten** (4, 5). Syncthing baut Verbindungen in beide Richtungen auf; es genügt, dass der Knoten erreichbar ist. Arbeitsrechner hinter einem NAT-Router brauchen keine eigene Freigabe.
- **Feste Adresse für den Knoten** (6): im Geräteeintrag auf den Rechnern unter *Advanced → Addresses* `tcp://deine-domain.tld:22000` statt `dynamic`.
- **Dateiversionierung „Staggered" am Knoten** (9). Er empfängt von allen Rechnern und ist damit der einzige Ort mit einem vollständigen Archiv — der Notfall-Rückgriff hängt daran (siehe „Wenn etwas kaputt ist"). Auf den Arbeitsrechnern genügt „Trash Can" oder „Simple".
- **Ordnertyp „Send & Receive" auf allen Geräten** (7). „Receive Only" am Knoten wäre falsch: Er muss die Änderungen des einen Rechners an die anderen weitergeben.
- **Angelegt wird der Ordner zuerst auf dem Rechner, der den Inhalt hat** (7) — nicht auf dem leeren Knoten, sonst wird der leere Stand verteilt.

### Wenn sich die Rechner gegenseitig erreichen

Syncthing ist im Kern ein Peer-to-Peer-Werkzeug: Rechner direkt zu koppeln ist zulässig, und der Wächter merkt davon nichts — er sieht nur Dateinamen im abgeglichenen Ordner. An die Stelle der Knoten-Einrichtung tritt dann die Ersteinrichtung auf dem ersten Rechner (siehe unten).

**Zwei Eigenschaften gehen dabei verloren**, und beide tragen hier etwas:

- **Der Abgleich braucht dann Gleichzeitigkeit.** Wer abwechselnd an zwei Rechnern arbeitet und den einen ausschaltet, bevor der andere läuft, überträgt nie etwas.
- **Der Notfall-Rückgriff verliert seine Quelle.** Syncthing archiviert nur **eintreffende** Fremdänderungen vor dem Überschreiben, niemals eigene. Ohne ein Gerät, das von allen empfängt, bleibt allein das lokale `.stversions/` — und genau die eigene Zerschreibung hebt es nicht auf.

Deshalb ist der dauerhaft laufende Knoten der hier beschriebene und empfohlene Weg.

### Auf jedem beteiligten Rechner

Diese Voraussetzungen prüft das Installationsskript einzeln:

| Voraussetzung | Fehlt sie, dann … |
| --- | --- |
| Syncthing läuft und gleicht `~/.claude` ab | Warnung — der Wächter wird eingerichtet, findet aber nie etwas |
| `/usr/bin/claude` vorhanden **und angemeldet** | Abbruch. Abhilfe: `claude` von Hand starten und `/login` |
| `python3-watchdog`, `zenity`, `libnotify-bin` | Rückfrage je Paket, ob nachinstalliert werden soll |
| `systemctl` und ein steuerndes Terminal | Abbruch — ohne Terminal könnte keine Rückfrage gestellt werden |

Das Skript **installiert nichts stillschweigend**: Fehlt ein Paket, nennt es die Folge und fragt; die Vorgabe bei leerer Antwort ist **nein**. Ohne `zenity` fällt die gesamte Meldung aus, ohne die Beobachtungsbibliothek der Dienst — beides ist Voraussetzung. `libnotify-bin` ist dagegen Zubehör: Ohne es fehlt allein die stündliche Betriebsmeldung, Erkennung und Eskalation arbeiten vollständig.

## Installation

**Der Normalfall ist ein Rechner, der schon ein eigenes, gewachsenes `~/.claude` hat** — darin stecken die Chats seiner lokalen Projekte und die aus Claude Desktop. Dieser Bestand darf nicht überschrieben werden, und genau deshalb sieht der Weg unten so aus und nicht wie ein gewöhnliches „Ordner synchronisieren": Der Erstabgleich **vereinigt** zwei gewachsene Bestände, und der Zusammenführungsschritt dabei ist eingeplant.

1. **Bestand sichern.** `cp -a ~/.claude ~/.claude.vor-sync` — die einzige Rückfalllinie dieses Vorgangs. Sie wird erst am Ende aufgelöst.
2. **Werkzeugpaket entpacken.** `downloads/claude-sync-watch_de_local.zip` aus diesem Ordner herunterladen, dann `unzip claude-sync-watch_de_local.zip -d ~`. Das legt `~/.claude-sync-watch/` mit allen benötigten Dateien an. **Das Paket bestimmt die Sprache:** Dieses hier bringt den deutschen Meldungskatalog und die deutsche Arbeitsanweisung mit, das englische (`claude-sync-watch_en_local.zip`) die englischen. Einzustellen ist dazu nichts. Dieser Ort ist **Vorschrift**, keine Empfehlung: Die Dienstdefinition verweist fest darauf, und das Installationsskript verweigert den Dienst an jedem anderen Ort. Der Ordner ist versteckt; Kontrolle mit `ls -d ~/.claude-sync-watch`. Der Dienst wird hier noch **nicht** eingerichtet.
3. **Ausschlussliste anlegen — vor dem Teilen.** `cp ~/.claude-sync-watch/.stignore ~/.claude/.stignore`. Warum vorher: Syncthing synchronisiert diese Datei nicht, sie muss auf jedem Rechner einzeln vorhanden sein — und fehlt sie beim ersten Abgleich, wandern die Zugangsdaten los. Was Syncthing später im Reiter *Ignore Patterns* anzeigt, ist genau diese Datei; vor dem Teilen gibt es den Reiter noch nicht.
4. **Den Ordner in Syncthing teilen.** Vier Handgriffe, Einzelheiten in Abschnitt 7 des Setup-Guides: **Add Folder**; als **Folder ID** dieselbe Kennung wie auf den übrigen Geräten eintragen — zeichengleich, sonst gilt der Ordner als ein anderer; als „Folder Path" `~/.claude`; im Reiter **Sharing** den Knoten anhaken; speichern. Am Knoten erscheint die Rückfrage, ob der Ordner angenommen werden soll. Alle Geräte bleiben auf **Send & Receive**.
5. **Erstabgleich abwarten.** Fertig, wenn die Oberfläche auf beiden Seiten „Up to Date" zeigt. Was dabei geschieht: Einseitig vorhandene Dateien werden verteilt; beidseitig vorhandene, inhaltlich verschiedene erzeugen Konfliktkopien mit `.sync-conflict-` im Namen. Wie viele es werden, hängt an der Divergenz der Bestände — **das ist der geplante Zusammenführungsschritt, kein Fehler.**
6. **Konfliktkopien auflösen, von Hand gestartet.** Der Wächter läuft noch nicht, und das ist Absicht: Er soll auf einem konfliktfreien Stand anfangen, und während eines laufenden Erstabgleichs kämen fortlaufend neue Kopien dazwischen. Deshalb hier einmal selbst:

        cd ~/.claude
        claude --append-system-prompt-file ~/.claude-sync-watch/conflict-resolution.de.md \
               "Der zu durchsuchende Ordner ist ~/.claude. Löse die dort liegenden Konfliktkopien auf."

   Das Arbeitsverzeichnis ist tragend, nicht Zierde: Claude Code übernimmt es vom aufrufenden Prozess. Die mitgegebene Arbeitsanweisung ist dieselbe, die der Wächter später verwendet — ohne sie zieht die Sitzung die Projektmethodik aus `~/.claude/CLAUDE.md` heran, die hier nicht gilt und in die Irre führt. Die Sitzung geht Paar für Paar mit Dir durch und schreibt oder löscht nichts ohne Deine Zustimmung. Zum Schluss selbst nachsehen: `find ~/.claude -name '*.sync-conflict-*'` muss leer bleiben.
7. **Dienst einrichten.** `~/.claude-sync-watch/install_service.sh` starten — aus jedem Arbeitsverzeichnis heraus, das Skript findet seinen Ordner selbst. Es prüft die Voraussetzungen von oben, vergleicht `~/.claude/.stignore` mit der maßgeblichen Fassung im Werkzeugordner und **bietet die Übernahme an**, falls sie abweicht; hier ist die Vorgabe **ja**. Wurde tatsächlich kopiert, empfiehlt es, den Ordner in Syncthings Oberfläche (`http://127.0.0.1:8384`) einmal neu einlesen zu lassen. Danach startet der Wächter bei jeder Anmeldung an der grafischen Sitzung von selbst und endet mit ihr. Mitlesen: `journalctl --user -u claude-sync-watch.service -f`.
8. **Sicherung auflösen**, nach angemessener Beobachtungszeit — nicht am selben Tag.

### Der allererste Rechner

Dort, wo der Verbund beginnt, gibt es noch keinen abgeglichenen Ordner und keinen Knoten. Zuerst wird also der Knoten eingerichtet (`syncthing-synology-setup-guide.md`, Abschnitte 1 bis 9), und der Ordner wird **von diesem Rechner aus** angelegt — er hat den Inhalt, der Knoten ist leer.

Die Schritte 1 bis 4 und 7 bis 8 von oben gelten unverändert. **Die Schritte 5 und 6 entfallen:** Es gibt keinen zweiten Bestand, mit dem sich etwas vereinigen könnte, also entstehen keine Konfliktkopien. Erst der nächste Rechner durchläuft den vollständigen Weg.

### Wieder abmelden

`~/.claude-sync-watch/uninstall_service.sh` entfernt den Dienst — nicht den Ordner und nicht den Abgleich. Wer das Werkzeug ganz loswerden will, löscht danach `~/.claude-sync-watch/` von Hand; `~/.claude` und die Syncthing-Freigabe bleiben davon unberührt.

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
