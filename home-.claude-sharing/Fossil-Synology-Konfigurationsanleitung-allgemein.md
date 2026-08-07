# Fossil SCM auf Synology (Docker, `tangentsoft/fossil`)

Single-User-Setup. Voraussetzung: Ein Reverse-Proxy auf der Synology (Systemsteuerung → Anmeldeportal → Erweitert → Reverse Proxy) leitet eine Subdomain Deiner Wahl (im Folgenden `git.deine-domain.tld`) auf einen internen Port (im Folgenden `8098`) weiter.

## 1. Datenordner anlegen

Direkt neben den anderen Docker-Volumes:

```bash
mkdir -p /volume1/docker/fossil
```

**Wichtig – Windows-ACL prüfen:** Synology-Freigabeordner haben oft zusätzlich zu den Unix-Rechten eine Windows-ACL (erkennbar am `+` hinter den Rechten bei `ls -ld`). Falls dort z. B. `everyone` nur Lese-/Ausführungsrechte hat, kann der Container keine Datei anlegen (Fehler `SQLITE_CANTOPEN`), obwohl `chmod 777` gesetzt ist. Prüfen mit:

```bash
synoacltool -get /volume1/docker/fossil
```

Falls eine ACL vorhanden ist und Schreibrechte fehlen, ACL entfernen und Unix-Rechte neu setzen (reiner Docker-Datenordner, kein SMB-Zugriff nötig):

```bash
sudo synoacltool -del /volume1/docker/fossil
sudo chmod 777 /volume1/docker/fossil
```

(`-del` setzt die Unix-Rechte auf `000` zurück – der `chmod`-Schritt danach ist zwingend.)

## 2. `docker-compose.yml`

In Container Manager → Projekt → "Vorhandene docker-compose.yml verwenden", Pfad `/volume1/docker/fossil`, Inhalt:

```yaml
services:
  fossil:
    image: tangentsoft/fossil:latest
    container_name: fossil
    command: --repolist /museum --port 8080 --https
    ports:
      - "8098:8080"
    volumes:
      - /volume1/docker/fossil:/museum
    restart: unless-stopped
```

Hinweise zu den Optionen:

- `--repolist /museum`: zeigt bei mehreren `.fossil`-Dateien im Ordner eine Übersicht, bei genau einer direkt deren Inhalt.
- Das Image hat bereits `ENTRYPOINT ["fossil", "server"]` fest eingebaut – `command:` enthält deshalb **nur** die Argumente, nicht `fossil server` selbst. Prüfbar mit `docker inspect tangentsoft/fossil:latest --format '{{.Config.Entrypoint}} {{.Config.Cmd}}'`.
- `--https`: sagt Fossil, dass Anfragen über einen TLS-terminierenden Reverse Proxy ankommen. Ohne diese Option erzeugt Fossil interne Links mit `http://`, was zu 404-Fehlern führt (der Browser landet dann auf Port 80 statt 443).

Port `8098` und Pfad `/volume1/docker/fossil` bei Bedarf an die eigene Umgebung anpassen (müssen mit der Reverse-Proxy-Regel bzw. dem gewünschten Speicherort übereinstimmen).

Beim Anlegen des Projekts "Automatisch starten" aktivieren.

**Falls der YAML-Editor im Container Manager eine Änderung nicht mehr annimmt** (zeigt weiterhin den alten Inhalt, obwohl gespeichert): Datei direkt im Projektordner bearbeiten und den Container über die Kommandozeile neu erstellen – dabei bleibt er als dasselbe Projekt im Manager sichtbar, da Compose den Projektnamen aus dem Ordnernamen ableitet:

```bash
sudo nano /volume1/docker/fossil/docker-compose.yml   # Inhalt korrigieren
cd /volume1/docker/fossil
sudo docker compose down
sudo docker compose up -d
```

## 3. Zertifikat – Subdomain im Zertifikat ergänzen

Falls die Reverse-Proxy-Subdomain (`git.deine-domain.tld`) noch nicht Teil eines gültigen Zertifikats ist: Ein bestehendes Let's-Encrypt-Zertifikat deckt neue Subdomains nicht automatisch ab, auch eine "Erneuerung" behält nur die bisherige Domainliste bei. Die neue Subdomain muss einmalig explizit als zusätzlicher "Alternativer Name" ergänzt werden (oder alternativ ein eigenes, neues Zertifikat nur für diese eine Subdomain angelegt werden):

**Systemsteuerung → Sicherheit → Zertifikat → Hinzufügen → "Vorhandenes Zertifikat ersetzen"** (bestehendes Zertifikat auswählen) → **"Zertifikat von Let's Encrypt abrufen"**. Im Feld "Betreff Alternativer Name" alle gewünschten Domains mit Semikolon **ohne Leerzeichen** eintragen, z. B.:

```
www.deine-domain.tld;git.deine-domain.tld
```

(Leerzeichen nach dem Semikolon führt zu "Falscher Wert" – ebenso ein versehentliches `:` statt `;` am Ende der Liste.) Das Ersetzen übernimmt automatisch alle bisherigen Dienst-Zuordnungen – kein manuelles Umhängen nötig. Der reine "Bearbeiten"-Dialog eines bestehenden Zertifikats erlaubt dagegen **nicht** das Ändern der Domainliste, nur Beschreibung und Dienst-Zuordnung.

## 4. Test

Nach dem Start:

```bash
sudo docker ps -a | grep fossil
sudo docker logs fossil
```

Erwartet: Status `Up`, keine `SQLITE_CANTOPEN`-Fehler im Log. Dann:

```bash
curl -I https://git.deine-domain.tld/
```

Ein HTTP-Status zeigt: Container läuft, Zertifikat passt, Proxy erreichbar.

## 5. Repository anlegen

Über den Container selbst, damit dauerhaft nur eine Fossil-Version im Spiel ist:

```bash
sudo docker exec -it fossil fossil init /museum/<name>.fossil --admin-user <dein-benutzername>
```

(Der Parameter heißt `--admin-user`, nicht `--user`.) Fossil gibt danach ein zufälliges Initial-Passwort aus – notieren oder direkt neu setzen:

```bash
sudo docker exec -it fossil fossil user password <dein-benutzername> -R /museum/<name>.fossil
```

(`-R`/`--repository` ist zwingend als Flag, nicht als reines Positionsargument.)

**Wichtig – jedes Repository hat eine eigene, unabhängige Benutzerverwaltung.** Derselbe Login-Name in zwei verschiedenen `.fossil`-Dateien sind zwei komplett getrennte Konten mit eigenem Passwort.

**Aufruf im Browser/Client:** Die URL verwendet den Dateinamen **ohne** `.fossil`-Endung, z. B. `https://git.deine-domain.tld/<name>` (Aufruf *mit* `.fossil` liefert 404). Das gilt auch für Clone/Push/Pull-URLs (siehe Abschnitt 7).

## 6. Zugriff absichern (pro Repository einmalig nötig!)

Standardmäßig dürfen die Pseudo-Benutzer `anonymous` (Login per Captcha) und `nobody` (ganz ohne Login) lesend zugreifen. Für ein privates Setup abschalten:

1. Auf `https://git.deine-domain.tld/<name>` mit dem Admin-Account einloggen.
2. **Admin → Setup → Access** → **„Require Login To View"** aktivieren.
3. **Admin → Users** → `anonymous` öffnen → Feld „Capabilities" leeren → speichern.
4. **Admin → Users** → `nobody` öffnen → Feld „Capabilities" leeren → speichern.

Erst „Require Login To View" allein reicht **nicht** – ohne Schritt 3+4 kommt man weiterhin per Captcha als `anonymous` rein, da dieser Pseudo-Nutzer von Haus aus noch Leserechte hat.

Test im privaten/Inkognito-Fenster: ohne Login sollte jetzt nichts mehr sichtbar sein; mit echtem Login weiterhin alles wie gewohnt.

**Diese vier Schritte gelten nur für das jeweilige Repository und müssen bei jedem neuen `.fossil`-Projekt wiederholt werden.**

## 7. Client-Nutzung

```bash
fossil clone https://<dein-benutzername>@git.deine-domain.tld/<name> <name>.fossil
fossil open <name>.fossil
```

(URL ohne `.fossil`-Endung, siehe Abschnitt 5.) Passwort wird abgefragt, mit „remember password" bestätigen, damit spätere `commit`/`sync`-Aufrufe die Zugangsdaten nicht erneut verlangen.

Autosync ist Standard (`fossil settings autosync` → `on`/`1`) – jeder `fossil commit` synchronisiert automatisch (Push zum Server, kurzes Pull). Prüfen lässt sich das direkt an der Ausgabe von `fossil commit`: Es folgt eine Zeile `Sync with https://...`.

## 8. Anleitung/Notizen in Fossil ablegen

Für Betriebs-/Nutzungsnotizen (z. B. diese Datei) eigenes, von echten Projekten getrenntes Repository anlegen, z. B. `hinweise.fossil` (Schritte 5+6 entsprechend anwenden). Datei sowohl als versionierte Datei als auch als Wiki-Seite ablegen – beides rein über HTTPS/Client, ohne `docker exec`:

```bash
cd <checkout-verzeichnis>
cp /pfad/zur/Anleitung.md .
fossil add Anleitung.md
fossil commit -m "Anleitung hinzugefügt"
```

Danach abrufbar unter `https://git.deine-domain.tld/hinweise/doc/tip/Anleitung.md` (Fossil rendert `.md`-Dateien im Baum automatisch).

Zusätzlich als Wiki-Seite (schneller Zugriff ohne Dateipfad im Kopf):

```bash
fossil wiki create "Fossil-Setup" Anleitung.md --mimetype text/x-markdown
fossil sync
```

Abrufbar unter `https://git.deine-domain.tld/hinweise/wiki`.

## 9. Ein Konfigurationsverzeichnis zwischen mehreren Rechnern synchronisieren

Beispiel im Folgenden anhand eines beliebigen Konfigurationsordners (`~/.beispiel-konfig`) – gilt sinngemäß für jeden Ordner, den man rechnerübergreifend abgleichen möchte.

**Sicherheitshinweis:** Falls dabei Zugangsdaten/Credentials enthalten sind – Fossil löscht (wie Git) niemals automatisch Historie. Einmal committete Credentials bleiben dauerhaft abrufbar, auch nach späterer Rotation. Vor dem ersten echten Commit unbedingt Abschnitt 6 (Zugriff absichern) für dieses Repository durchführen.

**Museum-Konvention:** Die `.fossil`-Datenbankdatei liegt bewusst **außerhalb** des zu synchronisierenden Ordners (z. B. in `~/fossil-repos/`), nur der eigentliche Checkout liegt **im** Zielordner selbst. Es entsteht kein `~/fossil-repos/.beispiel-konfig` – die echten Dateien bleiben exakt dort, wo sie sind.

**Repository einmalig anlegen** (Schritte 5+6 anwenden, z. B. Name `konfig-sync`).

**Ersteinrichtung auf dem Rechner, wo der Zielordner bereits Inhalt hat:**

```bash
mkdir -p ~/fossil-repos
cd ~/fossil-repos
fossil clone https://<dein-benutzername>@git.deine-domain.tld/konfig-sync konfig-sync.fossil

cd ~/.beispiel-konfig
fossil open ~/fossil-repos/konfig-sync.fossil -k
```

`-k` (`--keep`) sorgt dafür, dass bestehende Dateien nicht angetastet werden (bei leerem Repository ohnehin unkritisch, aber die sicherere Wahl). Ohne `-k`/`-f` verweigert `fossil open` die Arbeit in einem nicht-leeren Verzeichnis.

Nicht gewünschte Inhalte dauerhaft ausschließen – am besten **versioniert**, damit die Regel automatisch auf jeden weiteren Rechner mitwandert:

```bash
mkdir -p .fossil-settings
echo "*.log:*.sock:*/cache/*" > .fossil-settings/ignore-glob
fossil add .fossil-settings/ignore-glob
```

(Eine reine `fossil settings ignore-glob "..."`-Angabe ohne `.fossil-settings/`-Datei gilt dagegen nur lokal auf diesem einen Rechner und muss sonst überall einzeln wiederholt werden. Muster nach Bedarf an den tatsächlichen Ordnerinhalt anpassen.)

```bash
fossil add .
fossil commit -m "Initial sync"
```

**Auf jedem weiteren Rechner:**

```bash
mkdir -p ~/fossil-repos
cd ~/fossil-repos
fossil clone https://<dein-benutzername>@git.deine-domain.tld/konfig-sync konfig-sync.fossil

mkdir -p ~/.beispiel-konfig
cd ~/.beispiel-konfig
fossil open ~/fossil-repos/konfig-sync.fossil -k
```

**Laufender Gebrauch:** einfach im Zielordner regelmäßig `fossil commit -m "..."` ausführen – Autosync übernimmt Push/Pull automatisch.

**Automatisches Committen per Cronjob** (auf jedem beteiligten Rechner einrichten), da Fossil selbst nicht automatisch committet, nur automatisch synct:

`~/bin/fossil-autocommit.sh`:

```bash
#!/bin/bash
cd ~/.beispiel-konfig || exit 1
fossil add . >/dev/null 2>&1
if [ -n "$(fossil changes)" ]; then
    fossil commit -m "Auto-sync $(date '+%Y-%m-%d %H:%M')" --no-warnings
fi
```

```bash
chmod +x ~/bin/fossil-autocommit.sh
crontab -e
```

Zeile ergänzen (z. B. alle 10 Minuten):

```
*/10 * * * * $HOME/bin/fossil-autocommit.sh >> $HOME/fossil-sync.log 2>&1
```

`--no-warnings` ist notwendig, sonst hängt der Cronjob bei interaktiven Rückfragen (z. B. "contains long lines"). Bei gleichzeitigen Änderungen auf zwei Rechnern zwischen zwei Cron-Durchläufen kann ein Merge-Konflikt entstehen – zeigt sich beim nächsten `fossil update`/`commit`, Auflösung dann per `fossil merge`.

**Test, ob Auto-Commit/Sync tatsächlich funktioniert:**

1. Auf Rechner A: `echo "test" > ~/.beispiel-konfig/test-sync.md; fossil add test-sync.md; fossil commit -m "Test"` – Ausgabe sollte `Sync with https://...` enthalten.
2. Auf Rechner B: `cd ~/.beispiel-konfig && fossil update` – Datei sollte ankommen.
3. Kontrolle im Browser: `https://git.deine-domain.tld/konfig-sync/timeline` zeigt Check-ins von beiden Rechnern in einer gemeinsamen Chronik.

## 10. Backup

Idealerweise über eine ohnehin bestehende Backup-Konfiguration für den Docker-Datenordner (`/volume1/docker/...`) abdecken lassen – dann ist kein separater Snapshot-Job für Fossil nötig.

## 11. Offene Punkte / optionale Erweiterungen

- **HTTP → HTTPS Redirect:** Ein Aufruf von `http://git.deine-domain.tld` (Port 80) landet standardmäßig auf dem DSM-eigenen Standarddienst statt bei Fossil. Für den reinen Eigengebrauch meist unkritisch, da `https://` ohnehin per Lesezeichen/Autovervollständigung genutzt wird – bei Bedarf über die Reverse-Proxy-Regel (HSTS-Option, sofern die DSM-Version das anbietet) nachschärfen.
- **Watchtower** o. ä.: Update-Mechanismus für das Container-Image bei Bedarf ergänzen.
