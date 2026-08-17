# Testlauf — Protokoll des warmen Tests

Das laufende Protokoll zu Fahrplanpunkt 21: was angelegt wurde, was beobachtet wurde, was noch fehlt. Es steht hier und nicht im Fahrplan, weil der eine reine Aufgabenliste ist, und nicht in der Doku, weil eine laufende Beobachtung noch keine Festlegung ist.

**Diese Datei ist befristet.** Sie endet mit Punkt 21. Was von ihr bleibt, wandert dann dorthin, wo es normativ hingehört: der bestandene Lauf nach `implementation_doku.md` 3.1.7 bzw. 3.2 — dort steht schon der FreeCAD-Lauf —, gekippte Annahmen nach 1.7, geänderte Umgebungstatsachen nach Kapitel 4. Danach wird sie gelöscht.

## Das Testprojekt

| | |
| --- | --- |
| Titel | „Chats-Export, Test 1" |
| Kurzbeschreibung | „Das ist ein Testprojekt, angelegt zum Fahrplanpunkt 21.2" |
| Angelegt | 17. August 2026, gegen 15:20 Uhr |
| Angelegt mit | Claude Desktop, als gewöhnliches Projekt (nicht als Claude-Code-Projekt) |

Das Anlegedatum ist der **Sollwert** für 21.4: Der Sondierungsexport muss für dieses Projekt genau den 17. August 2026 als `created_at` führen. Die Uhrzeit ist dabei nur die Notiz, dass es kein Tageswechsel-Grenzfall war.

**Stand am 17. August 2026:** angelegt, sonst leer — keine Projektanweisung, kein Projektwissen, keine geplanten Aufgaben, kein Chat.

**Bestätigt:** Das Projekt ist in claude.ai im Browser sichtbar. Ein in Claude Desktop angelegtes gewöhnliches Projekt liegt also im Konto, nicht nur lokal.

**Offen und vor dem Füllen zu klären:** ob es für `recent_chats` und `read_conversation` auch **erreichbar** ist. Sichtbarkeit und Erreichbarkeit sind zweierlei; entschieden wird es durch die Chatliste (Doku 1.6 zur Bereichsbindung).

**Beobachtet, bisher nirgends dokumentiert:** Beim Anlegen eines Projekts gibt es **keine** Wahl zwischen Cowork und Nicht-Cowork. Die Unterscheidung fällt erst beim Starten des ersten Chats — dort stehen „Chat" und „Cowork" zur Wahl. Cowork gehört also nicht zum Projekt, sondern zum einzelnen Chat. Für diesen Testlauf werden **alle** Chats als gewöhnlicher Chat angelegt: Cowork-Chats sind über beide Wege unerreichbar, ihre IDs sind keine UUIDs und werden am Format abgewiesen (Doku 1.6, 4.3).

**Daraus eine offene Frage**, die dieser Testlauf beantworten könnte: Erscheint ein Cowork-Chat, der in einem gewöhnlichen claude.ai-Projekt geführt wird, trotzdem in dessen `recent_chats`-Liste? Wenn ja, legte `list` einen Protokolleintrag an, der nie zu holen ist — ein Chat, der dauerhaft als fehlend geführt wird. Wenn nein, fehlt er lautlos. Beides wäre wissenswert, keines ist bisher belegt.

## Das Testprojekt im Pro-Konto

| | |
| --- | --- |
| Titel | „Chats-Export aus Pro, Test 1" |
| „Was Sie erreichen wollen" | „Das ist ein Testprojekt im Pro-Konto." |
| Angelegt | 17. August 2026 |
| Konto | Pro — hier liegt die echte Quellumgebung, und nur hier gibt es den Export |

Dieses Projekt trägt den mehrstufigen Test. Der Sollwert für 21.4 ist der **17. August 2026**; die Uhrzeit spielt keine Rolle, weil der Export nur ein Datum führt.

Die Wahl zwischen „Chat" und „Cowork" beim Anlegen eines Chats erscheint auch hier — sie ist also keine Team-Eigenheit, sondern die Normalform auf allen bezahlten Plänen (belegt, [13455879](https://support.claude.com/en/articles/13455879-use-claude-cowork-on-team-and-enterprise-plans)). **Jeder Chat dieses Testprojekts wird als „Chat" angelegt**, nie als Cowork.

## Profil-Checkliste (Doku 4.1)

Alle Merkmale sind am 17. August 2026 **erzeugt worden**. Erzeugt heißt hier: Die Handlung ist getan — ob daraus in den Daten wirklich das Merkmal geworden ist, weist erst der Export in 21.7 nach. Bei zwei Merkmalen ist der Ausgang ausdrücklich offen:

| Merkmal | Chat | Stand |
| --- | --- | --- |
| Gabelung | 1 | erzeugt |
| Sendewiederholung | 1 | erzeugt |
| Anhang mit Inhalt | 2 | erzeugt |
| reiner Namensverweis | 2 | **offen im Ausgang** — ob ein Bild als `attachments` mit Inhalt oder als `files` ohne ankommt, ist unbekannt; genau das soll der Lauf klären |
| Denkschritte | 3 | erzeugt, dazu bewusst ein kurzer Block für die 200-Zeichen-Schwelle (3.1.3) |
| Erzeugnis | 4 | erzeugt, mit anschließender Änderung für die `delta`-Kennzeichnung |
| Hülle | 5 | **offen im Ausgang** — vor dem Export gelöscht; ob der Chat als Hülle erscheint oder gar nicht, entscheidet den Widerspruch aus 1.6 gegen [13346720](https://support.claude.com/en/articles/13346720-export-your-organization-s-data) |
| langer Chat | 6 | erzeugt |
| wachsender Chat | 6 | derselbe Chat; fortgesetzt wird er in 21.9 nach einem Tageswechsel |

**Beobachtung zur Gabelung:** Nach dem Bearbeiten der Frage kam eine neue Antwort, und die bisherige verschwand **im Web-Frontend**. Genau darum geht es bei Regel 2 in 3.1.2: Die Oberfläche zeigt den verworfenen Zweig nicht mehr, der Export soll ihn trotzdem führen. Damit hat 21.7 eine scharfe Erwartung — `analyse` muss für Chat 1 einen Nebenzweig ausweisen. Tut es das nicht, ist entweder die Gabelung anders entstanden als gedacht, oder der Export hält den verworfenen Zweig nicht.

**Langer und wachsender Chat sind derselbe** (Chat 6). Das ist zulässig und spart einen Chat: Ein wachsender Chat, der zugleich lang ist, macht das Ersetzen beim zweiten Export sogar aussagekräftiger. Eine Bedingung gehört dazu — für den Wegegleichheits-Vergleich in 21.13 darf **nicht** dieser Chat genommen werden. Dort müssen beide Wege denselben Stand sehen; ein wachsender Chat wäre ein bewegtes Ziel, und eine Abweichung ließe sich nicht mehr von einem echten Befund unterscheiden.

**Für 21.13 vorgesehen**, und ab jetzt unangetastet: Chat 3 oder 4 als schlichter Grundfall — und **Chat 1 als Härtefall**. Er trägt Gabelung und Sendewiederholung, und beide sieht der Lese-Weg nicht: Er liefert das gerenderte Transkript. Kommen nach Abzug der erlaubten Felder trotzdem zwei identische Transkripte heraus, ist Vorgabe 2.5 an der schwierigsten Stelle bestätigt. Weichen sie ab, haben wir einen Fall gefunden, den die Vorgabe bisher nicht kennt — und das wäre kein Testfehler, sondern der wertvollste Befund des ganzen Laufs.

## 21.3/21.4 Sondierungsexport — bestanden

ZIP vom 17. August 2026, Fenster vor dem Anlegen des Testprojekts. `inspect_export.py` berichtet:

- **Konversationen: 1**, erstellt am 2026-08-15 — aus einem anderen Projekt. **Kein einziger Chat des Testprojekts** ist enthalten; das Fenster schloss sie korrekt aus.
- **44 Projektdateien**, darunter „Chats-Export aus Pro, Test 1" mit `created_at` **2026-08-17** — also mit einem Datum **außerhalb und nach** dem gewählten Fenster.

**Damit ist die Behauptung geprüft, auf der Schritt 0 aus 1.5 ruht:** Projektdateien sind vom Zeitraumfilter ausgenommen. Und zwar gegen einen bekannten Sollwert — der Nutzer hatte das Anlegedatum unabhängig notiert, das Werkzeug liest genau dieses Datum aus einem Archiv, das den Chat des Projekts gar nicht kennt. Vorher waren es 43 Projektdateien, jetzt 44; die eine mehr ist unser Testprojekt.

**Schemawache:** Konversationsschlüssel und Nachrichtenschlüssel decken sich mit 3.1.1, und `project reference: NONE` bestätigt erneut den Befund, der den ganzen Entwurf trägt. `login_history.json` ist vorhanden.

**Eine Lücke in der Vergleichsgrundlage:** Die Schemawache gibt auch die **Blockschlüssel** aus — hier `citations`, `flags`, `start_timestamp`, `stop_timestamp`, `text`, `type`. Doku 3.1.1 führt nur die Block*typen*, nicht die Block*schlüssel*; 3.3 verspricht aber den Vergleich aller drei Schlüsselmengen mit 3.1.1. Für eine der drei fehlt also die Vergleichsgrundlage. Sie lässt sich aus dem Erstlauf-ZIP (21.7) gewinnen, das alle Blocktypen enthält, und gehört dann nach 3.1.1.

## Verlust des kalten Prüfmaterials

`tests/test_results/` ist **leer** — bis auf `.gitkeep`. Verschwunden sind die drei früheren Export-ZIPs und das gesamte FreeCAD-Archiv samt seiner `protokoll.json`. Am 14. August lagen sie noch dort und wurden für die Mengenmessung in 3.1.7 benutzt. Der Inhalt ist gitignoriert, steht also auch nicht in der Historie.

Folgen: Der Fahrplan definiert **kalt** über eben diese ZIPs — die Definition trifft derzeit ins Leere, bis das Erstlauf-ZIP vorliegt. Und **Fahrplanpunkt 24**, die Gegenprobe am FreeCAD-Altbestand, braucht dessen Protokoll mit den 22 Chats; ohne das ist er nicht ausführbar.

## Beobachtungen je Schritt

### 21.2 Testprojekt anlegen und füllen

Am 17. August 2026 angelegt, Angaben oben; in claude.ai sichtbar. Füllen steht aus, zuerst die Erreichbarkeitsprobe über die Chatliste.

### 21.5 vorgezogen — die Chatliste

Erster Versuch, gestellt im **ersten** Chat des Projekts: ein **leerer** Codeblock. Die Form stimmte — Codeblock, kein Kommentar, kein Text davor oder danach —, `MAPPING_PROMPT` tut also, was er soll; leer war nur der Inhalt.

Zweiter Versuch, gestellt in einem **zweiten** Chat: genau ein Eintrag, nämlich der erste Chat, mit UUID-förmiger ID und `updated_at`. Damit ist bewiesen, was zu beweisen war — das Projekt ist für `recent_chats` erreichbar, es ist ein gewöhnliches claude.ai-Projekt, und die Rohform passt zu `parse_chat_list`.

**Offen bleibt, warum der jeweils laufende Chat fehlt.** Zwei Erklärungen passen auf beide Beobachtungen gleich gut: Entweder listet `recent_chats` den laufenden Chat grundsätzlich nicht mit, oder ein frisch angelegter Chat ist noch nicht indiziert. Der Unterschied ist nicht akademisch: Gilt das Erste, dann **fehlt jedem Listenlauf systematisch genau der Chat, aus dem er gestartet wurde** — eine dauerhafte Lücke im Archiv, die niemand meldet.

**Entschieden.** Dritter Versuch, gestellt wieder im **ersten** Chat: genau ein Eintrag, nämlich der **zweite** Chat. Aus Chat 1 kommt Chat 2, aus Chat 2 kam Chat 1 — beide inzwischen indiziert, jeder sieht den anderen, keiner sich selbst.

**Beobachtet, nirgends dokumentiert: `recent_chats` listet den laufenden Chat nicht mit.** Zwei symmetrische Beobachtungen, die Indizierungs-Erklärung ist damit widerlegt.

**Die Folge wiegt schwer.** Jeder Listenlauf übergeht genau den Chat, aus dem er gestartet wurde. Das Protokoll erfährt nie von ihm, also fehlt er im Archiv — und `diff` kann ihn nicht als fehlend melden, weil das Protokoll ihn gar nicht kennt. Es ist ein Zuwenig, das keine der eingebauten Kontrollen bemerkt: Der Waisen-Scan meldet nur ein Zuviel, und die Vollständigkeitsrechnung des Lese-Wegs gilt je Chat, nicht für die Menge der Chats.

**Betrifft beide Wege**, denn beide bauen ihr Protokoll aus derselben Liste: `list --map` im ZIP-Weg und `map` im Lese-Weg.

**Gegenmittel ohne Code, vom Nutzer vorgeschlagen und übernommen:** die Liste in einem **eigens dafür angelegten Chat** holen und diesen **danach löschen**. Dann bleibt gar nichts zurück — der fehlende Chat ist der, der nichts enthielt als den Listenabzug, und im Projekt sammeln sich keine Karteileichen. Der zuerst erwogene Weg, immer denselben Abfragechat zu verwenden, ist schlechter: Er ließe die Karteileiche liegen und würde beim nächsten Lauf selbst mitarchiviert.

**Gegenprobe am Altbestand möglich:** Das FreeCAD-Archiv führt 22 Chats. Zeigt die Chatliste des Projekts heute 23, ist einer stillschweigend nie mitgekommen — vermutlich der, aus dem damals die Liste geholt wurde. Das wäre die Bestätigung des Befunds an echten Daten und kostet eine Abfrage.

### Kontolage — Befund mit Folgen über den Test hinaus

Das Testprojekt liegt im **Team-Konto**. Dort gibt es für ein gewöhnliches Mitglied **keinen** Datenexport: *„Data exports are available to individual Claude users on Free, Pro, and Max plans"* (belegt, [9450526](https://support.claude.com/en/articles/9450526-export-your-claude-data)), und für Organisationen *„Individual members of Team and Enterprise organizations do not have a self-serve export option"* — nur der Primary Owner kann exportieren, unter *Organization settings → Data and privacy* (belegt, [13346720](https://support.claude.com/en/articles/13346720-export-your-organization-s-data)).

Der eigentliche Bedarf des Nutzers ist **Pro → Team**: Quelle ist das Pro-Konto, in dem der Export vorhanden ist. Der Hauptweg ist damit nicht blockiert. Betroffen ist allein der umgekehrte Fall — Chats, die **im** Team-Konto liegen und archiviert werden sollen.

### Cowork als möglicher Ausweg — recherchiert

- Verfügbar auf Pro, Max, Team und Enterprise, über Desktop, Web und Mobile (belegt, [13455879](https://support.claude.com/en/articles/13455879-use-claude-cowork-on-team-and-enterprise-plans)).
- **Lokale Sitzung:** *„The agent loop runs natively on the device"* — die Unterhaltung bleibt auf dem Gerät. **Pfade und Dateiformat sind nicht dokumentiert** (belegt, [14479288](https://support.claude.com/en/articles/14479288-claude-cowork-architecture-overview)).
- **Cloud-Sitzung:** läuft in Anthropics Sandbox, *„sessions and files are saved to the member's Claude account"* — und auf **Team-Plänen ist die Cloud-Sitzung standardmäßig eingeschaltet**. Der Ausweg „Cowork legt mir die Dateien lokal hin" gilt dort also nur, wenn ausdrücklich lokal gearbeitet wird.
- Cowork ist über die **Compliance-API** erfasst — die nach 4.5 nur Enterprise offensteht.

**Bewertung:** Cowork und „nur noch Claude Code" retten nichts. Beide ändern, *wo künftig gearbeitet wird*, damit die Daten von vornherein lokal liegen; für Chats, die heute schon im Team-Konto stehen, tun sie nichts. Das ist ein anderer Problemtyp als der, für den dieses Vorhaben gebaut ist. Cowork wird deshalb **beobachtet, nicht gebaut** (Kapitel 4).

### Entscheidung zur Testumgebung

Der mehrstufige Test läuft im **Pro-Konto**: Dort liegt die echte Quellumgebung des Nutzers — sein Bedarf ist Pro → Team —, und nur dort gibt es den Export. Die neun Profilmerkmale entstehen also in einem neuen Projekt dieses Kontos; im Team-Projekt ist bisher nur ein Chat, es geht nichts verloren.

Das Team-Projekt **bleibt stehen** für Fahrplanpunkt 23: die Probe, ob der Lese-Weg dort ebenso arbeitet. Für Team-Chats ist er der einzige Weg, und ob `read_conversation` in einem Team-Projekt greift, ist unbelegt.

**Nicht geprüft wird der Organisationsexport.** Dafür bräuchte es Primary-Owner-Rechte; die zu erwerben wäre kein Prüfaufwand, sondern ein Eingriff in die Organisation. Und selbst mit ihnen bliebe das Verfahren für den laufenden Betrieb untauglich: Ein wiederkehrender Abgleich, der jedes Mal den Administrator braucht, ist keiner.
