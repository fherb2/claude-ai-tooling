# Implementierungsdokumentation Chats-Export

Vier Teile. **Teil 1** beschreibt, was gebaut wird, wie es zusammenwirkt und wie es benutzt wird. **Teil 2** hält die Vorgaben, die quer über alle Werkzeuge gelten. **Teil 3** hält je Skript die Festlegungen, die dort umgesetzt werden, samt dem Kontext, der dafür erarbeitet wurde. **Teil 4** ist die Prüfliste gegenüber der laufenden Anthropic-Entwicklung. Teil 1 verweist für Details nach 2 und 3 und wiederholt sie nicht.

Die **Beleglage** wird durchgehend ausgewiesen; die drei Stufen und ihre Regeln sind Vorgabe 2.1.

---

# 1 Zusammenhänge

## 1.1 Ziel

Chats aus claude.ai-Projekten sollen **im Zusammenhang ihres Projekts durchsuchbar** sein — nicht fortführbar. Sie dienen dazu, früher besprochenen Kontext wiederzufinden.

Es ist ein **wiederkehrender Abgleich**, keine einmalige Migration: neue Chats kommen laufend hinzu, vorhandene können weitergelaufen sein.

Je Chat entstehen bis zu drei Dateien — Gespräch, Denkschritte, Anhänge (Vorgabe 2.2) —, und daneben gibt es **genau eine** weitere: das Protokoll (1.4). Mehr Zustand gibt es nicht.

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

Daraus die Empfehlung: **wer warten kann, nimmt den Export** — auch beim Fortschreiben, mit einem auf wenige Wochen eingeschränkten Zeitraum. Der Lese-Weg ist der Weg für sofort, für einen einzelnen Chat, oder wenn der Export den Zeitraum nicht abdeckt. Für zwei neue Chats einen Kontoexport anzufordern wäre absurd; ihn für zweihundert alte zu vermeiden genauso.

**Verbindlich** ist die Wegegleichheit der beiden Wege — Wortlaut, erlaubte Abweichungen und ihr Wächter stehen als Vorgabe 2.5. Warum sie nicht zur Laufzeit erzwingbar ist, sagt Vorgabe 2.9.

## 1.3 Zielorte

Primär das Git-Repo eines Claude-Code-Projekts, dort `<projekt>/.claude/imported_chats/`. Die Dateien sind über `Read`/`Grep` erreichbar: kein Projektwissen, kein RAG, kein undokumentierter Schwellwert, kein Kontextverbrauch, bis wirklich gelesen wird.

Sekundär das Projektwissen einer claude.ai-/Desktop-/Cowork-Instanz — mit denselben Dateien, ohne zweite Ausgabeform; die Regeln dazu (ein flaches Verzeichnis je Quellprojekt, dieselben Dateien für beide Ziele) sind Vorgabe 2.10. JSON ist ein belegter Upload-Typ, und Projektdateien werden per Textextraktion verarbeitet.

**Nicht** nach `~/.claude/projects/…`, aus drei Gründen: dort wird nach `cleanupPeriodDays` (Standard **30 Tage**) automatisch gelöscht — *„Files in the paths below are deleted on startup once they're older than"* (belegt, [claude-directory](https://code.claude.com/docs/en/claude-directory)); der Ort ist nicht versioniert und *„not shared across machines"*, während `<projekt>/.claude/` gerade deshalb versioniert wird; und §1.2 der Arbeitsanweisungen behält `~/.claude/` der Engine vor. Die dortige Ordnernamensstruktur bleibt als Zuordnungshilfe nützlich.

## 1.4 Das Protokoll

Eine Datei je Quellprojekt, neben den Chatdateien. Sie wird **bei der Erstellung der Chatliste angelegt** — in beiden Wegen, bevor ein einziger Chat geholt ist — und ist ab da in jedem Schritt die Referenz. Aufbau, Felder und Statuswerte sind Vorgabe 2.4.

Warum ein Protokoll und nicht der Verzeichnisinhalt: **Innerhalb von claude.ai gibt es kein Verzeichnis zum Ablesen**, dort existiert nur Hochgeladenes. Eine kleine Datei kann eine Instanz lesen, N Chatdateien durchzählen nicht. Die `metadata` in jeder Chatdatei bleibt trotzdem, damit eine einzeln weitergegebene Datei für sich verständlich ist; bei Widerspruch gilt das Protokoll.

Das Protokoll gehört ins Projektwissen des **Quellprojekts**, weil der Fortschreibungsweg dort läuft — nur dort greift `read_conversation`. Nebeneffekt: das Quellprojekt trägt selbst die Auskunft, was von ihm exportiert wurde.

Nicht in Artefakte: die kennen keinen JSON-Typ, kein spezifiziertes Downloadformat, und der einzige dokumentierte Rückweg in einen neuen Chat ist manuelles Kopieren (belegt, [9487310](https://support.claude.com/en/articles/9487310-what-are-artifacts-and-how-do-i-use-them)).

## 1.5 Ablauf aus Nutzersicht

**Die Instanz ist das Frontend.** Kein Parametrierungswerkzeug: sie fragt, ob eine vollständige Migration oder eine Aktualisierung auf Basis eines vorhandenen Protokolls gemeint ist, welche Projekte betroffen sind und wohin geschrieben wird — und ruft das Skript entsprechend auf.

**Über den Kontoexport** — beim ersten Mal für alles, danach mit eingeschränktem Zeitraum fürs Nachpflegen. Der Ablauf ist derselbe, nur die Menge unterscheidet sich:

1. Kontoexport anfordern, ZIP herunterladen. **Zeitraum wählbar** — fürs Nachpflegen genügt der Zeitraum seit dem letzten Lauf, mit etwas Überlappung.
2. Je Quellprojekt dort die Chatliste anfordern, Antwort als Datei ablegen.
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

- **Cowork ist über beide Wege unerreichbar.** Lücke, keine Aufgabe. Die Anthropic-Entwicklung ist neu: Eventuell ein Weg Chats auch immer lokal in ~/.claude zu haben und über das eigene Konto auf verschiedenen Geräten parallel zu bekommen (Anthropic als Claude-Cloud ;-) ), wenn man zu Chatbeginn in Claude.ai und Claude Desktop "Cowork" wählt. -> Entwicklung weiter beobachten.
- **Gelöschte Chats sind unwiederbringlich.** Der Export enthält sie als Hüllen und sagt nicht, dass es Hüllen sind (3.1).
- **Hochgeladene Dateien: zur Hälfte erhalten.** Der Export kennt zwei verschiedene Dinge, und die Unterscheidung ist wesentlich. `attachments` tragen ein Feld `extracted_content` und damit ihren Text — 341 im Drei-Monats-Export, keines leer, zusammen 9.635.919 Zeichen, überwiegend `text/x-python` (238) und Markdown (26). `files` dagegen tragen nur `file_uuid` und `file_name` — 524 Stück, und **die** sind wirklich verloren. -> Prüfen, ob es für `files` einen anderen Abrufweg gibt. Und weiter die Entwicklung beobachten.
- **Die Projektzugehörigkeit gibt es nur in claude.ai.** Der einzige Punkt, an dem die Werkzeuge dort unentbehrlich bleiben, um exportierte Chats einzelnen Projekten zuzuordnen. -> Entwicklung weiter beobachten.

### Umgebungsfakten, die den Gesamtentwurf tragen


| Aussage                                                                                                                                                                                     | Beleglage                                                                                                               |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Kontoexport unter Settings → Privacy, Link per E-Mail, verfällt nach 24 h, Free/Pro/Max                                                                                                   | belegt ([9450526](https://support.claude.com/en/articles/9450526-export-your-claude-data))                              |
| **Der Export lässt einen Zeitraum wählen**                                                                                                                                                | **beobachtet**, in keinem Artikel erwähnt                                                                              |
| Gelöschte Inhalte*„will not be included in data exports initiated after the deletion"*                                                                                                    | belegt ([13346720](https://support.claude.com/en/articles/13346720-export-your-organization-s-data))                    |
| `read_conversation` ist **scope-gebunden**: dieselbe UUID liest im Projekt und scheitert außerhalb                                                                                         | beobachtet (Kontrollversuch)                                                                                            |
| Cowork-IDs (`cse_…`) werden an der Formatprüfung abgewiesen                                                                                                                               | beobachtet                                                                                                              |
| Projektdateien: 30 MB je Datei, Anzahl unbegrenzt,*„Text extraction only"*                                                                                                                 | belegt ([8241126](https://support.claude.com/en/articles/8241126-upload-files-to-claude))                               |
| RAG für Projekte schaltet automatisch nahe der Kontextgrenze ein,*„up to 10x"*, Claude nutzt dann ein *project knowledge search tool*; **kein Schwellwert dokumentiert**, nicht steuerbar | belegt ([11473015](https://support.claude.com/en/articles/11473015-retrieval-augmented-generation-rag-for-projects))    |
| RAG-Schwelle richte sich nach**Dateianzahl**, nicht Größe                                                                                                                                 | Community ([#25759](https://github.com/anthropics/claude-code/issues/25759)), als `invalid` geschlossen                 |
| Projektdateien im Container*„accessible … **while remaining in context**"* — spart **keinen** Kontext                                                                                    | belegt ([12111783](https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude))                  |
| Container-Netzzugang nur gegen eine Allowlist;`claude.ai` steht **nicht** darauf                                                                                                            | belegt (ebd.)                                                                                                           |
| Kontextfenster Opus 5 / Sonnet 5: 1 Mio Token auf bezahlten Plänen                                                                                                                         | belegt ([8606394](https://support.claude.com/en/articles/8606394-how-large-is-the-context-window-on-paid-claude-plans)) |
| Ein langes Gespräch bricht nicht ab, sondern**fasst frühere Teile zusammen**                                                                                                              | belegt (ebd.)                                                                                                           |
| Opus 4.7 und spätere Opus-Modelle erhalten**keine** Token-Budget-Tags                                                                                                                      | belegt ([Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows))                       |
| Claude-Code-Transkripte:`~/.claude/projects/<p>/<id>.jsonl`, Format *„internal … changes between versions"*, Aufräumung nach 30 Tagen, **kein Import**                                   | belegt ([sessions](https://code.claude.com/docs/en/sessions))                                                           |

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
| Dateianhänge seien im Export nur ein Name | Gilt nur für `files` (524). Die `attachments` (341) tragen `extracted_content` — 9,6 Mio Zeichen, überwiegend Python und Markdown. Ich hatte das weggeworfen und als Verlust gemeldet, den es nicht gab. |
| Der Lese-Weg sei dem Export gleichwertig | Er sieht **weder Denkschritte noch Anhänge** (3.2.1) — zusammen etwa so viel wie der Gesprächstext. Nachträglich ergänzen geht nicht, nur ersetzen. |

---

# 2 Vorgaben

Festlegungen, die quer über alle Werkzeuge dieses Ordners gelten. Aufnahmetest: Man muss auf eine Datei zeigen und sagen können „das verletzt diese Vorgabe". Was so nicht prüfbar ist, steht als Begründung in Kapitel 1 oder als Skript-Eigenheit in Kapitel 3. Weicht ein künftiges Werkzeug bewusst ab, wird die Vorgabe geändert oder das Werkzeug — nie stillschweigend beides gelassen.

## 2.1 Beleglage

Jede Aussage über die Umgebung trägt ihre Beleglage: **belegt** (Anthropic-Dokument, mit Quelle), **beobachtet** (am laufenden System gesehen, nirgends dokumentiert), **Community** (von Dritten berichtet, unbestätigt). Die drei werden nie vermischt, und eine Aufstufung verlangt den jeweiligen Nachweis — eine Community-Aussage wird durch eigenes Nachstellen zur Beobachtung, eine Beobachtung nur durch eine Anthropic-Quelle zum Beleg. In dieser Arbeit sind zwölf Annahmen gekippt (1.7); der Unterschied entschied jedes Mal.

## 2.2 Dateiformat der Chatdateien

Grundlage ist §1.12 der Arbeitsanweisungen: JSON, `messages` mit `role` (`user`/`assistant`) und `content`, dazu `metadata` mit `chat_date`, `imported_at`, `predecessor`, `successor`. Das dortige Schema ist ausdrücklich ein Beispielschema, also ein Mindestbestand; die Ergänzungen sind hier festgelegt.

Zusätzliche Metadatenfelder, in dieser Reihenfolge:


| Feld | Wozu |
| --- | --- |
| `chat_uuid`, `url`, `title` | Identität und Auffindbarkeit |
| `source` | `account-export` oder `read_conversation` |
| `source_updated_at` | Stand der Quelle beim Import — macht Veralten erkennbar |
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
| `title`, `created_at` | Auffindbarkeit |
| `listed_updated_at` | `updated_at` aus der zuletzt geholten Chatliste |
| `exported_updated_at` | Stand, auf dem der vorliegende Export beruht |
| `turns`, `total_turns` | Umfang beim Export |
| `end_token` | letztes `next_page_token`, falls bekannt — nur Rohmaterial für 3.2.5, nichts hängt daran |
| `file` | Name der Chatdatei, oder leer |
| `side_files` | Namen der Nebendateien, damit sie beim Ersetzen mit entfernt werden (2.6) |
| `status` | s. u. |
| `exported_at` | Zeitpunkt |

Statuswerte: `listed` (aus der Chatliste bekannt), `started` (teilweise gelesen — setzt nur der Lese-Weg, der ZIP-Weg schreibt einen Chat immer ganz), `exported`, `stale` (die Quelle ist neuer als der Export), `deleted` (Hülle an der Quelle). `stale` entsteht durch den Vergleich `listed_updated_at` gegen `exported_updated_at`; `updated_at` trägt diese Erkennung, und zwar beobachtet: es liegt in allen drei Quellen vor — Export, `recent_chats`, `read_conversation`-Envelope — und sprang bei gelöschten Chats auf den Löschzeitpunkt.

Auf oberster Ebene trägt das Protokoll `protocol_version`, `project` und `order` — die Bearbeitungsrichtung schreibt nur der Lese-Weg, der ZIP-Weg erhält sie unangetastet: ein Protokoll, ein Schema.

Erfüllt von beiden Wegen und geprüft: `tests/test_wegegleichheit.py` vergleicht auch die Protokolle — gleiche Schlüsselmengen, gleiche Kernfelder, und genau drei Felder dürfen sich unterscheiden, weil ein Weg sie nicht wissen kann: `created_at` (kennt nur der ZIP-Weg), `total_turns` (beweist nur der Lese-Weg), `file` (das Datumssegment fehlt dem Lese-Weg — 2.3).

## 2.5 Wegegleichheit

Beide Wege erzeugen für denselben Chat **dieselbe Chatdatei** und **dasselbe Protokoll** (Protokollabgleich in 2.4). Sonst hinge der Inhalt des Archivs davon ab, auf welchem Weg ein Chat hereinkam, und „habe ich diesen Chat?" würde unscharf.

Wo ein Weg etwas **nicht wissen kann**, steht `null` statt einer Vermutung. Der ZIP-Weg hat kein Sollmaß und behauptet keine Vollständigkeit (`total_turns`, `complete`, `turns_missing` sind `null`); der Lese-Weg kennt kein `created_at` und schreibt `chat_date: "unknown"`. Genau **fünf** Metadatenfelder dürfen sich unterscheiden — `source`, `chat_date`, `total_turns`, `complete`, `turns_missing` — und keines mehr.

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

## 2.10 Zielorte

Primärziel ist `<projekt>/.claude/imported_chats/` im versionierten Repo des Zielprojekts. **Dieselben Dateien** dienen unverändert auch dem Projektwissen einer claude.ai-/Desktop-/Cowork-Instanz; es gibt keine zielabhängige Ausgabeform. Ein Verzeichnis je Quellprojekt, **flach** — Projektwissen kennt keine Unterordner. Niemals nach `~/.claude/projects/…` schreiben; die Gründe stehen in 1.3.

## 2.11 Tests ohne echten Chatinhalt

Prüfstücke werden synthetisch gebaut; echter Chatinhalt gehört nie in Tests oder Fixtures. Echte Exporte liegen ausschließlich unter `test_results/`, deren Inhalte die `.gitignore` vom Repo fernhält. Diagnosewerkzeuge (3.3) geben Struktur und Zahlen aus, nie Inhalt — ihre Ausgabe muss unbedenklich in eine Konversation kopierbar sein.


# 3 Skripte

## 3.1 `chat_export_convert.py` — der Weg über den Kontoexport

**Status: gebaut, 136 Selbsttests, auch unter `-O`. Am Drei-Monats-Export mit 211 Chats gelaufen.**

Wandelt ein Kontoexport-ZIP in Chatdateien je Quellprojekt um und führt das Protokoll. Läuft lokal, wird nie hochgeladen.

### 3.1.1 Aufbau des Export-ZIP

Alles beobachtet, nichts davon dokumentiert.

```
users.json                    uuid, full_name, email_address, verified_phone_number
projects/<uuid>.json  (n×)    uuid, name, description, is_private,
                              prompt_template, created_at, updated_at,
                              creator, docs
memories.json
conversations.json            Liste von Konversationen
```

Projektdateien enthalten **keine Chats** — nur Projektanweisungen und Wissensdokumente. Die Chats liegen ausschließlich in `conversations.json`.

Eine Konversation hat genau sieben Felder: `uuid`, `name`, `summary`, `created_at`, `updated_at`, `account`, `chat_messages`. **Kein Projektbezug.**

Eine Nachricht: `uuid`, `text`, `content`, `sender` (`human`/`assistant`), `created_at`, `updated_at`, `attachments`, `files`, `parent_message_uuid`.

**`attachments` und `files` sind nicht dasselbe**, und die Verwechslung kostet Inhalt:

| Feld | Zahl | Felder | Inhalt |
| ------------- | ---- | ------------------------------------------------------------- | ------ |
| `attachments` | 341  | `file_name`, `file_size`, `file_type`, **`extracted_content`** | **da** |
| `files`       | 524  | `file_uuid`, `file_name`                                      | fehlt  |

Keiner der 341 ist leer, zusammen 9.635.919 Zeichen, Median 13.265, größter 169.818. Dateitypen überwiegend `text/x-python` (238), dazu `text/markdown` (26), `txt` (22), `x-shellscript` (11). Bei **22** ist der `file_name` leer, der Inhalt aber vorhanden — mehrere Kilobyte Code; ein Fragezeichen als Name würde das verstecken.

Blocktypen in `content`: `text`, `thinking`, `tool_use`, `tool_result`, `token_budget`. Bei `token_budget` war `remaining` in allen Fällen `null`. Nichts war als `truncated` oder `cut_off` markiert.

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

### 3.1.4 Dateiformat der Chatdateien

Format, Felder, Dateinamen und die Referenzmechanik sind die Vorgaben **2.2** und **2.3**; hier steht nur, was dieser Weg davon besonders macht.

Der ZIP-Weg ist der einzige, der `branches`, `dropped_duplicates`, `dropped_blocks`, `dropped_thinking` und die beiden `attachments_*`-Felder je mit Inhalt füllen kann — nur er sieht den Nachrichtenbaum und die Blockstruktur (2.5). Beim Drei-Monats-Export entstanden so 211 Gesprächs-, 145 Denk- und 62 Anhangdateien.


### 3.1.5 Aufbau des Protokolls

Das Protokoll ist Vorgabe **2.4**. Dieser Weg füllt weder `end_token` (das kennt nur der Lese-Weg) noch `total_turns` (er hat kein Sollmaß, 2.5) und benutzt `started` nie — er schreibt einen Chat immer ganz.


### 3.1.6 Kommandos

- `list --map <dump> --out <verzeichnis>` — Protokoll anlegen oder ergänzen aus einer Chatliste. Neue Chats `listed`, vorhandene gegen `exported_updated_at` geprüft und ggf. `stale`. **Der erste Schritt jedes Laufs**, vor jedem Chattext.
- `convert --zip <datei> --out <verzeichnis>` — die als `listed` oder `stale` geführten Chats aus dem ZIP holen, Baum ablaufen, Dateien schreiben, Protokoll fortschreiben.
- `diff --out <verzeichnis>` — Stand aus dem Protokoll: fehlend, veraltet, gelöscht, unbekannt. Braucht weder ZIP noch Chatdateien. Dazu der Waisen-Scan nach Vorgabe 2.6 — das Einzige, was ein Zuviel statt eines Zuwenig meldet.
- `report --out <verzeichnis>` — was verloren geht: Hüllen, übersprungene Dubletten, weggelassene Blocktypen, `files`-Verweise ohne Inhalt. Nebenzweige und Anhänge mit Inhalt stehen nicht als Verlust darin, weil sie mitkommen — wohl aber ihre Zahl, damit sichtbar ist, dass ein Chat nicht linear verlief bzw. wie viel Fremdmaterial daran hing.

- `analyse --zip <datei> [--map <dump>]` — beschreibt, was der Leser aus einem Archiv macht, ohne etwas zu schreiben: gewählter Pfad, Nebenzweige, Verluste, und bei gegebener Zuordnung die UUIDs, die das Archiv nicht kennt. Beantwortet eine andere Frage als 3.3 — das beschreibt den Rohexport, dieses die *Deutung*.

Dazu ein fertig einfügbarer Textblock für die **Projektanweisungen**: dass ein Chatarchiv vorliegt, wo es liegt, und dass es vor einer Rückfrage zu älterem Zusammenhang zu konsultieren ist. Damit wirkt die Anweisung dauerhaft.

### 3.1.7 Prüfung

- **Wegegleichheit:** `tests/test_wegegleichheit.py`, 31 Checks — der Wächter der Vorgabe 2.5. Stellt dieselbe Konversation beiden Wegen hin und vergleicht Dokument gegen Dokument, dann Datei gegen Datei über die zwei Kommandozeilen; prüft, dass genau die fünf erlaubten Metadatenfelder abweichen und dass nach Entfernen der Referenzfelder zwei identische Transkripte bleiben.
- Synthetisches ZIP als Prüfstück: Verzweigung, abweichendes `text`, Hülle, null Nachrichten, Dateiverweise, alle Blocktypen — ohne echten Chatinhalt (Vorgabe 2.11).
- `diff` gegen einen Bestand mit bekannter Lücke und einem veralteten Chat.
- Vertippte UUID in einer Zuordnungsdatei wird gemeldet, nicht verschluckt.
- **Integrität:** jede Nachricht landet auf dem gewählten Pfad, in einem Nebenzweig oder in der Dublettenzählung. Am Drei-Monats-Export: 7.393 im Export, 7.393 abgelegt oder gezählt.
- Lauf gegen ein echtes ZIP: **erledigt**. 211 Chats in 1,1 Sekunden, 33 MB, davon 13 MB Gesprächsdateien; 211 Gesprächs-, 145 Denk- und 62 Anhangdateien. Alle Summen deckungsgleich mit unabhängig gemessenen: 5 Hüllen, 29 Sendewiederholungen, 1.367 verworfene Denkblöcke, 18 Nebenzweige, 341 Anhänge mit Inhalt, 524 reine Namensverweise.

### 3.1.8 Offen

- Ob die Projektzuordnung in die Datei gehört oder nur in den Verzeichnisbaum.
- Ob `predecessor`/`successor` nach §1.12 automatisch bestimmbar sind. Bei Chats desselben Projekts mit Zeitstempeln vermutlich ja — unbelegt, wird zunächst leer gelassen.

## 3.2 `chat_read_store.py` — der Weg über `read_conversation`

**Status: gebaut, 107 Selbsttests, auch unter `-O`.**

### 3.2.1 Was die Umgebung hier hergibt — und was nicht

**Was nicht:** `read_conversation` liefert das **gerenderte Transkript**, keine Blockstruktur: `<turn n="0">Human: …</turn>`. Damit fehlen ihm zwei Dinge, die der Kontoexport hat, und das ist keine Einschränkung der Umsetzung, sondern der Quelle:

- **Denkschritte.** Im Export sind das 4.318 Blöcke mit 9,2 Mio Zeichen behaltenswerten Inhalts (3.1.1). Hier kommen sie nicht vor.
- **Anhänge.** Im Export 341 Dateien mit 9,6 Mio Zeichen `extracted_content`. Hier ebenfalls nicht.

Zusammen ist das etwa so viel wie der Gesprächstext selbst. **Ein über diesen Weg geholter Chat bleibt dauerhaft ärmer**, und ein späterer Export ergänzt es nicht — er kann den Chat nur ersetzen, weil der Bezug zwischen Nachricht und Block nachträglich nicht herstellbar ist.

Was dieser Weg dafür kann und der Export nicht: **Vollständigkeit beweisen** (3.2.2) und **sofort** liefern, ohne Antrag und Wartezeit.

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

`overview`, `state`, `map`, `ingest`, `status`, `export`.

`ingest` setzt `started` — eine Seite zu lesen *ist* das Aufnehmen der Arbeit; `read_conversation` liefert genau einen Chat je Aufruf, Absicht und Wirkung fallen zusammen. `export` setzt `done` nur bei bewiesener Vollständigkeit; ein Teilexport bleibt `started` und sagt es.

`map` ist der Zulieferer der Projektzuordnung und bleibt auch im Weg 3.1 gebraucht — und es setzt `stale`, wenn eine frische Liste einen neueren Stand zeigt als der Export. Die Statusführung folgt Vorgabe 2.4: dasselbe `protokoll.json` wie der ZIP-Weg, `started` und `deleted` setzt nur dieser Weg (letzteres nur von Hand — aus einer Fehlermeldung ist Löschung nicht von Unzugänglichkeit unterscheidbar).

### 3.2.4 Transkriptionsdisziplin

Es gilt Vorgabe **2.8**. Wegspezifisch ist nur das Verfahren bei zu großen Seiten: auf mehrere `ingest`-Aufrufe aufteilen oder ein Präfix an einer Sprechergrenze abschneiden — der Rest der Seite kommt beim nächsten Blättern ohnehin wieder.


### 3.2.5 Konvergenz und was offen bleibt

`export` erzeugt das Format nach Vorgabe 2.2 — denselben Metadatensatz in derselben Reihenfolge wie der ZIP-Weg —, benennt die Datei nach Vorgabe 2.3 (Datum ehrlich `ohne-datum`, weil `read_conversation` kein `created_at` liefert) und schreibt den Protokolleintrag nach Vorgabe 2.4 samt `end_token`. Geprüft durch `tests/test_wegegleichheit.py`, Chatdateien wie Protokolle; die erlaubten Abweichungen nennen 2.5 und 2.4.

Offen bleibt: **Zuwachs nachladen statt ersetzen.** Zu erforschen ist, wie man an einer definierten Stelle einsteigt — ob ein gespeichertes `next_page_token` über Tage gültig bleibt (nicht dokumentiert), oder ob es einen anderen Weg gibt, ab einem Turn-Index zu lesen. `read_conversation` nimmt heute nur `conversation_id`, `page_token` und `max_turns`; ein „ab Turn N" gibt es nicht. Bis das geklärt ist, gilt die Ersetzung als Ganzes — korrekt, nur teurer.

## 3.3 `inspect_export.py` — Diagnose eines Export-ZIP

**Status: gebaut, eigener Selbsttest, auch unter `-O`.** Die Scratchpad-Fassung ging beim Sitzungswechsel verloren und wurde aus dem Verlauf rekonstruiert — der Beleg, dass flüchtige Ablagen keine Werkzeuge halten.

Liest ein Kontoexport-ZIP ohne zu entpacken und berichtet Struktur und Zahlen, **nie Chatinhalt** (Vorgabe 2.11 — der Selbsttest weist mit Markertexten nach, dass nichts davon in der Ausgabe erscheint; Titel erscheinen bewusst, sie identifizieren die Chats). Aufruf: `inspect_export.py <export.zip>`.

Prüft: Archivinhalt; Anzahl, Zeitraum und Umfang der Konversationen; ausgehöhlte Konversationen samt der Löschungs-Erklärung aus 3.1.3; Verzweigungen je Chat; Blocktypen und Wahrheitsflaggen; die `text`-Blöcke-Abweichung (das flache Feld trägt die Denkschritte); **`attachments` mit `extracted_content` getrennt von reinen Namensverweisen** — der Prüfpunkt aus 4.2; und als Schemawache die Vereinigung aller Konversations-, Nachrichten- **und Blockschlüssel** zum Vergleich mit 3.1.1.

Es beantwortet eine andere Frage als `analyse` (3.1.6): dieses beschreibt den Rohexport, jenes die Deutung.

## 3.4 `chat_crawl_store.py` — Rekonstruktion aus Suchschnipseln

**Status: gebaut, 175 Selbsttests. Überholt, wo `read_conversation` existiert.**

Rekonstruiert Chats aus überlappenden Suchschnipseln, für Umgebungen ohne `read_conversation`.

**Warum überholt:** Am echten Lauf zeigte sich, dass `conversation_search` **feste, nicht überlappende Blöcke** liefert — zwischen 23 Segmenten dreier Chats gab es null Overlap. Die Overlap-Mechanik, das Herz des Skripts, hat damit fast nichts zu verbinden: der Crawl sammelt Text, ohne ihn zusammenzusetzen.

**Was daran gültig bleibt** und in 3.2 übernommen wurde: Zustandsdatei mit Status und Bearbeitungsrichtung, Rundenbegriff, Übergabeprozedur, Transkriptionsdisziplin, Upload-Probe.

Erhaltenswerte Einzelbefunde: Suchtreffer tragen `H: `/`A: `-Label und HTML-Entities; ein Auslassungszeichen wird nur als Lückenmarke erkannt, wenn es zwischen zwei Nicht-Leerzeichen klemmt — `abc ... def` und eine einzelne `...`-Zeile landen ohne jede Warnung im Transkript.

Ob das Skript bleibt, ist zu entscheiden, sobald sich 3.1 und 3.2 bewährt haben.


---

# 4 Projektpflege — Anthropic-Entwicklung

Anthropic baut an Export, Werkzeugen und Plattform laufend um; nichts hiervon ist zugesichert, das meiste nur beobachtet (2.1). Dieses Kapitel ist die **Prüfliste**: alles, was regelmäßig zu kontrollieren ist, gesammelt an einem Ort — bewusst auch dort wiederholt, wo es anderswo im Dokument verbaut ist. Bei einer Abweichung: betroffene Zeile in 1.6 bzw. Kapitel 3 korrigieren, prüfen, was daran hing, und wenn eine Annahme fällt, 1.7 ergänzen.

## 4.1 Testwerkzeuge

**Ziel:** Ein Satz kleiner Prüfwerkzeuge, mit denen sich vor einem Lauf schnell feststellen lässt, ob **(a)** das Kontoexport-Format und **(b)** die Werkzeugschnittstellen der Claude-Instanz (`recent_chats`, `read_conversation`, `conversation_search`) noch den hier dokumentierten Beobachtungen entsprechen — als Frühwarnung, bevor eine Änderung still Falsches produziert.

Vorhandene Bausteine, auf denen das aufsetzen kann: `inspect_export.py` (3.3) als Schemawache des Exports; die Format- und Upload-Proben in den Docstrings von 3.2 und 3.4 decken die Instanzseite bislang manuell ab. Mehr als das Ziel ist hier bewusst nicht festgelegt.

## 4.2 Kontoexport — was verwendet wird und zu prüfen ist

- Anforderung unter **Settings → Privacy → Export data**, Lieferung als Link per E-Mail, Link verfällt nach 24 h (belegt). **Die Zeitraumauswahl ist nirgends dokumentiert** — sie ist beobachtet und praktisch wichtig, denn auf ihr beruht das Nachpflegen (1.5). Fällt sie weg, wird jeder Lauf zum Vollexport.
- Dateiname `data-<uuid>-…-batch-0000.zip`; die batch-Zahl war bisher immer 0 — möglicherweise stückeln größere Exporte, nie beobachtet.
- Archivaufbau: `users.json`, `projects/<uuid>.json`, `memories.json`, `conversations.json` (3.1.1). Projektdateien enthalten **keine** Chats.
- Konversation: genau sieben Felder, **kein Projektbezug** — die Chatliste aus dem Projekt ist die einzige Zuordnungsquelle (1.6).
- Nachricht: `parent_message_uuid` macht die Nachrichten zum **Baum** (3.1.2); `sender` `human`/`assistant`; das flache `text` enthält die Denkschritte (3.1.1); `content`-Blocktypen `text`, `thinking`, `tool_use`, `tool_result`, `token_budget`.
- **`attachments` tragen `extracted_content`, `files` nur Namen** (3.1.1) — die Unterscheidung entscheidet, was das Archiv behalten kann.
- Gelöschte Chats erscheinen als Hüllen: Gerüst da, Inhalt leer (3.1.3).
- Erste Anlaufstelle bei Verdacht: `inspect_export.py` (3.3) laufen lassen und die Schlüsselmengen mit 3.1.1 vergleichen.

## 4.3 Werkzeuge der Claude-Instanz — was verwendet wird und zu prüfen ist

- `recent_chats(n≤20, sort_order, before, after)` — Zeit-Cursor, liefert die Chatliste; einzige Quelle der Projektzugehörigkeit.
- `read_conversation(conversation_id, page_token, max_turns≤50)` — Envelope mit `url`, `updated_at`, `total_turns`, `turns`, `next_page_token`/`prev_page_token`; Seitengröße durch Zeichenbudget (~8 Turns beobachtet); liest den *live store*; **scope-gebunden** (im Projekt nur dessen Chats); lehnt Cowork-IDs (`cse_…`) am Format ab; liefert das gerenderte Transkript **ohne** Denkschritte und Anhänge (3.2.1).
- `conversation_search(query, max_results≤10)` — liefert feste, **nicht überlappende** Blöcke; `H: `/`A: `-Labels; HTML-Entities kodiert (3.4).
- Prüfweg: die Format-/Upload-Proben in den Docstrings von 3.2/3.4 einmal je Umgebung durchgehen; weicht der Envelope ab, zuerst 3.2.1 nachziehen.

## 4.4 Plattformverhalten claude.ai — was den Entwurf trägt

- Kontextfenster 1 Mio Token (Opus 5/Sonnet 5, bezahlte Pläne, belegt); lange Chats werden **zusammengefasst statt abgebrochen**, und die Instanz erhält kein Kontextsignal (Opus ohne Budget-Tags) — darauf beruht, dass Übergaben zählergetrieben sind (3.4-Historie) und der Export-Weg bevorzugt wird (1.2).
- Projektwissen: Textextraktion; RAG schaltet ab undokumentierter Schwelle automatisch (Community: Dateianzahl); Projektdateien im Container *„while remaining in context"* — Containerzugriff spart keinen Kontext (1.6).
- Chat-Upload: 20 Dateien je Chat, JSON belegt zulässig — trägt die Übergabe der Protokolldatei (1.4/1.5).
- Container-Netzzugang nur gegen Allowlist, `claude.ai` steht nicht darauf — ein Skript im Container kann den Export-Link nicht laden (1.7).
- Claude-Code-Seite: `~/.claude/projects/…` wird nach `cleanupPeriodDays` (Standard 30 Tage) aufgeräumt — deshalb Vorgabe 2.10.
- Cowork: eigene ID-Welt, über beide Wege unerreichbar (1.6) — Entwicklung beobachten, Anthropic könnte hier den Umzugsweg schaffen, der dieses Werkzeug ablöst.