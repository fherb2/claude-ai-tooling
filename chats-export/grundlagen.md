# Grundlagen und Bauplan

Dieses Dokument hält fest, worauf die Werkzeuge in diesem Ordner aufbauen,
und was als nächstes gebaut wird. Es existiert, weil in einer einzigen
Arbeitssitzung vier Annahmen über die Umgebung gekippt sind — wer sie nicht
einzeln aufführt, merkt den fünften Sturz nicht.

**Beleglage wird durchgehend ausgewiesen.** „Belegt" heißt: in einem
Anthropic-Dokument nachlesbar, mit Quelle. „Beobachtet" heißt: am laufenden
System gesehen, aber nirgends dokumentiert. „Community" heißt: von Dritten
berichtet, unbestätigt. Die drei werden nicht vermischt.

---

## 1 Ziel

Chats aus claude.ai-Projekten sollen **im Zusammenhang ihres Projekts
durchsuchbar** sein — nicht fortführbar. Sie dienen dazu, früher besprochenen
Kontext wiederzufinden.

Primärer Zielort ist `<projekt>/.claude/imported_chats/` in dem Git-Repo, in
dem mit Claude Code am Code dieses Projekts gearbeitet wird. Dort sind die
Dateien über `Read`/`Grep` erreichbar: kein Projektwissen, kein RAG, kein
undokumentierter Schwellwert, und kein Kontextverbrauch, bis wirklich gelesen
wird.

Dieselben Dateien lassen sich unverändert zusätzlich ins
claude.ai-Projektwissen legen — JSON ist ein belegter Upload-Typ und
Projektdateien werden per Textextraktion verarbeitet. Das braucht keine
zweite Ausgabeform.

Es ist ein **wiederkehrender Abgleich**, keine einmalige Migration: neue Chats
kommen laufend hinzu, vorhandene können weitergelaufen sein.

Neben den Chatdateien gibt es **genau eine** weitere Datei: das Protokoll. Es
ist in jedem Schritt beider Lösungswege die Referenz und sagt einer Instanz
sofort, wo der Stand ist und wo fortzusetzen wäre.

Als Zielort kommen in Frage: das Git-Repo eines Claude-Code-Projekts
(`<projekt>/.claude/imported_chats/`, der Regelfall) oder das Projektwissen
einer claude.ai-/Desktop-/Cowork-Instanz. **Dieselben Dateien** dienen beidem;
es gibt keine zweite Ausgabeform.

Ausdrücklich **nicht** nach `~/.claude/projects/…` — Begründung in 4.3.

---

## 2 Umgebungsannahmen

| Aussage | Beleglage |
|---|---|
| Kontoexport unter Settings → Privacy, Downloadlink per E-Mail, Link verfällt nach 24 h, für Free/Pro/Max | belegt ([9450526](https://support.claude.com/en/articles/9450526-export-your-claude-data)) |
| Export enthält *„conversation data and the user data for your account"* — kein Format, kein Schema, keine Vollständigkeitsaussage | belegt (ebd.) |
| Gelöschte Inhalte *„will not be included in data exports initiated after the deletion"* | belegt ([13346720](https://support.claude.com/en/articles/13346720-export-your-organization-s-data)) |
| **Der Export lässt einen Zeitraum wählen** | **beobachtet**, in keinem Artikel erwähnt |
| ZIP-Aufbau: `users.json`, `projects/<uuid>.json`, `memories.json`, `conversations.json` | beobachtet |
| Eine Konversation hat genau 7 Felder; **kein Projektbezug** | beobachtet |
| `text` weicht bei 2.478 von 7.393 Nachrichten von den `content`-Textblöcken ab | beobachtet |
| Blocktypen: `text`, `thinking`, `tool_use`, `tool_result`, `token_budget` | beobachtet |
| `token_budget.remaining` war in allen Fällen `null` | beobachtet |
| Nachrichten bilden einen **Baum** über `parent_message_uuid` | beobachtet (1 Fall in 211 Konversationen) |
| Gelöschte Chats erscheinen als **Hüllen**: Skelett vorhanden, Inhalt leer | beobachtet, im Browser gegengeprüft (nicht mehr auffindbar) |
| Dateianhänge nur als `file_uuid` + `file_name`, **ohne Inhalt** | beobachtet (524 Verweise) |
| `read_conversation(conversation_id, page_token, max_turns)` liefert den vollen Turn-Text, `total_turns` im Envelope, Blättern in beide Richtungen, liest den *live store* | belegt (Werkzeugbeschreibung) + beobachtet (Text wortidentisch) |
| Seitengröße von einem Zeichenbudget begrenzt, ~8 Turns beobachtet trotz `max_turns=50` | beobachtet |
| `read_conversation` ist **scope-gebunden**: dieselbe UUID liest im Projekt und scheitert außerhalb | beobachtet (Kontrollversuch) |
| Cowork-IDs (`cse_…`) werden von `read_conversation` an der Formatprüfung abgewiesen | beobachtet |
| `conversation_search` liefert **feste, nicht überlappende Blöcke** | beobachtet (null Overlap zwischen 23 Segmenten) |
| Projektdateien: 30 MB je Datei, Anzahl unbegrenzt, *„total content must fit within Claude's context window"*, *„Text extraction only"* | belegt ([8241126](https://support.claude.com/en/articles/8241126-upload-files-to-claude)) |
| RAG für Projekte schaltet **automatisch** nahe der Kontextgrenze ein, *„up to 10x"* Kapazität, Claude nutzt dann ein *project knowledge search tool*; **kein Schwellwert dokumentiert**, nicht steuerbar | belegt ([11473015](https://support.claude.com/en/articles/11473015-retrieval-augmented-generation-rag-for-projects)) |
| Projektdateien im Container *„accessible … **while remaining in context**"* — spart also **keinen** Kontext | belegt ([12111783](https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude)) |
| Container-Netzzugang nur gegen eine Allowlist (Paketmanager, `api.anthropic.com`, `statsig.anthropic.com`); `claude.ai` steht **nicht** darauf | belegt (ebd.) |
| Kontextfenster Opus 5 / Sonnet 5: 1 Mio Token auf bezahlten Plänen | belegt ([8606394](https://support.claude.com/en/articles/8606394-how-large-is-the-context-window-on-paid-claude-plans)) |
| Ein langes Gespräch bricht nicht ab, sondern **fasst frühere Teile zusammen** | belegt (ebd.) |
| Opus 4.7 und spätere Opus-Modelle erhalten **keine** Token-Budget-Tags | belegt ([Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows)) |
| Claude-Code-Transkripte unter `~/.claude/projects/<p>/<id>.jsonl`; Format *„internal to Claude Code and changes between versions"*; Aufräumung nach 30 Tagen; **kein Import** | belegt ([sessions](https://code.claude.com/docs/en/sessions)) |
| RAG-Schwellwert richte sich nach **Dateianzahl**, nicht Größe (13 Dateien, „2 % Kapazität") | Community ([#25759](https://github.com/anthropics/claude-code/issues/25759)), von Anthropic als `invalid` geschlossen |

### Widersprüche in der Anthropic-Doku

Nicht aufgelöst, nur benannt:

- Dateigröße beim Upload: 500 MB ([8241126](https://support.claude.com/en/articles/8241126-upload-files-to-claude)) gegen *„30MB per file for both uploads and downloads"* ([12111783](https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude)).
- Projektwissen: *„must fit within Claude's context window"* gegen *„you can continue adding knowledge beyond these limits"* (RAG-Artikel).
- RAG-Verfügbarkeit: *„available for all Claude plans"* gegen *„only available to users with paid Claude plans"* ([9517075](https://support.claude.com/en/articles/9517075-what-are-projects)).

---

## 3 Migrationsmatrix

### Heraus

| Quelle | Weg | Format | Haken |
|---|---|---|---|
| claude.ai, alle Chats | Kontoexport | ZIP, `conversations.json` | kein Projektbezug; Gelöschtes als Hülle; Anhänge ohne Inhalt; Momentaufnahme |
| claude.ai, ein Projekt | `read_conversation` | Turns mit Index, `total_turns` | scope-gebunden; muss durch den Kontext |
| claude.ai, ein Projekt | `recent_chats` | UUID, Zeit, Titel | **einzige Quelle für die Projektzugehörigkeit** |
| Claude Code CLI | `/export [datei]` | Plain Text | kein JSON |
| Claude Code CLI | `<id>.jsonl` | JSONL | Format ausdrücklich instabil; 30 Tage |
| Cowork, Cloud | Sitzungsexport → `transcript.jsonl` | JSONL | Auslöser nirgends dokumentiert |
| Cowork, Cloud, Enterprise | Compliance API | JSON | nur Enterprise + Compliance-Key |
| Cowork, lokal | Dateisystem | `local_<uuid>.json` | offiziell nur für die 3P-Variante dokumentiert |

### Hinein

| Ziel | Weg | Haken |
|---|---|---|
| Git-Repo für Claude Code | Datei im Arbeitsverzeichnis | **der gewählte Weg**; keine fortsetzbare Sitzung |
| claude.ai-Projekt | Projektwissen hochladen | bleibt im Kontext bzw. wird per RAG durchsucht |
| claude.ai-Chat | Datei anhängen | 20 Dateien je Chat |
| claude.ai, neuer Chat | — | **kein dokumentierter Mechanismus** |
| Cowork-Projekt | Ordner verbinden | Cowork-Projekte sind lokal, nicht synchronisiert |

**Kernaussage:** Es gibt kein „Chat als Chat migrieren". Jeder Weg verwandelt
eine Konversation in Dateien. Die zwei echten Sitzungsübergaben (`--teleport`,
„Continue in") sind kontobasiert und gehen nie von einer Datei aus.

### Grenzen, die bleiben

- **Cowork ist über beide Wege unerreichbar.** Lücke, keine Aufgabe.
- **Gelöschte Chats sind unwiederbringlich.** Der Export enthält sie als
  Hüllen und sagt nicht, dass es Hüllen sind.
- **Dateianhänge gehen verloren.** Hochgeladener Code ist im Export nur ein
  Name.
- **Die Projektzugehörigkeit gibt es nur in claude.ai.** Das ist der einzige
  Punkt, an dem die Werkzeuge dort unentbehrlich bleiben.

---

## 4 Bauplan

### 4.1 Zwei Wege, eine Ablage

| | Nachholen | Fortschreiben |
|---|---|---|
| Anlass | viele alte Chats | wenige neue |
| Quelle | Export-ZIP | `read_conversation` |
| Kontextkosten | null | wenige Seiten |
| Werkzeug | `chat_export_convert.py` (neu) | `chat_read_store.py` (vorhanden) |

**Verbindliche Anforderung:** Beide Wege erzeugen für denselben Chat **dieselbe
Datei**. Sonst hängt der Inhalt des Archivs davon ab, auf welchem Weg ein Chat
hereinkam, und „habe ich diesen Chat?" wird unscharf.

### 4.2 Dateiformat

Nach §1.12 der Arbeitsanweisungen: JSON, `messages` mit `role`
(`user`/`assistant`) und `content`, dazu ein `metadata`-Objekt mit
`chat_date`, `imported_at`, `predecessor`, `successor`.

Das dortige Schema ist ausdrücklich ein **Beispielschema**, also ein
Mindestbestand. Zusätzlich geführt werden — projektintern hier dokumentiert,
nicht global:

| Feld | Wozu |
|---|---|
| `chat_uuid`, `title` | Identität und Auffindbarkeit |
| `source` | `account-export` oder `read_conversation` |
| `source_updated_at` | Stand der Quelle beim Import — **macht Veralten erkennbar** |
| `turns` | Anzahl importierter Redebeiträge |
| `total_turns` | nur beim Weg über `read_conversation`: belegt Vollständigkeit |
| `complete` | ob alles vorliegt, mit den zwei Zahlen daneben |
| `deleted` | Hülle eines gelöschten Chats, ohne `messages` |
| `dropped_branches` | verworfene Zweige des Nachrichtenbaums |
| `dropped_blocks` | weggelassene Blocktypen je Anzahl |
| `attachments_without_content` | Dateinamen, deren Inhalt der Export nicht hat |

Ohne `source_updated_at` und `turns` ist „ist dieser Chat veraltet?" nicht
entscheidbar, ohne ihn neu zu holen — genau der Aufwand, den der Abgleich
vermeiden soll.

Dateiname: `JJJJ-MM-TT_titel-slug.json`.

### 4.3 Entscheidungen und ihr Grund

| Entscheidung | Grund |
|---|---|
| Baum entlang `parent_message_uuid`, **jüngster** Zweig | Sortieren nach `created_at` schreibt nachbearbeitete Fragen doppelt ins Transkript. Der jüngste Zweig ist, was die Oberfläche zeigt. |
| `content`-Blöcke statt `text` | `text` weicht bei einem Drittel der Nachrichten ab |
| Hüllen mit `deleted: true` und ohne `messages` | Die Existenz bleibt erhalten, ohne ein leeres Transkript vorzutäuschen |
| Zuordnung aus rohem `recent_chats`-Dump | Kein Formatieren von Hand nötig |
| Jede zugeordnete UUID gegen das ZIP prüfen | Ein vertippter Wert würde einen Chat still falsch einordnen |
| **Nicht** nach `~/.claude/projects/…` schreiben | Drei Gründe: dort wird nach `cleanupPeriodDays` (Standard **30 Tage**) automatisch gelöscht — *„Files in the paths below are deleted on startup once they're older than"* ([claude-directory](https://code.claude.com/docs/en/claude-directory)); der Ort ist nicht versioniert und *„not shared across machines"*, während `<projekt>/.claude/` gerade deshalb versioniert wird; und §1.2 der Arbeitsanweisungen behält `~/.claude/` der Engine vor. Die dortige Ordnernamens­struktur bleibt als Zuordnungshilfe nützlich. |
| Protokoll ins **Projektwissen**, nicht in Artefakte | Artefakte kennen keinen JSON-Typ, kein spezifiziertes Downloadformat, und der einzige dokumentierte Rückweg in einen neuen Chat ist manuelles Kopieren ([9487310](https://support.claude.com/en/articles/9487310-what-are-artifacts-and-how-do-i-use-them)) |
| Protokoll ins Projektwissen des **Quellprojekts** | Lösung 2 läuft dort, weil nur dort `read_conversation` greift. Nebeneffekt: das Quellprojekt trägt selbst die Auskunft, was von ihm exportiert wurde. |
| **Ein Protokoll als Referenz**, nicht der Verzeichnisinhalt | Innerhalb von claude.ai gibt es kein Verzeichnis zum Ablesen — dort existiert nur, was hochgeladen wurde. Eine kleine Datei kann eine Instanz lesen, N Chatdateien durchzählen nicht. |
| `metadata` trotzdem in jeder Chatdatei | Jede Datei bleibt für sich verständlich, auch wenn sie einzeln weitergegeben wird. Bei Widerspruch gilt das Protokoll. |

### 4.4 Das Protokoll

Eine Datei je Quellprojekt, `protokoll.json`, neben den Chatdateien. Sie wird
**bei der Erstellung der Chatliste angelegt** — in beiden Lösungswegen, noch
bevor ein einziger Chat geholt ist. Ab da ist sie die Referenz.

Je Chat:

| Feld | Wozu |
|---|---|
| `title`, `created_at` | Auffindbarkeit |
| `listed_updated_at` | `updated_at` aus der zuletzt geholten Chatliste |
| `exported_updated_at` | Stand, auf dem der vorliegende Export beruht |
| `turns`, `total_turns` | Umfang beim Export; belegt Vollständigkeit |
| `end_token` | letztes `next_page_token`, falls bekannt — nur Rohmaterial für die Forschung aus 4.8, nichts hängt daran |
| `file` | Name der Chatdatei, oder leer |
| `status` | `listed`, `exported`, `stale`, `deleted` |
| `exported_at` | Zeitpunkt |

**So wird Zuwachs ohne die Chatdateien erkannt:** Eine frische Chatliste
liefert je Chat ein `updated_at`. Ist es neuer als `exported_updated_at`, wurde
weitergechattet — `status` wird `stale`. Die Instanz fordert dann **nur diese**
Chats an. Der Vergleich braucht nichts als das Protokoll und die neue Liste;
kein Chatarchiv, kein ZIP, kein Zeichen Chattext.

Der Zeitstempel trägt das, und zwar beobachtet, nicht vermutet: `updated_at`
liegt in **allen drei** Quellen vor — im Export, in `recent_chats` und im
Envelope von `read_conversation`. Dass er auf Änderungen anspringt, hat sich
bei den gelöschten Chats gezeigt: dort trug er exakt den Löschzeitpunkt,
sekundengleich über zwei Konversationen hinweg.

**Ein veralteter Chat wird als Ganzes ersetzt.** Das ist die Festlegung, und
sie macht den Entwurf von keiner undokumentierten Eigenschaft abhängig: Ein
Chat, der sich verlängert hat, wird neu geschrieben, nicht fortgeschrieben.
Aus dem ZIP kostet das nichts. Über `read_conversation` kostet es den ganzen
Chat erneut durch den Kontext — hinzunehmen, weil es nur die tatsächlich
geänderten trifft.

Den Zuwachs stattdessen **nachzuladen** bleibt das Ziel, ist aber noch
Forschung (4.8) und keine Voraussetzung.

### 4.5 Die zwei Lösungswege im Ablauf

**Lösung 1 — Massenexport.** Für umfangreiches Nachholen.

1. Kontoexport anfordern, ZIP herunterladen. Zeitraum wählbar.
2. Je Quellprojekt: dort die Chatliste anfordern, Antwort als Datei ablegen.
3. Lokal mit Claude Code: `convert` legt oder ergänzt das Protokoll, holt die
   Chats des Projekts aus dem ZIP an einen temporären Ort und schreibt sie
   dann an den Zielort.
4. Protokoll ins Projektwissen des Quellprojekts zurück — sonst weiß
   Lösung 2 beim nächsten Mal nicht, was schon da ist.

**Die Instanz ist das Frontend.** Kein Parametrierungswerkzeug: sie fragt, ob
es eine vollständige Migration oder eine Aktualisierung auf Basis eines
vorhandenen Protokolls ist, welche Projekte gemeint sind, und wohin geschrieben
wird. Dann ruft sie das Skript entsprechend auf.

**Lösung 2 — aus dem Chat heraus.** Für wenige neue oder veraltete Chats.

Läuft im Quellprojekt über `read_conversation`, wie erprobt. Liegt ein
Protokoll im Projektwissen, ist es Ausgangspunkt und nur Fehlendes und
`stale`-Markiertes wird geholt; liegt keines vor, wird es aus der Chatliste
angelegt. Nachteil: der Chattext muss durch den Kontext. Vorteil: sofort, ohne
Export-Antrag und ohne ZIP.

Beide Wege erzeugen dieselben Chatdateien **und** dasselbe Protokollformat.

### 4.6 Einheiten

**Neu: `chats-export/source/chat_export_convert.py`**

- `list --map <dump> --out <verzeichnis>` — Protokoll anlegen oder ergänzen
  aus einer Chatliste. Neue Chats werden `listed`, vorhandene gegen
  `exported_updated_at` geprüft und ggf. `stale`. **Der erste Schritt jedes
  Laufs**, vor jedem Chattext.
- `convert --zip <datei> --out <verzeichnis>` — die als `listed` oder `stale`
  geführten Chats aus dem ZIP holen, Baum ablaufen, Dateien nach 4.2
  schreiben, Protokoll fortschreiben.
- `diff --out <verzeichnis>` — Stand aus dem Protokoll: fehlend, veraltet,
  gelöscht, unbekannt. Braucht weder ZIP noch Chatdateien.
- `report --out <verzeichnis>` — was verloren geht: Hüllen, verworfene
  Zweige, weggelassene Blöcke, Anhänge ohne Inhalt.

Ein Verzeichnis je Quellprojekt, **flach**. Für das Repo ist es
`<projekt>/.claude/imported_chats/`, für das Projektwissen dasselbe
Verzeichnis zum Hochladen — Projektwissen kennt keine Unterordner. Deshalb
braucht es keine zielabhängige Ausgabeform.

**Änderung an `chats-export/source/chat_read_store.py`**

- `export` erzeugt das Format aus 4.2 statt des eigenen Dokuments — die
  Konvergenz nach 4.1.
- `map` bleibt unverändert; es ist der Zulieferer der Projektzuordnung.

**Textblock für die Projektanweisungen**

`convert` schreibt einen fertig einfügbaren Absatz mit: dass ein Chatarchiv
vorliegt, wo es liegt, und dass es vor einer Rückfrage zu älterem
Zusammenhang zu konsultieren ist. Damit wirkt die Anweisung dauerhaft und
muss nicht je Chat wiederholt werden.

### 4.7 Prüfung

- **Wegegleichheit:** einen Chat, der im ZIP liegt *und* über
  `read_conversation` lesbar ist, über beide Wege umwandeln und die Dateien
  vergleichen. Weichen sie ab, ist 4.1 verletzt.
- Synthetisches ZIP als Prüfstück: Verzweigung, abweichendes `text`, Hülle,
  null Nachrichten, Dateiverweise, alle Blocktypen. **Kein echter
  Chatinhalt in den Tests.**
- `diff` gegen einen Bestand mit bekannter Lücke und einem veralteten Chat.
- Vertippte UUID in einer Zuordnungsdatei wird gemeldet, nicht verschluckt.
- Beide Testsuiten grün, auch unter `-O`.

### 4.8 Offen

- **Zuwachs nachladen statt ersetzen.** Ziel, noch nicht gebaut. Zu erforschen
  ist, wie man an einer definierten Stelle in einen Chat einsteigt: ob ein
  gespeichertes `next_page_token` über Tage gültig bleibt (nicht dokumentiert),
  oder ob es einen anderen Weg gibt, ab einem Turn-Index bzw. ab einem
  Zeitstempel zu lesen. `read_conversation` nimmt heute nur
  `conversation_id`, `page_token` und `max_turns` — ein „ab Turn N" gibt es
  nicht. Bis das geklärt ist, gilt die Ersetzung als Ganzes aus 4.4; sie ist
  korrekt, nur teurer.
- Wie `thinking`- und `tool_use`-Blöcke abgebildet werden, falls sie
  mitkommen sollen. Derzeit vorgesehen: nur Text, Rest gezählt.
- Ob die Zuordnung eines Chats zu einem Projekt in die Datei gehört oder nur
  in den Verzeichnisbaum.
- Ob `predecessor`/`successor` nach §1.12 automatisch bestimmbar sind. Bei
  Chats desselben Projekts mit Zeitstempeln vermutlich ja — das ist aber
  unbelegt und wird zunächst leer gelassen.

---

## 5 Was in dieser Sitzung gekippt ist

Damit es nicht erneut abgeleitet wird:

| Angenommen | Tatsächlich |
|---|---|
| Chats seien nur über Suchschnipsel erreichbar | `read_conversation` liefert sie vollständig und geordnet |
| Suchschnipsel überlappten und ließen sich zusammennähen | Es sind feste, nicht überlappende Blöcke; null Overlap zwischen 23 Segmenten |
| Sinkende Segmentzahl sei das Erfolgsmaß | Gilt nur in der Konsolidierungsphase; in der Entdeckung *muss* sie steigen |
| `batch-0000` bedeute Stückelung der Konversationen | Die Zeitraumauswahl erklärt die Menge |
| Markdown sei für Durchsuchbarkeit besser | JSON macht die Sprecherrollen eindeutig; „Text extraction" ist bei JSON verlustfrei |
| §1.12 müsse geändert werden | Das dortige Schema ist ein Beispiel, Ergänzen ist erlaubt |
| Der Container könne den Downloadlink holen | Allowlist ohne `claude.ai`, und der Link ist sitzungsgebunden |
| Projektdateien im Container sparten Kontext | *„while remaining in context"* |
