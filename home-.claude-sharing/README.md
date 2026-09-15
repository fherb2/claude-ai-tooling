# Syncthing-Sync für `~/.claude`

*Stand: 2026-09-15*

*[English version](https://github.com/fherb2/claude-ai-tooling/blob/master/home-.claude-sharing/README.en.md)*

**Hält den Arbeitszustand von Claude Code und Claude Desktop — Konfiguration, Sitzungsprotokolle, Projektgedächtnis — automatisch zwischen mehreren Rechnern synchron, damit derselbe Kontext überall zur Verfügung steht. Und meldet den Ausnahmefall, den eine Synchronisation nicht selbst lösen kann: die beidseitig geänderte Datei.**

Der Abgleich läuft seit dem 11. August 2026 im Dauerbetrieb, erprobt über drei und mehr Rechner hinweg; der Wächter läuft dort als Dienst und hat echte Konflikte behandelt. Die Implementierung ist abgeschlossen, offen ist allein ein Pendant für Windows (`work-plan.md`).

## Ziel

Claude Code, Claude Desktop und die VSCode-Erweiterung halten ihren gesamten Arbeitszustand im Verzeichnis `~/.claude` des jeweiligen Rechners. Wer an mehreren Rechnern arbeitet, hat damit mehrere voneinander unabhängige Gedächtnisse: Was auf dem Laptop erarbeitet wurde, existiert auf dem Arbeitsplatzrechner nicht.

Den Abgleich selbst leistet Syncthing vollständig, über einen dauerhaft laufenden Vermittlungsknoten auf einer eigenen NAS. Die beteiligten Rechner müssen sich dafür weder sehen noch gleichzeitig eingeschaltet sein — jeder kennt nur den Knoten. Deshalb gilt alles hier Beschriebene für **beliebig viele** Rechner, nicht nur für zwei.

Die Eigenleistung dieses Vorhabens liegt woanders: Syncthing führt Dateien, die auf zwei Rechnern gleichzeitig geändert wurden, bewusst **nicht** zusammen, sondern legt die unterlegene Fassung als Konfliktkopie daneben — und meldet das niemandem. Genau dort setzt dieses Werkzeug an: Ein Wächter entdeckt solche Kopien, meldet sie und führt den Nutzer gemeinsam mit Claude durch die inhaltliche Auflösung.

## Was mitwandert — und was nicht

Abgeglichen wird der gesamte Inhalt von `~/.claude`, einschließlich der Sitzungsprotokolle und Chats unter `projects/` — sie sind der eigentliche Zweck. Ausgenommen ist, was in der Ausschlussliste `.stignore` steht; welches Muster warum, sagt Kapitel 3.9 der Doku. Daneben gibt es eine zweite Liste für einen einzelnen Rechner — siehe das nächste Kapitel.

Vier Punkte, die man vorher wissen sollte:

- **Zugangsdaten wandern nie.** `.credentials.json` ist ausgeschlossen, und die Zeile muss auf **jedem** Rechner in `~/.claude/.stignore` stehen, **bevor** der Ordner dort erstmals verbunden wird. Diese Datei wandert selbst nicht mit — Syncthing synchronisiert sie prinzipiell nicht.
- **`/rewind` über Rechnergrenzen entfällt.** Die Momentaufnahmen unter `file-history/` sind ausgeschlossen: Sie hängen an absoluten Pfaden des Rechners, der sie angelegt hat, und ihr Schreibmuster ist für einen Abgleich das ungünstigste im ganzen Ordner. Wer eine Sitzung auf dem anderen Rechner fortsetzt, hat dort keine Prüfpunkte zum Zurückspielen. Dafür gibt es die Versionsverwaltung des Projekts.
- **MCP-Server im User- und Local-Scope bleiben örtlich.** Sie liegen in `~/.claude.json`, also **außerhalb** des abgeglichenen Ordners. Wer sich auf einem Rechner einen MCP-Server einrichtet, trägt ihn auf dem anderen erneut ein. Für den Project-Scope gilt das nicht: `.mcp.json` gehört ins Repo des Projekts und wandert mit ihm.
- **Anmeldung und Gerätezustand bleiben örtlich** — ebenfalls `~/.claude.json`. Ein Kontowechsel ist deshalb eine rein örtliche Angelegenheit und erzeugt keine Konflikte.

## Einzelne Projekte von einem Rechner fernhalten

Nicht jeder Rechner soll alles bekommen. Ein Arbeitsplatzrechner kann die Konfiguration, die Skills und die `CLAUDE.md` vollständig übernehmen, von den Sitzungsprotokollen unter `projects/` aber nur ausgewählte Projekte — und die übrigen gar nicht. Dafür gibt es eine **zweite Ausschlussliste**, `~/.claude/.stignore-local`.

### Warum es zwei Listen gibt

`.stignore` hat eine maßgebliche Fassung, die auf allen Rechnern gleich ist; `install_service.sh` gleicht sie bei jeder Aktualisierung ab und bietet die Übernahme an, mit Vorgabe Ja. Wer seine eigenen Zeilen dort hineinschreibt, verliert sie beim nächsten Update — lautlos, weil ein Druck auf die Eingabetaste genügt.

`.stignore-local` wird dagegen nur angelegt, wenn sie fehlt, und **nie überschrieben**. Sie wird leer ausgeliefert und von der maßgeblichen Liste per `#include` eingebunden, und zwar weit oben: **Örtliche Muster gehen den allgemeinen vor.** Damit lässt sich hier auch eine Ausnahme von einem allgemeinen Ausschluss setzen. Nur die Zeile für die Zugangsdaten steht darüber und ist von hier aus unerreichbar.

Die Datei schließt sich selbst vom Abgleich aus — sonst trüge die Auswahl eines Rechners auf alle anderen.

### Vier Regeln, nach denen Syncthing die Muster liest

Alles Weitere folgt aus diesen vieren ([Ignoring Files](https://docs.syncthing.net/users/ignoring.html)):

1. **Die erste passende Zeile entscheidet** über eine Datei. Ausnahmen mit `!` müssen deshalb **über** dem Muster stehen, von dem sie ausnehmen.
2. **`*` erfasst keinen Pfadtrenner, `**` schon.** `/projects/*` trifft nur die oberste Ebene, `/projects/**` jeden Pfad darunter.
3. **Kommentare beginnen mit `//`, nicht mit `#`.** Das `#` ist für Direktiven wie `#include` reserviert; eine Zeile `# mein Kommentar` ist kein Kommentar, sondern wird als Muster oder als unbekannte Direktive gelesen — und meldet sich nicht.
4. **Führende und abschließende Leerzeichen werden entfernt**, Leerzeilen sind erlaubt.

### Wie ein Projektordner heißt

Claude Code legt unter `projects/` **je Arbeitsverzeichnis** einen Ordner an, nicht je Projekt. Der Name entsteht aus dem Pfad, wobei **jedes** Sonderzeichen zu einem Bindestrich wird — der Punkt eingeschlossen. Ein typischer Bestand:

    -home-mustermann                                  ← Sitzung direkt im Home
    -home-mustermann--claude                          ← /home/mustermann/.claude, zwei Bindestriche
    -home-mustermann-Downloads
    -home-mustermann-Musik
    -home-mustermann-git-image-pipeline
    -home-mustermann-git-image-pipeline-calibration   ← Sitzung in einem Unterordner
    -home-mustermann-git-sensor-firmware
    -home-mustermann-git-sensor-firmware-docs
    -tmp                                              ← Sitzung in /tmp
    -var-log-auswertung                               ← Sitzung in /var/log/auswertung

Zwei Dinge folgen daraus, und beide werden leicht übersehen:

**Ein Projekt sind oft mehrere Einträge.** Wer eine Sitzung in einem Unterordner startet, bekommt einen zweiten Ordner, dessen Name den ersten als Präfix trägt. Gibst Du nur den ersten frei, fehlen diese Sitzungen auf den anderen Rechnern.

**Den Namen liest man ab, man bildet ihn nicht.** `ls ~/.claude/projects/` zeigt, wie er wirklich heißt.

### Beispiel A — nur ein Projekt mitnehmen

Dieser Rechner soll von allen Sitzungsprotokollen einzig `image-pipeline` bekommen:

    // nur dieses Projekt, samt Sitzungen aus seinen Unterordnern
    !/projects/-home-mustermann-git-image-pipeline
    !/projects/-home-mustermann-git-image-pipeline/**
    !/projects/-home-mustermann-git-image-pipeline-*
    !/projects/-home-mustermann-git-image-pipeline-*/**

    // alles andere unter projects/
    /projects/**

Aus dem Bestand oben bleiben damit `-home-mustermann-git-image-pipeline` und `-home-mustermann-git-image-pipeline-calibration`; alle übrigen acht fallen weg.

**Die beiden `-*`-Zeilen haben einen Preis:** Ein eigenständiges Nachbarprojekt, dessen Name zufällig so beginnt — etwa `image-pipeline-old` —, wird mit erfasst. Gibt es so eines, zähle die Unterordner lieber einzeln auf.

### Beispiel B — das eigene Home und alle git-Projekte

    // eigenes Home und alles unter ~/git
    !/projects/-home-mustermann
    !/projects/-home-mustermann/**
    !/projects/-home-mustermann-git-*
    !/projects/-home-mustermann-git-*/**

    // alle uebrigen Ordner des eigenen Home
    /projects/-home-mustermann-*
    /projects/-home-mustermann-*/**

Hier genügt **ein** Sternchen für die Unterordner-Projekte, weil alle denselben Präfix tragen: `-home-mustermann-git-*` erfasst auch `…-image-pipeline-calibration`.

**Diese Fassung hat eine Lücke**, und sie ist der Grund für das nächste Beispiel: Sie sperrt nur, was mit `-home-mustermann-` beginnt. `-tmp` und `-var-log-auswertung` kämen durch — und solche Einträge entstehen, sobald Du Claude Code einmal in `/tmp`, `/var/log/…` oder sonstwo außerhalb Deines Home-Verzeichnisses startest.

### Beispiel C — dieselbe Auswahl, dicht gemacht

    // eigenes Home und alles unter ~/git
    !/projects/-home-mustermann
    !/projects/-home-mustermann/**
    !/projects/-home-mustermann-git-*
    !/projects/-home-mustermann-git-*/**

    // alles andere, gleich aus welchem Verzeichnis es stammt
    /projects/**

Der Unterschied ist die letzte Zeile. `/projects/**` fängt **jeden** Eintrag, gleich wie er heißt — Du musst die möglichen Namen also gar nicht kennen. Nur was darüber ausdrücklich erlaubt ist, kommt durch.

Damit werden auch die beiden `-home-mustermann`-Zeilen tragend, die in Beispiel B noch überflüssig waren: Vorher traf sie kein Muster, jetzt fängt sie das Auffangnetz, und nur die Ausnahme holt sie zurück.

**Diese Form ist die empfehlenswerte.** Eine Positivliste irrt in die harmlose Richtung: Ein vergessener Eintrag kostet ein Projekt, das auf diesem Rechner fehlt. Bei einer Negativliste landet ein neu angelegtes Projekt ungefragt dort, wo es nicht hinsoll.

### Ausschließen heißt beides zugleich

Was hier ausgeschlossen ist, wird **weder empfangen noch gesendet**. Eine Einbahnstraße — von hier senden, aber nichts empfangen — gibt es in Syncthing für einzelne Unterordner nicht: Die Richtungseinstellung („Send Only", „Receive Only") gilt immer für den ganzen Ordner und lässt sich auch nicht je Gegenstelle unterscheiden.

Was Du hier aussperrst, bleibt auf den anderen Rechnern selbstverständlich erhalten. Es kommt nur hier nicht an.

### Zwei Dinge liegen außerhalb von `projects/`

Projektbezogenes steckt nicht nur in den Sitzungsprotokollen:

| Ort | was drinsteckt |
| --- | --- |
| `history.jsonl` | jeder getippte Prompt, mit Zeitstempel und Projektpfad |
| `paste-cache/` | die eingefügten Textinhalte dazu |

Beide sind **nicht projektweise trennbar** — die Historie ist eine einzige Datei über alle Projekte, die Paste-Dateien tragen im Namen nur einen Hash. Für einen Rechner mit Auswahl gibt es dort nur ganz oder gar nicht:

    /history.jsonl
    /paste-cache

Der Preis betrifft allein diesen Rechner: Der Rückruf per Pfeiltaste, die Suche mit `Ctrl+R` und die Vervollständigung von `!`-Shell-Befehlen greifen dann nur noch auf das zurück, was hier getippt wurde.

### Prüfen, ob die Muster wirklich greifen

Ein falsch formuliertes Muster sieht aus, als wirkte es. Die Probe geht mit einer harmlosen Datei statt mit echtem Gut:

```bash
# auf diesem Rechner
echo "probe 1" > ~/.claude/probe-muster.txt
# → auf einem anderen Rechner abwarten, bis sie ankommt

echo "/probe-muster.txt" >> ~/.claude/.stignore-local
# → in Syncthing (http://127.0.0.1:8384) den Ordner einmal neu einlesen lassen

echo "probe 2" > ~/.claude/probe-muster.txt
# → auf dem anderen Rechner darf die Änderung NICHT mehr ankommen
```

Danach den Eintrag entfernen und die Probedatei überall löschen. Das Neueinlesen gehört dazu: Wann Syncthing eine geänderte Ausschlussliste von selbst liest, steht in seiner Dokumentation an keiner Stelle.

### Nachträglich ausschließen — die Reihenfolge entscheidet

Ist das Auszuschließende schon abgeglichen, hängt alles daran, was zuerst geschieht. Drei Fälle:

1. **Es wird laufend neu erzeugt** (etwa `backups/`): erst das Muster setzen und wirksam werden lassen, **dann** löschen. Die Löschung bleibt dann örtlich, ist also auf jedem Rechner einzeln nötig.
2. **Vor dem Muster löschen**: Die Löschung wandert an alle — und der Erzeuger schreibt die Datei sofort neu. Das läuft hin und her.
3. **Eine einmalige Datei, die niemand neu erzeugt**: einfach löschen. Die Löschung wandert überall hin, und das ist hier genau richtig.

**Ein Muster löscht nichts.** Was schon auf der Platte liegt, bleibt liegen — Syncthing hört nur auf, es zu pflegen. Wer Platz gewinnen will, löscht selbst.

**Vor jeder Aktualisierung** ist zu prüfen, ob in `~/.claude/.stignore` eigene Zeilen stehen — siehe „Aktualisieren".

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

Das Installationsskript prüft sie einzeln und **in dieser Reihenfolge** — es bricht beim ersten harten Fehlbefund ab, damit Du nicht erst nach zehn Meldungen erfährst, dass es gar nicht weitergeht.

**Abbruch, wenn es fehlt:**

| Voraussetzung | warum hart |
| --- | --- |
| ein steuerndes Terminal | Jeder Schritt danach darf fragen, und `sudo` liest sein Passwort von dort. Ohne Terminal bliebe eine Frage unbeantwortbar. Geprüft wird durch **Öffnen** von `/dev/tty` |
| der Werkzeugordner liegt in `~/.claude-sync-watch` | Die Dienstdefinition verweist fest darauf. Liegt er woanders, nennt das Skript den Verschiebebefehl |
| die eigenen Dateien sind vollständig | Wächter, Dienstdefinition, Meldungskatalog, Arbeitsanweisung, Ausschlussliste. Abhilfe: das Paket noch einmal vollständig entpacken |
| `/usr/bin/python3` ist ausführbar | Genau dieser Interpreter startet den Dienst — nicht der `python3` Deiner Shell |
| Claude Code ist vorhanden, ausführbar **und angemeldet** | **Wo** es liegt, sucht das Skript selbst: erst im Suchpfad, dann `~/.local/bin`, `/usr/local/bin`, `/usr/bin`. Die Anmeldung prüft es über `claude auth status`. Abhilfe: `claude` von Hand starten und `/login` |
| `python3-watchdog` im **Dienst-Interpreter** | Ohne die Beobachtungsbibliothek läuft der Dienst nicht. Das Skript fragt, ob es nachinstallieren soll; bei „nein" bricht es ab |
| `zenity` | Ohne Zenity fällt die gesamte Meldung und Eskalation aus — der Wächter existiert für nichts anderes. Rückfrage wie oben |
| `systemctl` | Dieses Skript richtet einen systemd-Benutzerdienst ein |
| `~/.claude` existiert | Ohne den Ordner gibt es nichts zu beobachten |

**Nur eine Warnung, die Einrichtung läuft weiter:**

| Befund | Folge |
| --- | --- |
| Claude Code antwortet nicht auf eine Probefrage | Abgelaufenes Abonnement, erschöpftes Kontingent oder keine Verbindung. Eine hängende Leitung ist kein Beweis für eine fehlende Anmeldung |
| `libnotify-bin` fehlt | **Zubehör, kein Abbruchgrund.** Es fehlt allein die stündliche Betriebsmeldung; Erkennung und Eskalation arbeiten vollständig |
| Syncthing gleicht `~/.claude` nicht ab | Der Wächter wird eingerichtet, findet aber nie etwas. Genau der stille Ausfall, vor dem diese Prüfung warnt |
| Syncthing läuft gerade nicht | Ohne laufendes Syncthing entstehen keine Konfliktkopien — der Dienst ist deswegen nicht falsch eingerichtet |

**Das Skript installiert nichts stillschweigend.** Fehlt ein Paket, nennt es die Folge und fragt; die Vorgabe bei leerer Antwort ist **nein**. Der Befehl, den es ausführen würde, steht vorher da (`sudo apt install …`), und das System fragt anschließend nach Deinem Passwort.

**Eine Falle, die zwei Interpreter betrifft:** Geprüft wird `watchdog` in `/usr/bin/python3`, nicht im `python3` Deiner Shell. Auf einem Rechner mit aktivem virtualenv sind das zwei verschiedene Programme — die Prüfung meldete dort „watchdog fehlt", während der Dienst tadellos lief, und schickte den Nutzer in eine Sackgasse. Seither prüft das Skript denselben Interpreter, den die Dienstdefinition startet.

## Installation

**Der Normalfall ist ein Rechner, der schon ein eigenes, gewachsenes `~/.claude` hat** — darin stecken die Chats seiner lokalen Projekte und die aus Claude Desktop. Dieser Bestand darf nicht überschrieben werden, und genau deshalb sieht der Weg unten so aus und nicht wie ein gewöhnliches „Ordner synchronisieren": Der Erstabgleich **vereinigt** zwei gewachsene Bestände, und der Zusammenführungsschritt dabei ist eingeplant.

1. **Bestand sichern.** `cp -a ~/.claude ~/.claude.vor-sync` — die einzige Rückfalllinie dieses Vorgangs. Sie wird erst am Ende aufgelöst.
2. **Werkzeugpaket entpacken.** `downloads/claude-sync-watch_de_local.zip` aus diesem Ordner herunterladen, dann `unzip claude-sync-watch_de_local.zip -d ~`. Das legt `~/.claude-sync-watch/` mit allen benötigten Dateien an. **Das Paket bestimmt die Sprache:** Dieses hier bringt den deutschen Meldungskatalog und die deutsche Arbeitsanweisung mit, das englische (`claude-sync-watch_en_local.zip`) die englischen. Einzustellen ist dazu nichts. Dieser Ort ist **Vorschrift**, keine Empfehlung: Die Dienstdefinition verweist fest darauf, und das Installationsskript verweigert den Dienst an jedem anderen Ort. Der Ordner ist versteckt; Kontrolle mit `ls -d ~/.claude-sync-watch`. Der Dienst wird hier noch **nicht** eingerichtet.
3. **Beide Ausschlusslisten anlegen — vor dem Teilen.**

        cp ~/.claude-sync-watch/.stignore ~/.claude/.stignore
        cp ~/.claude-sync-watch/.stignore-local ~/.claude/.stignore-local

   **Die zweite Zeile gehört dazu, nicht erst später:** Die maßgebliche Liste bindet die örtliche per `#include` ein, und eine fehlende Include-Datei ist für Syncthing ein Fehler — in der Zeit bis zum Einrichten des Dienstes liefe also der Erstabgleich mit einer Liste, deren Wirkung offen ist. Die örtliche Datei ist leer; gefüllt wird sie erst, wenn dieser Rechner eine Auswahl treffen soll. Warum überhaupt vorher: Syncthing synchronisiert diese Datei nicht, sie muss auf jedem Rechner einzeln vorhanden sein — und fehlt sie beim ersten Abgleich, wandern die Zugangsdaten los. Was Syncthing später im Reiter *Ignore Patterns* anzeigt, ist genau diese Datei; vor dem Teilen gibt es den Reiter noch nicht.
4. **Den Ordner in Syncthing teilen.** Die Oberfläche liegt unter `http://127.0.0.1:8384`. Dort **Add Folder**, und dann kommt es auf vier Felder an:

   - **Folder ID** — dieselbe Kennung wie auf den übrigen Geräten, **zeichengleich**. Wo Du sie findest: auf einem schon verbundenen Rechner in der Ordnerübersicht, den Ordner aufklappen, Zeile „Folder ID". Weicht sie auch nur in einem Zeichen ab, gilt der Ordner für Syncthing als ein anderer, und es wird nie etwas abgeglichen — ohne Fehlermeldung, denn aus seiner Sicht ist alles in Ordnung.
   - **Folder Path** — `~/.claude`.
   - **Reiter Sharing** — den Knoten anhaken. Die anderen Arbeitsrechner **nicht**: Der Verbund ist sternförmig, jeder Rechner kennt nur den Knoten.
   - **Reiter Ignore Patterns** — hier steht jetzt der Inhalt der `.stignore`, die Du in Schritt 3 angelegt hast. Ein Blick darauf ist die einfachste Bestätigung, dass sie am richtigen Ort liegt.

   Speichern. Am Knoten erscheint daraufhin die Rückfrage, ob der angebotene Ordner angenommen werden soll; dort ist als Pfad ein Unterordner des Syncthing-Datenverzeichnisses anzugeben. Alle Geräte bleiben auf **Send & Receive** — „Receive Only" am Knoten wäre falsch, er muss die Änderungen ja weitergeben. Die Handgriffe im Einzelnen stehen in Abschnitt 7 des Setup-Guides.
5. **Erstabgleich abwarten.** Die Oberfläche zeigt währenddessen „Syncing" mit einem Fortschrittswert, am Ende auf **beiden** Seiten „Up to Date". Wie lange das dauert, hängt an der Menge — bei einem gewachsenen `~/.claude` sind es einige hundert Megabyte, also Minuten, nicht Stunden.

   Was dabei geschieht: Einseitig vorhandene Dateien werden verteilt; beidseitig vorhandene, inhaltlich verschiedene erzeugen Konfliktkopien mit `.sync-conflict-` im Namen. Wie viele es werden, hängt an der Divergenz der Bestände — **das ist der geplante Zusammenführungsschritt, kein Fehler.** Zählen lassen sie sich mit

        find ~/.claude -name '*.sync-conflict-*' | wc -l

   **Bleibt die Anzeige auf „Out of Sync" stehen**, klappe den Ordner auf: Syncthing nennt dort die Dateien, die es nicht übertragen konnte. Der häufigste Grund sind Rechte, der zweithäufigste eine Datei, die sich während der Übertragung ständig ändert.
6. **Konfliktkopien auflösen, von Hand gestartet.** Der Wächter läuft noch nicht, und das ist Absicht: Er soll auf einem konfliktfreien Stand anfangen, und während eines laufenden Erstabgleichs kämen fortlaufend neue Kopien dazwischen. Deshalb hier einmal selbst:

        cd ~/.claude
        claude --append-system-prompt-file ~/.claude-sync-watch/conflict-resolution.de.md \
               "Der zu durchsuchende Ordner ist ~/.claude. Löse die dort liegenden Konfliktkopien auf."

   Das Arbeitsverzeichnis ist tragend, nicht Zierde: Claude Code übernimmt es vom aufrufenden Prozess. Die mitgegebene Arbeitsanweisung ist dieselbe, die der Wächter später verwendet — ohne sie zieht die Sitzung die Projektmethodik aus `~/.claude/CLAUDE.md` heran, die hier nicht gilt und in die Irre führt. Die Sitzung geht Paar für Paar mit Dir durch und schreibt oder löscht nichts ohne Deine Zustimmung. Zum Schluss selbst nachsehen: `find ~/.claude -name '*.sync-conflict-*'` muss leer bleiben.
7. **Dienst einrichten.** `~/.claude-sync-watch/install_service.sh` starten — aus jedem Arbeitsverzeichnis heraus, das Skript findet seinen Ordner selbst. Es prüft die Voraussetzungen von oben, vergleicht `~/.claude/.stignore` mit der maßgeblichen Fassung im Werkzeugordner und **bietet die Übernahme an**, falls sie abweicht; hier ist die Vorgabe **ja**. Wurde tatsächlich kopiert, empfiehlt es, den Ordner in Syncthings Oberfläche (`http://127.0.0.1:8384`) einmal neu einlesen zu lassen. Danach startet der Wächter bei jeder Anmeldung an der grafischen Sitzung von selbst und endet mit ihr. Mitlesen: `journalctl --user -u claude-sync-watch.service -f`.
8. **Sicherung auflösen**, nach angemessener Beobachtungszeit — nicht am selben Tag.

### Läuft es? Drei Kontrollen

Nach Schritt 7 lässt sich in einer Minute feststellen, ob alles steht:

```bash
systemctl --user status claude-sync-watch.service   # muss "active (running)" zeigen
journalctl --user -u claude-sync-watch.service -n 20
find ~/.claude -name '*.sync-conflict-*'            # muss leer bleiben
```

Dazu der Blick in Syncthings Oberfläche: Der Ordner steht auf **„Up to Date"**, und der Knoten ist als **verbunden** aufgeführt.

**Das Journal schweigt im Normalbetrieb**, und das ist Absicht: Der Sicherheits-Suchlauf läuft alle fünfzehn Minuten und würde es sonst mit „nichts gefunden" füllen. Eine Zeile erscheint nur, wenn ein Durchgang etwas gefunden hat. Das erste echte Lebenszeichen ist deshalb die **stündliche Betriebsmeldung** — spätestens nach einer Stunde sollte sie erscheinen.

### Der allererste Rechner

Dort, wo der Verbund beginnt, gibt es noch keinen abgeglichenen Ordner und keinen Knoten. Zuerst wird also der Knoten eingerichtet (`syncthing-synology-setup-guide.md`, Abschnitte 1 bis 9), und der Ordner wird **von diesem Rechner aus** angelegt — er hat den Inhalt, der Knoten ist leer.

Die Schritte 1 bis 4 und 7 bis 8 von oben gelten unverändert. **Die Schritte 5 und 6 entfallen:** Es gibt keinen zweiten Bestand, mit dem sich etwas vereinigen könnte, also entstehen keine Konfliktkopien. Erst der nächste Rechner durchläuft den vollständigen Weg.

### Aktualisieren

**Zuerst, noch vor dem Entpacken: eigene Zeilen retten.** Steht in `~/.claude/.stignore` etwas, das Du dort selbst eingetragen hast, überschreibt die Aktualisierung es — die maßgebliche Fassung gewinnt, und die Rückfrage hat die Vorgabe Ja. Sichtbar wird es mit

    diff ~/.claude/.stignore ~/.claude-sync-watch/.stignore

Alles, was dort nur für diesen Rechner gilt, gehört **vorher** nach `~/.claude/.stignore-local` (siehe „Einzelne Projekte von einem Rechner fernhalten"). Genau auf diesem Weg sind auf einem Rechner schon einmal zwei Ausschlüsse verschwunden. Nach der Umstellung auf die zweite Liste ist hier normalerweise nichts mehr zu tun — die Prüfung kostet einen Befehl und ist die einzige Gelegenheit, es zu merken.

Eine bestehende Installation wird nicht neu aufgesetzt, sondern überschrieben: das aktuelle Paket herunterladen und `unzip -o claude-sync-watch_de_local.zip -d ~` aufrufen. **Das `-o` gehört dazu** — ohne es fragt `unzip` bei jeder schon vorhandenen Datei einzeln nach. Danach `~/.claude-sync-watch/install_service.sh` starten: Erst das erneuert die Dienstdefinition und startet den Wächter mit der neuen Fassung. Wer nur entpackt, hat die neuen Dateien auf der Platte und den alten Wächter im Betrieb. Unberührt bleiben dabei `~/.claude` und die Zustandsdatei `zustand.json`.

**Entpacken löscht nichts.** Aus einer Installation von vor der Sprachtrennung bleibt deshalb `conflict-resolution.md` liegen — die Arbeitsanweisung ohne Sprachkürzel. Gelesen wird sie nicht mehr, denn der Wächter bildet den Namen aus seiner Sprache (`conflict-resolution.de.md`); sie sieht nur aus wie die maßgebliche. Das Installationsskript benennt, was es davon findet, und entfernt nichts von selbst: Auf einem fremden Rechner zu löschen ist nicht seine Sache. **Kein** Überbleibsel ist dagegen `__pycache__/` — den legt Python selbst an, sobald der Wächter seinen Meldungskatalog lädt; gelöscht entsteht er beim nächsten Lauf erneut.

**Ein Ordner, ein Katalog.** Liegen mehrere `messages_*.py` nebeneinander — weil beide Pakete entpackt oder Dateien aus dem Repository dazukopiert wurden —, entscheidet nicht mehr das Paket über die Sprache, sondern der Schalter `--lang`. Die Dienstdefinition übergibt keinen, also gilt Deutsch. Auch darauf weist das Installationsskript hin.

### Wieder abmelden

`~/.claude-sync-watch/uninstall_service.sh` entfernt den Dienst — nicht den Ordner und nicht den Abgleich. Wer das Werkzeug ganz loswerden will, löscht danach `~/.claude-sync-watch/` von Hand; `~/.claude` und die Syncthing-Freigabe bleiben davon unberührt.

## Im Alltag

**Der Abgleich braucht kein Zutun.** Er läuft ereignisgesteuert; eine Änderung ist meist binnen Sekunden auf dem Vermittlungsknoten, und ein ausgeschalteter Rechner holt beim nächsten Start selbsttätig nach.

**Zwei Gewohnheiten verhindern Konflikte, statt sie zu lösen:** nach dem Einschalten erst den Abgleich ankommen lassen und dann mit Claude arbeiten; und einen Rechner nicht ausschalten, solange die Oberfläche noch „Syncing" zeigt. Das Konfliktfenster ist bei abwechselnd benutzten Rechnern nicht die Übertragungsdauer, sondern die Zeit zwischen der letzten Änderung hier und dem ersten Nachholen dort.

**Einmal je Stunde meldet sich der Wächter** — kurz eingeblendet, nicht anzuklicken. Sie ist das Lebenszeichen eines Dienstes, dem man sonst nicht ansieht, ob er arbeitet oder seit Tagen klemmt:

    abgeglichen: 0.8 MB hoch, 0.3 MB herunter
    kein Konflikt seit 74 Stunde(n)

Vier Formen dieser Meldung verlangen Aufmerksamkeit und bleiben deshalb länger stehen: `3 Konflikt(e) seit 9 Stunde(n) ungelöst` — eine vertagte Lösung gerät nicht in Vergessenheit; `Rückstand: 7 Datei(en)` — es klemmt etwas, und davon erfährt man sonst nie etwas; `Abgleich für diesen Ordner angehalten — Änderungen und Konfliktkopien bleiben liegen` — eine selbst gesetzte, vergessene Pause legt den Abgleich sonst unbemerkt still; und `keine Verbindung zum Abgleich seit …`. Steht dort statt einer Zahl `Zähler neu gesetzt` oder `Zählung neu begonnen`, fehlt schlicht der Vergleichswert — nach einer Neuverbindung etwa, wie sie ein Wechsel des WLAN mit sich bringt.

**Bleibt die stündliche Meldung dauerhaft aus, ist das selbst ein Befund.** Dann nachsehen, ob der Dienst überhaupt läuft (`systemctl --user status claude-sync-watch.service`) und was im Journal steht (`journalctl --user -u claude-sync-watch.service -n 50`). Häufigste Ursache ist eine Anmeldung ohne grafische Sitzung — der Dienst hängt an ihr und endet mit ihr.

**Bei einem Konflikt** fragt ein Dialog, ob jetzt gelöst werden soll („Jetzt lösen" / „Später"). Bei Zustimmung öffnet sich ein Terminal mit einer Claude-Code-Sitzung, die alle anstehenden Konfliktpaare **einzeln mit dem Nutzer** durchgeht: Sie vergleicht Original und Kopie, erklärt den Unterschied und holt die Entscheidung ein — Original behalten, Kopie übernehmen oder zusammenfügen. Geschrieben oder gelöscht wird **nichts** ohne ausdrückliche Zustimmung zur konkreten Datei; am Ende berichtet die Sitzung, was sie getan hat.

Zwei Dinge dazu:

- **Gelöst wird immer nur an einem Rechner.** Löschung der Kopie und Aktualisierung des Originals wandern als gewöhnliche Dateivorgänge mit — wer hier löst, räumt überall auf. Wird derselbe Konflikt an zwei Rechnern unterschiedlich entschieden, entsteht ein neuer.
- **Ein unbeantworteter Dialog schließt sich nach fünfzehn Minuten selbst** und fragt frühestens nach dreißig Minuten erneut. Die stündliche Meldung ist die leise Erinnerung dazwischen.

## Wenn etwas kaputt ist

**Kein Notfall** ist eine inhaltlich unschön aufgelöste Datei — die wird normal nachgearbeitet. Ein Notfall sieht so aus: Claude Code startet nicht mehr, verlangt eine erneute Anmeldung, findet ein Projekt nicht mehr, oder eine Einstellung ist verschwunden. Auch dann kann die Ursache eine andere sein als der Abgleich, und die Reihenfolge trennt beides:

1. **Alle Claude-Sitzungen ordentlich schließen** (`/exit`), im Terminal wie in VSCode. Die des **anderen** Rechners erst, wenn das hier nichts gebracht hat.
2. **Hängengebliebene Prozesse beenden:** `pkill -u $USER claude`. Der Wächter ist davon nicht betroffen; er beobachtet nur.
3. **Sitzung neu öffnen.** Läuft sie wieder, ist hier Schluss — es war kein Synchronisationsschaden, und es ist nichts zurückzuholen.
4. Erst wenn es weiter kaputt ist: **Sicherung anlegen** (`cp -a ~/.claude ~/.claude.kaputt-<Datum>`), **dann** den Abgleich für diesen Ordner pausieren — in der Oberfläche den Ordner aufklappen und **Pause** wählen. Die Sicherung steht bewusst vor dem Pausieren: Pausieren hält nur die Weiterverbreitung auf, es macht nichts rückgängig.
5. **Einzelne Dateien zurückholen**, im Regelfall aus dem „Staggered"-Bestand der NAS — sie empfängt von allen Rechnern und archiviert deshalb jeden übertragenen Stand. Die Archivfassungen liegen dort im Unterordner `.stversions/` des abgeglichenen Ordners, benannt nach dem Zeitpunkt ihrer Verdrängung; zurückgeholt wird durch schlichtes Kopieren an den ursprünglichen Ort. Das **lokale** `~/.claude/.stversions/` taugt nur, wenn der Schaden von der Gegenseite hereinkam: Syncthing archiviert ausschließlich **eintreffende** Fremdänderungen vor dem Überschreiben, nie die eigenen — und genau die eigene Zerschreibung ist der häufigere Fall.
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
