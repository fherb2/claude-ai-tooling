---
name: chat-export
description: Holt Chats aus claude.ai-Projekten als durchsuchbare JSON-Dateien in das aktuelle Repository, über den angemeldeten Chrome oder aus einem Kontoexport-ZIP. Verwenden, sobald der Nutzer Chats eines claude.ai-Projekts importieren, nachtragen, sichern oder archivieren will, etwa "hol die neuen Chats aus dem Projekt X", "ich will meine Claude-Projekte ins Repo holen", "welche Chats fehlen hier noch?" oder "mach mal einen Export von Projekt Y". Setzt angehängte Browser-Werkzeuge voraus und einen laufenden, bei claude.ai angemeldeten Chrome.
license: CC0-1.0
---

# Chats aus claude.ai holen

Du holst Chats aus claude.ai-Projekten und legst sie als durchsuchbare JSON-Dateien ab. Sie sind zum Wiederfinden früheren Zusammenhangs gedacht, nicht zum Fortsetzen.

Die Arbeit teilt sich strikt: **Du deutest und ordnest zu, das Skript zählt und vergleicht.** Projektnamen mit Tippfehlern auf die echte Liste abbilden, auf "zeig mir einfach alle" sinnvoll reagieren — das ist deine Stärke. Einträge einer JSON-Datei aufsummieren ist es nicht; an diesem Werkzeug gemessen wurden zehn genannt, wo neun standen. **Rechne deshalb nie selbst.** Jede Zahl, die du nennst, stammt aus einem Skriptlauf.

Das Skript liegt neben dieser Datei: `${CLAUDE_SKILL_DIR}/chat_export_convert.py`.

**Zum Ton gegenüber dem Nutzer:** Knapp bei den Zwischenschritten, nicht wortkarg beim Ergebnis. Ein Ablauf, der nur Kommandos und Zahlen ausgibt und danach schweigt, lässt den Nutzer im Unklaren, ob noch etwas kommt — das ist unangenehm, kein Zeichen von Effizienz. Jeder Abschnitt bekommt einen kurzen, freundlichen Satz, was gerade geschieht und warum; nach dem letzten Schritt steht immer ausdrücklich, dass jetzt Schluss ist (Abschnitt „Abschluss").

## Genau zwei Haltepunkte

Mehr Rückfragen gibt es nicht. Wer einen dritten einbaut, macht den Ablauf unbrauchbar.

1. **Vor dem ersten Abruf.** Kurz erklären, was geschieht, und fragen, ob du anfangen sollst. Ein Ja deckt **alles Lesende** ab: Kontoauskunft, Projektliste, Chatlisten, Abgleich.
2. **Nach der Statistik.** Der Nutzer wählt je Projekt den Weg. Danach folgt **ein** Hinweis, was nun geschieht — kein weiterer Haltepunkt.

## Ablauf

### Voraussetzungen prüfen

**Ohne angehängte Browser-Werkzeuge brichst du ab und behilfst dich nicht.** Sie hängen nur an einer Nachricht, die der Nutzer mit `@browser` beginnt. Fehlen sie, sag genau das:

> Die Browser-Werkzeuge sind dieser Nachricht nicht angehängt. Ruf mich mit `@browser /chat-export` auf, oder starte Claude Code mit `claude --chrome`.

Melden sie beim ersten Aufruf "Browser extension is not connected" oder "Claude in Chrome is turned off in your settings", liegt es an einer dieser Bedingungen, und der Nutzer muss sie herstellen — nicht du:

- Chrome läuft und ist bei claude.ai angemeldet.
- Auf claude.ai unter Einstellungen → Connectors ist "Claude in Chrome" für dieses Konto eingeschaltet. Wirkt nicht rückwirkend auf schon offene Tabs.
- In Chrome unter Einstellungen → Downloads ist "Speicherort für jede Datei vor dem Download abfragen" **aus**. Sonst öffnet der erste Download einen Dateidialog, und ein Dialog blockiert die Anbindung vollständig.

### Konto nennen

Leg dir einen eigenen Tab an. Du siehst ausschließlich deine eigenen Tabs, nie die des Nutzers — ein vorab geöffneter claude.ai-Tab ist weder nötig noch erreichbar.

Hol `/api/organizations` **mit vollem Objekt, nicht nur `uuid`/`name`** — das Feld `capabilities` filtert automatisch. Eine Organisation ohne `"chat"` in `capabilities` ist eine reine API-/Console-Organisation (typischerweise `"Frank's Individual Org"`-artig benannt); Anthropic trennt Chat-Abo und API-Zugriff bewusst in getrennte Organisationen (belegt, [9876003](https://support.claude.com/en/articles/9876003-i-have-a-paid-claude-subscription-pro-max-team-or-enterprise-plans-why-do-i-have-to-pay-separately-to-use-the-claude-api-and-console)) — **das ist normal, keine Störung.** Nimm sie aus der Auswahl, ohne zu fragen.

Bleibt danach mehr als eine Organisation mit Chat-Fähigkeit übrig, prüfe **zuerst selbst**, in welcher die genannten oder gewünschten Projekte liegen (`/projects` je Kandidat), bevor du fragst — das kostet nur einen zusätzlichen Aufruf und erspart dem Nutzer eine Frage, die du dir selbst beantworten kannst. Nur wenn das Ergebnis mehrdeutig bleibt (Treffer in mehreren, oder in keiner), frag nach.

Nenne das erkannte Ergebnis **unverlangt**:

> Chrome ist bei claude.ai angemeldet als: *Name der Organisation*. Dort suche ich die Projekte.

Das ersetzt jede vorherige Anweisung, sich anzumelden. Es ist verlässlicher als eine Zusicherung: Denselben Projektnamen kann es in einem zweiten Konto geben. Das Konto in Chrome muss **nicht** mit dem übereinstimmen, mit dem Claude Code selbst arbeitet — das ist geprüft und in Ordnung.

### Projekte bestimmen

Hier arbeitest du, nicht das Skript. Drei Fälle:

- **Der Nutzer hat die Projekte genannt.** Ordne zu und mach weiter. Passt eine Nennung nur ungefähr, frag einmal nach ("„Modelbahn Fahrpult" finde ich so nicht wörtlich — gemeint ist wohl *Modellbahn-Fahrpult*?").
- **Der Nutzer will erst sehen, was es gibt.** Zeig die Projekte als Vorlage, nach letzter Änderung sortiert, mit dem, was hier schon liegt.
- **Es liegt nur ein Archiv hier und der Nutzer sagt nichts weiter.** Nimm dieses und sag, dass du es nimmst.

### Statistik holen

Je gewähltes Projekt die Chatliste über **alle** Seiten holen, dann `list --web --project "<Projektname>"` und `diff` laufen lassen. Gib **immer** `--project` mit — sonst bleibt das Feld im Protokoll leer, obwohl der Ordnername den Projektnamen längst trägt. Bei mehreren Projekten steht **eine** Tabelle mit einer Zeile je Projekt, damit die Haltepunkte bei zwei bleiben:

```
Projekt                 Archiv  Quelle   neu  gewachsen  verschw.  Umfang   Empfehlung
Modellbahn-Fahrpult         34      39     5          2         1   ~310 N.  Web
```

**Ein Chat, den die frische Liste nicht mehr führt, wird gemeldet und nie automatisch entfernt.** Seine Dateien bleiben liegen. Von hier aus lässt sich Löschung an der Quelle nicht von einem Verschieben in ein anderes Projekt unterscheiden, und beides nicht von einer Liste, die nicht zu Ende geblättert wurde. Jede automatische Entfernung wäre im dritten Fall Datenverlust aus einem Bedienfehler.

### Weg wählen lassen

Leg beide Wege mit ihrem Preis vor und **empfiehl**, entscheide nicht:

- **Web-Weg** — Abruf über die Weboberfläche, gebremst auf 4–12 s Abstand. Sofort, kein Warten. Belastet die Weboberfläche, deshalb die Bremse. Gut für wenige Chats mit kleinen Anhängen.
- **Export-Weg** — ein Kontoexport, der bis zu einem errechneten Datum zurückreichen muss. Antrag, E-Mail, Download; die Wartezeit bestimmt claude.ai. Trägt alles in einem Zug, ohne Last je Chat. Gut für viele Chats oder große Anhänge.

**Nicht jedes Konto hat einen Export.** In Team- und Enterprise-Konten hat ein gewöhnliches Mitglied keinen Selbstbedienungs-Export; dort ist der Web-Weg die **einzige** Möglichkeit, nicht die bequemere. Ob ein Export zur Verfügung steht, kannst du nicht zuverlässig aus den Daten ablesen — sag es als Vorbehalt dazu und frag im Zweifel.

Eine Antwort genügt für alle Projekte; sie darf sie auch trennen ("Export für Modellbahn, Web für FreeCAD").

### Der Hinweis vor dem Lauf

Kein Haltepunkt, sondern die Ansage. Sie **nennt das Ersetzen mit Zahlen**, weil dabei Dateien entfernt werden:

> Ich hole 9 Chats über den Web-Weg, Abstand 4–12 s zufällig, etwa 2 Minuten. Alles kommt als eine Datei in den Download-Ordner. Beim Umwandeln werden 2 Chats ersetzt; ihre bisherigen 3 Dateien entferne ich vorher und nenne sie einzeln.

### Web-Weg ausführen

Je Chat ein `fetch` aus der geöffneten Seite heraus, **alles in ein Objekt**, und genau **ein** Download am Ende. Mehrere Downloads aus derselben Seite lösen eine Nachfrage aus, und jede Nachfrage ist eine Gelegenheit für einen blockierenden Dialog.

Zwischen den Chat-Abrufen wartest du **4 bis 12 Sekunden, gleichverteilt gewürfelt** — nicht fest getaktet, damit kein regelmäßiges Muster entsteht. Der Zweck ist, den Server nicht zu belasten und nicht als Massenabruf aufzufallen.

Zeig den Fortschritt je Chat. Danach prüfst du lokal, dass die Datei angekommen ist, und lässt `convert --bundle` laufen.

### Export-Weg ausführen

Nenne die Fenstergrenze aus dem Skriptlauf **mit Begründung** — der Zeitraumfilter greift auf das Erstelldatum, nicht auf die letzte Änderung; ein zu kurzes Fenster ließe einen gewachsenen Altchat ganz aus, und nichts würde das melden. Biete an, den Antrag im Browser auszufüllen und den Absenden-Knopf vorzulegen.

**Zur Exportseite führt kein Deep-Link.** Eine direkte Navigation auf `claude.ai/settings/data-privacy-controls` (oder ähnliche Einstellungs-URLs) landet auf der gewöhnlichen Chat-Oberfläche, nicht im Einstellungsdialog — die Seite rendert Einstellungen client-seitig, nur ein echter Klick öffnet sie. Geh über die Oberfläche: das Konto-/Einstellungsmenü öffnen, „Datenschutz" anklicken, darin zu „Daten exportieren" scrollen. Ein Element-Suchwerkzeug für „Datenschutz" bzw. „Daten exportieren" findet beide Buttons zuverlässig.

Dann reißt die Kette, und du sagst es geradeheraus: Der Link kommt per E-Mail und gilt 24 Stunden. **In das Postfach gehst du nicht.** Sobald der Nutzer Bescheid gibt, findest du die ZIP im Download-Ordner und lässt `convert --zip` laufen.

### Abschluss

Berichte, was geschrieben, ersetzt und aufgeräumt wurde — die entfernten Dateien **einzeln benannt**, stilles Löschen wäre die nächste Fehlerquelle.

Steht in der `CLAUDE.md` des Zielprojekts noch kein Verweis auf das Archiv, sag das als **Bemerkung, nicht als Frage** — sonst entsteht ein dritter Haltepunkt:

> Hinweis: In der CLAUDE.md dieses Projekts steht kein Verweis auf das Archiv. Ohne ihn liegt es hier und wird nie gelesen. Sag Bescheid, wenn ich den Block einsetzen soll.

**Schließe immer ausdrücklich ab.** Der letzte Satz sagt klar, dass alle angekündigten Schritte erledigt sind und nichts weiter von dir aussteht — nicht nur eine Liste, was passiert ist. Ein Nutzer, der nach der letzten Werkzeugausgabe nichts mehr von dir hört, weiß sonst nicht, ob du noch arbeitest oder fertig bist; genau das nachzufragen ist ihm unangenehm. Etwa:

> Damit bin ich fertig — alle vier Projekte geprüft, FreeCAD-Bedienung aktualisiert, sonst nichts offen. Sag Bescheid, wenn noch etwas dazukommen soll.

## Die Endpunkte

Alle gleichursprünglich aus einer geöffneten claude.ai-Seite per `fetch` erreichbar. `<org>` ist die UUID aus `/api/organizations`.

```
GET /api/organizations
GET /api/organizations/<org>/projects
GET /api/organizations/<org>/projects/<projekt>/conversations_v2?limit=100&offset=0
GET /api/organizations/<org>/chat_conversations/<chat>?tree=True&rendering_mode=messages&render_all_tools=true
```

Der Listen-Endpunkt gibt `data` und `pagination` mit `has_more`, `limit`, `offset`, `total` zurück — das Blättern ist deterministisch, es muss nichts geraten werden. Je Chat kommen `uuid`, `name`, `created_at`, `updated_at`, `project_uuid` und `model`.

Der Konversations-Endpunkt liefert den **vollständigen Nachrichtenbaum** in einer einzigen Antwort, ohne Paginierung — auch bei über 180 Nachrichten und rund 600 KB. Die Felder tragen dieselben Namen wie im Kontoexport, weshalb der Konverter beide Quellen gleich behandelt.

## Das Bundle

Eine JSON-Datei mit zwei je nach Schritt gefüllten Teilen. Der Download entsteht aus der Seite heraus über einen Blob und einen angeklickten Link mit `download`-Attribut.

```json
{"fetched_at": "...", "organization": "...",
 "conversations": [{"uuid": "...", "name": "...", "created_at": "...", "updated_at": "..."}],
 "chats": [ ... vollständige Konversationen ... ]}
```

`conversations` speist `list --web`, `chats` speist `convert --bundle`.

## Die Skriptaufrufe

```
python3 ${CLAUDE_SKILL_DIR}/chat_export_convert.py list    --web <bundle> --out <verzeichnis> [--project <name>]
python3 ${CLAUDE_SKILL_DIR}/chat_export_convert.py convert --bundle <bundle> --out <verzeichnis> [--target repo|knowledge|home]
python3 ${CLAUDE_SKILL_DIR}/chat_export_convert.py convert --zip <export.zip> --out <verzeichnis>
python3 ${CLAUDE_SKILL_DIR}/chat_export_convert.py diff    --out <verzeichnis>
python3 ${CLAUDE_SKILL_DIR}/chat_export_convert.py report  --out <verzeichnis>
```

`list` kommt immer zuerst — es baut das Protokoll, und nur daraus ergibt sich, was zu holen ist. Ein Projekt ohne Chats ist kein Fehler: Es entsteht ein leeres, gültiges Protokoll. Der vollständige Docstring des Skripts ist seine Betriebsanleitung; lies ihn, wenn ein Kommando anders reagiert als erwartet.

Zielverzeichnis ist `<projekt>/.claude/imported_chats/<quellprojekt>/`, ein flaches Verzeichnis je Quellprojekt. **Bündelt das laufende Repo mehrere eigenständige Vorhaben** (erkennbar an dessen eigener `CLAUDE.md`) und passt keines davon zum gewählten claude.ai-Projekt, frag einmal nach dem Zielordner, bevor du anlegst — das zählt nicht gegen die zwei Haltepunkte, weil es kein Lese- oder Wegentscheid ist, sondern eine Vorbedingung, die die Struktur des Repos vorgibt, nicht der Skill.

## Was du nie tust

- **Nicht entscheiden, welcher Weg genommen wird.** Beide mit ihrem Preis vorlegen.
- **Nicht selbst zählen.** Jede Zahl kommt aus einem Skriptlauf.
- **Nichts entfernen, was verschwunden scheint.** Melden und liegen lassen.
- **Nichts zusammenfassen.** Chattext wird kopiert, nie nacherzählt — das Bundle geht als Datei am Modell vorbei.
- **Nicht ungebremst abrufen.** 4 bis 12 Sekunden, gleichverteilt gewürfelt.
- **Nicht ins E-Mail-Postfach gehen.**
- **Keine Zusicherung verlangen, die du selbst prüfen kannst.** Das Konto wird genannt, nicht erfragt.
