# Implementierungsdokumentation Chats-Export

**In Entwicklung — nicht zur Benutzung vorgesehen.** Diese Dokumentation beschreibt ein Vorhaben im Bau. Halbfertige, lückenhafte und noch nicht zusammengeführte Passagen sind in dieser Phase der Normalzustand und kein Mangel: Was hier steht, ist Arbeitsstand, nicht Zusage.

**Widersprüche zur `README.md` sind ausdrücklich erlaubt** und werden nicht nachgeführt. Sie hält bewusst einen älteren Stand samt Warnhinweis für fremde Leser und wird erst am Ende dieser Phase neu geschrieben (aus 1.1, 1.2 und 1.5). Widersprüche **innerhalb dieser Doku** und zwischen **Doku und Code** sind dagegen Defekte: Sie werden benannt und bekommen einen Fahrplanpunkt, keine Ausnahme.

**Die Phase endet**, wenn zwei Dinge vorliegen — ein bestandener mehrstufiger Test an einem eigens dafür gebauten Testprojekt (aktives Weiterschreiben eines Chats zwischen zwei Läufen, Sitzungsübergabe, Fortsetzung eines früheren Chats) und ein erster Durchlauf in ein echtes Zielprojekt einschließlich Rückweg des Protokolls und wirksamer Projektanweisung. Dann fällt dieser Hinweis, und mit ihm der Warnhinweis der README.

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

## 1.2 Die zwei Wege

Der Engpass ist nicht die Suche, sondern die **Transkription**: Chattext erreicht ein Dateisystem nur, indem eine Instanz ihn ausschreibt. Daraus folgen zwei Wege — und **beide taugen für Altbestand wie für Fortschreiben.** Der Kontoexport lässt einen Zeitraum wählen, also kann man ihn auch auf die letzten Wochen einschränken und daraus nachpflegen.


|                | über den Kontoexport                              | über `read_conversation`               |
| -------------- | ------------------------------------------------- | -------------------------------------- |
| Quelle         | ZIP, Zeitraum wählbar                             | der live store, je Chat einzeln         |
| Aufwand        | Antrag, E-Mail, Download                          | keiner, direkt im Chat                 |
| Kontextkosten  | **null**                                          | jeder Turn geht durch den Kontext      |
| **Inhalt**     | Gespräch **plus Denkschritte plus Anhänge**       | **nur das Gespräch**                   |
| Vollständigkeit| nicht beweisbar (kein Sollmaß)                    | **beweisbar** gegen `total_turns`      |
| Skript         | `chat_export_convert.py` (3.1)                    | `chat_read_store.py` (3.2)             |

**Der Kontoexport ist inhaltlich der reichere Weg**, und das ist keine Kleinigkeit: Denkschritte und Anhänge sind zusammen etwa so umfangreich wie der Gesprächstext selbst und im Lese-Weg **gar nicht sichtbar** — `read_conversation` liefert das gerenderte Transkript, keine Blockstruktur. Was auf diesem Weg hereinkommt, ist also dauerhaft ärmer, und ein späterer Export bringt es nicht nach, ohne den Chat zu ersetzen.

**Die Wahl zwischen den Wegen gibt es aber nicht überall.** Sie setzt voraus, dass ein Export überhaupt zu haben ist, und das ist an den Kontotyp gebunden (1.6): Selbstbedienung nur auf Free, Pro und Max. Ein gewöhnliches Mitglied eines Team- oder Enterprise-Kontos hat **keinen** Export — dort ist der Lese-Weg nicht die schnellere Alternative, sondern der einzige Weg, und sein ärmeres Ergebnis ist dann kein Abwägungsergebnis, sondern eine Tatsache, mit der man lebt.

Der Primary Owner einer Organisation kann exportieren, aber das hilft dem Einzelnen kaum: Dieses Vorhaben ist ein **wiederkehrender** Abgleich (1.1), und ein Verfahren, das bei jedem Durchgang den Administrator braucht, ist für den laufenden Betrieb untauglich. Wer regelmäßig nachpflegen will, kann nicht jedes Mal um einen Organisationsexport bitten.

Daraus die Empfehlung — **für Konten, die einen Export haben**: **wer warten kann, nimmt den Export** — auch beim Fortschreiben, mit einem auf wenige Wochen eingeschränkten Zeitraum. Der Lese-Weg ist der Weg für sofort, für einen einzelnen Chat, oder wenn der Export den Zeitraum nicht abdeckt. Für zwei neue Chats einen Kontoexport anzufordern wäre absurd; ihn für zweihundert alte zu vermeiden genauso.

**Verbindlich** ist die Wegegleichheit der beiden Wege — Wortlaut, erlaubte Abweichungen und ihr Wächter stehen als Vorgabe 2.5. Warum sie nicht zur Laufzeit erzwingbar ist, sagt Vorgabe 2.9.

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

Das Protokoll gehört ins Projektwissen des **Quellprojekts**, weil der Fortschreibungsweg dort läuft — nur dort greift `read_conversation`. Nebeneffekt: das Quellprojekt trägt selbst die Auskunft, was von ihm exportiert wurde.

Nicht in Artefakte: die kennen keinen JSON-Typ, kein spezifiziertes Downloadformat, und der einzige dokumentierte Rückweg in einen neuen Chat ist manuelles Kopieren (belegt, [9487310](https://support.claude.com/en/articles/9487310-what-are-artifacts-and-how-do-i-use-them)).

## 1.5 Ablauf aus Nutzersicht

**Die Instanz ist das Frontend.** Kein Parametrierungswerkzeug: sie fragt, ob eine vollständige Migration oder eine Aktualisierung auf Basis eines vorhandenen Protokolls gemeint ist, welche Projekte betroffen sind und wohin geschrieben wird — und ruft das Skript entsprechend auf.

**Über den Kontoexport** — beim ersten Mal für alles, danach mit eingeschränktem Zeitraum fürs Nachpflegen. Der Ablauf ist derselbe, nur die Menge unterscheidet sich:

0. **Sondierungsexport, wenn der nötige Zeitraum unklar ist.** Einen Export über einen möglichst kurzen Zeitraum anfordern: er enthält trotzdem **alle** Projektdateien mit ihrem `created_at` (3.1.1). `inspect_export.py` listet sie nach Datum; das Datum des betroffenen Projekts wird mit `list --project-created` ins Protokoll übernommen und begrenzt ab dann jedes Fenster (Vorgabe 2.4). Exakt statt geschätzt, und für ein paar Megabyte statt Dutzenden. Entfällt beim Nachpflegen, wenn das Protokoll die Stände schon kennt.
1. Kontoexport anfordern, ZIP herunterladen. **Setzt voraus, dass es ihn gibt** — Free, Pro oder Max, oder Primary-Owner-Rechte in einer Organisation (1.6). Fehlt beides, führt dieser Ablauf ins Leere: Dann bleibt allein der Lese-Weg unten. **Zeitraum wählbar** — fürs Nachpflegen der Zeitraum seit dem letzten Lauf mit Überlappung, für eine Erstmigration ab dem Projektbeginn aus Schritt 0. Der Zeitraum filtert `created_at`, nicht `updated_at` (4.2): ein alter Chat, der letzte Woche weiterlief, fehlt in einem kurzen Fenster **ganz**.
2. Je Quellprojekt dort die Chatliste anfordern, Antwort als Datei ablegen. Kein Skript nötig — `recent_chats` ist ein eingebautes Werkzeug der Instanz dort; nur der Prompt dazu ist wörtlich vorgegeben, als `MAPPING_PROMPT` in `chat_export_convert.py` (3.1.6), weil eine Freihand-Formulierung den Codeblock-Zwang leicht vergisst und die `<chat>`-Tags dann dem Markdown-Renderer zum Opfer fallen (beobachtet).

   **Die Abfrage gehört in einen eigens dafür angelegten Chat, der danach gelöscht wird.** Grund: `recent_chats` listet den laufenden Chat nicht mit (1.6), also fehlt der Abfragechat in seiner eigenen Liste — und damit im Protokoll und im Archiv, ohne dass irgendetwas es meldet. Ein frischer, hinterher gelöschter Chat macht diese Lücke harmlos: Was nie archiviert werden musste, fehlt auch nicht, und im Projekt bleibt keine Karteileiche liegen. Fragt man dagegen in einem Arbeitschat, verschwindet ausgerechnet dieser lautlos aus dem Archiv. Die Regel gilt für **beide** Wege, denn beide bauen ihr Protokoll aus dieser Liste (3.1.6, 3.2.3).
3. Lokal mit Claude Code: Protokoll anlegen oder ergänzen, Chats des Projekts aus dem ZIP holen und an den Zielort schreiben. `list` merkt selbst, was neu und was veraltet ist; `convert` holt nur das.
4. Protokoll ins Projektwissen des Quellprojekts zurück — sonst weiß der Lese-Weg beim nächsten Mal nicht, was schon da ist.

**Über `read_conversation`** — für sofort, für einzelne Chats, oder wenn ein Export den Zeitraum nicht abdeckt. Läuft im Quellprojekt. Liegt dort ein Protokoll im Projektwissen, ist es Ausgangspunkt und nur Fehlendes und Veraltetes wird geholt; liegt keines vor, wird es aus der Chatliste angelegt.

**Die Wahl ist nicht beliebig:** Was über den Lese-Weg hereinkommt, hat keine Denkschritte und keine Anhänge (1.2) und bleibt dauerhaft ärmer. Wer beides will, muss den Chat später über den Export **ersetzen** — nachträglich ergänzen kann man es nicht, weil dazu der Bezug zwischen Nachricht und Block fehlt.

**Wie Zuwachs erkannt wird:** Eine frische Chatliste liefert je Chat ein `updated_at`. Ist es neuer als der Stand im Protokoll, wurde weitergechattet. Der Vergleich braucht nichts als das Protokoll und die neue Liste — kein Chatarchiv, kein ZIP, kein Zeichen Chattext (Mechanik in Vorgabe 2.4). Ein veralteter Chat wird **als Ganzes ersetzt**, nicht fortgeschrieben, und das Ersetzen räumt auf — Vorgabe 2.6.

## 1.6 Was die Umgebung erlaubt und verbietet

### Migrationsmatrix, heraus


| Quelle                    | Weg                                 | Format                        | Haken                                                                           |
| ------------------------- | ----------------------------------- | ----------------------------- | ------------------------------------------------------------------------------- |
| claude.ai, alle Chats     | Kontoexport                         | ZIP,`conversations.json`      | kein Projektbezug; Gelöschtes als Hülle; `files` nur als Name; Momentaufnahme |
| claude.ai, ein Projekt    | `read_conversation`                 | Turns mit Index,`total_turns` | scope-gebunden; muss durch den Kontext; **keine Denkschritte, keine Anhänge**  |
| claude.ai, ein Projekt    | `recent_chats`                      | UUID, Zeit, Titel             | **einzige Quelle für die Projektzugehörigkeit**                               |
| Claude Code CLI           | `/export [datei]`                   | Plain Text                    | kein JSON                                                                       |
| Claude Code CLI           | `<id>.jsonl`                        | JSONL                         | Format ausdrücklich instabil; 30 Tage                                          |
| Cowork, Cloud             | Sitzungsexport →`transcript.jsonl` | JSONL                         | Auslöser nirgends dokumentiert                                                 |
| Cowork, Cloud, Enterprise | Compliance API                      | JSON                          | nur Enterprise + Compliance-Key                                                 |
| Cowork, lokal             | Dateisystem                         | `local_<uuid>.json`           | offiziell nur für die 3P-Variante dokumentiert                                 |

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

- **Cowork ist über beide Wege unerreichbar.** Lücke, keine Aufgabe. Die Anthropic-Entwicklung ist neu: Eventuell ein Weg Chats auch immer lokal in ~/.claude zu haben und über das eigene Konto auf verschiedenen Geräten parallel zu bekommen (Anthropic als Claude-Cloud ;-) ), wenn man zu Chatbeginn in Claude.ai und Claude Desktop "Cowork" wählt. Als Beobachtung geführt in Kapitel 4.
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
| `read_conversation` ist **scope-gebunden**: dieselbe UUID liest im Projekt und scheitert außerhalb                                                                                         | beobachtet (Kontrollversuch)                                                                                            |
| **`recent_chats` listet den laufenden Chat nicht mit.** Aus Chat A kommt B, aus B kommt A — jeder sieht den anderen, keiner sich selbst                                                    | beobachtet (zwei symmetrische Versuche)                                                                                 |
| Cowork-IDs (`cse_…`) werden an der Formatprüfung abgewiesen                                                                                                                               | beobachtet                                                                                                              |
| Projektdateien: 30 MB je Datei, Anzahl unbegrenzt,*„Text extraction only"*                                                                                                                 | belegt ([8241126](https://support.claude.com/en/articles/8241126-upload-files-to-claude))                               |
| RAG für Projekte schaltet automatisch nahe der Kontextgrenze ein,*„up to 10x"*, Claude nutzt dann ein *project knowledge search tool*; **kein Schwellwert dokumentiert**, nicht steuerbar | belegt ([11473015](https://support.claude.com/en/articles/11473015-retrieval-augmented-generation-rag-for-projects))    |
| RAG-Schwelle richte sich nach**Dateianzahl**, nicht Größe                                                                                                                                 | Community ([#25759](https://github.com/anthropics/claude-code/issues/25759)), als `invalid` geschlossen                 |
| Projektdateien im Container*„accessible … **while remaining in context**"* — spart **keinen** Kontext                                                                                    | belegt ([12111783](https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude))                  |
| Container-Netzzugang nur gegen eine Allowlist;`claude.ai` steht **nicht** darauf                                                                                                            | belegt (ebd.)                                                                                                           |
| Kontextfenster Opus 5 / Sonnet 5: 1 Mio Token auf bezahlten Plänen                                                                                                                         | belegt ([8606394](https://support.claude.com/en/articles/8606394-how-large-is-the-context-window-on-paid-claude-plans)) |
| Ein langes Gespräch bricht nicht ab, sondern**fasst frühere Teile zusammen**                                                                                                              | belegt (ebd.)                                                                                                           |
| Opus 4.7 und spätere Opus-Modelle erhalten**keine** Token-Budget-Tags                                                                                                                      | belegt ([Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows))                       |
| Claude-Code-Transkripte:`~/.claude/projects/<p>/<id>.jsonl`, Format *„internal … changes between versions"*, Aufräumung nach `cleanupPeriodDays` (Standard 30, Minimum 1, einstellbar), **kein Import**                                   | belegt ([sessions](https://code.claude.com/docs/en/sessions))                                                           |

Formatnahe Fakten stehen bei dem Skript, das sie verarbeitet: Aufbau des Export-ZIP in 3.1.1, `read_conversation`-Envelope in 3.2.1, Suchschnipsel in 3.4. Was quer über alle Werkzeuge gilt, steht als Vorgabe in Kapitel 2; die Prüfliste gegen Anthropic-Änderungen ist Kapitel 4.

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
| Chats seien nur über Suchschnipsel erreichbar             | `read_conversation` liefert sie vollständig und geordnet                        |
| Suchschnipsel überlappten und ließen sich zusammennähen | Feste, nicht überlappende Blöcke; null Overlap zwischen 23 Segmenten           |
| Sinkende Segmentzahl sei das Erfolgsmaß                   | Gilt nur in der Konsolidierungsphase; in der Entdeckung*muss* sie steigen        |
| `batch-0000` bedeute Stückelung der Konversationen        | Die Zeitraumauswahl erklärt die Menge                                           |
| Markdown sei für Durchsuchbarkeit besser                  | JSON macht die Sprecherrollen eindeutig; Textextraktion ist bei JSON verlustfrei |
| §1.12 der Arbeitsanweisungen müsse geändert werden      | Das dortige Schema ist ein Beispiel, Ergänzen ist erlaubt                       |
| Der Container könne den Downloadlink holen                | Allowlist ohne`claude.ai`, und der Link ist sitzungsgebunden                     |
| Projektdateien im Container sparten Kontext                | *„while remaining in context"*                                                  |
| `attachments` und `files` bezeichneten verschiedene Dinge, `files` sei reiner Verlust | Sie überschneiden sich: Ein Textupload steht in **beiden**, als Dateiobjekt und als extrahierter Text. 319 der 524 `files`-Einträge des Drei-Monats-Exports tragen ihren Inhalt in derselben Nachricht (1.6, 3.1.1). Unser `report` meldete sie trotzdem als Verlust — der Fehler fiel erst am eigenen Testlauf auf, an einer einzigen hochgeladenen Datei. |
| Dateianhänge seien im Export nur ein Name | Gilt nur für `files` (524). Die `attachments` (341) tragen `extracted_content` — 9,6 Mio Zeichen, überwiegend Python und Markdown. Ich hatte das weggeworfen und als Verlust gemeldet, den es nicht gab. |
| Eine Erstmigration brauche einen Vollexport | Der Zeitraumfilter wirkt nicht auf `projects/`: ein Ein-Wochen-Export liefert jedes Projekt mit `created_at` und damit die exakte Fenstergrenze (3.1.1). |
| Der Projektbeginn sei nur im Chat selbst zu erfahren | Weder `recent_chats` noch `read_conversation` liefern ein `created_at`, und keine öffentliche API kennt claude.ai-Projekte — außer der Compliance-API für Enterprise (4.5). Das Datum steht im Export. |
| Der Lese-Weg sei dem Export gleichwertig | Er sieht **weder Denkschritte noch Anhänge** (3.2.1) — zusammen etwa so viel wie der Gesprächstext. Nachträglich ergänzen geht nicht, nur ersetzen. |
| Aufzählung und Lesbarkeit deckten sich — `recent_chats` liste genau die Chats, die dort lesbar sind | Der **laufende** Chat fehlt: Er ist lesbar, erscheint aber nie in seiner eigenen Liste (1.6). Jeder Listenlauf übergeht damit den Chat, aus dem er gestartet wurde, und keine der eingebauten Kontrollen bemerkt es. |
| Der Export-Weg stehe jedem Konto offen | Nur Free, Pro und Max; in Team und Enterprise exportiert allein der Primary Owner (1.6). Für ein gewöhnliches Mitglied ist der Lese-Weg **der einzige** Weg — der ganze Entwurf lehnte sich an diese Annahme, ausgesprochen war sie nie. |
| `~/.claude/projects/…` scheide als Zielort aus | Die Aufbewahrungsdauer ist einstellbar (`cleanupPeriodDays`) und trifft ohnehin jede Sitzung desselben Projekts. Für Chats, die niemand mitlesen soll, ist der Ort damit sogar der bequemste — unter den drei Bedingungen aus 1.3. |

---

# 2 Vorgaben

Festlegungen, die quer über alle Werkzeuge dieses Ordners gelten. Aufnahmetest: Man muss auf eine Datei zeigen und sagen können „das verletzt diese Vorgabe". Was so nicht prüfbar ist, steht als Begründung in Kapitel 1 oder als Skript-Eigenheit in Kapitel 3. Weicht ein künftiges Werkzeug bewusst ab, wird die Vorgabe geändert oder das Werkzeug — nie stillschweigend beides gelassen.

## 2.1 Beleglage

Jede Aussage über die Umgebung trägt ihre Beleglage: **belegt** (Anthropic-Dokument, mit Quelle), **beobachtet** (am laufenden System gesehen, nirgends dokumentiert), **Community** (von Dritten berichtet, unbestätigt). Die drei werden nie vermischt, und eine Aufstufung verlangt den jeweiligen Nachweis — eine Community-Aussage wird durch eigenes Nachstellen zur Beobachtung, eine Beobachtung nur durch eine Anthropic-Quelle zum Beleg. In dieser Arbeit sind sechzehn Annahmen gekippt (1.7); der Unterschied entschied jedes Mal.

## 2.2 Dateiformat der Chatdateien

Grundlage ist §1.12 der Arbeitsanweisungen: JSON, `messages` mit `role` (`user`/`assistant`) und `content`, dazu ein `metadata`-Objekt. Das dortige Schema ist ausdrücklich ein Beispielschema, also ein Mindestbestand — hier bewusst mit klareren Namen geführt und um zwei Felder unterschritten, aus folgendem Grund.

`predecessor`/`successor` entfallen ganz: §1.11 verlangt für ihre Bestimmung entweder eine Dateinummerierung (haben wir nicht) oder einen inhaltlichen Anhaltspunkt (verstieße gegen Vorgabe 2.7 — Auswahl nie durch Inhalt) oder Nachfragen beim Nutzer je Chat (skaliert nicht). Ein bloßer Zeitstempel reicht nach §1.11 ausdrücklich nicht, und selbst „gleiches Projekt" ist kein verlässliches Indiz — ein Testchat dieses Werkzeugs lag beobachtbar im FreeCAD-Projekt, ohne mit FreeCAD zusammenzuhängen. Chats, die abwechselnd nebeneinander geführt werden, ergeben ohnehin kein sinnvolles Vorgänger/Nachfolger-Schema. Die Rolle, die eine Historie tatsächlich braucht — welche Chats einen älteren, durch andere überholten Stand zeigen — übernimmt `last_updated_at` (s. u.), nicht durch Inhalt, nicht durch den Anlegezeitpunkt, nicht durch einen Zeitstempel je Redebeitrag (den liefert keiner der beiden Wege). §1.12 wird auf dieses Tooling nachgezogen, sobald geklärt ist, wie eine Sitzung in einem fremden Projekt es referenziert; die hier verwendeten Feldnamen sind der Vorschlag dafür.

`chat_date` heißt `created_at` — der Name trifft die Sache, die er meint, und deckt sich mit dem Feld im Rohexport (3.1.1). `source_updated_at` heißt `last_updated_at` — er ist nie ein API-Name gewesen, sondern unsere eigene Benennung, und der alte Name legte fälschlich nahe, er stamme aus der Quelle selbst.

Zusätzliche Metadatenfelder, in dieser Reihenfolge:


| Feld | Wozu |
| --- | --- |
| `chat_uuid`, `url`, `title` | Identität und Auffindbarkeit |
| `source` | `account-export` oder `read_conversation` |
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
| `title`, `created_at` | Auffindbarkeit; `created_at` kennt nur der ZIP-Weg |
| `created_after` | Untergrenze für Chats ohne `created_at`: der Stand des **vorherigen** Abgleichs beim ersten Sehen — damals war das Projekt gelistet und der Chat nicht dabei, also entstand er später. Wird nur beim ersten Sehen gesetzt und danach nie überschrieben |
| `listed_updated_at` | `updated_at` aus der zuletzt geholten Chatliste |
| `exported_updated_at` | Stand, auf dem der vorliegende Export beruht |
| `turns`, `total_turns` | Umfang beim Export |
| `end_token` | letztes `next_page_token`, falls bekannt — nur Rohmaterial für 3.2.5, nichts hängt daran |
| `file` | Name der Chatdatei, oder leer |
| `side_files` | Namen der Nebendateien, damit sie beim Ersetzen mit entfernt werden (2.6) |
| `status` | s. u. |
| `exported_at` | Zeitpunkt |

Statuswerte: `listed` (aus der Chatliste bekannt), `started` (teilweise gelesen — setzt nur der Lese-Weg, der ZIP-Weg schreibt einen Chat immer ganz), `exported`, `stale` (die Quelle ist neuer als der Export), `deleted` (Hülle an der Quelle). `stale` entsteht durch den Vergleich `listed_updated_at` gegen `exported_updated_at`; `updated_at` trägt diese Erkennung, und zwar beobachtet: es liegt in allen drei Quellen vor — Export, `recent_chats`, `read_conversation`-Envelope — und sprang bei gelöschten Chats auf den Löschzeitpunkt.

Auf oberster Ebene trägt das Protokoll `protocol_version`, `project`, `project_created_at` (Beginn des Quellprojekts, von Hand aus einem Sondierungsexport eingetragen — `list`/`map --project-created`), `listed_at` (Zeitpunkt des letzten Listenabgleichs, gesetzt von `list` bzw. `map`) und `order` — die Bearbeitungsrichtung schreibt nur der Lese-Weg, der ZIP-Weg erhält sie unangetastet: ein Protokoll, ein Schema.

**Die Fenstergrenze, in einer Tabelle.** Wie weit ein Export zurückreichen muss, damit er einen Chat erfasst, ergibt sich aus drei Quellen unterschiedlicher Güte — genommen wird das Minimum über alle zu holenden Chats:

| Chat-Lage | Fensterstart | Güte |
| --- | --- | --- |
| schon exportiert, aber gewachsen | sein `created_at` aus dem Protokoll | exakt |
| erst beim letzten Abgleich hinzugekommen | sein `created_after` | exakt — vorher existierte er nicht |
| gelistet, aber nie in einem Archiv, ohne `created_after` | `created_at` des Projekts aus einem Sondierungsexport (3.1.1) | exakt, aber projektweit statt chatweise |
| kein Protokoll (Erstmigration) | ebenso der Projektbeginn | dito |

Der Projektbeginn ist dabei die Untergrenze über alles: kein Chat eines Projekts kann älter sein als das Projekt. Ein zu großzügiges Fenster kostet nur Downloadgröße, ein zu knappes kostet Inhalt — deshalb im Zweifel aufrunden, nach unten.

Umgesetzt als `window_start()` in beiden Skripten, mit `unbounded` als eigenem Ergebnis: hat ein wartender Chat keine der drei Quellen, wird das **gemeldet statt geschätzt**. Im ZIP-Weg tragen `list` und `diff` das Ergebnis vor, beide über dieselbe Funktion `window_lines()` — zwei Kommandos, die dieselbe Rechnung in eigenen Worten ausgeben, driften auseinander (3.1.6). Der Projektbeginn kommt von Hand herein (`--project-created`), weil ihn kein Werkzeug ableiten kann — eine Konversation im Archiv trägt keinen Projektbezug, die Zuordnung Projekt→Datum existiert nur beim Nutzer. Gegen den Tippfehler dabei steht `project_start_warnings()`: ein Chat, der älter ist als sein Projekt, kann nicht zu ihm gehören, also stimmt entweder das Datum oder die Chatliste nicht. Ohne diese Prüfung würde ein falsch getipptes Datum jedes künftige Fenster still verkürzen. Beide Funktionen laufen in `tests/test_wegegleichheit.py` über dieselbe Falltabelle, damit die zwei Implementierungen nicht auseinanderdriften.

Erfüllt von beiden Wegen und geprüft: `tests/test_wegegleichheit.py` vergleicht auch die Protokolle — gleiche Schlüsselmengen, gleiche Kernfelder, und genau drei Felder dürfen sich unterscheiden, weil ein Weg sie nicht wissen kann: `created_at` (kennt nur der ZIP-Weg), `total_turns` (beweist nur der Lese-Weg), `file` (das Datumssegment fehlt dem Lese-Weg — 2.3).

## 2.5 Wegegleichheit

Beide Wege erzeugen für denselben Chat **dieselbe Chatdatei** und **dasselbe Protokoll** (Protokollabgleich in 2.4). Sonst hinge der Inhalt des Archivs davon ab, auf welchem Weg ein Chat hereinkam, und „habe ich diesen Chat?" würde unscharf.

Wo ein Weg etwas **nicht wissen kann**, steht `null` statt einer Vermutung. Der ZIP-Weg hat kein Sollmaß und behauptet keine Vollständigkeit (`total_turns`, `complete`, `turns_missing` sind `null`); der Lese-Weg kennt kein `created_at` und schreibt dort `"unknown"`. Genau **fünf** Metadatenfelder dürfen sich unterscheiden — `source`, `created_at`, `total_turns`, `complete`, `turns_missing` — und keines mehr.

In den Nachrichten sind `thinking_ref`, `attachments_ref` und `creations_ref` die einzigen erlaubten Zusatzfelder, und nur der ZIP-Weg erzeugt sie — der Lese-Weg sieht weder Denkschritte noch Anhänge noch Werkzeugaufrufe (3.2.1). Nach ihrem Entfernen müssen zwei identische Transkripte übrig bleiben. `branches` ist aus demselben Grund das einzige optionale Feld auf oberster Ebene: eine leere Liste im Lese-Weg würde einen Befund behaupten, den er nicht treffen kann.

Zur Laufzeit erzwingt das nichts (2.9). Der Wächter ist `tests/test_wegegleichheit.py` — **jede** Formatänderung an einem der beiden Skripte läuft durch diesen Test, und er hat sich bewährt: er fiel durch, als der Lese-Weg ein neu hinzugekommenes Feld nicht kannte.

## 2.6 Ersetzen

Ein veralteter Chat wird **als Ganzes ersetzt**, nie fortgeschrieben — das macht den Entwurf von keiner undokumentierten Eigenschaft abhängig, und aus dem ZIP kostet es nichts.

**Ersetzen heißt aufräumen:** Vor dem Schreiben entfernt das Werkzeug alle im Protokoll vermerkten Dateien des vorherigen Eintrags (`file` und `side_files`) und **nennt sie in der Ausgabe** — stilles Löschen wäre die nächste Fehlerquelle. Aufgeräumt wird vor dem Schreiben, weil sich der Dateistamm geändert haben kann. Zwei nachgestellte Fälle erzwingen das: die **Umbenennung** (der Name trägt den Titel-Slug, ohne Aufräumen entsteht ein zweiter Stamm und ein Grep findet beide Fassungen) und die **wegfallende Nebendatei** (die neue Fassung hat kein Denken oder keinen Anhang mehr, die alte Datei bliebe auffindbar).

Die Gegenrichtung gehört dazu: `diff` meldet **Waisen** — Dateien im Verzeichnis, die kein Protokolleintrag beansprucht. Es ist die einzige Stelle, die ein Zuviel statt eines Zuwenig bemerkt, und sie warnt davor, blind zu löschen: das Protokoll ist die Autorität, nicht das Verzeichnis.

## 2.7 Auswahl strukturell, nie inhaltlich

Filterentscheidungen stützen sich auf Struktur — Feldwerte, Längen, Flaggen — und nie auf Inhaltsmerkmale wie Trigger-Wörter: die sind sprachabhängig und brechen, sobald ein Chat die Sprache wechselt. Inhaltssignale sind als **Prüfmaßstab** erlaubt, um einen strukturellen Schwellwert zu validieren, stehen aber nie im Code. Anwendungsfall mit Messung: die Denkblock-Auswahl in 3.1.3.

## 2.8 Transkriptionsdisziplin

Gilt für jeden Weg, auf dem Chattext durch den Kontext einer Instanz läuft. **Auslassen und Umformulieren sind Gegensätze, keine Grade:** Ausgelassenes fehlt sichtbar und ist nachholbar; Umformuliertes landet im Archiv, als wäre es echt — ein erfundener Datensatz, kein beschädigter. Deshalb: nie zusammenfassen, nie „handhabbar machen", nie ein eigenes Auslassungszeichen schreiben. Lieber weniger übertragen, das aber exakt. Die wegspezifischen Verfahren für zu große Stücke stehen bei den Skripten (3.2.4, 3.4).

## 2.9 Hochladbare Skripte sind eigenständig

Ein Skript, das in eine Konversation hochgeladen wird (`chat_read_store.py`, `chat_crawl_store.py`), importiert nichts aus diesem Repo, hält kleine Helfer bewusst doppelt und trägt seine vollständige Betriebsanleitung im eigenen Docstring — die hochgeladene Datei ist alles, was die Instanz dort hat. Die Folge ist der Preis von 2.5: Formatgleichheit ist nicht erzwingbar, nur per Test gesichert.

Dieselbe Zusage gilt für `chat_export_convert.py` und `inspect_export.py`, obwohl sie nie hochgeladen werden: Claude Code liest nur den Docstring, nicht zwangsläufig diese Doku. Zweimal ist die Zusage stillschweigend gebrochen worden — ein Feature kam hinzu, der Docstring blieb beim alten Stand. `tests/test_docstrings.py` ist der Wächter dagegen: mechanisch für jedes Kommando und jedes `--Flag` (per Regex aus dem Quelltext gezogen, gegen den eigenen Docstring geprüft), von Hand für Begriffe, die kein Parser findet (Feldnamen, Dateiendungen, Funktionsnamen) — diese Liste muss bei jedem neuen Feature nachgezogen werden, das ist kein Testversehen, sondern der Punkt.

## 2.10 Zielorte

Primärziel ist `<projekt>/.claude/imported_chats/` im versionierten Repo des Zielprojekts. **Dieselben Dateien** dienen unverändert auch dem Projektwissen einer claude.ai-/Desktop-/Cowork-Instanz; es gibt keine zielabhängige Ausgabeform. Ein Verzeichnis je Quellprojekt, **flach** — Projektwissen kennt keine Unterordner. Ein **dritter** Zielort ist `~/.claude/projects/<projekt>/`, für Chats, die nicht ins geteilte Repo dürfen — aber nur auf ausdrückliche Anordnung des Nutzers und nur unter den drei Bedingungen aus 1.3 (hochgesetzte Aufbewahrungsdauer, bewusst erteilte Ausnahme von §1.2 der Arbeitsanweisungen, Kenntnis von `claude project purge`). Ohne diese Anordnung schreibt kein Lauf dorthin.

Diese Vorgabe gilt den **Archivdateien**. Der Anweisungsblock, den `convert` am Ende ausgibt (3.1.6), ist keine Archivdatei, sondern Konsolenausgabe für den Nutzer — er ist bewusst zielabhängig, weil die drei Zielorte sich im Suchmittel und im Einsetzort unterscheiden.

## 2.11 Tests ohne echten Chatinhalt

Prüfstücke werden synthetisch gebaut; echter Chatinhalt gehört nie in Tests oder Fixtures. Echte Exporte liegen ausschließlich unter `test_results/`, deren Inhalte die `.gitignore` vom Repo fernhält. Diagnosewerkzeuge (3.3) geben Struktur und Zahlen aus, nie Inhalt — ihre Ausgabe muss unbedenklich in eine Konversation kopierbar sein.


# 3 Skripte

## 3.1 `chat_export_convert.py` — der Weg über den Kontoexport

**Status: gebaut, geprüft durch `tests/test_export_convert.py`, auch unter `-O`. Am Drei-Monats-Export mit 211 Chats gelaufen.**

Wandelt ein Kontoexport-ZIP in Chatdateien je Quellprojekt um und führt das Protokoll. Läuft lokal, wird nie hochgeladen.

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

- `list --map <dump> --out <verzeichnis>` — Protokoll anlegen oder ergänzen aus einer Chatliste. Neue Chats `listed`, vorhandene gegen `exported_updated_at` geprüft und ggf. `stale`. Meldet die Fenstergrenze (Vorgabe 2.4) und warnt vor einem unplausiblen Projektdatum. **Der erste Schritt jedes Laufs**, vor jedem Chattext.

  Der Rohtext für `--map` kommt nicht von hier: er entsteht in einem Chat des Quellprojekts über das dort eingebaute `recent_chats` — und zwar in einem eigens dafür angelegten, danach gelöschten Chat, weil der laufende Chat in seiner eigenen Liste fehlt (Begründung in 1.5). `MAPPING_PROMPT` (Modulkonstante, siehe Docstring) ist der dafür wörtlich vorgegebene Prompt — nur im Codeblock ausgegeben bleibt er intakt, sonst verschluckt der Markdown-Renderer die `<chat>`-Tags als HTML (beobachtet).
- `convert --zip <datei> --out <verzeichnis>` — die als `listed` oder `stale` geführten Chats aus dem ZIP holen, Baum ablaufen, Dateien schreiben, Protokoll fortschreiben.
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

**Status: gebaut, geprüft durch `tests/test_read_store.py`, auch unter `-O`.**

### 3.2.1 Was die Umgebung hier hergibt — und was nicht

**Was nicht:** `read_conversation` liefert das **gerenderte Transkript**, keine Blockstruktur: `<turn n="0">Human: …</turn>`. Damit fehlen ihm zwei Dinge, die der Kontoexport hat, und das ist keine Einschränkung der Umsetzung, sondern der Quelle:

- **Denkschritte.** Im Export sind das 4.318 Blöcke mit 9,2 Mio Zeichen behaltenswerten Inhalts (3.1.1). Hier kommen sie nicht vor.
- **Anhänge.** Im Export 341 Dateien mit 9,6 Mio Zeichen `extracted_content`. Hier ebenfalls nicht.

Zusammen ist das etwa so viel wie der Gesprächstext selbst. **Ein über diesen Weg geholter Chat bleibt dauerhaft ärmer**, und ein späterer Export ergänzt es nicht — er kann den Chat nur ersetzen, weil der Bezug zwischen Nachricht und Block nachträglich nicht herstellbar ist.

Was dieser Weg dafür kann und der Export nicht: **Vollständigkeit beweisen** (3.2.2), **sofort** liefern, ohne Antrag und Wartezeit — und, das Wichtigste, er ist **vom Kontotyp unabhängig**. Er benutzt die Werkzeuge der Instanz innerhalb des Projekts und braucht keinen Export. Damit ist er für ein gewöhnliches Mitglied eines Team- oder Enterprise-Kontos nicht der bequemere, sondern der einzige Weg (1.2, 1.6).

**Was doch:**


| Aussage                                                                                                                                                                    | Beleglage                     |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- |
| `read_conversation(conversation_id, page_token, max_turns)` liefert den vollen Turn-Text, `total_turns` im Envelope, Blättern in beide Richtungen, liest den *live store* | belegt (Werkzeugbeschreibung) |
| Turns kommen wortidentisch, nicht als Ausschnitt                                                                                                                           | beobachtet                    |
| Seitengröße von einem Zeichenbudget begrenzt, ~8 Turns trotz`max_turns=50`                                                                                               | beobachtet                    |
| Ein`page_token` aus einem Suchtreffer öffnet den Chat an dieser Stelle                                                                                                    | belegt (Werkzeugbeschreibung) |
| `max_turns` maximal 50, Standard 20                                                                                                                                        | belegt                        |

Envelope, wie beobachtet:

```
<chat url="…" updated_at="…" total_turns="58" turns="0-7" next_page_token="t8"
  ><title>…</title>
<turn n="0">Human: …</turn>
<turn n="1">Assistant:  …</turn>
```

Anders als bei Suchtreffern: `Human: `/`Assistant: ` ausgeschrieben statt `H: `/`A: `, und Entities kamen unkodiert (`→` als echtes Zeichen).

### 3.2.2 Datenmodell

Turns als Abbildung Index → `{role, text}`. Ein Turn hat **Identität**, also ist dasselbe Blatt zweimal einzulesen folgenlos — jeder Turn überschreibt sich mit gleichem Inhalt. Kein Overlap-Vergleich, keine Mehrdeutigkeit, keine Kantenbuchführung, kein Raten der Reihenfolge.

**Vollständigkeit ist eine Rechnung:** `total_turns` aus dem Envelope gegen die gehaltenen Indizes. Fehlende werden namentlich benannt. Das ist der schärfste Unterschied zu 3.4, dessen Anleitung verbieten muss, einen Chat je für vollständig zu erklären.

Der einzige Fall, der eine Warnung verdient: ein Index, der zweimal mit **unterschiedlichem** Text kommt. Das kann das Werkzeug allein nicht erzeugen — entweder wurde der Chat zwischen zwei Aufrufen geändert, oder eine Transkription war nicht wortgetreu. Der neuere Text gewinnt, das Ereignis wird festgehalten.

### 3.2.3 Kommandos und Statusmechanik

`plan`, `overview`, `state`, `map`, `ingest`, `status`, `export`.

**`plan` ist der erste Handgriff und schreibt nichts.** Es nimmt eine frische Chatliste, vergleicht sie mit dem Protokoll und legt die Lage vor: wie viele Chats neu, gewachsen oder aus einem früheren Lauf offen sind, dazu das Exportdatum aus `window_start()` **mit Begründung**, und als Gegenrechnung der Aufwand des Lese-Wegs samt seinem dauerhaften Verlust. Es entscheidet nicht — die Wahl zwischen den Wegen ist eine Abwägung zwischen Wartezeit und Inhalt, die nur der Nutzer treffen kann (1.2).

Zwei Eigenheiten sind bewusst so: Für Chats ohne bekannten Umfang wird **nicht geschätzt**, sondern ihre Anzahl genannt — eine erfundene Turn-Zahl wäre schlechter als eine ehrliche Lücke. Und Chats, die das Protokoll kennt und die frische Liste nicht mehr führt, werden gemeldet, aber **nie automatisch entfernt**: das kann Löschung an der Quelle bedeuten, Verschieben in ein anderes Projekt — oder eine Chatliste, die der Nutzer nicht bis zum Ende geblättert hat. Diese Meldung erscheint auch dann, wenn sonst nichts zu holen ist; dort ist sie der einzige Befund und der wichtigste.

`ingest` setzt `started` — eine Seite zu lesen *ist* das Aufnehmen der Arbeit; `read_conversation` liefert genau einen Chat je Aufruf, Absicht und Wirkung fallen zusammen. `export` setzt `done` nur bei bewiesener Vollständigkeit; ein Teilexport bleibt `started` und sagt es.

`map` nimmt dieselbe Liste entgegen und unterliegt derselben Regel: Sie wird in einem eigens angelegten, danach gelöschten Chat geholt, weil der laufende Chat in seiner eigenen Liste fehlt (1.5, 1.6). `map` ist der Zulieferer der Projektzuordnung und bleibt auch im Weg 3.1 gebraucht — und es setzt `stale`, wenn eine frische Liste einen neueren Stand zeigt als der Export. Die Statusführung folgt Vorgabe 2.4: dasselbe `protokoll.json` wie der ZIP-Weg, `started` und `deleted` setzt nur dieser Weg (letzteres nur von Hand — aus einer Fehlermeldung ist Löschung nicht von Unzugänglichkeit unterscheidbar).

### 3.2.4 Transkriptionsdisziplin

Es gilt Vorgabe **2.8**. Wegspezifisch ist nur das Verfahren bei zu großen Seiten: auf mehrere `ingest`-Aufrufe aufteilen oder ein Präfix an einer Sprechergrenze abschneiden — der Rest der Seite kommt beim nächsten Blättern ohnehin wieder.


### 3.2.5 Konvergenz und was offen bleibt

`export` erzeugt das Format nach Vorgabe 2.2 — denselben Metadatensatz in derselben Reihenfolge wie der ZIP-Weg —, benennt die Datei nach Vorgabe 2.3 (Datum ehrlich `ohne-datum`, weil `read_conversation` kein `created_at` liefert) und schreibt den Protokolleintrag nach Vorgabe 2.4 samt `end_token`. Geprüft durch `tests/test_wegegleichheit.py`, Chatdateien wie Protokolle; die erlaubten Abweichungen nennen 2.5 und 2.4.

Offen bleibt: **Zuwachs nachladen statt ersetzen.** Zu erforschen ist, wie man an einer definierten Stelle einsteigt — ob ein gespeichertes `next_page_token` über Tage gültig bleibt (nicht dokumentiert), oder ob es einen anderen Weg gibt, ab einem Turn-Index zu lesen. `read_conversation` nimmt heute nur `conversation_id`, `page_token` und `max_turns`; ein „ab Turn N" gibt es nicht. Bis das geklärt ist, gilt die Ersetzung als Ganzes — korrekt, nur teurer. Als Prüfpunkt geführt in 4.3 (warm, über mehrere Tage).

## 3.3 `inspect_export.py` — Diagnose eines Export-ZIP

**Status: gebaut, eigener Selbsttest, auch unter `-O`.** Die Scratchpad-Fassung ging beim Sitzungswechsel verloren und wurde aus dem Verlauf rekonstruiert — der Beleg, dass flüchtige Ablagen keine Werkzeuge halten.

Liest ein Kontoexport-ZIP ohne zu entpacken und berichtet Struktur und Zahlen, **nie Chatinhalt** (Vorgabe 2.11 — der Selbsttest weist mit Markertexten nach, dass nichts davon in der Ausgabe erscheint; Titel erscheinen bewusst, sie identifizieren die Chats). Aufruf: `inspect_export.py <export.zip>`.

Prüft: Archivinhalt; **die Projekte nach Erstellungsdatum** — das ist der Zulieferer für `--project-created` (Vorgabe 2.4), und der Grund, warum ein Sondierungsexport genügt; Anzahl, Zeitraum und Umfang der Konversationen; ausgehöhlte Konversationen samt der Löschungs-Erklärung aus 3.1.3; Verzweigungen je Chat; Blocktypen und Wahrheitsflaggen; die `text`-Blöcke-Abweichung (das flache Feld trägt die Denkschritte); **`attachments` mit `extracted_content` getrennt von reinen Namensverweisen** — der Prüfpunkt aus 4.2; und als Schemawache die Vereinigung aller Konversations-, Nachrichten- **und Blockschlüssel** zum Vergleich mit 3.1.1.

Es beantwortet eine andere Frage als `analyse` (3.1.6): dieses beschreibt den Rohexport, jenes die Deutung.

## 3.4 `chat_crawl_store.py` — Rekonstruktion aus Suchschnipseln

**Status: gebaut, geprüft durch `tests/test_crawl_store.py`. Überholt, wo `read_conversation` existiert.**

Rekonstruiert Chats aus überlappenden Suchschnipseln, für Umgebungen ohne `read_conversation`.

**Warum überholt:** Am echten Lauf zeigte sich, dass `conversation_search` **feste, nicht überlappende Blöcke** liefert — zwischen 23 Segmenten dreier Chats gab es null Overlap. Die Overlap-Mechanik, das Herz des Skripts, hat damit fast nichts zu verbinden: der Crawl sammelt Text, ohne ihn zusammenzusetzen.

**Was daran gültig bleibt** und in 3.2 übernommen wurde: Zustandsdatei mit Status und Bearbeitungsrichtung, Rundenbegriff, Übergabeprozedur, Transkriptionsdisziplin, Upload-Probe.

Erhaltenswerte Einzelbefunde: Suchtreffer tragen `H: `/`A: `-Label und HTML-Entities; ein Auslassungszeichen wird nur als Lückenmarke erkannt, wenn es zwischen zwei Nicht-Leerzeichen klemmt — `abc ... def` und eine einzelne `...`-Zeile landen ohne jede Warnung im Transkript.

Ob das Skript bleibt, ist zu entscheiden, sobald sich 3.1 und 3.2 bewährt haben.

**Offen und derzeit nicht beurteilbar** ist, in welchem Verhältnis es zum übrigen Bestand steht: ob es Rückfallweg für Umgebungen ohne `read_conversation` bleibt, nur noch Ersatzteillager an Befunden ist oder ersatzlos entfällt. Die Entscheidung braucht Kontext, den wir noch nicht haben; bis dahin bleibt es unangetastet (Fahrplan 10).


---

# 4 Projektpflege — Anthropic-Entwicklung

Anthropic baut an Export, Werkzeugen und Plattform laufend um; nichts hiervon ist zugesichert, das meiste nur beobachtet (2.1). Dieses Kapitel ist die **Prüfliste**: alles, was regelmäßig zu kontrollieren ist, gesammelt an einem Ort.

**Was hier steht und was nicht.** Kapitel 4 sagt, **was zu prüfen ist und wie**. Die Festlegung selbst hat ihr normatives Zuhause anderswo und wird hier nur so knapp wiedergegeben, dass die Liste für sich lesbar bleibt; bei Widerspruch gilt die verlinkte Stelle, nicht die Wiedergabe. Verfahren, die drei Prüfarten und die Übersicht über alle Punkte stehen in 4.1.

## 4.1 Verfahren und Übersicht

**Ziel:** Ein Satz kleiner Prüfwerkzeuge, mit denen sich vor einem Lauf schnell feststellen lässt, ob **(a)** das Kontoexport-Format und **(b)** die Werkzeugschnittstellen der Claude-Instanz (`recent_chats`, `read_conversation`, `conversation_search`) noch den hier dokumentierten Beobachtungen entsprechen — als Frühwarnung, bevor eine Änderung still Falsches produziert.

Vorhandene Bausteine: `inspect_export.py` (3.3) als Schemawache des Exports, dazu die Format- und Upload-Proben in den Docstrings von 3.2 und 3.4. **Die Lücke ist die warme Seite:** Für den Export gibt es ein Werkzeug, für die Instanzschnittstellen nur Proben von Hand. Das bleibt das offene Ziel dieses Abschnitts.

**Das Profil des Testprojekts.** Für die warme Seite gibt es kein Werkzeug, aber eine **Prüfvorlage**: ein eigens angelegtes claude.ai-Projekt, dessen Inhalt bewusst gewählt ist. Zwei Randbedingungen stehen dabei gegeneinander. Es muss **klein** bleiben — im Lese-Weg geht jeder Turn durch den Kontext, und ein kleiner Export ist schneller da. Und es muss trotzdem **jedes strukturelle Merkmal** tragen, auf das der Code reagiert: Ein fehlendes Merkmal lässt seinen Codeweg ungeprüft, ohne dass es auffällt — der Lauf meldet dann nicht etwa eine Lücke, sondern schlicht nichts.

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
| langer Chat | einer mit deutlich über acht Turns | Seitengrenze und Übergabe im Lese-Weg (3.2.1, 3.2.4) |
| wachsender Chat | einer, der Tage später fortgesetzt wird | `stale`, Ersetzen (2.6) und die Fensterrechnung (2.4) |

Die Zeile zum wachsenden Chat ist die einzige mit Vorlaufzeit: Der Zeitraumfilter des Exports arbeitet auf Tagesebene, also muss zwischen Anlegen und Fortsetzen mindestens ein Tageswechsel liegen.

**Drei Rezepte sind am ersten Lauf gescheitert; zwei davon sind repariert, eines nicht.** Der Lauf vom 17. August lieferte Gabelung, beide Anhangsarten und den langen Chat wie vorgesehen — und weder Denkschritte noch Erzeugnis noch Sendewiederholung. Ein Merkmal, das nicht entsteht, lässt seinen Codeweg ungeprüft, ohne dass etwas auffällt; deshalb stehen die Ursachen hier und nicht nur im Verlaufsprotokoll:

- **Denkschritte:** Alle 14 Blöcke lagen unter 200 Zeichen und wurden nach 3.1.3 verworfen — im echten Bestand liegt der Median bei 682. Eine beiläufige Planungsfrage genügt also nicht; die Aufgabe muss echte Abwägung erzwingen.
- **Erzeugnis:** Der Chat drehte sich um Bildgenerierung. Das erzeugt zwar 27 `tool_use`-Blöcke, aber keinen der drei Werkzeugnamen aus 3.1.3. Das Rezept muss ausdrücklich ein Artefakt verlangen.
- **Sendewiederholung:** Zwei identisch abgeschickte Nachrichten stehen als Eltern und Kind hintereinander — der Code sucht aber **Geschwister ohne Nachfahren** an einer Gabelung. Das ist eine andere Struktur, und wir kennen keinen Handgriff, der sie herstellt. Belegt ist das Phänomen nur aus echten Daten (14 Kinder mit je 440 Zeichen, 3.1.2). Bis jemand das Rezept findet, bleibt dieser Codeweg ungeprüft — ausdrücklich vermerkt statt stillschweigend als abgedeckt geführt.

**Drei Prüfarten.** Jeder Punkt trägt genau eine:

- **kalt** — prüfbar mit dem, was auf der Platte liegt: die heruntergeladenen Export-ZIPs unter `tests/test_results/` und ein Arbeitsordner. Kein Netz, kein Konto, kein fremder Zustand; beliebig oft wiederholbar.
- **warm** — nur mit Zugriff auf ein echtes Projekt: ein claude.ai-Projekt für `recent_chats`, `read_conversation`, Upload und Projektwissen, oder ein Claude-Code-Projekt als Zielort. Braucht Vorbereitung, ist nicht beliebig wiederholbar und hinterlässt Spuren an der Quelle.
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
| Chatliste über `recent_chats` | 4.3 | warm |
| Übergeht `recent_chats` weiterhin den laufenden Chat? | 4.3, 1.6 | warm |
| Envelope, Seitengröße und Scope-Bindung von `read_conversation` | 4.3, 3.2.1 | warm |
| Abweisung von Cowork-IDs | 4.3 | warm |
| Blockverhalten von `conversation_search` | 4.3, 3.4 | warm |
| Bleibt ein `page_token` über Tage gültig? | 4.3, 3.2.5 | warm, über mehrere Tage |
| Gibt es für `files` einen Abrufweg? | 4.3, 1.6 | warm |
| RAG-Schwelle des Projektwissens | 4.4 | Beobachtung |
| Container-Allowlist ohne `claude.ai` | 4.4 | warm |
| Räumt die Aufräumung fremde Dateien in `~/.claude/projects/` mit weg? | 4.4, 1.3 | kalt |
| Was nimmt `claude project purge` mit? | 4.4, 1.3 | kalt, destruktiv |
| Cowork über beide Wege unerreichbar | 4.4, 1.6 | Beobachtung |

## 4.2 Kontoexport — was verwendet wird und zu prüfen ist

- **Wer überhaupt exportieren darf, hängt am Kontotyp** (1.6): Selbstbedienung nur auf Free, Pro und Max; in Team und Enterprise allein der Primary Owner, unter *Organization settings → Data and privacy*. Fällt das weg oder ändert es sich, ändert sich, für wen der Hauptweg überhaupt existiert. *Prüfung: in den Einstellungen des jeweiligen Kontos nachsehen — warm.*
- **Der Organisationsexport des Primary Owner ist ungeprüft.** Ob sein ZIP denselben Aufbau trägt wie das persönliche — Mitgliederliste, `conversations.json`, Projektdateien mit `created_at` —, ist unbelegt, und der ganze Konverter hängt daran. *Prüfung: `inspect_export.py` über ein solches Archiv laufen lassen — warm, uns mangels Owner-Rechten derzeit nicht möglich. Der Rechteerwerb dafür wäre kein Prüfaufwand, sondern ein Eingriff in die Organisation, und für den laufenden Betrieb hilft er ohnehin nicht (1.2).*
- Anforderung unter **Settings → Privacy → Export data**, Lieferung als Link per E-Mail, Link verfällt nach 24 h (belegt). **Die Zeitraumauswahl ist nirgends dokumentiert** — sie ist beobachtet und praktisch wichtig, denn auf ihr beruht das Nachpflegen (1.5). Fällt sie weg, wird jeder Lauf zum Vollexport. Zwei Läufe mit verschiedenen Grenzen haben sie inzwischen bestätigt: `created` vom 1.5. bis 6.8.2026 (211 Konversationen) und vom 1.11. bis 1.12.2025 (78). Die Grenze wirkt auf `created_at`, nicht auf `updated_at` — ein alter Chat, der letzte Woche weiterlief, ist im Kurzzeitraum also **nicht** enthalten. Wer nachpflegt, muss den Zeitraum daher weit genug zurück legen, um weitergelaufene Altchats mitzunehmen, oder sie über den Lese-Weg holen. *Prüfung: beim nächsten Antrag sehen, ob die Auswahl noch angeboten wird — warm; die tatsächlich gelieferte Spanne danach am ZIP gegenprüfen — kalt.*
- Dateiname `data-<uuid>-…-batch-0000.zip`; die batch-Zahl war bisher immer 0 — möglicherweise stückeln größere Exporte, nie beobachtet. *Beobachtung: durch keinen Versuch auslösbar, bemerkbar erst an einem hinreichend großen Export.*
- **Projektdateien sind vom Zeitraumfilter ausgenommen** (3.1.1) — beobachtet an zwei Exporten mit verschiedenen Zeiträumen, beide mit denselben 43 Projektdateien. Darauf beruht der Sondierungsexport aus 1.5; fällt es weg, muss der Projektbeginn anders beschafft werden. *Prüfung: die beiden vorliegenden ZIPs mit verschiedenen Zeiträumen gegeneinander halten — dieselbe Projektliste heißt, es gilt noch. Kalt.*
- Archivaufbau: `users.json`, `projects/<uuid>.json`, `memories.json`, `conversations.json`, dazu wechselnd `login_history.json` (3.1.1). Projektdateien enthalten **keine** Chats. **Die Mitgliederliste wächst:** `login_history.json` kam zwischen zwei Exporten im Abstand von zwei Tagen hinzu — ein neues Mitglied ist deshalb allein kein Alarm, ein fehlendes `conversations.json` schon. *Prüfung: `inspect_export.py` laufen lassen und Mitglieder- wie Schlüsselmengen mit 3.1.1 vergleichen — kalt.*
- Konversation: genau sieben Felder, **kein Projektbezug** — die Chatliste aus dem Projekt ist die einzige Zuordnungsquelle (1.6). *Prüfung: käme je ein Projektfeld hinzu, entfiele der ganze Umweg über die Chatliste — am nächsten ZIP ablesbar, kalt.*
- Nachricht: `parent_message_uuid` macht die Nachrichten zum **Baum** (3.1.2); `sender` `human`/`assistant`; das flache `text` enthält die Denkschritte (3.1.1); `content`-Blocktypen `text`, `thinking`, `tool_use`, `tool_result`, `token_budget`. *Prüfung: Nachrichten- und Blocktypmengen aus `inspect_export.py` gegen 3.1.1 — ein neuer Blocktyp fiele dort sofort auf. Kalt.*
- **`attachments` tragen `extracted_content`, `files` nur Namen — und beide oft dieselbe Datei** (3.1.1, 1.6). Die Unterscheidung entscheidet, was das Archiv behalten kann; die Überschneidung entscheidet, wie viel Verlust überhaupt zu melden ist. *Prüfung: dieselbe Schemawache, die beide getrennt ausweist, dazu der Anteil der `files`-Einträge mit Namenspartner — kalt. Ob es für die übrigen einen Abrufweg gibt, ist eigener Punkt in 4.3.*
- Gelöschte Chats erscheinen als Hüllen: Gerüst da, Inhalt leer (3.1.3). *Prüfung: `inspect_export.py` weist sie aus — kalt.*
- Erste Anlaufstelle bei Verdacht: `inspect_export.py` (3.3) laufen lassen und die Schlüsselmengen mit 3.1.1 vergleichen.

## 4.3 Werkzeuge der Claude-Instanz — was verwendet wird und zu prüfen ist

- `recent_chats(n≤20, sort_order, before, after)` — Zeit-Cursor, liefert die Chatliste; einzige Quelle der Projektzugehörigkeit; **listet den laufenden Chat nicht mit** (1.6). *Prüfung: Liste in einem Projekt abrufen und die Form des Rohblocks gegen das halten, was `MAPPING_PROMPT` verlangt (3.1.6) — warm. Die Auslassung des laufenden Chats gegenprüfen, indem dieselbe Liste aus zwei verschiedenen Chats geholt wird: Fällt sie weg, kann der Abfragechat wieder ein beliebiger sein und die Regel aus 1.5 entfällt — warm.*
- `read_conversation(conversation_id, page_token, max_turns≤50)` — Envelope mit `url`, `updated_at`, `total_turns`, `turns`, `next_page_token`/`prev_page_token`; Seitengröße durch Zeichenbudget (~8 Turns beobachtet); liest den *live store*; **scope-gebunden** (im Projekt nur dessen Chats); lehnt Cowork-IDs (`cse_…`) am Format ab; liefert das gerenderte Transkript **ohne** Denkschritte und Anhänge (3.2.1). *Prüfung: Envelope eines bekannten Chats gegen 3.2.1 halten; die Scope-Bindung mit einer UUID aus einem anderen Bereich gegenprüfen, die Formatabweisung mit einer Cowork-ID — warm.*
- `conversation_search(query, max_results≤10)` — liefert feste, **nicht überlappende** Blöcke; `H: `/`A: `-Labels; HTML-Entities kodiert (3.4). *Prüfung: nur nötig, solange 3.4 in Betrieb bleibt (Fahrplan 10) — warm.*
- **Bleibt ein `page_token` über Tage gültig?** Offen und entscheidend dafür, ob Zuwachs nachgeladen statt ersetzt werden kann (3.2.5). *Prüfung: ein Token aufheben und nach Tagen erneut einsetzen — warm, über mehrere Tage.*
- **Gibt es für `files` einen Abrufweg?** Der Export trägt zu ihnen nur `file_uuid` und `file_name`, ihr Inhalt fehlt (1.6). *Prüfung: Werkzeugbeschreibungen und Doku sichten, dann in einer Instanz einen Abruf versuchen — warm.*
- Prüfweg: die Format-/Upload-Proben in den Docstrings von 3.2/3.4 einmal je Umgebung durchgehen; weicht der Envelope ab, zuerst 3.2.1 nachziehen.

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
