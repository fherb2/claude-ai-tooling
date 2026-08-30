# Die Marken

Diese Datei beschreibt allein die Kennzeichnung. Sie gilt wortgleich, gleich ob Du die Zeilen selbst schreibst oder sie dem Nutzer zum Eintragen gibst — verschieden ist nur, wer sie setzt und wer den Suchlauf ausführt. Das steht in der Regeldatei, die Dich hierher geschickt hat.

## Wozu die Marken dienen

Jede Marke und jede Trennzeile beginnt mit derselben Zeichenfolge `@@~`. Die Zahl der Tilden dahinter ist beliebig und für die Suche gleichgültig — als Trennstrich verwendet aber sinnvoll oft zu wiederholen, im Verhältnis zum umgebenden Text, bevor das abschließende `~@@` folgt.

**Die Marken sind eine Erleichterung, keine Automatik.** Sie dienen dazu, die Änderungen für den Rückbau zu erkennen und vergessene Fragmente zu finden. Was beim Rückbau tatsächlich geschieht, entscheiden sie nicht.

Zwei Suchläufe mit getrennten Aufgaben:

```
grep -rn '@@~DEBUG' .   # Selbsttest: findet die Marken
grep -rn '@@~' .        # Aufräumen: findet zusätzlich die Trennzeilen
```

Darauf beruht der ganze Zweck: Am Ende der Fehlersuche muss der Originalzustand vollständig wiederherstellbar sein — ohne Erinnerung und auch von jemandem, der nicht dabei war. Eine unmarkierte Debug-Zeile ist deshalb kein Schönheitsfehler, sondern ein Rest, den niemand mehr findet.

Beim Zählen gilt: Jede Blockmarkierung zählt zwei Treffer (Anfang und Ende), jede sonstige markierte Zeile einen.

## Die fünf Marken

Halte Dich zeichengenau an die folgenden fünf Marken.

| Marke | Wo sie steht | Wann |
| --- | --- | --- |
| `@@~DEBUG >>kennung<< ~@@` | am Zeilenende, hinter dem Kommentarzeichen | an jeder einzeln eingefügten Debug-Zeile |
| `@@~DEBUG: ORIGINAL >>kennung<< ~@@` | am Zeilenanfang, zwischen Kommentarzeichen und Code | an jeder Originalzeile, die stillgelegt wurde |
| `@@~DEBUG: START >>kennung<< ~~~~~~~~~~~~@@` | eigene Kommentarzeile vor der ersten Debug-Zeile | bei fünf oder mehr Debug-Zeilen am Stück |
| `@@~DEBUG: END >>kennung<< ~~~~~~~~~~~~@@` | eigene Kommentarzeile hinter der letzten Debug-Zeile | bei demselben Block |
| `@@~~~~~~~~~~~~~~~~~~~~~~~~@@` | eigene Kommentarzeile | vor jedem START und nach jedem END |

Vier Dinge gelten dabei ausnahmslos:

- **Vor jeder Marke steht das Kommentarzeichen der Sprache**, dahinter ein Leerzeichen. Die Marke selbst beginnt mit `@@~` und endet mit einer oder mehreren Tilden und `@@`.
- **Um die Kennung steht je ein Leerzeichen**, und hinter dem abschließenden `~@@` ebenfalls eines, bevor Code oder Kommentar folgt.
- **Eine Marke ohne Kennung ist unvollständig.** Die Trennzeile ist die einzige Ausnahme; sie gehört keinem Vorhaben.
- **Hinter ` @@~DEBUG >>kennung<< ~@@ ` darf die Zeile zusätzlich kommentiert werden.** Hinter ` @@~DEBUG: ORIGINAL >>kennung<< ~@@ ` nicht: Dort folgt der stillgelegte Code unverändert.

So sieht das in den verbreiteten Sprachen aus, wenn eine einzelne Anweisung gegen eine andere ausgetauscht wird — die Blockmarken und die Trennzeile folgen demselben Muster.

Python:

```python
value = fallback()  # @@~DEBUG >>cache-bypass<< ~@@ bypass cache on purpose
# @@~DEBUG: ORIGINAL >>cache-bypass<< ~@@ value = cache.get(key)
```

C, C++, Java, JavaScript, Rust und Verwandte:

```c
int n = 0;  // @@~DEBUG >>size-probe<< ~@@
// @@~DEBUG: ORIGINAL >>size-probe<< ~@@ int n = compute_size(buf);
```

Shell:

```bash
path="/tmp/probe"  # @@~DEBUG >>path-probe<< ~@@
# @@~DEBUG: ORIGINAL >>path-probe<< ~@@ path="$(resolve_path "$1")"
```

Kennt eine Sprache keinen Zeilenkommentar, gehört die Marke in einen Blockkommentar: `/* @@~DEBUG >>kennung<< ~@@ */`.

### Die Tilden in den Marken

Die Tildenkette ist reine Optik — sie hebt die Marke im Quelltext hervor. Für das Auffinden zählt sie nicht, gesucht wird nach `@@~`.

Beim Schreiben: mindestens eine Tilde in den Zeilenmarken, mindestens zwölf in den Blockmarken, mindestens vierundzwanzig in der Trennzeile. Verwende mehr, wenn das in Bezug zum umgebenden Code klarer als Abgrenzung wahrgenommen werden kann.

**Genau zwei Tilden sind verboten.** `~~` ist in Markdown Durchstreichung, und Kommentare und Docstrings könnten Markdown enthalten. Erlaubt ist eine Tilde oder drei und mehr.

Drei und mehr Tilden am **Zeilenanfang** öffnen in Markdown einen Code-Block. Weil vor jeder Marke das Kommentarzeichen der Sprache steht, kann das nicht eintreten — ein weiterer Grund, es nicht wegzulassen.

## Kennungen

Jedes Debug-Vorhaben bekommt eine Kennung: kurz, kleingeschrieben, mit Bindestrichen. Sie steht in jeder Marke dieses Vorhabens zwischen `>>` und `<<`.

**Wozu sie da ist.** Sie sagt an jeder einzelnen Zeile, zu welchem Vorhaben diese Zeile gehört. Erst dadurch ist beim Aufräumen entscheidbar, was zusammengehört — auch dann, wenn zwei Vorhaben ineinanderliegen und ihre Zeilen einander im Code abwechseln. `grep -rn '>>kennung<<' .` holt ein Vorhaben vollständig heraus, unabhängig davon, wo seine Zeilen stehen.

**Was sie benennt: die Frage, der Du nachgehst — nicht die Stelle im Code.** Zwei Vorhaben in derselben Funktion bekämen sonst dieselbe Kennung, und genau die Unterscheidung ginge verloren, für die es sie gibt. Nur wenn die Stelle die kürzeste wahre Beschreibung der Frage ist, benennt die Kennung sie.

**Wer sie wählt: Du.** Du liest den Kontext des Programmcodes und der Aufgabe und wählst daraus eine sinnvolle Kennung, ohne zu fragen. Mit dem Nutzer abzustimmen ist sie nur in sichtlich unentscheidbaren Situationen — vor allem in dieser einen: wenn Du nicht erkennen kannst, ob eine neue Markierung zu einem schon laufenden Vorhaben gehört oder ein eigenes ist. Diese Frage ist es wert, denn eine falsche Zuordnung reaktiviert beim Aufräumen fremden Code. Erkläre dem Nutzer kurz, warum Du in diesem Fall fragst und nicht selbst entscheidest.

**Zwei Regeln, die zusammen gelten.** Eine Kennung gehört zu genau einem Vorhaben, und ein Vorhaben hat genau eine Kennung. Triffst Du auf vorhandenen Debug-Code, dessen Vorhaben Du fortsetzt, übernimmst Du dessen Kennung, statt eine neue zu erfinden.

## Die drei Fälle beim Einfügen

Welcher Fall greift, entscheidet die Zahl der eingefügten Debug-Zeilen am Stück. **„Am Stück“ heißt: durch höchstens eine nicht zum Debugging gehörende Zeile getrennt.** Liegen die Debug-Zeilen weiter auseinander, sind es getrennte Fälle, und jede Gruppe wird für sich gezählt. Bist Du unsicher, ob eine Gruppe die Grenze von vier Zeilen überschreitet, nimm die Blockform.

### Fall 1: eine einzelne Anweisungszeile zum Debuggen ändern

- Die betreffende Zeile wird unter das Original kopiert.
- Das Original wird stillgelegt: Kommentarzeichen an den Zeilenanfang, dahinter ` @@~DEBUG: ORIGINAL >>kennung<< ~@@ `, dahinter der unveränderte Code.
- Die Kopie darunter wird geändert und bekommt ` @@~DEBUG >>kennung<< ~@@ ` angehängt, wie in Fall 2 beschrieben.

### Fall 2: bis zu vier eingefügte Debug-Zeilen

- An jede eingefügte Zeile kommt ein Kommentar, der hinter dem Kommentarzeichen mit ` @@~DEBUG >>kennung<< ~@@ ` beginnt.
- Originalzeilen, die unmittelbar davor, dahinter oder zwischen den Debug-Zeilen stehen und stillgelegt werden müssen, bekommen ` @@~DEBUG: ORIGINAL >>kennung<< ~@@ ` zwischen Kommentarzeichen und Code.

### Fall 3: fünf oder mehr Debug-Zeilen am Stück

- Vor der ersten Debug-Zeile steht eine eigene Kommentarzeile, die hinter dem Kommentarzeichen mit ` @@~DEBUG: START >>kennung<< ~~~~~~~~~~~~@@ ` beginnt.
- Hinter der letzten Debug-Zeile steht eine ebensolche Kommentarzeile mit ` @@~DEBUG: END >>kennung<< ~~~~~~~~~~~~@@ `.
- Vor die START-Zeile und hinter die END-Zeile kommt je eine Trennzeile ` @@~~~~~~~~~~~~~~~~~~~~~~~~@@ `.
- An den Zeilen dazwischen entfällt die Marke ` @@~DEBUG >>kennung<< ~@@ ` — mit der Ausnahme, die der nächste Abschnitt beschreibt.
- **Stillgelegte Originalzeilen behalten ihre Marke ` @@~DEBUG: ORIGINAL >>kennung<< ~@@ ` auch innerhalb eines Blocks.** Der Verzicht betrifft allein ` @@~DEBUG >>kennung<< ~@@ `. Ohne die ORIGINAL-Marke ist im Block nicht mehr zu erkennen, welche Zeilen wieder zu aktivieren sind — und genau darauf kommt es beim Aufräumen an.

### Verschachtelung

Ein Debug-Vorhaben darf innerhalb eines anderen entstehen; beim Debuggen ist das der Normalfall und nicht die Ausnahme. Jedes trägt seine eigene Kennung, und **die Zuordnung ergibt sich allein aus ihr, nie aus der Lage im Code.** Eine stillgelegte Zeile kann räumlich im Block eines fremden Vorhabens stehen und trotzdem zu dem umschließenden gehören.

Daraus folgt die Ausnahme zu Fall 3: **Eine eingefügte Zeile, die zu einem anderen Vorhaben gehört als der Block, in dem sie steht, trägt ` @@~DEBUG >>ihre-kennung<< ~@@ `** — auch innerhalb eines Blocks, wo die Marke sonst entfällt.

Stoßen das END des einen und das START des nächsten Blocks aneinander, genügt eine Trennzeile.

## Originalcode wird nie gelöscht

Originalcode, der für die Fehlersuche weichen muss, wird **ausschließlich auskommentiert — niemals gelöscht und niemals überschrieben.** Das gilt auch dann, wenn er kurz ist und man ihn sich mühelos merken könnte. Die stillgelegte Zeile ist die einzige verlässliche Quelle für den Rückweg: Sie steht im Suchlauf, sie steht im Diff, und sie steht dort auch noch, wenn jemand anders aufräumt.

## Worauf beim Ändern außerdem zu achten ist

- An Entscheidungsstellen — Verzweigungen, Case-Aufteilungen — und in Schleifen kommt es besonders auf die richtige Anwendung der Marken an, damit der Originalzustand mit minimalem Aufwand und nachvollziehbar wiederherstellbar bleibt.
- Die vorgefundene Einrückung beziehungsweise die der verwendeten Programmiersprache bleibt unverändert. Auch Blockmarken und Trennzeilen folgen ihr — **nicht** der Schachtelungstiefe der Debug-Vorhaben und nicht der Reihenfolge, in der sie eingefügt wurden.

## Eine markierte Zeile zurückbauen

Aus einer Zeile mit ` @@~DEBUG: ORIGINAL >>kennung<< ~@@ ` verschwinden die Marke **und** das vorangestellte Kommentarzeichen; die Zeile steht danach wieder genau so da wie vor dem Debugging. Eingefügte Debug-Zeilen werden ganz entfernt, die Trennzeilen eines Blocks gehen mit ihm weg.

## Beispiel

Ausgangszustand:

```python
def load_config(path):
    raw = read_file(path)
    config = parse(raw)
    validate(config)
    return config
```

Fall 1 und Fall 2 — eine geänderte Anweisungszeile, eine eingefügte Ausgabe, zwei stillgelegte Originalzeilen:

```python
def load_config(path):
    # @@~DEBUG: ORIGINAL >>fixed-input<< ~@@ raw = read_file(path)
    raw = '{"mode": "test"}'  # @@~DEBUG >>fixed-input<< ~@@ fixed input instead of file
    config = parse(raw)
    print(f"config={config}")  # @@~DEBUG >>fixed-input<< ~@@
    # @@~DEBUG: ORIGINAL >>fixed-input<< ~@@ validate(config)
    return config
```

Der Selbsttest findet hier vier Treffer, passend zu vier geänderten oder eingefügten Zeilen.

Fall 3 — derselbe Ausgangszustand, aber fünf Debug-Zeilen am Stück, darin eine stillgelegte Originalzeile:

```python
def load_config(path):
    raw = read_file(path)
    config = parse(raw)
    # @@~~~~~~~~~~~~~~~~~~~~~~~~@@
    # @@~DEBUG: START >>config-shape<< ~~~~~~~~~~~~@@
    print(f"path={path}")
    print(f"raw bytes={len(raw)}")
    print(f"keys={sorted(config)}")
    print(f"mode={config.get('mode')}")
    # @@~DEBUG: ORIGINAL >>config-shape<< ~@@ validate(config)
    print("validate() skipped")
    # @@~DEBUG: END >>config-shape<< ~~~~~~~~~~~~@@
    # @@~~~~~~~~~~~~~~~~~~~~~~~~@@
    return config
```

Der Selbsttest findet hier drei Treffer: zwei für den Block, einen für die stillgelegte Originalzeile darin. Der Aufräum-Suchlauf findet fünf, weil die beiden Trennzeilen dazukommen.

Verschachtelung — ein zweites Vorhaben entsteht innerhalb des ersten:

```python
def load_config(path):
    # @@~~~~~~~~~~~~~~~~~~~~~~~~@@
    # @@~DEBUG: START >>read-path<< ~~~~~~~~~~~~@@
    print(f"path={path}")
    # @@~DEBUG: ORIGINAL >>read-path<< ~@@ raw = read_file(path)
    raw = '{"mode": "test"}'
    # @@~~~~~~~~~~~~~~~~~~~~~~~~@@
    # @@~DEBUG: START >>parse-strict<< ~~~~~~~~~~~~@@
    print(f"raw head={raw[:40]!r}")
    print(f"raw bytes={len(raw)}")  # @@~DEBUG >>read-path<< ~@@
    # @@~DEBUG: ORIGINAL >>parse-strict<< ~@@ config = parse(raw)
    config = parse(raw, strict=False)
    print(f"keys={sorted(config)}")
    # @@~DEBUG: END >>parse-strict<< ~~~~~~~~~~~~@@
    # @@~~~~~~~~~~~~~~~~~~~~~~~~@@
    # @@~DEBUG: ORIGINAL >>read-path<< ~@@ validate(config)
    print("validate() skipped")
    # @@~DEBUG: END >>read-path<< ~~~~~~~~~~~~@@
    # @@~~~~~~~~~~~~~~~~~~~~~~~~@@
    return config
```

Zwei Stellen zeigen, wozu die Kennung da ist. Die Zeile mit `raw bytes` steht im Block von `parse-strict`, gehört aber zu `read-path` — deshalb trägt sie eine Marke, obwohl im Block sonst keine steht. Und die stillgelegte `validate(config)` steht hinter dem Block von `parse-strict`, gehört ebenfalls zu `read-path` und bleibt liegen, wenn `parse-strict` aufgeräumt wird.

Der Selbsttest findet hier acht Treffer: vier für die beiden Blöcke, drei für die stillgelegten Originalzeilen, einen für die markierte Einzelzeile.
