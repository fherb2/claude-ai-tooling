# Syncthing auf Synology (SynoCommunity-Paket) — Abgleich eines Ordners zwischen mehreren Rechnern

Aufbau für zwei (oder mehr) Rechner, die sich gegenseitig **nie** direkt sehen und auch nicht gleichzeitig eingeschaltet sein müssen. Die Synology dient als dauerhaft laufender Vermittlungsknoten.

## 0. Vorbemerkung: warum ein Knoten und kein Relay

Syncthing ist im Kern ein Peer-to-Peer-Werkzeug. Für den hier beschriebenen Fall ist eine Eigenheit entscheidend: Die öffentlichen **Relay-Server speichern nichts**. Sie leiten nur zwischen zwei Geräten weiter, die **gleichzeitig** verbunden sind — laut Doku „the relay only retransmits the encrypted data much like a router" ([Relaying](https://docs.syncthing.net/users/relaying.html)). Zwei Rechner, die nie zusammen online sind, können über ein Relay also *nicht* abgleichen.

Deshalb läuft auf der Synology eine **vollwertige Syncthing-Instanz**, die eine komplette Kopie des Ordners hält. Rechner A gleicht mit ihr ab, später gleicht Rechner B mit ihr ab. Der Datenfluss ist damit A → Synology → B, ohne dass sich A und B je begegnen.

Daraus folgt: Der Ordner liegt dreimal vor (A, Synology, B). Der Platzbedarf auf der Synology entspricht der Ordnergröße plus dem, was die Versionierung (Abschnitt 9) aufhebt.

## 1. Paketquelle hinzufügen und Syncthing installieren

Syncthing wird als Paket von **SynoCommunity** installiert. Das Paket ist aktiv gepflegt und folgt der offiziellen Versionsreihe.

**Paketquelle eintragen:**

1. **Paketzentrum → Einstellungen → Allgemein**: Vertrauensebene auf **„Synology Inc. und vertrauenswürdige Herausgeber"** setzen.
2. Reiter **Paketquelle → Hinzufügen**:
   - Name: `SynoCommunity`
   - Speicherort: `https://packages.synocommunity.com/`
3. Bestätigen. Die Community-Pakete erscheinen danach im Paketzentrum unter **Community**.

**Installieren:** Dort `Syncthing` suchen und installieren.

**Zum Warnhinweis:** Bei Installation und jeder Aktualisierung meldet DSM, das Paket stamme von Drittanbietern und sei nicht von Synology geprüft. Das ist unter DSM 7 unvermeidbar — dort lassen sich grundsätzlich keine Fremdherausgeber als vertrauenswürdig einstufen — und kein Hinweis auf ein Problem.

**Der Installationsassistent fragt nach Benutzername und Passwort für die Weboberfläche.** Beides gleich ordentlich vergeben: Daraus werden die Zugangsdaten erzeugt, und die Oberfläche ist damit von der ersten Sekunde an geschützt. Das ist ein handfester Vorteil gegenüber einer Installation von Hand, bei der Syncthing zunächst ganz ohne Passwort startet.

## 2. Ablageorte und Datenordner

### Wo das Paket selbst liegt

Die Ablage gibt DSM vor, sie ist nicht wählbar:

- **Konfiguration und Datenbank:** `/var/packages/syncthing/var` (verweist auf `/volume1/@appdata/syncthing`)
- **Programm:** `/var/packages/syncthing/target` (verweist auf `/volume1/@appstore/syncthing`)

Diese Trennung ist beabsichtigt: Bei einer Paketaktualisierung ersetzt DSM den Programmteil, der `var`-Bereich mit deinen Einstellungen bleibt erhalten.

### Ordner für die abzugleichenden Daten anlegen

Dafür einen **freigegebenen Ordner** anlegen (Systemsteuerung → Freigegebener Ordner → Erstellen), z. B. `syncthing-data`. Innerhalb davon später je Abgleich ein Unterordner.

**Rechte vergeben — hier liegt der entscheidende Handgriff:** Das Paket läuft unter dem von DSM angelegten Benutzer **`sc-syncthing`**. Dieser muss Lese- und Schreibrechte auf dem Ordner haben:

- Systemsteuerung → Freigegebener Ordner → Ordner auswählen → **Bearbeiten → Berechtigungen**
- In der Auswahlliste oben von „Lokale Benutzer" auf **„System-interner Benutzer"** umschalten
- `sc-syncthing` suchen und **Lesen/Schreiben** setzen

Ohne diesen Schritt scheitert Syncthing beim Anlegen seiner Ordnermarkierung; typische Fehlermeldungen sind `Failed to create folder marker: stat .stfolder: permission denied` oder `Loading ignores: lstat .stignore: permission denied`.

### Drei Synology-Besonderheiten, die unabhängig vom Installationsweg gelten

- Ist beim freigegebenen Ordner **„Zugriff auf Administratoren beschränken"** aktiviert, kommt Syncthing nicht hinein. Deaktivieren.
- Der Papierkorb-Ordner **`#recycle`** ist standardmäßig nur für Administratoren zugänglich und erzeugt fortlaufend Fehler des Dateisystem-Beobachters. Entweder `sc-syncthing` Zugriff geben oder `#recycle` in die Ausschlüsse (Abschnitt 8) aufnehmen. Am einfachsten ist es, den Papierkorb für diesen Ordner gar nicht erst zu aktivieren.
- Falls der Ordner zusätzlich eine **Windows-ACL** trägt (erkennbar am `+` hinter den Rechten bei `ls -ld`), können die Unix-Rechte davon überlagert werden. Für einen reinen Abgleichordner ohne SMB-Zugriff ist die ACL entbehrlich.

## 3. Weboberfläche prüfen

Nach dem Start ist die Oberfläche unter `http://<synology-ip>:8384` erreichbar; im Hauptmenü von DSM liegt außerdem ein Symbol für Syncthing.

Anmelden mit den im Assistenten vergebenen Zugangsdaten. Dann kurz kontrollieren:

- **Actions → Settings → GUI**: Benutzername ist gesetzt, Passwort ist gesetzt.
- **„Use HTTPS for GUI"** aktivieren, falls nicht ohnehin schon geschehen.

Das Paket verknüpft, sofern auf der Synology ein gültiges Zertifikat vorliegt, das **DSM-Zertifikat** in Syncthings Konfiguration. Die Oberfläche kann damit ohne weiteres Zutun per HTTPS laufen.

**Niemals `insecureAdminAccess` setzen** — diese Einstellung erlaubt den Zugriff auf die Oberfläche ganz ohne Anmeldung.

Sollte die Oberfläche vom Netz aus nicht erreichbar sein, sondern nur lokal auf der NAS, ist in den Einstellungen die Lauschadresse der Oberfläche zu prüfen (`GUI Listen Address`): Sie muss `0.0.0.0:8384` lauten, nicht `127.0.0.1:8384`.

## 4. Portfreigabe im Router und DSM-Firewall

Da Syncthing hier nativ auf der NAS läuft, belegt es deren Ports direkt — eine Portabbildung wie bei einem Container gibt es nicht.


| Port      | Zweck                   | ins Internet?    |
| --------- | ----------------------- | ---------------- |
| 8384/tcp  | Weboberfläche          | **nein**         |
| 22000/tcp | Abgleichprotokoll       | **ja**           |
| 22000/udp | QUIC-Transport          | ja (empfohlen)   |
| 21027/udp | Geräteerkennung im LAN | nein, rein lokal |

**Im Router** müssen **22000/TCP und 22000/UDP** auf die Synology weitergeleitet werden ([Firewall-Doku](https://docs.syncthing.net/users/firewall.html)). Der extern freigegebene Port muss derselbe sein wie der interne.

**In der DSM-Firewall** (Systemsteuerung → Sicherheit → Firewall), sofern aktiviert, müssen dieselben Ports freigegeben sein. Diesen Schritt gibt es bei einer Container-Installation nicht, weil dort die Portabbildung das mit erledigt — beim Paket ist er leicht zu übersehen.

Ohne diese Freigaben funktioniert der Abgleich nur, solange beide Seiten gleichzeitig online sind und über einen öffentlichen Relay zueinander finden — also genau nicht in dem Szenario, für das dieser Aufbau gedacht ist.

## 5. Weboberfläche von außen erreichbar machen (optional)

Für den reinen Eigengebrauch entbehrlich: Die Konfiguration erfolgt selten, und ein Zugriff aus dem LAN oder über VPN genügt meist. Wer die Oberfläche dennoch von außen erreichen will, legt sie hinter den Reverse Proxy (Systemsteuerung → Anmeldeportal → Erweitert → Reverse Proxy), Ziel `http://localhost:8384`.

**Wichtig sind vor allem großzügige Zeitüberschreitungen** (`proxy_read_timeout`/`proxy_send_timeout` in der Größenordnung von 600 Sekunden). Die Oberfläche hält lange Abfragen offen, um Änderungen sofort anzuzeigen; bei knappen Zeitüberschreitungen bricht die Verbindung ständig ab. Weiterzureichen sind außerdem die üblichen Kopfzeilen `Host`, `X-Real-IP`, `X-Forwarded-For` und `X-Forwarded-Proto`. Im DSM findet sich unter „Benutzerdefinierter Kopfbereich" auch ein Fertigmuster für WebSocket-Header; ob Syncthings Oberfläche WebSockets zwingend braucht, ist in der Doku **nicht** beschrieben — das Muster zu setzen schadet nicht, die Zeitüberschreitungen sind der wichtigere Punkt.

## 6. Geräte koppeln

Zur Client-Installation siehe Kapitel 10.

Jedes Syncthing hat eine **Geräte-ID** — eine lange Zeichenkette, die zugleich der öffentliche Schlüssel ist. Gekoppelt wird immer beidseitig:

1. Auf der Synology: **Actions → Show ID**, ID notieren (oder QR-Code).
2. Auf Rechner A: **Add Remote Device**, ID der Synology eintragen, Namen vergeben, speichern.
3. Zurück auf der Synology erscheint eine Rückfrage, ob das neue Gerät zugelassen werden soll → bestätigen.
4. Für Rechner B genauso.

**Erwartetes Ergebnis:** Synology kennt A und B; A kennt nur die Synology; B kennt nur die Synology. A und B werden **nicht** miteinander gekoppelt — sie sollen sich ja nicht sehen.

**Wichtig — „Introducer" ausgeschaltet lassen.** Ist diese Option bei einem Gerät gesetzt, reicht es die ihm bekannten Geräte-IDs an seine Gegenstellen weiter. Auf der Synology gesetzt, würde sie also A und B einander bekannt machen, die sich daraufhin direkt zu verbinden versuchen — genau das, was dieser Aufbau vermeiden soll. Die Vorgabe ist „aus"; sie darf nicht versehentlich beim Anlegen des Geräts aktiviert werden.

**Portfreigabe nur auf der Synology-Seite nötig.** Weil Syncthing-Verbindungen in beide Richtungen aufgebaut werden können, genügt es, dass der Knoten erreichbar ist. Die Arbeitsrechner hinter einem NAT-Router brauchen keine eigene Freigabe.

Damit die entfernten Rechner die Synology zuverlässig finden, empfiehlt es sich, beim Gerät „Synology" unter **Advanced → Addresses** statt `dynamic` die feste Adresse einzutragen:

```
tcp://deine-domain.tld:22000
```

Mit einer festen Adresse ist die globale Geräteerkennung nicht mehr zwingend; wer den Verkehr strikt auf den eigenen Server begrenzen will, kann in den Einstellungen zusätzlich die Relay-Nutzung abschalten. Die globale Erkennung als Rückfallweg eingeschaltet zu lassen, schadet dagegen nicht.

## 7. Ordner anlegen und teilen

Auf **einem** Rechner (dem mit dem vorhandenen Inhalt) beginnen — nicht auf der leeren Synology, sonst wird der leere Stand verteilt.

1. Auf Rechner A: **Add Folder**
   - „Folder Label": sprechender Name
   - „Folder Path": der abzugleichende Ordner
   - „Folder ID": eine feste Kennung — **muss auf allen Geräten identisch sein**. Syncthing schlägt eine zufällige vor; die kann man übernehmen, muss sie dann aber auf den anderen Geräten exakt so eintragen.
2. Reiter **Sharing**: Synology anhaken.
3. Reiter **Ignore Patterns**: **jetzt schon** die Ausschlüsse eintragen (Abschnitt 8) — bevor der erste Abgleich läuft.
4. Speichern.
5. Auf der Synology erscheint die Rückfrage, ob der angebotene Ordner angenommen werden soll → annehmen und als Pfad einen Unterordner des in Abschnitt 2 angelegten Ordners angeben, z. B. `/volume1/syncthing-data/<name>`.
6. Nach dem ersten vollständigen Abgleich auf Rechner B denselben Ordner anlegen — mit **derselben Folder-ID** — und mit der Synology teilen.

**Ordnertyp:** Alle drei Geräte müssen auf **„Send & Receive"** stehen (Vorgabe). „Receive Only" auf der Synology wäre falsch: Der Knoten muss die Änderungen von A ja auch an B weitergeben können.

## 8. Ausschlüsse: `.stignore`

Ausgeschlossen wird über die Datei `.stignore` im Wurzelverzeichnis des abgeglichenen Ordners (oder gleichwertig über das Feld „Ignore Patterns" in der Oberfläche).

**Drei Eigenheiten, die man kennen muss** ([Ignore-Doku](https://docs.syncthing.net/users/ignoring.html)):

1. **Muster greifen standardmäßig auf allen Ebenen.** `foo` trifft `foo`, `unterordner/foo` und jedes Verzeichnis namens `foo`. Ein führender Schrägstrich beschränkt auf die Wurzel: `/foo` trifft nur `foo`.
2. **Ein Verzeichnismuster mit abschließendem Schrägstrich trifft den *Inhalt*, nicht das Verzeichnis selbst.** `verzeichnis/` schließt den Inhalt aus, `verzeichnis` das Verzeichnis mitsamt Inhalt.
3. **Das erste passende Muster entscheidet.** Reihenfolge ist also bedeutsam, sobald Ausnahmen (`!`) im Spiel sind.

Weitere Zeichen: `*` überspringt keine Verzeichnistrenner, `**` schon; `?` steht für ein Zeichen außer dem Trenner; Kommentare beginnen mit `//`. Die Präfixe `(?i)` (Groß-/Kleinschreibung egal) und `(?d)` (Löschen des Verzeichnisses trotz ignorierter Inhalte erlauben) lassen sich kombinieren, aber nur getrennt geschrieben — `(?d)(?i)`, nicht `(?di)`.

Punktdateien werden **nicht** gesondert behandelt, sondern ganz normal abgeglichen. Nur Syncthings eigene Objekte (`.stfolder`, `.stignore`, `.stversions`) sind davon ausgenommen.

Beispiel für ein Konfigurationsverzeichnis mit Zugangsdaten:

```
// Zugangsdaten niemals abgleichen - bewusst OHNE führenden Schraegstrich,
// damit die Datei auf jeder Ebene ausgeschlossen ist
.credentials.json

// Ganze Verzeichnisse samt Inhalt
/telemetry
/cache

// Fluechtige Dateien
*.log
*.sock

// Synology-Papierkorb, falls im Zielordner aktiviert
#recycle
```

**Ausdrücklich prüfen, ob die Muster wirklich greifen** — ein falsch formuliertes Muster sieht aus, als würde es wirken, und tut es nicht. Kontrolle schlicht dadurch, dass die betreffenden Dateien auf der Gegenseite **nicht** auftauchen.

### `.stignore` wandert nicht von selbst mit

Laut Doku wird die Datei „never synced to other devices". Die Ausschlüsse müssen also auf **jedem** Gerät eingerichtet werden — und zwar *bevor* der erste Abgleich läuft, sonst sind die Zugangsdaten bereits verteilt.

Es gibt einen dokumentierten Umweg — die Doku sagt wörtlich: „The `.stignore` file itself will never be synced to other devices, although it can `#include` files that are synchronized between devices." Die Wurzeldatei enthält dann nur

```
#include gemeinsame-ausschluesse
```

und die Datei `gemeinsame-ausschluesse` liegt im abgeglichenen Ordner und wandert als gewöhnliche Datei mit. Die eingebundenen Muster bleiben dabei relativ zur Ordnerwurzel, auch wenn die Datei in einem Unterverzeichnis liegt.

**Für Zugangsdaten ist dieser Umweg jedoch der falsche Weg** — und zwar aus einem Grund, der sich nicht durch Sorgfalt umgehen lässt: Die eingebundene Datei erreicht ein neues Gerät erst *durch* den Abgleich. Beim allerersten Abgleich existiert sie dort noch nicht, die Schutzregel greift also genau in dem Moment nicht, in dem sie gebraucht wird — und eine fehlende Include-Datei ist zudem ein Fehler, der die gesamte Ignore-Liste unwirksam machen kann.

**Daraus folgt als Regel:** Die Ausschlussregel für Zugangsdaten gehört **wörtlich und lokal** in die `.stignore` **jedes** Geräts, eingetragen **bevor** der Ordner erstmals verbunden wird. `#include` eignet sich nur für unkritische, gemeinsam gepflegte Zusatzmuster.

## 9. Dateiversionierung

Anders als eine Versionsverwaltung hebt Syncthing standardmäßig **nichts** auf: Eine überschriebene oder gelöschte Datei ist weg — und die Löschung wird auf alle Geräte weitergereicht. Die FAQ weist ausdrücklich darauf hin, dass versehentliche Massenlöschung sich so überall auswirkt.

Gegenmittel ist die Dateiversionierung, einzustellen **je Ordner und je Gerät** unter **Folder → Edit → File Versioning** — sie propagiert ausdrücklich *nicht*, muss also überall einzeln gesetzt werden:

- **Trash Can**: gelöschte/ersetzte Dateien wandern nach `.stversions`, Aufbewahrung nach Tagen begrenzbar. Einfachste sinnvolle Wahl.
- **Staggered**: hebt Versionen mit über die Zeit abnehmender Dichte auf (letzte Stunde alle 30 Sekunden, letzter Tag stündlich, letzte 30 Tage täglich, danach wöchentlich) und löscht sie automatisch nach einer einstellbaren Höchstdauer — „The maximum time to keep a version in days", `0` bedeutet unbegrenzt ([Versionierungs-Doku](https://docs.syncthing.net/users/versioning.html)).

**Einheiten-Falle:** In der Weboberfläche wird die Höchstdauer in **Tagen** eingetragen, in der Konfigurationsdatei heißt derselbe Wert `maxAge` und zählt **Sekunden**. Wer die Konfigurationsdatei direkt bearbeitet, verrechnet sich hier leicht um den Faktor 86400.

**Entscheidende Einschränkung, die man kennen muss:** Die Versionierung greift laut Doku ausschließlich für Änderungen, die **von anderen Geräten eintreffen** — wörtlich: *„Versioning applies to changes received from other devices. […] If Alice changes a file locally on her own computer Syncthing will not and can not archive the old version."*

Wer also auf Rechner A versehentlich eine Datei löscht, findet auf Rechner A **keine** archivierte Fassung. Wohl aber auf der Synology und auf Rechner B, denn dort trifft die Löschung als Fremdänderung ein und wird vorher archiviert. Das Sicherheitsnetz liegt damit nicht dort, wo der Fehler passiert, sondern auf den anderen Geräten — was genügt, solange man weiß, wo man suchen muss.

**Empfehlung:** Auf der Synology „Staggered" mit einer Höchstdauer nach Bedarf (z. B. 30 Tage) — sie ist das Gerät, das Fremdänderungen von beiden Rechnern empfängt und damit der wirksamste Ort für den Rückgriff. Auf den Arbeitsrechnern genügt „Trash Can" mit wenigen Tagen.

## 10. Client einrichten — Linux

Die Paketquellen der Distribution hinken oft weit hinterher (Ubuntu 24.04 liefert z. B. noch die 1.x-Reihe, aktuell ist 2.x). Protokollseitig sind beide Reihen zwar verträglich, für Fehlerbehebungen und gleiches Verhalten auf allen Geräten ist die offizielle Paketquelle aber die bessere Wahl. Die aktuell vom Projekt empfohlene Vorgehensweise hier: [https://apt.syncthing.net/](https://apt.syncthing.net/).

```bash
sudo mkdir -p /etc/apt/keyrings
sudo curl -L -o /etc/apt/keyrings/syncthing-archive-keyring.gpg https://syncthing.net/release-key.gpg
echo "deb [signed-by=/etc/apt/keyrings/syncthing-archive-keyring.gpg] https://apt.syncthing.net/ syncthing stable-v2" | sudo tee /etc/apt/sources.list.d/syncthing.list
sudo apt-get update
sudo apt-get install syncthing
```

Als Benutzerdienst starten (läuft nur bei angemeldetem Benutzer — für einen Arbeitsplatzrechner richtig):

```bash
systemctl --user enable syncthing.service
systemctl --user start syncthing.service
```

Oberfläche danach unter `http://127.0.0.1:8384`. Sie lauscht standardmäßig nur auf der Rückschleife und ist damit von außen nicht erreichbar — hier ist kein Passwort zwingend, schadet aber nicht.

Soll der Abgleich auch ohne angemeldeten Benutzer laufen, stattdessen den Systemdienst verwenden:

```bash
sudo systemctl enable --now syncthing@<benutzername>.service
```

## 11. Client einrichten — Windows

Syncthing selbst ist eine einzelne ausführbare Datei ohne Installationsprogramm. Für den Dauerbetrieb bieten sich an:

- **Aufgabenplanung**: neue Aufgabe, Auslöser „Bei der Anmeldung", Aktion `syncthing.exe` mit den Argumenten `--no-console --no-browser`.
- **Autostart-Ordner**: Verknüpfung auf `syncthing.exe --no-console --no-browser` in `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup` ablegen.

Für einen Betrieb ohne angemeldeten Benutzer gibt es die Möglichkeit, Syncthing per NSSM als Dienst einzurichten — dann ist ein Passwort für die Oberfläche zwingend, weil sie sonst unter einem Systemkonto ungeschützt läuft.

Die Ordner-Einrichtung erfolgt danach identisch zu Abschnitt 7, mit **derselben Folder-ID** und den **gleichen Ausschlüssen** aus Abschnitt 8.

## 12. Laufender Betrieb: Konflikte

Syncthing führt Dateien **nicht** inhaltlich zusammen. Wurde dieselbe Datei auf zwei Geräten geändert und unterscheidet sich der Inhalt, bleibt eine Fassung unter dem ursprünglichen Namen bestehen, die andere wird umbenannt nach dem Muster

```
<name>.sync-conflict-<datum>-<zeit>-<geraet>.<endung>
```

Es gewinnt die Fassung mit dem **jüngeren Änderungszeitpunkt**; bei Gleichstand entscheidet die größere Geräte-ID. Die Konfliktkopie wird anschließend wie eine gewöhnliche Datei behandelt und **auf alle Geräte verteilt** — sie ist also überall sichtbar und lässt sich überall auflösen.

Damit ist der Konflikt zuverlässig maschinell auffindbar: Es genügt, im abgeglichenen Ordner nach `*.sync-conflict-*` zu suchen. Beide Fassungen liegen als gewöhnliche Dateien nebeneinander und können mit einem Werkzeug freier Wahl verglichen und zusammengeführt werden. Nach dem Auflösen die Konfliktkopie löschen — die Löschung wandert mit.

**Für Skripte wichtig:** Das genaue Format von Datum, Uhrzeit und Gerätekennung im Dateinamen ist in der Doku *nicht* festgelegt. Ein Skript sollte deshalb auf dem dokumentierten, festen Textbestandteil aufsetzen — also auf dem Muster `*.sync-conflict-*` — und nicht auf einem strengen regulären Ausdruck mit fester Stellenzahl.

Die Anzahl aufbewahrter Konfliktkopien je Datei steuert `maxConflicts` (Vorgabe `10`, `-1` unbegrenzt, `0` schaltet Konfliktkopien ganz ab). **`0` sollte man hier nicht setzen** — dann verschwindet die unterlegene Fassung ersatzlos.

**Ausnahme:** In Ordnern vom Typ „Receive Only" gewinnt immer die Cluster-Fassung, und die Konfliktkopie wird *nicht* verteilt. Ein weiterer Grund, überall bei „Send & Receive" zu bleiben.

**Änderungserkennung:** Syncthing beobachtet das Dateisystem und sammelt Änderungen standardmäßig 10 Sekunden lang, bevor ein Suchlauf angestoßen wird (`fsWatcherDelayS`); Löschungen werden zusätzlich um eine Minute verzögert. Bei einer Datei, die sich *fortlaufend* ändert, erzwingt `fsWatcherTimeoutS` irgendwann trotzdem einen Suchlauf. Unabhängig davon läuft stündlich ein vollständiger Suchlauf; die Doku rät ausdrücklich, diesen aktiviert zu lassen.

**Auf der Empfangsseite** schreibt Syncthing nie direkt in die Zieldatei, sondern in eine temporäre Kopie, die anschließend über die alte Fassung geschoben wird. Ein Leser auf der Gegenseite sieht daher immer eine vollständige Datei, nie einen halb geschriebenen Zustand.

## 13. Test der Einrichtung

1. Auf Rechner A eine Datei im abgeglichenen Ordner anlegen. In der Oberfläche der Synology muss sie binnen weniger Sekunden auftauchen.
2. Rechner A ausschalten. Rechner B starten — die Datei muss dort ankommen, **ohne** dass A läuft. Das ist der eigentliche Nachweis, dass der Vermittlungsknoten seine Aufgabe erfüllt.
3. Auf Rechner B die Datei ändern, auf Rechner A (wieder eingeschaltet) prüfen, ob die Änderung ankommt.
4. **Konflikttest:** Beide Rechner vom Netz trennen, auf beiden dieselbe Datei unterschiedlich ändern, beide wieder verbinden. Erwartet: Auf beiden Geräten liegt anschließend die Datei plus eine `*.sync-conflict-*`-Kopie mit der jeweils anderen Fassung.
5. **Ausschlusstest:** Eine Datei anlegen, die einem Ausschlussmuster entspricht, und prüfen, dass sie auf den anderen Geräten **nicht** erscheint. Bei Zugangsdaten ist dieser Test nicht optional.

## 14. Aktualisierung

Hier verhält sich das Paket anders als eine Installation von Hand: Es nutzt **Syncthings eingebauten Selbstaktualisierer**. SynoCommunity baut das Paket deshalb nach eigener Aussage nur selten neu — die Aktualisierung übernimmt Syncthing selbst.

Bequem, aber es bedeutet auch: Du bestimmst den Zeitpunkt nicht. Wer das nicht möchte, kann die Selbstaktualisierung in den Einstellungen abschalten und Aktualisierungen dem Paketzentrum überlassen.

**Ausnahme mit Schadenspotenzial:** Auf sehr alten ARMv5-Geräten (DS213air, DS213 und ähnliche) ist die Selbstaktualisierung abgeschaltet, und ihre manuelle Benutzung **zerstört die Installation**. Für aktuelle Geräte ohne Belang.

Die stabile Reihe erscheint monatlich, jeweils am ersten Dienstag.

## 15. Backup

Der Abgleich ist **kein Backup** — er verteilt Löschungen zuverlässig auf alle Geräte. Zwei Dinge gehören deshalb in die Sicherung:

- Der **Datenordner** aus Abschnitt 2 (z. B. `/volume1/syncthing-data`) — er enthält die eigentlichen Inhalte samt der `.stversions`-Ordner aus der Versionierung.
- Die **Konfiguration** unter `/volume1/@appdata/syncthing` — sie enthält Geräte-ID, Schlüssel und alle Einstellungen. Geht sie verloren, ist die Instanz für die Gegenstellen eine fremde und muss neu gekoppelt werden.

**Achtung:** `@appdata` ist ein verstecktes Systemverzeichnis und in Standard-Sicherungskonfigurationen nicht immer enthalten. Hier lohnt eine gezielte Kontrolle — das ist ein Unterschied zu einer Container-Installation, deren Daten im gewöhnlichen Docker-Ordner liegen.

## 16. Fallstricke und offene Punkte

- **`.stignore` wandert nicht mit.** Auf jedem neuen Gerät einzeln einrichten, *bevor* der erste Abgleich läuft. Der `#include`-Umweg ist dokumentiert, für Zugangsdaten aber untauglich (Abschnitt 8).
- **Ausschlussmuster still wirkungslos.** Ein falsch geschriebenes Muster fällt nicht auf. Nach jeder Änderung den Test aus Abschnitt 13.5 fahren.
- **Rechte für `sc-syncthing`.** Der häufigste Stolperstein beim Paketweg; erkennbar an `permission denied` rund um `.stfolder` und `.stignore` (Abschnitt 2).
- **DSM-Firewall.** Beim Paketweg leicht zu übersehen, weil es keine Portabbildung gibt, die es mit erledigt (Abschnitt 4).
- **Versionierung schützt nicht am Ort des Fehlers.** Lokale Änderungen werden nicht archiviert, nur eintreffende (Abschnitt 9).
- **Dateien, die während des Abgleichs beschrieben werden.** Es gibt **keinen** dokumentierten Mechanismus, der die Übertragung zurückstellt, bis eine Datei zur Ruhe gekommen ist: `fsWatcherDelayS` verzögert nur den Suchlauf, und `fsWatcherTimeoutS` erzwingt bei dauernd wachsenden Dateien sogar irgendwann einen. Übertragen wird der Zwischenstand zum Zeitpunkt des Suchlaufs. Die Empfangsseite sieht dank des Umbenennens zwar stets eine *technisch* vollständige Datei — deren letzte Zeile kann bei einer gerade wachsenden Protokolldatei aber *inhaltlich* abgeschnitten sein. Für Ordner, in die eine laufende Anwendung fortwährend schreibt, ist das vor dem produktiven Einsatz zu bewerten.
- **Bekannter Fehler bei entfernten Geräten:** Nach dem Entfernen eines Geräts können verwaiste Einträge in den Versionsvektoren zurückbleiben und massenhaft Falschkonflikte auslösen ([Issue #10590](https://github.com/syncthing/syncthing/issues/10590)). Relevant erst, wenn ein Gerät je aus dem Verbund genommen wird.
- **Kein Zeitpunktzustand.** Anders als eine Versionsverwaltung kennt Syncthing keinen konsistenten Gesamtstand über mehrere Dateien hinweg; jede Datei wird für sich abgeglichen.
