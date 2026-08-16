---
name: temp-debug-code
description: Kennzeichnungsregeln für temporären Debug-Code — eingefügte Debug- und print-Ausgaben sowie zum Testen stillgelegter Originalcode werden mit festen, suchbaren Marken versehen, damit sie später rückstandsfrei entfernt und der Originalzustand vollständig wiederhergestellt werden kann. Verwenden, bevor in einer Sitzung zum ersten Mal eine Debug-Ausgabe eingefügt oder bestehender Code zum Testen auskommentiert wird, oder wenn der Nutzer /temp-debug-code aufruft.
license: CC0-1.0
---

# Temporärer Debug-Code und zeitweises Stilllegen von Originalcode

## Wofür diese Regeln gelten — und wofür nicht

Diese Regeln gelten ausschließlich für **temporären** Debug-Code: für Zeilen, die nur zur Fehlersuche entstehen und wieder verschwinden sollen, sobald die Ursache gefunden ist. Dazu gehört ebenso der Originalcode, den Du für die Dauer der Fehlersuche stilllegst.

Nicht Gegenstand dieser Regeln ist Debug-Code, der dauerhaft im Quelltext bleiben soll — etwa Ausgaben hinter einem Debug-Flag, hinter einer Log-Stufe oder hinter einer Konfigurationsvariablen. Solcher Code ist regulärer Programmcode, wird nicht markiert und folgt den üblichen Regeln des Projekts.

## Wozu die Marken dienen

Jede der hier definierten Marken beginnt mit derselben Zeichenfolge ` # DEBUG`. Ein einziger Suchlauf findet deshalb restlos jede Änderung, die zum Debuggen entstanden ist:

```
grep -rn " # DEBUG" .
```

Darauf beruht der ganze Zweck: Am Ende der Fehlersuche muss der Originalzustand vollständig wiederherstellbar sein — ohne Erinnerung, auch von jemandem, der nicht dabei war, und notfalls per Skript. Eine unmarkierte Debug-Zeile ist deshalb kein Schönheitsfehler, sondern ein Rest, den niemand mehr findet.

**Selbsttest, verpflichtend.** Führe den Suchlauf aus, sobald Du Deine Debug-Änderungen geschrieben hast, und vergleiche die Trefferzahl mit dem, was Du geändert hast: jede Blockmarkierung zählt zwei Treffer (Anfang und Ende), jede sonstige markierte Zeile einen. Stimmen die Zahlen nicht überein, fehlt eine Marke — such sie, bevor Du weiterarbeitest.

## Die Marken

Halte Dich zeichengenau an die folgenden vier Marken. **Zu jeder Marke gehören ein führendes und ein abschließendes Leerzeichen** — vorn und hinten genau eines, ausnahmslos. Ohne sie greift der Suchlauf nicht mehr zuverlässig.

| Marke | Wo sie steht | Wann |
| --- | --- | --- |
| `# DEBUG #` | am Zeilenende, hinter dem Kommentar-Marker | an jeder einzeln eingefügten Debug-Zeile |
| `# DEBUG: ORIGINAL #` | am Zeilenanfang, zwischen Kommentar-Marker und Code | an jeder Originalzeile, die Du stillgelegt hast |
| `# DEBUG: START ------------ #` | eigene Kommentarzeile vor der ersten Debug-Zeile | bei fünf oder mehr Debug-Zeilen am Stück |
| `# DEBUG: END ------------ #` | eigene Kommentarzeile hinter der letzten Debug-Zeile | bei demselben Block |

In der Tabelle sind die umschließenden Leerzeichen nicht sichtbar; maßgeblich ist der Satz darüber und sind die Beispiele darunter.

### Das `#` gehört zur Marke

Das `#` am Anfang und am Ende jeder Marke ist Bestandteil der Marke und **nicht** der Kommentar-Marker der Programmiersprache. In Python trifft es deshalb auf ein zweites `#`, und die Zeile trägt zwei Rauten hintereinander. Das sieht nach einem Versehen aus, ist aber Absicht: Nur so lautet die Marke in jeder Sprache gleich und wird von einem einzigen Suchmuster gefunden. Entferne diese vermeintliche Dopplung nicht und vereinfache sie nicht.

Python:

```python
value = fallback()  # # DEBUG # bypass cache on purpose
# # DEBUG: ORIGINAL # value = cache.get(key)
```

C, C++, Java, JavaScript, Rust und Verwandte:

```c
int n = 0;  // # DEBUG #
// # DEBUG: ORIGINAL # int n = compute_size(buf);
```

Shell:

```bash
path="/tmp/probe"  # # DEBUG #
# # DEBUG: ORIGINAL # path="$(resolve_path "$1")"
```

Kennt eine Sprache keinen Zeilenkommentar, setzt Du die Marke in einen Blockkommentar: `/* # DEBUG # */`.

### Die Bindestriche in den Blockmarken

Die Bindestrichkette ist reine Optik — sie hebt Anfang und Ende des Blocks im Quelltext hervor. Für das Auffinden zählt sie nicht, gesucht wird nach ` # DEBUG`. Schreibe zwölf Bindestriche; findest Du im Bestand eine abweichende Anzahl, ist das kein Fehler und nichts zu korrigieren.

## Die drei Fälle beim Einfügen

### Fall 1: eine einzelne Anweisungszeile zum Debuggen ändern

- Kopiere die betreffende Zeile unter das Original.
- Lege das Original still: Kommentar-Marker an den Zeilenanfang, dahinter ` # DEBUG: ORIGINAL # `, dahinter der unveränderte Code.
- Ändere die Kopie darunter und hänge ihr ` # DEBUG # ` an, wie in Fall 2 beschrieben.

### Fall 2: bis zu vier eingefügte Debug-Zeilen

- Hänge an jede eingefügte Zeile einen Kommentar an, der hinter dem Kommentar-Marker mit ` # DEBUG # ` beginnt.
- Hinter der Marke darfst Du die Zeile zusätzlich kommentieren.
- Originalzeilen, die unmittelbar davor, dahinter oder zwischen den Debug-Zeilen stehen und stillgelegt werden müssen, bekommen ` # DEBUG: ORIGINAL # ` zwischen Kommentar-Marker und Code.

„Am Stück" heißt: durch höchstens eine nicht zum Debugging gehörende Zeile getrennt. Liegen die Debug-Zeilen weiter auseinander, sind es getrennte Fälle, und jede Gruppe wird für sich gezählt.

### Fall 3: fünf oder mehr Debug-Zeilen am Stück

- Lege vor der ersten Debug-Zeile eine eigene Kommentarzeile an, die hinter dem Kommentar-Marker mit ` # DEBUG: START ------------ # ` beginnt.
- Lege hinter der letzten Debug-Zeile eine ebensolche Kommentarzeile mit ` # DEBUG: END ------------ # ` an.
- An den Zeilen dazwischen entfällt die Marke ` # DEBUG # `.
- **Stillgelegte Originalzeilen behalten ihre Marke ` # DEBUG: ORIGINAL # ` auch innerhalb eines Blocks.** Der Verzicht betrifft allein ` # DEBUG # `. Ohne die ORIGINAL-Marke ist im Block nicht mehr zu erkennen, welche Zeilen wieder zu aktivieren sind — und genau darauf kommt es beim Aufräumen an.

Bist Du unsicher, ob ein Fall die Grenze von vier Zeilen überschreitet, nimm die Blockform.

## Originalcode wird nie gelöscht

Originalcode, der für die Fehlersuche weichen muss, wird **ausschließlich auskommentiert — niemals gelöscht und niemals überschrieben.** Das gilt auch dann, wenn er kurz ist und Du ihn Dir mühelos merken könntest. Die stillgelegte Zeile ist die einzige verlässliche Quelle für den Rückweg: Sie steht im Suchlauf, sie steht im Diff, und sie steht dort auch noch, wenn jemand anders aufräumt.

## Worauf Du beim Ändern außerdem achtest

- An Entscheidungsstellen — Verzweigungen, Case-Aufteilungen — und in Schleifen kommt es besonders auf die richtige Anwendung der Marken an, damit der Originalzustand mit minimalem Aufwand und für den Nutzer nachvollziehbar wiederherstellbar bleibt.
- Übernimm die vorgefundene Einrückung beziehungsweise die der verwendeten Programmiersprache unverändert.

## Debug-Code wieder entfernen

Bevor Du neuen Debug-Code einfügst, prüfe, ob vorhandener seinen Zweck erfüllt hat und entfernt werden kann. Ausschlaggebend ist dabei nicht, wann er entstanden ist, sondern **zu welchem Problemlösungsauftrag er gehört**:

- Gehört er zu dem Auftrag, an dem Du gerade arbeitest, und hat er seinen Dienst getan, entfernst Du ihn selbständig und aktivierst die dabei stillgelegten Codebereiche wieder.
- Gehört er zu einem früheren, bereits abgeschlossenen Auftrag, entscheidest Du nicht selbst: Lege dem Nutzer die Stelle vor und lass ihn entscheiden. Entscheidet er sich gegen das Entfernen, schlägst Du dieselbe Stelle erst dann wieder vor, wenn ein neuer Tag oder ein neuer Chat begonnen hat oder wenn der Nutzer Dich ausdrücklich beauftragt, Debug-Code zu finden und zu entfernen.

Wenn Du Debug-Code entfernst, prüfe sehr genau, ob dabei stillgelegter Originalcode wieder zu aktivieren ist. Aus einer Zeile mit ` # DEBUG: ORIGINAL # ` verschwinden dabei die Marke **und** der vorangestellte Kommentar-Marker; die Zeile steht danach wieder genau so da wie vor dem Debugging. Führe zum Schluss den Suchlauf aus: Was er noch findet, ist noch nicht aufgeräumt.

## Fundstellen, die diesen Vorgaben nicht folgen

Findest Du im Quelltext Zeilen, die sich nicht exakt an diese Vorgaben halten, informiere den Nutzer und schlage ihm die Korrektur vor. Zeige ihm dazu beispielhaft das Ergebnis der Korrektur im Chat, damit er leichter entscheiden kann. Keine solche Korrektur ohne vorherige Zustimmung des Nutzers.

## Beispiel

Ausgangszustand:

```python
def load_config(path):
    raw = read_file(path)
    config = parse(raw)
    validate(config)
    return config
```

Fall 1 und Fall 2 — eine geänderte Anweisungszeile, eine eingefügte Ausgabe, eine stillgelegte Originalzeile:

```python
def load_config(path):
    # # DEBUG: ORIGINAL # raw = read_file(path)
    raw = '{"mode": "test"}'  # # DEBUG # fixed input instead of file
    config = parse(raw)
    print(f"config={config}")  # # DEBUG #
    # # DEBUG: ORIGINAL # validate(config)
    return config
```

Der Suchlauf findet hier vier Treffer, passend zu vier geänderten oder eingefügten Zeilen.

Fall 3 — derselbe Ausgangszustand, aber fünf Debug-Zeilen am Stück, darin eine stillgelegte Originalzeile:

```python
def load_config(path):
    raw = read_file(path)
    config = parse(raw)
    # # DEBUG: START ------------ #
    print(f"path={path}")
    print(f"raw bytes={len(raw)}")
    print(f"keys={sorted(config)}")
    print(f"mode={config.get('mode')}")
    # # DEBUG: ORIGINAL # validate(config)
    print("validate() skipped")
    # # DEBUG: END ------------ #
    return config
```

Der Suchlauf findet hier drei Treffer: zwei für den Block, einen für die stillgelegte Originalzeile darin.
