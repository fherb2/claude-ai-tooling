# Implementierungsdokumentation Chats-Export

**In Entwicklung — nicht zur Benutzung vorgesehen.** Diese Dokumentation beschreibt ein Vorhaben im Bau. Halbfertige, lückenhafte und noch nicht zusammengeführte Passagen sind in dieser Phase der Normalzustand und kein Mangel: Was hier steht, ist Arbeitsstand, nicht Zusage.

**Widersprüche zur `README.md` sind ausdrücklich erlaubt** und werden nicht nachgeführt. Sie hält bewusst einen älteren Stand samt Warnhinweis für fremde Leser und wird erst am Ende dieser Phase neu geschrieben (aus 1.1, 1.2 und 1.5). Widersprüche **innerhalb dieser Doku** und zwischen **Doku und Code** sind dagegen Defekte: Sie werden benannt und bekommen einen Fahrplanpunkt, keine Ausnahme.

**Die Phase endet**, wenn zwei Dinge vorliegen — ein mehrstufiger Test an einem eigens gebauten Testprojekt, der die tragenden Behauptungen abdeckt (aktives Weiterschreiben eines Chats zwischen zwei Läufen samt Fensterrechnung, Ersetzen, wirksamer Anweisungsblock), und ein erster vollständiger Durchlauf in ein echtes Zielprojekt. Dann fällt dieser Hinweis, und mit ihm der Warnhinweis der README.

Der Vergleich beider Wege an echten Daten war ursprünglich als dritte Bedingung gedacht und ist **keine mehr**: Er sollte Export gegen `read_conversation` halten, und dieses Werkzeug gibt es nicht mehr (1.2). Zwischen ZIP-Weg und Web-Weg ist die Wegegleichheit stattdessen baulich erfüllt und im Test Datei für Datei belegt (3.1) — an echten Daten sogar schärfer, als der geplante Vergleich es gewesen wäre: Für denselben Chat liefern Web-API und Export-ZIP dieselben Nachrichten-UUIDs.

---

Vier Teile. **Teil 1** beschreibt, was gebaut wird, wie es zusammenwirkt und wie es benutzt wird. **Teil 2** hält die Vorgaben, die quer über alle Werkzeuge gelten. **Teil 3** hält je Skript die Festlegungen, die dort umgesetzt werden, samt dem Kontext, der dafür erarbeitet wurde. **Teil 4** ist die Prüfliste gegenüber der laufenden Anthropic-Entwicklung. Teil 1 verweist für Details nach 2 und 3 und wiederholt sie nicht.

Die **Beleglage** wird durchgehend ausgewiesen; die drei Stufen und ihre Regeln sind Vorgabe 2.1.

---

# 1 Zusammenhänge

## 1.1 Ziel

Chats aus claude.ai-Projekten sollen **im Zusammenhang ihres Projekts durchsuchbar** sein — nicht fortführbar. Sie dienen dazu, früher besprochenen Kontext wiederzufinden.

Beides ist vorgesehen: der **einmalige Umzug** und das **wiederholte Nachreichen**. Ausgelegt wird auf den zweiten Fall, weil er die härtere Anforderung stellt — neue Chats kommen laufend hinzu, vorhandene können weitergelaufen sein.

Warum Nachreichen der Dauerbetrieb ist und nicht die Ausnahme, liegt an der Rollenteilung der Umgebungen: claude.ai und Claude Desktop sind die Orte für allgemeines Bearbeiten, Recherchieren und Durchdenken; Claude Code ist der Ort des eigentlichen Code-Building-Prozesses, und seine Sitzungen sind an einen dedizierten Rechner gebunden. Wer aus Gründen, die nur er selbst kennt, auf claude.ai weiterchattet, will dieselben Chats trotzdem im Quellcodeprojekt auswertbar haben.

Je Chat entstehen bis zu vier Dateien — Gespräch, Denkschritte, Anhänge, Erzeugnisse (Vorgabe 2.2) —, und daneben gibt es **genau eine** weitere: das Protokoll (1.4). Mehr Zustand gibt es nicht.

## 1.2 Die Wege

Der Engpass ist nicht die Suche, sondern die **Transkription**: Chattext erreicht ein Dateisystem nur, wenn er irgendwie dorthin gelangt, ohne durch den Kontext einer Instanz zu laufen — sonst wird aus Kopieren unweigerlich Nacherzählen (Vorgabe 2.8). Beide benutzbaren Wege umgehen diesen Engpass, und beide bedient dasselbe Skript, `chat_export_convert.py` (3.1).

| | Kontoexport | Web-Weg |
| --- | --- | --- |
| Quelle | ZIP per E-Mail, Zeitraum wählbar | die internen Endpunkte der claude.ai-Weboberfläche |
| Zugang | Konto mit Selbstbedienungs-Export | angemeldeter Chrome plus Browser-Anbindung |
| Wartezeit | Antrag, E-Mail, Download | keine |
| Menge | alles in einem Zug, keine Last je Chat | je Chat ein Abruf, deshalb gebremst |
| Projektbezug | fehlt — braucht eine Chatliste aus claude.ai | `project_uuid` und `created_at` stehen in den Daten |
| Aufruf | `convert --zip` | `list --web`, `convert --bundle` |

**Wann welcher.** Der Kontoexport ist der Anker: Er existiert, weil die Datenschutz-Grundverordnung ihn erzwingt — sein Format kann sich ändern, aber er verschwindet nicht. Der Web-Weg ist die bessere Wahl für **kleine Nachträge** eines Projekts, und für eine Erstmigration oder ganze Chats mit reichlich Anhängen bleibt der Export vorzuziehen: Ein Massenabruf über die Weboberfläche fällt serverseitig auf und kann Captcha- oder Cloudflare-Prüfungen auslösen. Deshalb die Abrufbremse von 4 bis 12 Sekunden je Chat.

**Für Team- und Enterprise-Konten ist der Web-Weg der einzige.** Dort hat ein gewöhnliches Mitglied keinen Selbstbedienungs-Export (1.6); der Primary Owner kann exportieren, aber ein Verfahren, das bei jedem Durchgang den Administrator braucht, ist für einen **wiederkehrenden** Abgleich (1.1) untauglich. Am 22. August 2026 wurde der Web-Weg in einem Team-Konto durchgespielt: Projektliste und Chatlisten kamen vollständig.

Bei den Denkschritten ist die Ausbeute ungewiss — sie **können** enthalten sein, müssen es aber nicht (3.1.1), und zwar in beiden Wegen gleichermaßen, weil die Plattform sie nicht mehr ausschreibt. Anhänge und Erzeugnisse sind davon unberührt.

**Ein dritter Weg ist entfallen:** `read_conversation`, ein eingebautes Werkzeug der claude.ai-Instanz, wurde am 18. August 2026 nicht mehr angeboten — zwölf Tage nach belegter Nutzung, ohne erkennbaren Grund. Er lieferte nur das gerenderte Transkript, also weder Denkschritte noch Anhänge, und wäre dem Web-Weg heute in jeder Hinsicht unterlegen. Der Nachweis der Abwesenheit steht in `testlauf.md`; warum das Skript trotzdem liegen bleibt, sagt 3.2.

**Verbindlich ist die Wegegleichheit** — Wortlaut, erlaubte Abweichungen und ihr Wächter stehen als Vorgabe 2.5. Zwischen ZIP-Weg und Web-Weg ist sie **baulich** erfüllt, weil beide durch denselben Konverter laufen (3.1); geprüft wird sie zusätzlich gegen die zweite Umsetzung in 3.2.

## 1.3 Richtungen und Zielorte

**Zwei Richtungen, dasselbe Werkzeug.** Entwickelt wird gegen **claude.ai → Claude Code**; Ziel ist dort das versionierte Repo des Zielprojekts. Die zweite Richtung ist **claude.ai → claude.ai** — ein anderes Projekt, gegebenenfalls unter einem anderen Konto. Dort kann nur das Projektwissen Ziel sein, was unproblematisch ist: Dieselbe Dateistruktur trägt die Durchsuchbarkeit auch da. Entscheidend ist, dass das **kein anderes Werkzeug** ist. Es sind dieselben Dateien aus demselben Lauf; verschieden ist allein, wohin sie gelegt werden. Vorgabe 2.10 setzt das voraus („keine zielabhängige Ausgabeform"), hier steht der Grund.

Primär das Git-Repo eines Claude-Code-Projekts, dort `<projekt>/.claude/imported_chats/`. Die Dateien sind über `Read`/`Grep` erreichbar: kein Projektwissen, kein RAG, kein undokumentierter Schwellwert, kein Kontextverbrauch, bis wirklich gelesen wird.

Sekundär das Projektwissen einer claude.ai-/Desktop-/Cowork-Instanz — mit denselben Dateien, ohne zweite Ausgabeform; die Regeln dazu (ein flaches Verzeichnis je Quellprojekt, dieselben Dateien für beide Ziele) sind Vorgabe 2.10. JSON ist ein belegter Upload-Typ, und Projektdateien werden per Textextraktion verarbeitet.

**Als dritter Zielort** kommt `~/.claude/projects/<projekt>/` in Frage — für Chats, die gerade **nicht** ins geteilte Repo sollen, weil Fremde sie nicht mitlesen dürfen. Sie liegen dann als nebenher geführtes zweites Chat-Projekt neben den Sitzungen, auf die Claude Code ohnehin zugreift, und werden dorthin regelmäßig nachgereicht. Drei Bedingungen gehören untrennbar dazu:

- **Die Aufbewahrungsdauer muss vorher hochgesetzt werden.** Dort wird nach `cleanupPeriodDays` aufgeräumt — *„The default is 30 days and the minimum is 1; setting `0` fails with a validation error"* (belegt, [claude-directory](https://code.claude.com/docs/en/claude-directory)); eine Obergrenze oder ein „aus" ist nicht dokumentiert. Das ist kein Ausschlussgrund, denn dieselbe Frist trifft ohnehin jede Claude-Code-Sitzung desselben Projekts — es ist eine **Nutzerpflicht**, die in die Anwenderdokumentation gehört. Namentlich aufgeräumt werden `projects/<p>/<sitzung>.jsonl` sowie `subagents/` und `tool-results/` je Sitzung; ob die Aufräumung auch **fremde** Dateien in diesem Ordner anfasst, sagt die Dokumentation nicht und bleibt Prüfpunkt (Kapitel 4).
- **`claude project purge` löscht unabhängig von jeder Frist**: *„Transcripts and auto memory under `projects/`"* für ein Projekt (belegt, ebd.). Wer das Kommando benutzt, nimmt ein dort liegendes Archiv mit.
- **§1.2 der Arbeitsanweisungen behält `~/.claude/` der Engine vor.** Ein Lauf, der dorthin schreibt, ist deshalb eine vom Nutzer ausdrücklich angeordnete Ausnahme und nie der Normalfall (Vorgabe 2.10).
- **Der Ordner liegt außerhalb des Arbeitsverzeichnisses.** Eine Claude-Code-Sitzung erreicht ihn nur, wenn er ihr als zusätzliches Verzeichnis freigegeben ist — *„The `--add-dir` flag gives Claude access to additional directories outside your main working directory"* (belegt, [memory](https://code.claude.com/docs/en/memory)). Ein Archiv, das die Instanz nicht öffnen kann, ist kein Archiv; der Anweisungsblock für diesen Zielort sagt es deshalb ausdrücklich (3.1.6).

Dass der Ort nicht versioniert und *„not shared across machines"* ist, spricht hier ausnahmsweise nicht dagegen, sondern dafür — genau das ist der Zweck, während `<projekt>/.claude/` umgekehrt gerade wegen der Versionierung Primärziel ist. Die dortige Ordnernamensstruktur bleibt als Zuordnungshilfe nützlich.

## 1.4 Das Protokoll

Eine Datei je Quellprojekt, neben den Chatdateien. Sie wird **bei der Erstellung der Chatliste angelegt** — in beiden Wegen, bevor ein einziger Chat geholt ist — und ist ab da in jedem Schritt die Referenz. Aufbau, Felder und Statuswerte sind Vorgabe 2.4.

Warum ein Protokoll und nicht der Verzeichnisinhalt: **Innerhalb von claude.ai gibt es kein Verzeichnis zum Ablesen**, dort existiert nur Hochgeladenes. Eine kleine Datei kann eine Instanz lesen, N Chatdateien durchzählen nicht. Die `metadata` in jeder Chatdatei bleibt trotzdem, damit eine einzeln weitergegebene Datei für sich verständlich ist; bei Widerspruch gilt das Protokoll.

**Gezählt wird im Skript, nicht im Kopf der Instanz** — und das ist keine Vorsicht, sondern eine Messung. Am hochgeladenen Protokoll gefragt, gab eine Instanz einen einzelnen Wert zeichengenau wieder, bis auf die Mikrosekunden eines Zeitstempels, nannte aber **zehn** Chats, wo neun eingetragen waren. Nachschlagen gelingt, Aufsummieren nicht. Deshalb rechnen `plan`, `overview` und `map` in dem Skript, das die JSON parst; die Instanz führt es aus, statt das Protokoll zu überschlagen. Hinge die Entscheidung „was fehlt noch" daran, dass sie richtig zählt, wäre der Fehler still.

Das Protokoll gehört ins Projektwissen des **Quellprojekts**, weil dort die Chatliste entsteht, mit der jeder Lauf beginnt (1.5). Nebeneffekt: das Quellprojekt trägt selbst die Auskunft, was von ihm exportiert wurde.

Nicht in Artefakte: die kennen keinen JSON-Typ, kein spezifiziertes Downloadformat, und der einzige dokumentierte Rückweg in einen neuen Chat ist manuelles Kopieren (belegt, [9487310](https://support.claude.com/en/articles/9487310-what-are-artifacts-and-how-do-i-use-them)).

## 1.5 Ablauf aus Nutzersicht

**Claude Code ist das Frontend**, angeleitet durch den Skill `chat-export` (3.5). Kein Parametrierungswerkzeug: Er stellt fest, welche Projekte betroffen sind und was schon da ist, legt die Lage vor und ruft das Skript auf. Zwei Haltepunkte sind vorgesehen — vor dem ersten Abruf und nach der Statistik; die Wahl des Wegs trifft der Nutzer, nicht der Skill.

**Über den Web-Weg**, der Regelfall für Nachträge:

1. Projektliste holen, Projekt bestimmen, Chatliste über alle Seiten holen. Alles aus einem Tab auf claude.ai heraus, ohne Chat und ohne dass ein Zeichen durch einen Kontext läuft.
2. `list --web` gegen das Protokoll: Was ist neu, was gewachsen, was verschwunden. Die Fenstergrenze braucht hier nichts geschätzt zu werden, denn `created_at` steht je Chat in der Liste.
3. Die fehlenden Chats abrufen, gebremst, alles in **einen** Behälter, **ein** Download.
4. `convert --bundle`: Dateien schreiben, Protokoll fortschreiben, Ersetztes benennen.

**Über den Kontoexport**, für Erstmigration und große Mengen:

1. Zeitraum aus dem Protokoll errechnen lassen (`diff` nennt ihn samt Begründung), Export anfordern, ZIP herunterladen. **Setzt voraus, dass es ihn gibt** — Free, Pro oder Max (1.6); in einem Team-Konto führt dieser Ablauf ins Leere und der Web-Weg ist der einzige. Der Zeitraum filtert `created_at`, nicht `updated_at` (4.2): ein alter Chat, der letzte Woche weiterlief, fehlt in einem kurzen Fenster **ganz**.
2. Die Projektzuordnung fehlt dem Export. Sie kommt entweder aus der Chatliste des Web-Wegs (`list --web`) oder, wo der nicht zur Verfügung steht, aus einem `recent_chats`-Abzug in claude.ai (`list --map`) — dann gilt die Regel unten.
3. `convert --zip`: dieselben Dateien, derselbe Protokollstand wie im Web-Weg.

**Nur wenn die Chatliste aus einem claude.ai-Chat kommt:** Die Abfrage gehört in einen eigens dafür angelegten Chat, der danach gelöscht wird. Grund: `recent_chats` listet den laufenden Chat nicht mit (1.6), also fehlt der Abfragechat in seiner eigenen Liste — und damit im Protokoll und im Archiv, ohne dass irgendetwas es meldet. Ein frischer, hinterher gelöschter Chat macht die Lücke harmlos. Der Web-Weg hat dieses Problem nicht: Er listet ohne Chat und übergeht nichts.

**Der Rückweg des Protokolls** ins Projektwissen des Quellprojekts ist **kein Pflichtschritt mehr**. Er trug den entfallenen Lese-Weg, der dort arbeitete. Als Selbstauskunft bleibt er nützlich — das Quellprojekt sagt dann selbst, was von ihm archiviert wurde —, aber der Abgleich braucht ihn nicht: Das Protokoll liegt beim Archiv (1.4).

**Der Sondierungsexport ist entfallen.** Er diente allein dazu, das `created_at` des Projekts zu erfahren, weil keine andere Quelle es hergab. Der Projekt-Endpunkt des Web-Wegs liefert es direkt (2.4). Wer nur den Export-Weg hat, kann ihn weiter benutzen — ein Kurzzeitraum-Export enthält alle Projektdateien mit ihrem Datum (3.1.1) —, braucht ihn aber nicht mehr als Regelschritt.

**Wie Zuwachs erkannt wird:** Eine frische Chatliste liefert je Chat ein `updated_at`. Ist es neuer als der Stand im Protokoll, wurde weitergechattet. Der Vergleich braucht nichts als das Protokoll und die neue Liste — kein Chatarchiv, kein ZIP, kein Zeichen Chattext (Mechanik in Vorgabe 2.4). Ein veralteter Chat wird **als Ganzes ersetzt**, nicht fortgeschrieben, und das Ersetzen räumt auf — Vorgabe 2.6.

## 1.6 Was die Umgebung erlaubt und verbietet

### Migrationsmatrix, heraus


| Quelle                    | Weg                                 | Format                        | Haken                                                                           |
| ------------------------- | ----------------------------------- | ----------------------------- | ------------------------------------------------------------------------------- |
| claude.ai, alle Chats     | Kontoexport                         | ZIP,`conversations.json`      | kein Projektbezug; Gelöschtes als Hülle; `files` nur als Name; Momentaufnahme |
| claude.ai, ein Projekt    | **interne Web-Endpunkte**           | JSON, Baum vollständig        | undokumentiert, jederzeit änderbar; braucht angemeldeten Browser                |
| claude.ai, ein Projekt    | `recent_chats`                      | UUID, Zeit, Titel             | nur Metadaten, ohne `created_at`; übergeht den laufenden Chat                   |
| Claude Code CLI           | `/export`, `<id>.jsonl`             | Text bzw. JSONL               | geprüft und verworfen: kein JSON bzw. Format instabil und 30 Tage Frist         |
| Cowork                    | Sitzungsexport, Dateisystem         | JSONL, `local_<uuid>.json`    | geprüft und verworfen: Auslöser bzw. Ablage nicht dokumentiert                   |
| Cowork, Cloud, Enterprise | Compliance API                      | JSON                          | könnte alles, nur Enterprise (4.5)                                              |

### Migrationsmatrix, hinein


| Ziel                      | Weg                         | Haken                                            |
| ------------------------- | --------------------------- | ------------------------------------------------ |
| Git-Repo für Claude Code | Datei im Arbeitsverzeichnis | **der gewählte Weg**                            |
| claude.ai-Projekt         | Projektwissen hochladen     | bleibt im Kontext bzw. wird per RAG durchsucht   |
| claude.ai-Chat            | Datei anhängen             | 20 Dateien je Chat                               |
| claude.ai, neuer Chat     | —                          | **kein dokumentierter Mechanismus**              |
| Cowork-Projekt            | Ordner verbinden            | Cowork-Projekte sind lokal, nicht synchronisiert |

**Es gibt kein „Chat als Chat migrieren".** Jeder Weg verwandelt eine Konversation in Dateien. Die zwei echten Sitzungsübergaben (`--teleport`, „Continue in") sind kontobasiert und gehen nie von einer Datei aus.

### Grenzen, die bleiben

- **Cowork ist über keinen Weg erreichbar.** Eigene ID-Welt, kein Export, kein Projektbezug; Lücke, keine Aufgabe. Anthropic baut daran, und ein künftiger Cowork-Weg könnte dieses Vorhaben ganz ablösen — als Beobachtung geführt in Kapitel 4.
- **Gelöschte Chats sind unwiederbringlich.** Der Export enthält sie als Hüllen und sagt nicht, dass es Hüllen sind (3.1). Der scheinbare Widerspruch zur belegten Zusage oben löst sich beim genauen Lesen auf: Nicht enthalten sind die *Inhalte*, der *Eintrag* bleibt. Beide Aussagen stimmen. Und weil die Chatliste den gelöschten Chat nicht mehr führt, kann ihn kein Lauf mehr einem Projekt zuordnen — er kommt im Archiv also gar nicht erst vor.
- **Hochgeladene Dateien: das meiste kommt mit.** Der Export führt sie in zwei Feldern, und die sind **nicht disjunkt** — dieselbe Datei steht oft in beiden. `attachments` tragen `extracted_content` und damit ihren Text — 341 im Drei-Monats-Export, keines leer, zusammen 9.635.919 Zeichen, überwiegend `text/x-python` (238) und Markdown (26). `files` tragen nur `file_uuid` und `file_name` — 524 Stück, aber das ist kein Verlustmaß: Ein Textupload wird **zweimal** verzeichnet, einmal als Dateiobjekt unter `files` und einmal mit seinem Text unter `attachments`. Die Beleglage abgestuft:
  - **Gemessen:** 319 der 524 `files`-Einträge haben ihren Inhalt in derselben Nachricht. Für sie ist nichts verloren.
  - **Gemessen:** 205 haben keinen Namenspartner mit Inhalt; nach Entdopplung innerhalb der Nachricht meldet das Werkzeug 200.
  - **Unsicher:** 24 davon liegen in Nachrichten, die einen **namenlosen** Anhang mit Inhalt tragen (s. 3.1.1). Das sind vermutlich dieselben Uploads — der Name steht nur auf der `files`-Seite, der Inhalt nur auf der `attachments`-Seite —, aber über den Namen lassen sie sich nicht zusammenführen. Der Code rät hier nicht (3.1.3).
  - **Nicht behauptet** wird, dass die restlichen rund 180 unwiederbringlich sind. Belegbar ist nur: Der Export führt für sie keinen Inhalt. Ob es einen anderen Abrufweg gibt, ist eigener Prüfpunkt (4.3, warm).
- **Die Projektzugehörigkeit gibt es nur in claude.ai.** Der einzige Punkt, an dem die Werkzeuge dort unentbehrlich bleiben, um exportierte Chats einzelnen Projekten zuzuordnen. Ob eine Konversation im Export je einen Projektbezug bekommt, führt Kapitel 4 als Prüfpunkt (4.2, kalt).

### Umgebungsfakten, die den Gesamtentwurf tragen


| Aussage                                                                                                                                                                                     | Beleglage                                                                                                               |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Kontoexport unter Settings → Privacy, Link per E-Mail, verfällt nach 24 h — *„available to individual Claude users on Free, Pro, and Max plans"*                                          | belegt ([9450526](https://support.claude.com/en/articles/9450526-export-your-claude-data))                              |
| **In Team und Enterprise hat ein gewöhnliches Mitglied keinen Export**: *„Individual members of Team and Enterprise organizations do not have a self-serve export option"*; nur der Primary Owner exportiert, und zwar unter *Organization settings → Data and privacy* | belegt ([13346720](https://support.claude.com/en/articles/13346720-export-your-organization-s-data))                    |
| **Der Export lässt einen Zeitraum wählen**                                                                                                                                                | **beobachtet**, in keinem Artikel erwähnt                                                                              |
| Gelöschte Inhalte*„will not be included in data exports initiated after the deletion"*                                                                                                    | belegt ([13346720](https://support.claude.com/en/articles/13346720-export-your-organization-s-data))                    |
| **Der Löschvorgang nimmt den Inhalt, nicht den Eintrag.** Zwei am 17. August gelöschte Chats standen im danach angeforderten Export als Hüllen — Gerüst da, null Zeichen Text            | beobachtet                                                                                                              |
| **Ein gelöschter Chat verschwindet dagegen aus `recent_chats`** und ist damit keinem Projekt mehr zuzuordnen                                                                              | beobachtet                                                                                                              |
| **`recent_chats` listet den laufenden Chat nicht mit.** Aus Chat A kommt B, aus B kommt A — jeder sieht den anderen, keiner sich selbst                                                    | beobachtet (zwei symmetrische Versuche)                                                                                 |
| Projektdateien: 30 MB je Datei, Anzahl unbegrenzt,*„Text extraction only"*                                                                                                                 | belegt ([8241126](https://support.claude.com/en/articles/8241126-upload-files-to-claude))                               |
| RAG für Projekte schaltet automatisch nahe der Kontextgrenze ein,*„up to 10x"*, Claude nutzt dann ein *project knowledge search tool*; **kein Schwellwert dokumentiert**, nicht steuerbar | belegt ([11473015](https://support.claude.com/en/articles/11473015-retrieval-augmented-generation-rag-for-projects))    |
| RAG-Schwelle richte sich nach**Dateianzahl**, nicht Größe                                                                                                                                 | Community ([#25759](https://github.com/anthropics/claude-code/issues/25759)), als `invalid` geschlossen                 |
| Projektdateien im Container*„accessible … **while remaining in context**"* — spart **keinen** Kontext                                                                                    | belegt ([12111783](https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude))                  |
| Container-Netzzugang nur gegen eine Allowlist;`claude.ai` steht **nicht** darauf                                                                                                            | belegt (ebd.)                                                                                                           |
| Kontextfenster Opus 5 / Sonnet 5: 1 Mio Token auf bezahlten Plänen                                                                                                                         | belegt ([8606394](https://support.claude.com/en/articles/8606394-how-large-is-the-context-window-on-paid-claude-plans)) |
| Ein langes Gespräch bricht nicht ab, sondern**fasst frühere Teile zusammen**                                                                                                              | belegt (ebd.)                                                                                                           |
| Opus 4.7 und spätere Opus-Modelle erhalten**keine** Token-Budget-Tags                                                                                                                      | belegt ([Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows))                       |
| Claude-Code-Transkripte:`~/.claude/projects/<p>/<id>.jsonl`, Format *„internal … changes between versions"*, Aufräumung nach `cleanupPeriodDays` (Standard 30, Minimum 1, einstellbar), **kein Import**                                   | belegt ([sessions](https://code.claude.com/docs/en/sessions))                                                           |

Formatnahe Fakten stehen bei dem Skript, das sie verarbeitet: Aufbau des Export-ZIP in 3.1.1, Suchschnipsel in 3.4. Was quer über alle Werkzeuge gilt, steht als Vorgabe in Kapitel 2; die Prüfliste gegen Anthropic-Änderungen ist Kapitel 4.

### Widersprüche in der Anthropic-Doku

Benannt, nicht aufgelöst:

- Dateigröße beim Upload: 500 MB ([8241126](https://support.claude.com/en/articles/8241126-upload-files-to-claude)) gegen *„30MB per file for both uploads and downloads"* ([12111783](https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude)).
- Projektwissen: *„must fit within Claude's context window"* gegen *„you can continue adding knowledge beyond these limits"*.
- RAG-Verfügbarkeit: *„available for all Claude plans"* gegen *„only available to users with paid Claude plans"* ([9517075](https://support.claude.com/en/articles/9517075-what-are-projects)).
- Die Exports-Zip-Files tragen einen batch-Abschnitt mit einer Zahl im Namen, die bei Tests immer auf 0 steht. Möglicherweise werden größere Exports in mehrere Zip-Files aufgeteilt.

## 1.7 Widerlegte Annahmen

Damit sie nicht erneut abgeleitet werden:


| Angenommen                                                 | Tatsächlich                                                                     |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Chats seien nur über Suchschnipsel erreichbar             | Die internen Web-Endpunkte liefern einen Chat vollständig samt Baum, Anhängen und Werkzeugaufrufen (1.2). Zwischenzeitlich tat das auch `read_conversation`, das aber wieder verschwand — die Annahme fiel also zweimal, aus verschiedenen Gründen |
| Suchschnipsel überlappten und ließen sich zusammennähen | Feste, nicht überlappende Blöcke — womit die Overlap-Mechanik des Crawlers nichts zu verbinden hatte (3.4) |
| `batch-0000` bedeute Stückelung der Konversationen        | Die Zeitraumauswahl erklärt die Menge                                           |
| Markdown sei für Durchsuchbarkeit besser                  | JSON macht die Sprecherrollen eindeutig; Textextraktion ist bei JSON verlustfrei — am echten Upload bestätigt: ein Zeitstempel kam mit Mikrosekunden unverändert zurück (1.4) |
| §1.12 der Arbeitsanweisungen müsse geändert werden      | Das dortige Schema ist ein Beispiel, Ergänzen ist erlaubt                       |
| Der Container könne den Downloadlink holen                | Allowlist ohne`claude.ai`, und der Link ist sitzungsgebunden                     |
| Projektdateien im Container sparten Kontext                | *„while remaining in context"*                                                  |
| Der Export trage die Denkschritte verlässlich | Er kann sie tragen, muss aber nicht: Ein Denkblock ist entweder mit Text da oder als `thinking_hidden` leer, und das Verhältnis schwankt bis hin zu „ausschließlich leer" (3.1.1). Ein Archiv ohne Denkdatei ist deshalb eine Stichprobe, kein Formatbefund. |
| `attachments` und `files` bezeichneten verschiedene Dinge, `files` sei reiner Verlust | Sie überschneiden sich: Ein Textupload steht in **beiden**, als Dateiobjekt und als extrahierter Text. 319 der 524 `files`-Einträge des Drei-Monats-Exports tragen ihren Inhalt in derselben Nachricht (1.6, 3.1.1). Unser `report` meldete sie trotzdem als Verlust — der Fehler fiel erst am eigenen Testlauf auf, an einer einzigen hochgeladenen Datei. |
| Dateianhänge seien im Export nur ein Name | Gilt nur für `files` (524). Die `attachments` (341) tragen `extracted_content` — 9,6 Mio Zeichen, überwiegend Python und Markdown. Ich hatte das weggeworfen und als Verlust gemeldet, den es nicht gab. |
| Eine Erstmigration brauche einen Vollexport | Der Zeitraumfilter wirkt nicht auf `projects/`: ein Ein-Wochen-Export liefert jedes Projekt mit `created_at` und damit die exakte Fenstergrenze (3.1.1). |
| Der Projektbeginn sei nur im Chat selbst zu erfahren | Er steht im Export bei den Projektdateien — und seit dem Web-Weg direkt am Projekt-Endpunkt, weshalb der Sondierungsexport entfiel (1.5, 2.4). |
| Aufzählung und Lesbarkeit deckten sich — `recent_chats` liste genau die Chats, die dort lesbar sind | Der **laufende** Chat fehlt: Er ist lesbar, erscheint aber nie in seiner eigenen Liste (1.6). Jeder Listenlauf übergeht damit den Chat, aus dem er gestartet wurde, und keine der eingebauten Kontrollen bemerkt es. |
| Der Export-Weg stehe jedem Konto offen | Nur Free, Pro und Max; in Team und Enterprise exportiert allein der Primary Owner (1.6). Der ganze Entwurf lehnte sich an diese Annahme, ausgesprochen war sie nie. Für solche Konten trägt heute der Web-Weg (1.2). |
| `~/.claude/projects/…` scheide als Zielort aus | Die Aufbewahrungsdauer ist einstellbar (`cleanupPeriodDays`) und trifft ohnehin jede Sitzung desselben Projekts. Für Chats, die niemand mitlesen soll, ist der Ort damit sogar der bequemste — unter den drei Bedingungen aus 1.3. |

---

# 2 Vorgaben

Festlegungen, die quer über alle Werkzeuge dieses Ordners gelten. Aufnahmetest: Man muss auf eine Datei zeigen und sagen können „das verletzt diese Vorgabe". Was so nicht prüfbar ist, steht als Begründung in Kapitel 1 oder als Skript-Eigenheit in Kapitel 3. Weicht ein künftiges Werkzeug bewusst ab, wird die Vorgabe geändert oder das Werkzeug — nie stillschweigend beides gelassen.

## 2.1 Beleglage

Jede Aussage über die Umgebung trägt ihre Beleglage: **belegt** (Anthropic-Dokument, mit Quelle), **beobachtet** (am laufenden System gesehen, nirgends dokumentiert), **Community** (von Dritten berichtet, unbestätigt). Die drei werden nie vermischt, und eine Aufstufung verlangt den jeweiligen Nachweis — eine Community-Aussage wird durch eigenes Nachstellen zur Beobachtung, eine Beobachtung nur durch eine Anthropic-Quelle zum Beleg. In dieser Arbeit sind fünfzehn Annahmen gekippt (1.7); der Unterschied entschied jedes Mal.

## 2.2 Dateiformat der Chatdateien

Grundlage ist §1.12 der Arbeitsanweisungen: JSON, `messages` mit `role` (`user`/`assistant`) und `content`, dazu ein `metadata`-Objekt. Das dortige Schema ist ausdrücklich ein Beispielschema, also ein Mindestbestand — hier bewusst mit klareren Namen geführt und um zwei Felder unterschritten, aus folgendem Grund.

`predecessor`/`successor` entfallen ganz: §1.11 verlangt für ihre Bestimmung entweder eine Dateinummerierung (haben wir nicht) oder einen inhaltlichen Anhaltspunkt (verstieße gegen Vorgabe 2.7 — Auswahl nie durch Inhalt) oder Nachfragen beim Nutzer je Chat (skaliert nicht). Ein bloßer Zeitstempel reicht nach §1.11 ausdrücklich nicht, und selbst „gleiches Projekt" ist kein verlässliches Indiz — ein Testchat dieses Werkzeugs lag beobachtbar im FreeCAD-Projekt, ohne mit FreeCAD zusammenzuhängen. Chats, die abwechselnd nebeneinander geführt werden, ergeben ohnehin kein sinnvolles Vorgänger/Nachfolger-Schema. Die Rolle, die eine Historie tatsächlich braucht — welche Chats einen älteren, durch andere überholten Stand zeigen — übernimmt `last_updated_at` (s. u.), nicht durch Inhalt, nicht durch den Anlegezeitpunkt, nicht durch einen Zeitstempel je Redebeitrag (den liefert keiner der beiden Wege). §1.12 wird auf dieses Tooling nachgezogen, sobald geklärt ist, wie eine Sitzung in einem fremden Projekt es referenziert; die hier verwendeten Feldnamen sind der Vorschlag dafür.

`chat_date` heißt `created_at` — der Name trifft die Sache, die er meint, und deckt sich mit dem Feld im Rohexport (3.1.1). `source_updated_at` heißt `last_updated_at` — er ist nie ein API-Name gewesen, sondern unsere eigene Benennung, und der alte Name legte fälschlich nahe, er stamme aus der Quelle selbst.

Zusätzliche Metadatenfelder, in dieser Reihenfolge:


| Feld | Wozu |
| --- | --- |
| `chat_uuid`, `url`, `title` | Identität und Auffindbarkeit |
| `source` | `account-export`, `web-api` oder `read_conversation` — der Behälter, aus dem der Chat kam |
| `last_updated_at` | Stand der Quelle beim Import — macht Veralten erkennbar; **die** für Historie/Sortierung entscheidende Angabe (2.5) |
| `turns` | Anzahl importierter Redebeiträge |
| `total_turns`, `complete`, `turns_missing` | Vollständigkeit samt Beleg; nur der Lese-Weg kann sie füllen (2.5) |
| `deleted` | Hülle eines an der Quelle gelöschten Chats; dann ohne `messages` |
| `branches` | mitgenommene Nebenzweige des Nachrichtenbaums (3.1.2); **einziges optionales Feld** — s. 2.5 |
| `dropped_duplicates` | übersprungene Sendewiederholungen |
| `dropped_blocks` | weggelassene Blocktypen je Anzahl, **ohne** `thinking` — das liegt in der Denkdatei und wäre kein Verlust |
| `dropped_thinking` | verworfene Denkblöcke nach den Schwellen in 3.1.3 |
| `attachments_with_content` | Anhänge, deren Text mitkam (Dateien, nicht Nachrichten) |
| `creations` | Erzeugnisse der KI, deren Inhalt mitkam (Artefakte, erstellte Dateien, Änderungen) |
| `attachments_without_content` | Namen der Verweise, deren Inhalt die Quelle nicht hat |

Nachrichten tragen `n`, `role`, `content`. `warnings` ist auf oberster Ebene immer vorhanden, auch leer.

**Bis zu vier Dateien je Chat**, gleicher Stamm; eine Nebendatei entsteht nur, wenn es etwas hineinzuschreiben gibt:

```
2026-06-27_dachluken-steuerung_a1b2c3d4.json              das Gespräch
2026-06-27_dachluken-steuerung_a1b2c3d4.thinking.json     die Denkschritte
2026-06-27_dachluken-steuerung_a1b2c3d4.attachments.json  die Anhänge
2026-06-27_dachluken-steuerung_a1b2c3d4.creations.json    die Erzeugnisse
```

Der Grund für die Auslagerung ist stets dieselbe Rechnung: Denkschritte (9,2 Mio Zeichen), Anhänge (9,6 Mio) und Erzeugnisse (4,4 Mio — von der KI erstellte Artefakte, Dateien und Änderungen, Messung in 3.1.1) übertreffen zusammen den Gesprächstext (11,3 Mio) deutlich. Wer das Gespräch liest, trüge sonst fast das Doppelte — und die Mengenentscheidung fällt erst bei der Benutzung: fürs Repo alles, fürs Projektwissen nur die Gesprächsdateien.

**Verknüpfung über die Nachrichten-UUID**, kein eigener Bezeichner: In der Gesprächsdatei trägt eine Nachricht mit Denkschritten `thinking_ref`, eine mit Anhängen `attachments_ref`, eine mit Erzeugnissen `creations_ref` — jeweils die UUID der Nachricht aus der Quelle. In der Nebendatei trägt jeder Eintrag `ref` mit derselben UUID, dazu die Rückreferenz `chat_uuid`, `chat_file`, `branch` und `turn`. `turn` zählt innerhalb seiner Folge und wiederholt sich zwischen Hauptpfad und Zweig — erst das Paar `(branch, turn)` ist eindeutig, `branch` ist `null` für den Hauptpfad. Damit findet ein Grep der UUID die Stelle in genau einer Nebendatei, und aus der Nebendatei führt der Weg zurück; die Suche über Inhalte funktioniert unabhängig davon.

## 2.3 Dateinamen

`JJJJ-MM-TT_titel-slug_uuid8` plus Endung; das Datum ist das `created_at` der Quelle (sonst `ohne-datum`), der Slug transliteriert Umlaute, kennt nur `a-z0-9-`, ist höchstens 50 Zeichen lang und fällt auf `ohne-titel` zurück. Die acht UUID-Zeichen stehen **immer** im Namen, nicht erst bei Kollision: Zwei Chats teilen im echten Export tatsächlich Datum und Titel, und ein Name, der davon abhängt, was sonst im selben Lauf umgewandelt wird, wäre nicht reproduzierbar.

## 2.4 Das Protokoll

Eine `protokoll.json` je Quellprojekt, neben den Chatdateien. Sie wird mit der Chatliste angelegt — vor jedem Chattext — und ist ab da die Referenz; bei Widerspruch zwischen Protokoll und Verzeichnis gilt das Protokoll. Je Chat:


| Feld | Wozu |
| --- | --- |
| `title`, `created_at` | Auffindbarkeit; `created_at` liefern der ZIP-Weg und die Chatliste des Web-Wegs, ein `recent_chats`-Abzug nicht |
| `created_after` | Untergrenze für Chats ohne `created_at`: der Stand des **vorherigen** Abgleichs beim ersten Sehen — damals war das Projekt gelistet und der Chat nicht dabei, also entstand er später. Wird nur beim ersten Sehen gesetzt und danach nie überschrieben |
| `listed_updated_at` | `updated_at` aus der zuletzt geholten Chatliste |
| `exported_updated_at` | Stand, auf dem der vorliegende Export beruht |
| `turns`, `total_turns` | Umfang beim Export |
| `end_token` | letztes `next_page_token`, falls bekannt — schreibt nur der Lese-Weg (3.2), nichts hängt daran |
| `file` | Name der Chatdatei, oder leer |
| `side_files` | Namen der Nebendateien, damit sie beim Ersetzen mit entfernt werden (2.6) |
| `status` | s. u. |
| `exported_at` | Zeitpunkt |

Statuswerte: `listed` (aus der Chatliste bekannt), `started` (teilweise gelesen — setzt nur der Lese-Weg, der ZIP-Weg schreibt einen Chat immer ganz), `exported`, `stale` (die Quelle ist neuer als der Export), `deleted` (Hülle an der Quelle). `stale` entsteht durch den Vergleich `listed_updated_at` gegen `exported_updated_at`; `updated_at` trägt diese Erkennung, und zwar beobachtet: es liegt in allen Quellen vor — Export, Web-Chatliste, `recent_chats` — und sprang bei gelöschten Chats auf den Löschzeitpunkt.

**Ein Chat, den die frische Liste nicht mehr führt, wird gemeldet und nie automatisch entfernt.** Die Meldung nennt ihn samt Status; das Protokoll behält ihn, und seine Dateien bleiben liegen. Der Grund ist, dass drei sehr verschiedene Fälle von hier aus ununterscheidbar sind: Löschung an der Quelle, Verschieben in ein anderes Projekt — oder eine Chatliste, die der Nutzer nicht bis zum Ende geblättert hat. Beim letzten Fall wäre jede Entfernung ein Datenverlust aus einem Bedienfehler. Die Regel bindet **beide** Wege; sie sagen es im selben Wortlaut, gehalten als Konstante `VANISHED_NOTE` in beiden Skripten und gegen Auseinanderdriften gesichert durch `tests/test_wegegleichheit.py`, denn teilen können die Skripte sich nichts (Vorgabe 2.9).

Auf oberster Ebene trägt das Protokoll `protocol_version`, `project`, `project_created_at` (Beginn des Quellprojekts — aus dem Projekt-Endpunkt des Web-Wegs oder aus den Projektdateien eines Exports, eingetragen über `list --project-created`), `listed_at` (Zeitpunkt des letzten Listenabgleichs, gesetzt von `list` bzw. `map`) und `order` — die Bearbeitungsrichtung schreibt nur der Lese-Weg, der ZIP-Weg erhält sie unangetastet: ein Protokoll, ein Schema.

**Die Fenstergrenze, in einer Tabelle.** Wie weit ein Export zurückreichen muss, damit er einen Chat erfasst, ergibt sich aus drei Quellen unterschiedlicher Güte — genommen wird das Minimum über alle zu holenden Chats:

| Chat-Lage | Fensterstart | Güte |
| --- | --- | --- |
| schon exportiert, aber gewachsen | sein `created_at` aus dem Protokoll | exakt |
| erst beim letzten Abgleich hinzugekommen | sein `created_after` | exakt — vorher existierte er nicht |
| gelistet, aber nie in einem Archiv, ohne `created_after` | `created_at` des Projekts aus einem Sondierungsexport (3.1.1) | exakt, aber projektweit statt chatweise |
| über den Web-Weg gelistet | sein eigenes `created_at` aus der Chatliste | exakt — deshalb braucht dieser Weg keinen Sondierungsexport |
| kein Protokoll (Erstmigration) | ebenso der Projektbeginn | dito |

Der Projektbeginn ist dabei die Untergrenze über alles: kein Chat eines Projekts kann älter sein als das Projekt. Ein zu großzügiges Fenster kostet nur Downloadgröße, ein zu knappes kostet Inhalt — deshalb im Zweifel aufrunden, nach unten.

Umgesetzt als `window_start()` in beiden Skripten, mit `unbounded` als eigenem Ergebnis: hat ein wartender Chat keine der drei Quellen, wird das **gemeldet statt geschätzt**. Im ZIP-Weg tragen `list` und `diff` das Ergebnis vor, beide über dieselbe Funktion `window_lines()` — zwei Kommandos, die dieselbe Rechnung in eigenen Worten ausgeben, driften auseinander (3.1.6). Der Projektbeginn kommt von außen herein (`--project-created`), weil eine Konversation im Archiv keinen Projektbezug trägt: Im Web-Weg liefert ihn der Projekt-Endpunkt, im reinen Export-Weg liest ihn `inspect_export.py` aus den Projektdateien, sonst kennt ihn nur der Nutzer. Gegen den Tippfehler dabei steht `project_start_warnings()`: ein Chat, der älter ist als sein Projekt, kann nicht zu ihm gehören, also stimmt entweder das Datum oder die Chatliste nicht. Ohne diese Prüfung würde ein falsch getipptes Datum jedes künftige Fenster still verkürzen. Beide Funktionen laufen in `tests/test_wegegleichheit.py` über dieselbe Falltabelle, damit die zwei Implementierungen nicht auseinanderdriften.

Erfüllt von beiden Wegen und geprüft: `tests/test_wegegleichheit.py` vergleicht auch die Protokolle — gleiche Schlüsselmengen, gleiche Kernfelder, und genau drei Felder dürfen sich unterscheiden, weil ein Weg sie nicht wissen kann: `created_at` (kennt nur der ZIP-Weg), `total_turns` (beweist nur der Lese-Weg), `file` (das Datumssegment fehlt dem Lese-Weg — 2.3).

## 2.5 Wegegleichheit

Beide Wege erzeugen für denselben Chat **dieselbe Chatdatei** und **dasselbe Protokoll** (Protokollabgleich in 2.4). Sonst hinge der Inhalt des Archivs davon ab, auf welchem Weg ein Chat hereinkam, und „habe ich diesen Chat?" würde unscharf.

Wo ein Weg etwas **nicht wissen kann**, steht `null` statt einer Vermutung. Der ZIP-Weg hat kein Sollmaß und behauptet keine Vollständigkeit (`total_turns`, `complete`, `turns_missing` sind `null`); der Lese-Weg kennt kein `created_at` und schreibt dort `"unknown"`. Genau **fünf** Metadatenfelder dürfen sich unterscheiden — `source`, `created_at`, `total_turns`, `complete`, `turns_missing` — und keines mehr.

In den Nachrichten sind `thinking_ref`, `attachments_ref` und `creations_ref` die einzigen erlaubten Zusatzfelder, und nur der ZIP-Weg erzeugt sie — der Lese-Weg sieht weder Denkschritte noch Anhänge noch Werkzeugaufrufe (3.2). Nach ihrem Entfernen müssen zwei identische Transkripte übrig bleiben. `branches` ist aus demselben Grund das einzige optionale Feld auf oberster Ebene: eine leere Liste im Lese-Weg würde einen Befund behaupten, den er nicht treffen kann.

Zur Laufzeit erzwingt das nichts (2.9). Der Wächter ist `tests/test_wegegleichheit.py` — **jede** Formatänderung an einem der beiden Skripte läuft durch diesen Test, und er hat sich bewährt: er fiel durch, als der Lese-Weg ein neu hinzugekommenes Feld nicht kannte.

## 2.6 Ersetzen

Ein veralteter Chat wird **als Ganzes ersetzt**, nie fortgeschrieben — das macht den Entwurf von keiner undokumentierten Eigenschaft abhängig, und aus dem ZIP kostet es nichts.

**Ersetzen heißt aufräumen:** Vor dem Schreiben entfernt das Werkzeug alle im Protokoll vermerkten Dateien des vorherigen Eintrags (`file` und `side_files`) und **nennt sie in der Ausgabe** — stilles Löschen wäre die nächste Fehlerquelle. Aufgeräumt wird vor dem Schreiben, weil sich der Dateistamm geändert haben kann. Zwei nachgestellte Fälle erzwingen das: die **Umbenennung** (der Name trägt den Titel-Slug, ohne Aufräumen entsteht ein zweiter Stamm und ein Grep findet beide Fassungen) und die **wegfallende Nebendatei** (die neue Fassung hat kein Denken oder keinen Anhang mehr, die alte Datei bliebe auffindbar).

Die Gegenrichtung gehört dazu: `diff` meldet **Waisen** — Dateien im Verzeichnis, die kein Protokolleintrag beansprucht. Es ist die einzige Stelle, die ein Zuviel statt eines Zuwenig bemerkt, und sie warnt davor, blind zu löschen: das Protokoll ist die Autorität, nicht das Verzeichnis.

## 2.7 Auswahl strukturell, nie inhaltlich

Filterentscheidungen stützen sich auf Struktur — Feldwerte, Längen, Flaggen — und nie auf Inhaltsmerkmale wie Trigger-Wörter: die sind sprachabhängig und brechen, sobald ein Chat die Sprache wechselt. Inhaltssignale sind als **Prüfmaßstab** erlaubt, um einen strukturellen Schwellwert zu validieren, stehen aber nie im Code. Anwendungsfall mit Messung: die Denkblock-Auswahl in 3.1.3.

## 2.8 Transkriptionsdisziplin

Gilt für jeden Weg, auf dem Chattext durch den Kontext einer Instanz läuft. **Auslassen und Umformulieren sind Gegensätze, keine Grade:** Ausgelassenes fehlt sichtbar und ist nachholbar; Umformuliertes landet im Archiv, als wäre es echt — ein erfundener Datensatz, kein beschädigter. Deshalb: nie zusammenfassen, nie „handhabbar machen", nie ein eigenes Auslassungszeichen schreiben. Lieber weniger übertragen, das aber exakt. Das wegspezifische Verfahren für zu große Stücke steht bei dem Skript, das es braucht (3.4).

## 2.9 Hochladbare Skripte sind eigenständig

Ein Skript, das in eine Konversation hochgeladen wird (`chat_read_store.py`, `chat_crawl_store.py`), importiert nichts aus diesem Repo, hält kleine Helfer bewusst doppelt und trägt seine vollständige Betriebsanleitung im eigenen Docstring — die hochgeladene Datei ist alles, was die Instanz dort hat. Die Folge ist der Preis von 2.5: Formatgleichheit ist nicht erzwingbar, nur per Test gesichert.

Dieselbe Zusage gilt für `chat_export_convert.py` und `inspect_export.py`, obwohl sie nie hochgeladen werden: Claude Code liest nur den Docstring, nicht zwangsläufig diese Doku. Zweimal ist die Zusage stillschweigend gebrochen worden — ein Feature kam hinzu, der Docstring blieb beim alten Stand. `tests/test_docstrings.py` ist der Wächter dagegen: mechanisch für jedes Kommando und jedes `--Flag` (per Regex aus dem Quelltext gezogen, gegen den eigenen Docstring geprüft), von Hand für Begriffe, die kein Parser findet (Feldnamen, Dateiendungen, Funktionsnamen) — diese Liste muss bei jedem neuen Feature nachgezogen werden, das ist kein Testversehen, sondern der Punkt.

## 2.10 Zielorte

Primärziel ist `<projekt>/.claude/imported_chats/` im versionierten Repo des Zielprojekts. **Dieselben Dateien** dienen unverändert auch dem Projektwissen einer claude.ai-/Desktop-/Cowork-Instanz; es gibt keine zielabhängige Ausgabeform. Ein Verzeichnis je Quellprojekt, **flach** — Projektwissen kennt keine Unterordner. Ein **dritter** Zielort ist `~/.claude/projects/<projekt>/`, für Chats, die nicht ins geteilte Repo dürfen — aber nur auf ausdrückliche Anordnung des Nutzers und nur unter den drei Bedingungen aus 1.3 (hochgesetzte Aufbewahrungsdauer, bewusst erteilte Ausnahme von §1.2 der Arbeitsanweisungen, Kenntnis von `claude project purge`). Ohne diese Anordnung schreibt kein Lauf dorthin.

Diese Vorgabe gilt den **Archivdateien**. Der Anweisungsblock, den `convert` am Ende ausgibt (3.1.6), ist keine Archivdatei, sondern Konsolenausgabe für den Nutzer — er ist bewusst zielabhängig, weil die drei Zielorte sich im Suchmittel und im Einsetzort unterscheiden.

## 2.11 Tests ohne echten Chatinhalt

Prüfstücke werden synthetisch gebaut; echter Chatinhalt gehört nie in Tests oder Fixtures. Echte Exporte liegen ausschließlich unter `test_results/`, deren Inhalte die `.gitignore` vom Repo fernhält. Diagnosewerkzeuge (3.3) geben Struktur und Zahlen aus, nie Inhalt — ihre Ausgabe muss unbedenklich in eine Konversation kopierbar sein.


# 3 Skripte

## 3.1 `chat_export_convert.py` — der Weg über den Kontoexport und über die Web-Endpunkte

**Status: gebaut, geprüft durch `tests/test_export_convert.py`, auch unter `-O`. Am Drei-Monats-Export mit 211 Chats gelaufen.**

Wandelt Chats in Dateien je Quellprojekt um und führt das Protokoll. Läuft lokal, wird nie hochgeladen. Es liegt in `skills/chat-export/` — es ist das eine Skript, das der Skill mitbringt (3.5), und der Ordner trägt genau die Struktur, die er am Zielort haben wird.

**Zwei Quellen, ein Konverter.** Die Chats kommen entweder aus einem Kontoexport-ZIP (`--zip`) oder aus einem **Web-Behälter** (`--bundle`) — der Datei, die ein Browserschritt aus den claude.ai-Endpunkten schreibt. Beide führen dieselben Feldnamen je Konversation, weshalb sich der Unterschied auf das Auspacken beschränkt: Ab `conversation_record()` ist der Code geteilt. Am 19. August 2026 am echten Fall bestätigt — für denselben Chat nannten Web-API und Export-ZIP nicht nur dieselben Zahlen, sondern **dieselben Nachrichten-UUIDs** (Protokoll in `testlauf.md`).

Damit ist die Wegegleichheit (Vorgabe 2.5) hier **baulich** gegeben statt bloß geprüft. Abweichen darf genau ein Feld: Die Chatdatei nennt als Herkunft `web-api` statt `account-export`, und `source` ist eines der fünf erlaubten. Dass sonst nichts abweicht, vergleicht `tests/test_export_convert.py` Datei für Datei — an einem Prüfbestand, der alle drei Nebendateiarten und einen Nebenzweig trägt, damit der Vergleich etwas aussagt.

Die Chatliste des Web-Behälters trägt außerdem `created_at` je Chat. Das ist der Grund, warum `list --web` ohne Sondierungsexport auskommt: Die Fenstergrenze steht exakt in den Daten, statt über den Projektbeginn genähert zu werden (Vorgabe 2.4).

### 3.1.1 Aufbau des Export-ZIP

Alles beobachtet, nichts davon dokumentiert.

```
users.json                    uuid, full_name, email_address, verified_phone_number
projects/<uuid>.json  (n×)    uuid, name, description, is_private,
                              is_starter_project, prompt_template,
                              created_at, updated_at, creator, docs
memories.json
login_history.json            erst im zweiten Export vorhanden, s. u.
conversations.json            Liste von Konversationen
```

**Die Mitgliederliste ist nicht stabil.** `login_history.json` fehlte im Export vom 6. August 2026 und war im Export vom 8. August enthalten — zwei Tage Abstand, gleiches Konto. Der Fund kam von der Schemawache (3.3), die das Archiv gegen diese Liste hält; Konversations-, Nachrichten- und Blockschlüssel waren unverändert, der Zuwachs also harmlos. Folgerung für den Entwurf: Ein Werkzeug darf sich nie darauf verlassen, **welche** Mitglieder ein Archiv hat, sondern nur darauf, dass `conversations.json` darunter ist. Weiteres in 4.2.

Projektdateien enthalten **keine Chats** — nur Projektanweisungen und Wissensdokumente. Die Chats liegen ausschließlich in `conversations.json`.

**Die Projektdateien sind vom Zeitraumfilter ausgenommen, und ihr `created_at` ist der Projektbeginn.** Zwei Exporte mit verschiedenen Zeiträumen enthielten dieselben 43 Projektdateien, jede mit `created_at`, ältestes 2025-06-18 — der Filter wirkt auf `conversations.json`, nicht auf `projects/`. Daraus folgt eine Rechnung, die den Entwurf trägt: **kein Chat eines Projekts kann älter sein als das Projekt**, also ist dessen `created_at` die garantierte Untergrenze für jedes Exportfenster. Gegengeprüft am echten Fall: Projekt `FreeCAD-Bedienung` trägt `created_at` 2025-11-10, und der älteste Chat darin wurde am 2025-11-10 erstellt. Praktische Folge in 1.5: **ein Kurzzeitraum-Export von einer Woche liefert alle Projektdaten** (5 MB statt 58) und damit das Datum, ab dem der eigentliche Export gehen muss.

Eine Konversation hat genau sieben Felder: `uuid`, `name`, `summary`, `created_at`, `updated_at`, `account`, `chat_messages`. **Kein Projektbezug.**

Eine Nachricht: `uuid`, `text`, `content`, `sender` (`human`/`assistant`), `created_at`, `updated_at`, `attachments`, `files`, `parent_message_uuid`.

**`attachments` und `files` sind nicht dasselbe**, und die Verwechslung kostet Inhalt:

| Feld | Zahl | Felder | Inhalt |
| ------------- | ---- | ------------------------------------------------------------- | ------ |
| `attachments` | 341  | `file_name`, `file_size`, `file_type`, **`extracted_content`** | **da** |
| `files`       | 524  | `file_uuid`, `file_name`                                      | fehlt  |

Keiner der 341 ist leer, zusammen 9.635.919 Zeichen, Median 13.265, größter 169.818. Dateitypen überwiegend `text/x-python` (238), dazu `text/markdown` (26), `txt` (22), `x-shellscript` (11). Bei **22** ist der `file_name` leer, der Inhalt aber vorhanden — mehrere Kilobyte Code; ein Fragezeichen als Name würde das verstecken.

**Die beiden Felder sind nicht disjunkt.** Am Testlauf vom 17. August direkt beobachtet: Dieselbe Nachricht führt `test_docstrings.py` zweimal — unter `attachments` mit 4.481 Zeichen `extracted_content` und unter `files` mit `file_uuid` und Namen. Ein angehängtes Bild dagegen steht **nur** unter `files`. Der Export verzeichnet also jeden Upload als Dateiobjekt und legt den extrahierten Text daneben, wenn er einen gewinnen konnte. Am Drei-Monats-Export nachgemessen: 319 der 524 `files`-Einträge haben ihren Inhalt in derselben Nachricht, 205 nicht (Beleglage und Rest in 1.6). Verbindender Schlüssel ist allein der Name — `files` trägt eine `file_uuid`, `attachments` keine —, weshalb die 22 namenlosen Anhänge oben genau die Fälle sind, die sich nicht zuordnen lassen.

Blocktypen in `content`: `text`, `thinking`, `tool_use`, `tool_result`, `token_budget`. Bei `token_budget` war `remaining` in allen Fällen `null`. Nichts war als `truncated` oder `cut_off` markiert.

**Die Blockschlüssel, als Vergleichsgrundlage.** 3.3 verspricht, die Vereinigung aller Konversations-, Nachrichten- **und Blockschlüssel** gegen diesen Abschnitt zu halten; für die dritte Menge fehlte sie bisher. Beobachtet am Testexport vom 17. August 2026, der alle Blocktypen außer `token_budget` enthielt:

```
alternative_display_type, approval_key, approval_key_legacy, approval_options,
citations, citations_grouping_mode, content, context, cut_off, display_content,
flags, hidden, hidden_in_chat, icon_name, id, input, integration_icon_url,
integration_name, is_error, is_mcp_app, mcp_server_url, message, meta, name,
signature, start_timestamp, stop_timestamp, structured_content, summaries, text,
thinking, thinking_hidden, tool_identifier, tool_origin, tool_use_id, truncated,
type
```

Es ist die Vereinigung über **alle** Blocktypen, nicht die Feldliste eines einzelnen: `thinking`, `thinking_hidden` und `summaries` gehören zum Denkblock, `input`, `name` und `tool_use_id` zum Werkzeugaufruf, die `mcp_*`- und `approval_*`-Namen zu dessen neueren Spielarten. Ein **fehlender** Name ist das Warnsignal, ein hinzugekommener meist nur ein Ausbau — dieselbe Lesart wie bei den Archivmitgliedern oben.

**Der Werkzeugverkehr, vermessen.** `tool_result` ist mit 28,6 Mio Zeichen der größte Einzelposten des Exports — 2,5× der Gesprächstext —, aber überwiegend fremd oder redundant: `project_knowledge_search` 9,2 Mio (Treffer aus dem eigenen Projektwissen, also Duplikate vorhandener Doku), `web_search` 8,5 Mio (fremde Snippets), `view` 4,9 Mio (Wiederanzeigen ohnehin erfasster Dateien), `bash_tool` 2,9 Mio (Kommandoausgaben). In `tool_use` (5,9 Mio input) stecken dagegen die **Erzeugnisse der KI**, das Gegenstück zu den Anhängen: `artifacts` create/rewrite/update mit 1,79 Mio Zeichen Inhalt (240 Aufrufe), `create_file.file_text` mit 2,44 Mio (218 Dateien: 88× md, 50× py, 35× json), `str_replace` mit 0,13 Mio Änderungstext — zusammen **4,4 Mio Zeichen**, bei Chats ohne begleitendes Repo die einzige Kopie dieser Werke. Messhinweis: `create_file` trägt den Inhalt im Feld `file_text`, nicht `content`.

**Die Denkschritte, vermessen.** 4.318 `thinking`-Blöcke, Länge Median 682, Mittel 2.153, größter 66.488 Zeichen — keine Statusnotizen. Sie sind auch **nicht redundant**: über 1.840 Nachrichten mit substanziellem Denken *und* sichtbarer Antwort verglichen, taucht nur ein **Median von 9 %** des Denk-Vokabulars in der Antwort wieder auf; in 1.824 Fällen unter 40 %, in keinem über 80 %. **42 %** der Blöcke (1.809) enthalten Abwägungen — Diagnosen, verworfene Alternativen samt Grund, Ursachenlisten. URLs kommen dagegen kaum vor (13 Blöcke), Dateinamen in 1.067.

Das Feld `summaries` (in 3.788 Blöcken, Median 241 Zeichen) ist **keine Zusammenfassung der Schlüsse**, sondern eine Verlaufsmeldung dessen, was gerade durchdacht wird — für ein Archiv wertlos.

**Denken kann dabei sein, muss aber nicht.** Ein Denkblock kommt in zwei Ausprägungen: mit Text, oder als `thinking_hidden` mit null Zeichen. Beide stehen nebeneinander, und das Verhältnis schwankt erheblich — im Drei-Monats-Export 788 versteckte unter 4.318, in den Testexporten vom 17. und 18. August 2026 ausschließlich versteckte, und innerhalb **eines einzigen** Chats wechselte es von Tag zu Tag. Woran es hängt, ist nicht ermittelt und wird hier auch nicht vermutet.

**Ein Export ohne Denktext ist deshalb kein Befund über das Format.** Wer in einem frischen Archiv keine Denkdatei findet, hat eine Stichprobe gezogen, mehr nicht; der Schluss „der Export führt keine Denkschritte" wäre falsch und ist hier schon einmal beinahe gezogen worden. Ist Denktext vorhanden, wird er unverändert genutzt; fehlt er, ist nichts zu holen, und das Verwerfen leerer Blöcke nach 3.1.3 bleibt verlustfrei.

Drei strukturelle Befunde, die die Auswahl tragen (Details der Ableitung in 3.1.3):

| Merkmal                        | Blöcke      | Volumen        | mit Abwägungsmarker |
| ------------------------------ | ----------- | -------------- | ------------------- |
| `thinking_hidden=True`         | 788 (18 %)  | **0 Zeichen**  | 0 %                 |
| kürzer als 200 Zeichen         | 1.367 (32 %)| 71.784 (0,8 %) | 2 %                 |
| Rest (nicht hidden, ≥200)      | 2.951 (68 %)| 9.227.033 (99,2 %) | 60 %            |

Die Medianlänge trennt dabei deutlicher als jedes Verhältnis: mit Marker 2.537 Zeichen, ohne 176 — Faktor 14. Ein `summaries` existiert außerdem **nicht immer** (530 Blöcke ohne), ein Verhältnis wäre für die also gar nicht bildbar.

**Das flache `text`-Feld enthält die Denkschritte.** Gemessen am Drei-Monats-Export: Summe über `text` 20.810.589 Zeichen, Summe der Textblöcke 11.266.956 — die Differenz von 9,5 Mio sind die `thinking`-Inhalte. In einem Beispiel beginnt `text` mit dem Wortlaut des Denkblocks, während der erste Textblock nur ein Leerzeichen enthält. Das eigentliche Gesprächsvolumen ist also **11,3 Mio Zeichen**, nicht 20,8. Wer `text` nimmt, schreibt Claudes interne Überlegungen ins Archiv; wer die Textblöcke nimmt, bekommt das Gesagte. Auch die Blockreihenfolge ist nicht schematisch — beobachtet wurde `['text', 'thinking', 'text']` —, weshalb die Textblöcke in ihrer Reihenfolge aneinandergehängt werden und nicht etwa „alles nach dem Denken".

### 3.1.2 Der Nachrichtenbaum

Die Nachrichten eines Chats bilden **keine Kette, sondern einen Baum**: jede zeigt per `parent_message_uuid` auf ihre Vorgängerin. Hängen an *einer* Vorgängerin mehrere Nachrichten, gabelt sich der Chat — weil eine Frage nachbearbeitet, eine Antwort neu erzeugt oder eine Nachricht mehrfach gesendet wurde.

Befund am Drei-Monats-Export: **20 Gabelungen in 13 von 211 Konversationen.** Kein Randfall.

**Regel 1: Gefolgt wird dem Pfad zur neuesten Nachricht im ganzen Baum** — nicht dem jüngsten Kind an der Gabelung. Die beiden Regeln fallen fast immer zusammen, aber nicht immer, und der Unterschied kostet Inhalt. Gegenbeispiel aus „Home-Verzeichnis zurück synchronisieren":

| Kind | Zeit | Nachfahren |
| --------- | -------- | -------------- |
| `019efe1f` | 09:31:50 | **29** |
| `019efe20` | 09:33:55 | 1 |

Hier trägt das **ältere** Kind das Gespräch. „Jüngstes Kind" hätte 29 Nachrichten weggeworfen und eine Sackgasse ins Archiv geschrieben. Der Pfad zur neuesten Nachricht greift in allen 20 Fällen richtig.

**Regel 2: Verworfene Zweige kommen mit, in ein eigenes Feld — außer wenn ihr Text mit dem gewählten Geschwister identisch ist.** Was in den verworfenen Zweigen steckt, zeigen dieselben Daten:

- **Meist Dubletten.** Bei „Dell DA300 Dockingstation" hängen **14 Kinder** an derselben Stelle, alle mit **exakt 440 Zeichen**, im Abstand von Sekunden bis Minuten — ein Sende-Sturm. Ebenso 10× 37 Zeichen und 5× 553 Zeichen in anderen Chats. Ohne die Ausnahme in Regel 2 stünden allein dort 13 Kopien derselben Nachricht im Archiv.
- **Manchmal Fehlversuche.** Bei „Negativform Bajonett-Kurven" zwei Assistant-Kinder: eines mit **0 Zeichen**, eines mit 41.077. Das leere ist eine fehlgeschlagene Antwort.
- **Selten echter Inhalt.** Bei „Technische 2D-Zeichnung" sind die verworfenen Kinder 113 und 149 Zeichen — umformulierte Fragen, inhaltlich redundant. Im Gegenbeispiel oben hängen am verworfenen Zweig zwei echte Nachrichten.

Deshalb mitnehmen statt zählen: Das Ziel des Archivs ist Wiederfinden, nicht die Rekonstruktion des Gesprächsverlaufs. Wer sucht, will den Satz finden, egal auf welchem Zweig er stand. Eine bloße Zahl („1 Zweig verworfen") verschweigt, ob darin zwei oder vierzig Nachrichten lagen.

### 3.1.3 Festlegungen und ihr Grund


| Festlegung                                             | Grund                                                                                                                                                                                                              |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Baum ablaufen statt nach`created_at` sortieren, Regeln in **3.1.2** | Sortieren nach Zeit schreibt nachbearbeitete Fragen doppelt ins Transkript und mischt Zweige, die nie aufeinander folgten |
| `content`-Blöcke statt `text`                         | `text` **enthält die Denkschritte** (Messung in 3.1.1) — es zu verwenden würde das Archiv mit internen Überlegungen fluten                                                                                                |
| Hüllen mit`deleted: true` und ohne `messages`         | Die Existenz bleibt erhalten, ohne ein leeres Transkript vorzutäuschen                                                                                                                                            |
| Zuordnung aus rohem`recent_chats`-Dump                 | Kein Formatieren von Hand nötig                                                                                                                                                                                   |
| Jede zugeordnete UUID gegen das ZIP prüfen            | Ein vertippter Wert würde einen Chat still falsch einordnen                                                                                                                                                       |
| Denkschritte und Anhänge in eigene Dateien nach Vorgabe **2.2** | Diagnosen und verworfene Alternativen erreichen die Antwort nie (9 % Vokabelüberlappung, Messung 3.1.1); getrennt gelegt bleibt das Gespräch schlank und die Mengenentscheidung fällt bei der Benutzung |
| Denkblöcke verwerfen, wenn`thinking_hidden` oder kürzer als 200 Zeichen | Verlustfrei bzw. nahezu: die hidden-Blöcke sind leer, die kurzen tragen 0,8 % des Inhalts und nur 2 % von ihnen einen Marker. Ein Drittel der Einträge fällt weg, das Volumen bleibt — Filtern schafft Ordnung, nicht Platz. Auswahl strukturell nach Vorgabe **2.7**; die Marker waren nur der Prüfmaßstab |
| Erzeugnisse in die vierte Datei, `tool_result` nur zählen | Die Auswahl ist strukturell (Werkzeugname + Feld, Vorgabe 2.7): `artifacts`-, `create_file`- und `str_replace`-Aufrufe tragen die Werke der KI (4,4 Mio Zeichen, Messung 3.1.1) — oft die einzige Kopie. `tool_result` (28,6 Mio) ist überwiegend fremd oder Duplikat und bliebe Ballast. Änderungen (`update`, `str_replace`) sind Deltas ohne Basis und werden als solche gekennzeichnet |

Das Ersetzen eines veralteten Chats samt Aufräumen der Vorgängerdateien ist Vorgabe **2.6**; beide erzwingenden Fälle — Umbenennung, wegfallende Nebendatei — sind dort benannt und hier nachgestellt worden.

**Hüllen erkennen:** Nachrichten vorhanden, aber `text` und `content` leer. Das sind gelöschte Chats — im Browser gegengeprüft, sie existieren nicht mehr. Der Zeitstempel unterscheidet zwei Löschwege: bei einer Massenlöschung tragen mehrere Chats sekundengleich dasselbe `updated_at`, bei einzeln gelöschten folgt es der eigenen letzten Nachricht. Der Unterschied ist unerklärt und praktisch belanglos.

**Das Löschen nimmt den Inhalt, nicht den Eintrag.** Am eigenen Testlauf nachgestellt: Zwei Chats wurden gelöscht, der Export **danach** angefordert — beide standen darin, mit Gerüst und null Zeichen Text. Anthropic sagt zu, gelöschte *Inhalte* kämen nicht in später angeforderte Exporte, und genau das trifft zu (1.6); der Eintrag selbst bleibt. In die Chatliste kommen sie dagegen nicht mehr, weshalb kein Lauf sie einem Projekt zuordnen kann — eine Hülle im Archiv entsteht also nur für einen Chat, der **zwischen** Listenabgleich und Export gelöscht wurde.

### 3.1.4 Dateiformat der Chatdateien

Format, Felder, Dateinamen und die Referenzmechanik sind die Vorgaben **2.2** und **2.3**; hier steht nur, was dieser Weg davon besonders macht.

Der ZIP-Weg ist der einzige, der `branches`, `dropped_duplicates`, `dropped_blocks`, `dropped_thinking` und die beiden `attachments_*`-Felder je mit Inhalt füllen kann — nur er sieht den Nachrichtenbaum und die Blockstruktur (2.5). Beim Drei-Monats-Export entstanden so 211 Gesprächs-, 145 Denk-, 62 Anhang- und 71 Erzeugnisdateien.


### 3.1.5 Aufbau des Protokolls

Das Protokoll ist Vorgabe **2.4**. Dieser Weg füllt weder `end_token` (das kennt nur der Lese-Weg) noch `total_turns` (er hat kein Sollmaß, 2.5) und benutzt `started` nie — er schreibt einen Chat immer ganz.


### 3.1.6 Kommandos

- `list --map <dump> | --web <behälter> --out <verzeichnis>` — Protokoll anlegen oder ergänzen aus einer Chatliste. `--map` nimmt den rohen `recent_chats`-Abzug, `--web` die Liste aus dem Web-Behälter; letztere bringt `created_at` je Chat mit und macht damit den Sondierungsexport entbehrlich. Fehlt beides, bricht der Aufruf ab. Neue Chats `listed`, vorhandene gegen `exported_updated_at` geprüft und ggf. `stale`. Meldet die Fenstergrenze (Vorgabe 2.4) und warnt vor einem unplausiblen Projektdatum. Meldet außerdem den umgekehrten Fall — Chats, die das Protokoll kennt und die Liste nicht mehr führt (Vorgabe 2.4); entfernt wird dabei nichts. **Der erste Schritt jedes Laufs**, vor jedem Chattext.

  Der Rohtext für `--map` kommt nicht von hier: er entsteht in einem Chat des Quellprojekts über das dort eingebaute `recent_chats` — und zwar in einem eigens dafür angelegten, danach gelöschten Chat, weil der laufende Chat in seiner eigenen Liste fehlt (Begründung in 1.5). `MAPPING_PROMPT` (Modulkonstante, siehe Docstring) ist der dafür wörtlich vorgegebene Prompt — nur im Codeblock ausgegeben bleibt er intakt, sonst verschluckt der Markdown-Renderer die `<chat>`-Tags als HTML (beobachtet).
- `convert --zip <datei> | --bundle <datei> --out <verzeichnis>` — die als `listed` oder `stale` geführten Chats aus der angegebenen Quelle holen, Baum ablaufen, Dateien schreiben, Protokoll fortschreiben. **Genau eine** Quelle, nie beide: Zwei Angaben oder keine bricht mit einer Meldung ab, statt sich eine auszusuchen.

  Der **Web-Behälter** ist eine JSON-Datei mit zwei je nach Schritt gefüllten Teilen — `conversations` mit den Kopfdaten je Chat für `list --web`, `chats` mit den vollständigen Konversationen für `convert --bundle`; dazu `fetched_at` und `organization` als Herkunftsvermerk. Gelesen von `load_bundle()`, ausgepackt von `bundle_records()` und `bundle_conversations()`. Ein Behälter ohne den gebrauchten Teil bricht mit einer Meldung ab und rät nicht.
- `diff --out <verzeichnis>` — Stand aus dem Protokoll: fehlend, veraltet, gelöscht, unbekannt. Braucht weder ZIP noch Chatdateien. Dazu **die Fenstergrenze** (Vorgabe 2.4) samt der Warnung vor einem unplausiblen Projektdatum — dieselben Sätze, die `list` ausgibt, hier aber ohne frische Chatliste: „was fehlt noch" und „wie weit muss der nächste Export zurückreichen" sind eine Frage, zweimal gestellt. Dazu der Waisen-Scan nach Vorgabe 2.6 — das Einzige, was ein Zuviel statt eines Zuwenig meldet.
- `report --out <verzeichnis>` — was ein bestehender Bestand an Verlusten trägt: Hüllen, übersprungene Dubletten, weggelassene Blocktypen, verworfene Denkblöcke, `files`-Verweise ohne Inhalt. Was mitkam, steht als Gegengewicht daneben — Nebenzweige, Denkblöcke, Anhänge mit Inhalt, Erzeugnisse —, damit sichtbar ist, dass ein Chat nicht linear verlief bzw. wie viel an ihm hing. Die behaltenen Denkblöcke werden dabei aus den Nebendateien gezählt: die Gesprächsdatei führt nur die verworfenen, und ein zusätzliches Metadatenfeld dafür würde das Dateiformat beider Wege ändern (Vorgaben 2.2 und 2.5) — zu viel für eine Berichtszeile.

- `analyse --zip <datei> [--map <dump>]` — beschreibt, was der Leser aus einem Archiv macht, ohne etwas zu schreiben: gewählter Pfad, Nebenzweige, Umfang, und bei gegebener Zuordnung die UUIDs, die das Archiv nicht kennt. Es nennt **beide Seiten** — was mitkäme (Denkblöcke, Anhänge mit Inhalt, Erzeugnisse) und was wegfiele (verworfene Denkblöcke, Blocktypen, Hüllen, Sendewiederholungen, Namensverweise). Beantwortet eine andere Frage als 3.3 — das beschreibt den Rohexport, dieses die *Deutung*.

Der Unterschied zu `report` ist die Blickrichtung, nicht der Inhalt: `report` läuft über einen **fertigen Bestand**, `analyse` über das **ZIP** und schreibt nichts — es ist die Vorschau vor dem Lauf. Beide nennen deshalb dieselben Posten, und dass sie dieselben Zahlen liefern, sichert `tests/test_export_convert.py` über drei Prüfbestände ab. Der Grund für die Absicherung ist eine erlebte Drift: Anhänge kamen zuerst, Denkschritte und Erzeugnisse später, `report` wurde nachgezogen und `analyse` nicht — die Vorschau verschwieg damit zwei der drei Nebendateiarten und mit ihnen den größten mitgenommenen Posten überhaupt (Denkschritte, 9,2 Mio Zeichen gegen 9,6 der Anhänge und 4,4 der Erzeugnisse, Messung in 3.1.1).

Dazu ein fertig einfügbarer Textblock für das **Zielprojekt**: dass ein Chatarchiv vorliegt, wo es liegt, und dass es vor einer Rückfrage zu älterem Zusammenhang zu konsultieren ist. Damit wirkt die Anweisung dauerhaft — er ist die einzige Stelle, an der dieses Werkzeug im Zielprojekt fortwirkt; ohne ihn liegt das Archiv da und wird nie gelesen.

**Drei Fassungen, weil die Zielorte sich in genau dem unterscheiden, was der Block sagen soll** — wo das Archiv liegt und womit die Instanz es erreicht (1.3). Gewählt wird über `convert --target`; es steuert **nur** den Wortlaut, nicht eine geschriebene Datei (Vorgabe 2.10).

| `--target` | Zielort | Suchmittel | einzusetzen in |
| --- | --- | --- | --- |
| `repo` (Vorgabe) | `<projekt>/.claude/imported_chats/` | `Grep` und `Read` | die `CLAUDE.md` des Zielprojekts |
| `knowledge` | Projektwissen einer claude.ai-Instanz | Projektwissen bzw. Kontext | die Projektanweisungen dort |
| `home` | `~/.claude/projects/<projekt>/` | `Grep` und `Read` | die `CLAUDE.md` des Zielprojekts |

Die `home`-Fassung trägt zusätzlich die Zugänglichkeitsbedingung aus 1.3 und die Anweisung, ihr Fehlen zu melden statt das Archiv für leer zu halten.

**Nicht** in eine `CLAUDE.md` unterhalb von `.claude/imported_chats/`: Eine solche Datei lädt erst, wenn dort schon gelesen wird, und überlebt keine Kompaktierung — sie wäre genau dann stumm, wenn sie gebraucht wird (Begründung in der Repo-`CLAUDE.md`).

**Pfad und Dateiarten kommen aus dem Lauf**, nicht aus einer festen Liste: der Pfad aus `--out`, die genannten Nebendateien aus den `side_files` des Protokolls. Ein Lauf ohne Anhänge kündigt keine `.attachments.json` an — sonst suchte die Instanz nach etwas, das es nicht gibt.

### 3.1.7 Prüfung

- **Wegegleichheit:** `tests/test_wegegleichheit.py` — der Wächter der Vorgabe 2.5. Stellt dieselbe Konversation beiden Wegen hin und vergleicht Dokument gegen Dokument, dann Datei gegen Datei über die zwei Kommandozeilen; prüft, dass genau die fünf erlaubten Metadatenfelder abweichen und dass nach Entfernen der Referenzfelder zwei identische Transkripte bleiben.
- Synthetisches ZIP als Prüfstück: Verzweigung, abweichendes `text`, Hülle, null Nachrichten, Dateiverweise, alle Blocktypen — ohne echten Chatinhalt (Vorgabe 2.11).
- `diff` gegen einen Bestand mit bekannter Lücke und einem veralteten Chat.
- Vertippte UUID in einer Zuordnungsdatei wird gemeldet, nicht verschluckt.
- **Integrität:** jede Nachricht landet auf dem gewählten Pfad, in einem Nebenzweig oder in der Dublettenzählung. Am Drei-Monats-Export: 7.393 im Export, 7.393 abgelegt oder gezählt.
- Lauf gegen ein echtes ZIP: **erledigt**. 211 Chats in gut einer Sekunde, 37 MB — davon 13 MB Gespräch, 9,9 MB Denkschritte, 9,9 MB Anhänge, 4,9 MB Erzeugnisse; 211 Gesprächs-, 145 Denk-, 62 Anhang- und 71 Erzeugnisdateien. Die Verteilung bestätigt die Rechnung aus Vorgabe 2.2 am geschriebenen Ergebnis: Wer nur das Gespräch liest, trägt gut ein Drittel statt des Ganzen. Alle Summen deckungsgleich mit unabhängig gemessenen: 5 Hüllen, 29 Sendewiederholungen, 1.367 verworfene Denkblöcke, 18 Nebenzweige, 341 Anhänge mit Inhalt, 524 reine Namensverweise.
- Lauf gegen ein **Quellprojekt**: das FreeCAD-Projekt mit 22 Chats, aus **zwei** ZIPs verschiedener Zeiträume zu einem Verzeichnis zusammengeführt. Die Stichprobe hat der Nutzer inhaltlich abgenommen — der bislang einzige Beleg, dass ein Mensch das Ergebnis auf Inhalt und nicht nur auf Zahlen geprüft hat.

### 3.1.8 Offen

- **Gehört die Projektzuordnung in die Chatdatei oder nur in den Verzeichnisbaum?** Offene Entwurfsfrage, aus dem Vorhandenen nicht entscheidbar: Sie braucht den Kontext eines echten Ablaufs. Sinnvoll am mehrstufigen Test zu klären, der beide Varianten praktisch vorführt.

## 3.2 `chat_read_store.py` — der Weg über `read_conversation`

**Status: gebaut und geprüft durch `tests/test_read_store.py`, auch unter `-O` — aber nicht lauffähig.** Das Werkzeug, auf dem der ganze Weg ruht, wird von claude.ai nicht mehr angeboten; Datum, Nachweis und Tragweite stehen in 1.2. Ohne es gibt es keinen Einstieg: Das Skript liest nichts selbst, es verarbeitet, was eine Instanz ihm hereinreicht.

**Was der Weg lieferte.** `read_conversation` gab das **gerenderte Transkript** eines Chats, nach Turns durchnummeriert und seitenweise geblättert — keine Blockstruktur. Daraus folgt, was ihm fehlte, und zwar aus der Quelle und nicht aus der Umsetzung: **Denkschritte** und **Anhänge**, im Kontoexport zusammen etwa so viel wie der Gesprächstext selbst (Messungen in 3.1.1). Ein über diesen Weg geholter Chat blieb dauerhaft ärmer, und ein späterer Export ergänzt ihn nicht — er kann ihn nur ersetzen, weil sich der Bezug zwischen Nachricht und Block nachträglich nicht herstellen lässt. Darauf ruhen die erlaubten Abweichungen in Vorgabe 2.5 und die gekippte Annahme in 1.7.

Dafür konnte er dreierlei, was der Export nicht kann: **Vollständigkeit beweisen** — die gehaltenen Turn-Indizes gegen ein Sollmaß aus der Quelle —, **sofort** liefern, ohne Antrag und Wartezeit, und er war **vom Kontotyp unabhängig**, weil er keinen Export brauchte. Der letzte Punkt wiegt am schwersten: Für ein gewöhnliches Mitglied eines Team- oder Enterprise-Kontos war er nicht der bequemere, sondern der einzige Weg (1.2, 1.6).

**Kommandos:** `plan`, `overview`, `state`, `map`, `ingest`, `status`, `export`. Zwei Eigenheiten sind Entwurf und nicht Zufall, und beide gelten unabhängig davon, welches Werkzeug die Turns beschafft. **`plan` schreibt nichts und entscheidet nichts** — es legt die Lage vor, nennt für Chats ohne bekannten Umfang deren Anzahl statt einer erfundenen Turn-Zahl und überlässt die Wahl dem Nutzer. Und ein Chat, den die frische Liste nicht mehr führt, wird **gemeldet und nie automatisch entfernt**, auch dann, wenn sonst nichts ansteht (Vorgabe 2.4). `map` ist der Zulieferer der Projektzuordnung und unterliegt derselben Regel wie `list` im ZIP-Weg: Die Chatliste wird in einem eigens angelegten, danach gelöschten Chat geholt (1.5). Die Statusführung folgt Vorgabe 2.4; `started` und `deleted` setzt nur dieser Weg.

**Warum Skript und Tests trotzdem liegen bleiben.** Sie halten die **zweite Umsetzung** des Dateiformats, und daran hängt Vorgabe 2.5: `tests/test_wegegleichheit.py` stellt beiden Wegen dieselbe Konversation hin und vergleicht Chatdateien wie Protokolle. Fiele die zweite Seite weg, wäre die Vorgabe unprüfbar und der ZIP-Weg das einzige Maß seiner selbst. Entsteht je ein zweiter Weg, erbt er Format, Protokollmechanik und Kommandoschnitt, statt sie neu zu erfinden. Ob das Werkzeug zurückkehrt, wird als Beobachtung geführt (4.3).

## 3.3 `inspect_export.py` — Diagnose eines Export-ZIP

**Status: gebaut, eigener Selbsttest, auch unter `-O`.** Die Scratchpad-Fassung ging beim Sitzungswechsel verloren und wurde aus dem Verlauf rekonstruiert — der Beleg, dass flüchtige Ablagen keine Werkzeuge halten.

Liest ein Kontoexport-ZIP ohne zu entpacken und berichtet Struktur und Zahlen, **nie Chatinhalt** (Vorgabe 2.11 — der Selbsttest weist mit Markertexten nach, dass nichts davon in der Ausgabe erscheint; Titel erscheinen bewusst, sie identifizieren die Chats). Aufruf: `inspect_export.py <export.zip>`.

Prüft: Archivinhalt; **die Projekte nach Erstellungsdatum** — das ist der Zulieferer für `--project-created` (Vorgabe 2.4), und der Grund, warum ein Sondierungsexport genügt; Anzahl, Zeitraum und Umfang der Konversationen; ausgehöhlte Konversationen samt der Löschungs-Erklärung aus 3.1.3; Verzweigungen je Chat; Blocktypen und Wahrheitsflaggen; die `text`-Blöcke-Abweichung (das flache Feld trägt die Denkschritte); **`attachments` mit `extracted_content` getrennt von reinen Namensverweisen** — der Prüfpunkt aus 4.2; und als Schemawache die Vereinigung aller Konversations-, Nachrichten- **und Blockschlüssel** zum Vergleich mit 3.1.1.

Es beantwortet eine andere Frage als `analyse` (3.1.6): dieses beschreibt den Rohexport, jenes die Deutung.

## 3.4 `chat_crawl_store.py` — Rekonstruktion aus Suchschnipseln

**Status: gebaut, geprüft durch `tests/test_crawl_store.py`. Zukunft offen — Fahrplan 10.**

Rekonstruiert Chats aus überlappenden Suchschnipseln, für Umgebungen ohne `read_conversation`.

**Warum überholt:** Am echten Lauf zeigte sich, dass `conversation_search` **feste, nicht überlappende Blöcke** liefert — zwischen 23 Segmenten dreier Chats gab es null Overlap. Die Overlap-Mechanik, das Herz des Skripts, hat damit fast nichts zu verbinden: der Crawl sammelt Text, ohne ihn zusammenzusetzen.

**Was daran gültig bleibt** und in 3.2 übernommen wurde: Zustandsdatei mit Status und Bearbeitungsrichtung, Rundenbegriff, Übergabeprozedur, Transkriptionsdisziplin, Upload-Probe.

Erhaltenswerte Einzelbefunde: Suchtreffer tragen `H: `/`A: `-Label und HTML-Entities; ein Auslassungszeichen wird nur als Lückenmarke erkannt, wenn es zwischen zwei Nicht-Leerzeichen klemmt — `abc ... def` und eine einzelne `...`-Zeile landen ohne jede Warnung im Transkript.

**Zwei Befunde haben seine Grundlage weiter untergraben.** Der Satz, der es einst außer Dienst stellte — „überholt, wo `read_conversation` existiert" — ist gegenstandslos, weil es dieses Werkzeug nirgends mehr gibt. Nach dieser Logik wäre der Crawler das einzige verbliebene Werkzeug; dagegen steht aber die Beobachtung vom 18. August, dass `conversation_search` bei einem Chat mit zehn Turns eine **Zusammenfassung** statt Schnipsel lieferte. Wer eine Zusammenfassung einliest, archiviert eine Nacherzählung und verstößt gegen Vorgabe 2.8. Ob das Skript bleibt, Ersatzteillager an Befunden wird oder ersatzlos entfällt, entscheidet Fahrplan 10; bis dahin bleibt es unangetastet und liegt bei den Tests, die es allein noch anfassen.

## 3.5 Der Skill `chat-export` — das Frontend

**Status: `SKILL.md` geschrieben, noch nicht am echten Lauf erprobt.** Die README steht aus.

Der Skill ist die Klammer um das Skript: Er führt den Nutzer durch beide Wege, ohne ihm die Entscheidung abzunehmen. Er liegt in `skills/chat-export/` und enthält genau zwei Dateien — `SKILL.md` und `chat_export_convert.py`. **Das ist alles, was ein Nutzer kopiert**; die übrigen Skripte dieses Ordners gehören zur Entwicklung und kommen in der `SKILL.md` nicht vor.

Zwei Festlegungen tragen den Entwurf, und beide stehen dort normativ:

- **Die Instanz deutet und ordnet zu, das Skript zählt und vergleicht.** Projektnamen mit Tippfehlern auf die echte Liste abbilden oder auf „zeig mir einfach alle" sinnvoll reagieren — das kann eine Instanz besser als jedes Skript. Aufsummieren kann sie nicht verlässlich (1.4). Der Ablauf folgt dieser Trennung durchgehend.
- **Genau zwei Haltepunkte.** Einer vor dem ersten Abruf, der alles Lesende abdeckt; einer nach der Statistik für die Wahl des Wegs. Der Hinweis danach nennt die Zahl der zu ersetzenden Chats und zu entfernenden Dateien, weil das Löschen ist. Der Anweisungsblock für die `CLAUDE.md` wird deshalb Schlussbemerkung statt Frage — sonst entstünde ein dritter.

**Voraussetzungen, die der Nutzer herstellen muss** und die der Skill nicht umgehen kann: angehängte Browser-Werkzeuge (in der VS-Code-Erweiterung `@browser` je Nachricht), ein laufender und bei claude.ai angemeldeter Chrome mit eingeschalteter Erweiterung, und in Chrome ausgeschaltetes Nachfragen nach dem Speicherort — ein Dateidialog blockiert die Anbindung vollständig. Die Kontobindung ist dabei **keine** Bedingung: Chrome und Claude Code dürfen an verschiedenen Konten hängen (belegt, `chrome-zugriff.md`). Was der Skill sieht, ist immer die Sitzung, die im Tab gerade aktiv ist — deshalb **nennt** er das erkannte Konto, statt eines vorauszusetzen.

Das angestrebte Verhalten ist als Nutzerdurchgang in `Zielvorlage.md` beschrieben; die Mechanik der Browser-Anbindung samt ihrer Fallstricke in `chrome-zugriff.md`. Beide sind befristet und gehen in die Anwenderdokumentation über, sobald der Skill erprobt ist.

---

# 4 Projektpflege — Anthropic-Entwicklung

Anthropic baut an Export, Werkzeugen und Plattform laufend um; nichts hiervon ist zugesichert, das meiste nur beobachtet (2.1). Dieses Kapitel ist die **Prüfliste**: alles, was regelmäßig zu kontrollieren ist, gesammelt an einem Ort.

**Was hier steht und was nicht.** Kapitel 4 sagt, **was zu prüfen ist und wie**. Die Festlegung selbst hat ihr normatives Zuhause anderswo und wird hier nur so knapp wiedergegeben, dass die Liste für sich lesbar bleibt; bei Widerspruch gilt die verlinkte Stelle, nicht die Wiedergabe. Verfahren, die drei Prüfarten und die Übersicht über alle Punkte stehen in 4.1.

## 4.1 Verfahren und Übersicht

**Ziel:** Ein Satz kleiner Prüfwerkzeuge, mit denen sich vor einem Lauf schnell feststellen lässt, ob **(a)** das Kontoexport-Format, **(b)** die internen Web-Endpunkte und **(c)** die Werkzeugschnittstellen der Claude-Instanz (`recent_chats`, `conversation_search`) noch den hier dokumentierten Beobachtungen entsprechen — als Frühwarnung, bevor eine Änderung still Falsches produziert. Der Web-Weg ist dabei der empfindlichste: undokumentiert und ohne Ankündigung änderbar.

Vorhandene Bausteine: `inspect_export.py` (3.3) als Schemawache des Exports, dazu die Format- und Upload-Proben in den Docstrings von 3.2 und 3.4. **Die Lücke ist die warme Seite:** Für den Export gibt es ein Werkzeug, für die Instanzschnittstellen nur Proben von Hand. Das bleibt das offene Ziel dieses Abschnitts.

**Das Profil des Testprojekts.** Für die warme Seite gibt es kein Werkzeug, aber eine **Prüfvorlage**: ein eigens angelegtes claude.ai-Projekt, dessen Inhalt bewusst gewählt ist. Zwei Randbedingungen stehen dabei gegeneinander. Es muss **klein** bleiben — ein kleiner Export ist schneller da, und jedes Merkmal muss von Hand erzeugt werden. Und es muss trotzdem **jedes strukturelle Merkmal** tragen, auf das der Code reagiert: Ein fehlendes Merkmal lässt seinen Codeweg ungeprüft, ohne dass es auffällt — der Lauf meldet dann nicht etwa eine Lücke, sondern schlicht nichts.

Das Profil steht hier und nicht im Fahrplan, weil es sich nicht verbraucht: Nach jeder Anthropic-Änderung, die eine Prüfung aus 4.2 oder 4.3 anschlagen lässt, wird dieselbe Vorlage wieder gebraucht. Es ist eine Prüf**vorlage**, kein Prüf**punkt** — die Übersicht weiter unten führt die Punkte, hier steht das Material, an dem man sie durchspielt.

| Merkmal | Wie es entsteht | Was es prüft |
| --- | --- | --- |
| Gabelung | eine bereits gestellte Frage nachträglich bearbeiten | Baumlauf und Regel 1 (3.1.2) — **erprobt**, erzeugt zuverlässig einen Nebenzweig |
| Anhang mit Inhalt | eine **Textdatei** hochladen (`.py`, `.md`) | `attachments` mit `extracted_content` (3.1.1) — **erprobt** |
| reiner Namensverweis | ein **Bild** hochladen | `files` ohne Inhalt (1.6) — **erprobt**: Bilder werden nicht textextrahiert |
| Denkschritte | eine Aufgabe, die **wirklich** Abwägung erzwingt — mehrere Ansätze unter Nebenbedingungen gegeneinander stellen und die Wahl begründen lassen; dazu eine banale Frage für den kurzen Block | Denkdatei und die Schwellen aus 3.1.3 |
| Erzeugnis | ausdrücklich ein **Artefakt** erstellen lassen und danach ändern | Creations-Datei (3.1.3) |
| Sendewiederholung | **kein bekanntes Rezept** — s. u. | Dublettenerkennung, Regel 2 (3.1.2) |
| Hülle | einen Chat anlegen und wieder löschen | Erkennung gelöschter Chats (3.1.3) |
| langer Chat | einer mit vielen Nachrichten | Baumlauf über eine lange Kette und die Integritätsrechnung (3.1.2, 3.1.7) |
| wachsender Chat | einer, der Tage später fortgesetzt wird | `stale`, Ersetzen (2.6) und die Fensterrechnung (2.4) |

Die Zeile zum wachsenden Chat ist die einzige mit Vorlaufzeit: Der Zeitraumfilter des Exports arbeitet auf Tagesebene, also muss zwischen Anlegen und Fortsetzen mindestens ein Tageswechsel liegen.

**Die Rezepte für Denkschritte und Erzeugnis sind bereits einmal fehlgeschlagen** — zu leichte Fragen, und ein Chat über Bildgenerierung, der keinen der drei Werkzeugnamen aus 3.1.3 erzeugt. Beide Lehren stehen oben in der Tabelle; deshalb ist sie dort so ausführlich formuliert.

**Für die Sendewiederholung gibt es kein Rezept.** Zwei identisch abgeschickte Nachrichten stehen als Eltern und Kind hintereinander, der Code sucht aber **Geschwister ohne Nachfahren** an einer Gabelung. Belegt ist das Phänomen nur aus echten Daten (14 Kinder mit je 440 Zeichen, 3.1.2); herstellen konnten wir es nicht. Dieser Codeweg bleibt damit ungeprüft — ausdrücklich vermerkt statt stillschweigend als abgedeckt geführt.

**Drei Prüfarten.** Jeder Punkt trägt genau eine:

- **kalt** — prüfbar mit dem, was auf der Platte liegt: die heruntergeladenen Export-ZIPs unter `tests/test_results/` und ein Arbeitsordner. Kein Netz, kein Konto, kein fremder Zustand; beliebig oft wiederholbar.
- **warm** — nur mit Zugriff auf ein echtes Projekt: ein claude.ai-Projekt für `recent_chats`, `conversation_search`, Upload und Projektwissen, oder ein Claude-Code-Projekt als Zielort. Braucht Vorbereitung, ist nicht beliebig wiederholbar und hinterlässt Spuren an der Quelle.
- **Beobachtung** — nicht prüfbar, nur bemerkbar, wenn es kippt: Die Sache ist undokumentiert und durch keinen Versuch auslösbar. Sie „warm" zu nennen verspräche eine Prüfung, die es nicht gibt.

Ein warmer Punkt kann **mangels Rechten unerreichbar** sein, ohne deshalb eine Beobachtung zu werden: Er wäre prüfbar, nur nicht von uns. Das wird dazugeschrieben statt stillschweigend umgewidmet — sonst sieht ein späterer Leser eine Prüfung, die nie jemand vorhatte durchzuführen.

**Was eine Prüfung ist.** Drei Teile: was man tut, woran man erkennt, dass die dokumentierte Aussage noch stimmt, und was folgt, wenn nicht. Der letzte Teil ist immer derselbe — betroffene Zeile in 1.6 bzw. Kapitel 3 korrigieren, prüfen, was daran hing, und wenn eine Annahme fällt, 1.7 ergänzen. Ein Punkt ohne erkennbares Kriterium ist keine Prüfung, sondern eine Beobachtung.

**Übersicht.** Alle Punkte mit ihrem normativen Zuhause und ihrer Art — bewusst nur Zeiger, damit diese Tabelle nicht neben den Abschnitten herdriften kann:

| Prüfpunkt | Zuhause | Art |
| --- | --- | --- |
| Verfügbarkeit des Exports je Kontotyp | 4.2, 1.6 | warm |
| Aufbau des Organisationsexports (Primary Owner) | 4.2 | warm, mangels Rechten unerreichbar |
| Zeitraumauswahl des Exports | 4.2 | warm beim Anfordern, danach kalt |
| Zeitraumgrenze wirkt auf `created_at`, nicht `updated_at` | 4.2 | kalt |
| Projektdateien vom Zeitraumfilter ausgenommen | 4.2 | kalt |
| Archivmitglieder und Schlüsselmengen | 4.2, 3.1.1 | kalt |
| `attachments` mit Inhalt gegen `files` ohne | 4.2, 3.1.1 | kalt |
| Hüllen gelöschter Chats | 4.2, 3.1.3 | kalt |
| Bekommt eine Konversation je einen Projektbezug? | 4.2, 1.6 | kalt |
| Stückelung großer Exporte (`batch-0000`) | 4.2 | Beobachtung |
| Web-Endpunkte: Pfade, Felder, Paginierung | 4.3, 1.2 | warm |
| Bleibt der Browser-Zugriff ohne Captcha-Prüfung möglich? | 4.3 | warm |
| Chatliste über `recent_chats` | 4.3 | warm |
| Übergeht `recent_chats` weiterhin den laufenden Chat? | 4.3, 1.6 | warm |
| Wird `read_conversation` wieder angeboten? | 4.3, 3.2, 1.2 | Beobachtung |
| Blockverhalten von `conversation_search` | 4.3, 3.4 | warm |
| Gibt es für `files` einen Abrufweg? | 4.3, 1.6 | warm |
| RAG-Schwelle des Projektwissens | 4.4 | Beobachtung |
| Container-Allowlist ohne `claude.ai` | 4.4 | warm |
| Räumt die Aufräumung fremde Dateien in `~/.claude/projects/` mit weg? | 4.4, 1.3 | kalt |
| Was nimmt `claude project purge` mit? | 4.4, 1.3 | kalt, destruktiv |
| Cowork über beide Wege unerreichbar | 4.4, 1.6 | Beobachtung |

## 4.2 Kontoexport — was verwendet wird und zu prüfen ist

- **Wer überhaupt exportieren darf, hängt am Kontotyp** (1.6): Selbstbedienung nur auf Free, Pro und Max; in Team und Enterprise allein der Primary Owner, unter *Organization settings → Data and privacy*. Fällt das weg oder ändert es sich, ändert sich, für wen der Hauptweg überhaupt existiert. *Prüfung: in den Einstellungen des jeweiligen Kontos nachsehen — warm.*
- **Der Organisationsexport des Primary Owner ist ungeprüft.** Ob sein ZIP denselben Aufbau trägt wie das persönliche — Mitgliederliste, `conversations.json`, Projektdateien mit `created_at` —, ist unbelegt, und der ganze Konverter hängt daran. *Prüfung: `inspect_export.py` über ein solches Archiv laufen lassen — warm, uns mangels Owner-Rechten derzeit nicht möglich. Der Rechteerwerb dafür wäre kein Prüfaufwand, sondern ein Eingriff in die Organisation, und für den laufenden Betrieb hilft er ohnehin nicht (1.2).*
- Anforderung unter **Settings → Privacy → Export data**, Lieferung als Link per E-Mail, Link verfällt nach 24 h (belegt). **Die Zeitraumauswahl ist nirgends dokumentiert** — sie ist beobachtet und praktisch wichtig, denn auf ihr beruht das Nachpflegen (1.5). Fällt sie weg, wird jeder Lauf zum Vollexport. Zwei Läufe mit verschiedenen Grenzen haben sie inzwischen bestätigt: `created` vom 1.5. bis 6.8.2026 (211 Konversationen) und vom 1.11. bis 1.12.2025 (78). Die Grenze wirkt auf `created_at`, nicht auf `updated_at` — ein alter Chat, der letzte Woche weiterlief, ist im Kurzzeitraum also **nicht** enthalten. Wer nachpflegt, muss den Zeitraum daher weit genug zurück legen, um weitergelaufene Altchats mitzunehmen — einen zweiten Weg, sie einzeln zu holen, gibt es derzeit nicht (1.2). *Prüfung: beim nächsten Antrag sehen, ob die Auswahl noch angeboten wird — warm; die tatsächlich gelieferte Spanne danach am ZIP gegenprüfen — kalt.*
- Dateiname `data-<uuid>-…-batch-0000.zip`; die batch-Zahl war bisher immer 0 — möglicherweise stückeln größere Exporte, nie beobachtet. *Beobachtung: durch keinen Versuch auslösbar, bemerkbar erst an einem hinreichend großen Export.*
- **Projektdateien sind vom Zeitraumfilter ausgenommen** (3.1.1) — beobachtet an zwei Exporten mit verschiedenen Zeiträumen, beide mit denselben 43 Projektdateien. Darauf beruht der Sondierungsexport (1.5), der nur noch gebraucht wird, wo der Web-Weg nicht zur Verfügung steht; fällt es weg, muss der Projektbeginn dort anders beschafft werden. *Prüfung: die beiden vorliegenden ZIPs mit verschiedenen Zeiträumen gegeneinander halten — dieselbe Projektliste heißt, es gilt noch. Kalt.*
- Archivaufbau: `users.json`, `projects/<uuid>.json`, `memories.json`, `conversations.json`, dazu wechselnd `login_history.json` (3.1.1). Projektdateien enthalten **keine** Chats. **Die Mitgliederliste wächst:** `login_history.json` kam zwischen zwei Exporten im Abstand von zwei Tagen hinzu — ein neues Mitglied ist deshalb allein kein Alarm, ein fehlendes `conversations.json` schon. *Prüfung: `inspect_export.py` laufen lassen und Mitglieder- wie Schlüsselmengen mit 3.1.1 vergleichen — kalt.*
- Konversation: genau sieben Felder, **kein Projektbezug** — die Chatliste aus dem Projekt ist die einzige Zuordnungsquelle (1.6). *Prüfung: käme je ein Projektfeld hinzu, entfiele der ganze Umweg über die Chatliste — am nächsten ZIP ablesbar, kalt.*
- Nachricht: `parent_message_uuid` macht die Nachrichten zum **Baum** (3.1.2); `sender` `human`/`assistant`; das flache `text` enthält die Denkschritte (3.1.1); `content`-Blocktypen `text`, `thinking`, `tool_use`, `tool_result`, `token_budget`. *Prüfung: Nachrichten- und Blocktypmengen aus `inspect_export.py` gegen 3.1.1 — ein neuer Blocktyp fiele dort sofort auf. Kalt.*
- **`attachments` tragen `extracted_content`, `files` nur Namen — und beide oft dieselbe Datei** (3.1.1, 1.6). Die Unterscheidung entscheidet, was das Archiv behalten kann; die Überschneidung entscheidet, wie viel Verlust überhaupt zu melden ist. *Prüfung: dieselbe Schemawache, die beide getrennt ausweist, dazu der Anteil der `files`-Einträge mit Namenspartner — kalt. Ob es für die übrigen einen Abrufweg gibt, ist eigener Punkt in 4.3.*
- Gelöschte Chats erscheinen als Hüllen: Gerüst da, Inhalt leer (3.1.3). *Prüfung: `inspect_export.py` weist sie aus — kalt.*
- **Denkschritte können enthalten sein oder fehlen** (3.1.1); der Anteil leerer `thinking_hidden`-Blöcke schwankt bis hin zu „alle". *Prüfung: den Anteil in jedem vorliegenden Archiv auszählen — kalt. Ein Nullbefund ist dabei kein Formatbefund, sondern eine Stichprobe; nicht daraus schließen, der Export führe keine Denkschritte mehr.*
- Erste Anlaufstelle bei Verdacht: `inspect_export.py` (3.3) laufen lassen und die Schlüsselmengen mit 3.1.1 vergleichen.

## 4.3 Werkzeuge der Claude-Instanz — was verwendet wird und zu prüfen ist

- **Die internen Web-Endpunkte** (1.2) sind die empfindlichste Stelle des ganzen Entwurfs: undokumentiert, von Dritten rückentwickelt, ohne Ankündigung änderbar. Gebraucht werden `/api/organizations` (Konto und Organisations-UUID ohne Vorwissen), `…/projects` (Projekte mit `created_at`), `…/projects/<p>/conversations_v2` (Chatliste mit `pagination`) und `…/chat_conversations/<c>?tree=True&rendering_mode=messages&render_all_tools=true` (vollständiger Baum, keine Paginierung). *Prüfung: die vier Pfade aus einem angemeldeten Tab aufrufen und Feldnamen sowie Antwortgröße gegen 1.2 halten — warm. Fällt einer weg, trägt nur noch der Kontoexport, und in Team-Konten gar nichts mehr.*
- **Captcha- und Cloudflare-Prüfungen** sind der zweite Grund, warum der Web-Weg gebremst ist. Bisher trat keine auf; die Anbindung würde anhalten und fragen. *Prüfung: nicht auslösbar ohne genau das zu provozieren, was vermieden werden soll — bemerkbar allein am Anhalten während eines Laufs. Warm.*
- `recent_chats(n≤20, sort_order, before, after)` — Zeit-Cursor, liefert die Chatliste; einzige Quelle der Projektzugehörigkeit; **listet den laufenden Chat nicht mit** (1.6). *Prüfung: Liste in einem Projekt abrufen und die Form des Rohblocks gegen das halten, was `MAPPING_PROMPT` verlangt (3.1.6) — warm. Die Auslassung des laufenden Chats gegenprüfen, indem dieselbe Liste aus zwei verschiedenen Chats geholt wird: Fällt sie weg, kann der Abfragechat wieder ein beliebiger sein und die Regel aus 1.5 entfällt — warm.*
- **`read_conversation` wird nicht mehr angeboten** (1.2, 3.2). Damit entfallen alle Prüfungen an seiner Schnittstelle; sie stünden für ein Werkzeug, das keine Instanz mehr hat. *Beobachtung: eine Rückkehr ist durch keinen Versuch auslösbar und fällt allein dem auf, der Werkzeuge aufzählt. Käme es wieder, ist zuerst 3.2 gegen das tatsächliche Verhalten zu halten, bevor der Weg als benutzbar gilt — die frühere Beschreibung ist gelöscht und nicht als Sollwert aufgehoben.*
- `conversation_search(query, max_results≤10)` — liefert feste, **nicht überlappende** Blöcke; `H: `/`A: `-Labels; HTML-Entities kodiert (3.4). **Und nicht immer Blöcke:** Am 18. August kam für einen Chat mit zehn Turns eine **Zusammenfassung** zurück, für einen mit zwei Turns der vollständige Wortlaut. Was die Umschaltung auslöst, ist unbekannt. Für den Crawler ist das entscheidend — eine Zusammenfassung einzulesen verstößt gegen Vorgabe 2.8. *Prüfung: einen kurzen und einen langen Chat suchen und die Trefferart vergleichen — warm; nur nötig, solange 3.4 in Betrieb bleibt (Fahrplan 10).*
- **Gibt es für `files` einen Abrufweg?** Der Export trägt zu ihnen nur `file_uuid` und `file_name`, ihr Inhalt fehlt (1.6). *Prüfung: Werkzeugbeschreibungen und Doku sichten, dann in einer Instanz einen Abruf versuchen — warm.*
- Prüfweg: die Format-/Upload-Proben in den Docstrings von 3.2/3.4 einmal je Umgebung durchgehen; weicht das Verhalten ab, zuerst die betroffene Sektion in Kapitel 3 nachziehen.

## 4.4 Plattformverhalten claude.ai — was den Entwurf trägt

- Kontextfenster 1 Mio Token (Opus 5/Sonnet 5, bezahlte Pläne, belegt); lange Chats werden **zusammengefasst statt abgebrochen**, und die Instanz erhält kein Kontextsignal (Opus ohne Budget-Tags) — darauf beruht, dass Übergaben zählergetrieben sind (3.4-Historie) und der Export-Weg bevorzugt wird (1.2).
- Projektwissen: Textextraktion; RAG schaltet ab undokumentierter Schwelle automatisch (Community: Dateianzahl); Projektdateien im Container *„while remaining in context"* — Containerzugriff spart keinen Kontext (1.6). *Beobachtung: die Schwelle ist undokumentiert und nicht steuerbar; bemerkbar allein daran, dass eine Instanz zu suchen beginnt, statt zu lesen.*
- Chat-Upload: 20 Dateien je Chat, JSON belegt zulässig — trägt die Übergabe der Protokolldatei (1.4/1.5).
- Container-Netzzugang nur gegen Allowlist, `claude.ai` steht nicht darauf — ein Skript im Container kann den Export-Link nicht laden (1.7). *Prüfung: einen Abruf aus dem Container versuchen — warm.*
- Claude-Code-Seite: `~/.claude/projects/…` wird nach `cleanupPeriodDays` aufgeräumt — Standard 30 Tage, Minimum 1, `0` ist ein Validierungsfehler, eine Obergrenze ist nicht dokumentiert (belegt). Namentlich betroffen sind `<sitzung>.jsonl` sowie `subagents/` und `tool-results/` je Sitzung; **ob fremde Dateien in diesem Ordner mit weggeräumt werden, sagt die Dokumentation nicht** — offener Prüfpunkt. Zweiter Löschweg: `claude project purge` entfernt *„Transcripts and auto memory under `projects/`"* für ein Projekt, unabhängig von der Frist. Beides trägt die Bedingungen des dritten Zielorts (1.3, Vorgabe 2.10). *Prüfung: eine fremde Datei mit zurückdatiertem Zeitstempel dort ablegen und einen Start abwarten — kalt. `claude project purge` nur mit `--dry-run` oder in einer Wegwerf-Umgebung — kalt, aber destruktiv.*
- Cowork: eigene ID-Welt, über beide Wege unerreichbar (1.6) — Anthropic könnte hier den Umzugsweg schaffen, der dieses Werkzeug ablöst. *Beobachtung: nicht auslösbar, nur zu bemerken.*

## 4.5 Compliance-API — der Weg, der dieses Werkzeug ablösen würde

Festgehalten, damit es nicht erneut recherchiert wird: Es gibt eine API, die genau das kann, was dieser Ordner nachbaut — sie ist nur nicht erreichbar. **Enterprise ist für dieses Konto nicht zu erwarten**; der Abschnitt ist Beleglage, keine Aufgabe.

Von den drei öffentlichen API-Familien kennt nur eine claude.ai-Projekte: die **Claude-API** (`/v1/messages`, `/v1/models`, `/v1/files`, Managed Agents) hat keine Projekt-Ressource, und die **Admin-API** verwaltet Organisationsmitglieder, Invites, Workspaces, Workspace-Mitglieder, API-Keys und Federation — dort kommt „project" nicht vor. Namensfalle: *Workspaces* sind Console-Konstrukte zur Bündelung von API-Keys und Rate-Limits, **nicht** claude.ai-Projekte (belegt, [Admin API](https://platform.claude.com/docs/en/manage-claude/admin-api)).

Die **Compliance-API** dagegen: *„Programmatic access to your organization's Claude activity, chats, files, projects, and users"* (belegt, [Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api)). Sie hat `List projects`, `Get project details` und `List project attachments`, und ihr Chat-Objekt trägt genau die zwei Angaben, deren Fehlen den ganzen Entwurf dieses Ordners prägt: **`created_at` je Chat** und **`project_id` je Chat** (belegt, [Retrieve and delete chats, files, and projects](https://platform.claude.com/docs/en/manage-claude/compliance-content-data)). Dazu `created_at.gte`/`updated_at.gte`-Filter, ein Cursor, den die Doku ausdrücklich als *„the recommended way to export chats and keep an export current"* benennt, und Volltext über `/v1/compliance/apps/chats/{id}/messages`. Damit entfielen auf einen Schlag: die Chatliste als einzige Zuordnungsquelle (1.6), das `created_at`-Problem des Lese-Wegs (2.5), die Zeitraumrechnung (1.5) und der Transkriptionsengpass (1.2).

Warum es trotzdem nichts ändert: Die Inhaltsendpunkte sind **ausschließlich Claude-Enterprise-Organisationen** zugänglich, über einen in claude.ai erstellten Compliance Access Key; ein Console-Konto erreicht allein den Activity Feed, und ein Admin-Key wird an den Inhaltsendpunkten mit 403 abgewiesen.

Zwei Punkte sind **unbelegt** und müssten vor einer Umstellung geklärt werden: das Feldset des Projekt-Objekts steht in der Doku nicht (nur die Sortierung nach Erstellungsdatum), und ob Denkschritte in den Chat-Messages enthalten sind — für Cowork-Transkripte sagt die Doku ausdrücklich *„Thinking blocks and images are not included"*, für Chats sagt sie nichts. Sollte auch dort das Denken fehlen, bliebe der Kontoexport selbst gegenüber der Compliance-API der inhaltlich reichere Weg (1.2).
