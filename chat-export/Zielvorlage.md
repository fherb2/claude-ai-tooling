# Zielvorlage: der Skill `chat-export` aus Sicht des Nutzers

**Was diese Datei ist.** Eine Beschreibung des angestrebten Verhaltens, geschrieben als Durchgang aus der Sicht dessen, der das Werkzeug benutzt. Sie dient dazu, den Entwurf zu beurteilen, bevor er gebaut wird, und ist später die Vorlage für die Anwenderdokumentation (Fahrplanpunkt 13).

**Was sie nicht ist.** Sie ist **kein Plan** im Sinne der Arbeitsanweisungen §1.3 und der Repo-`CLAUDE.md`. Der Plan des nächsten Schrittes steht ausdetailliert im Fahrplan, Punkt 27, und nur dort; eine neue Sitzung nimmt ihren Auftrag von dort, nicht von hier. Diese Datei beschreibt das Ziel, nicht den Weg dorthin.

**Stand.** Nichts hiervon existiert. Was existiert, sind die Skripte darunter — Baumlauf, Blockauswahl, Protokollführung, Fensterrechnung, Ersetzen samt Aufräumen — und der am 19. August 2026 belegte Zugriff auf beide claude.ai-Endpunkte über die Chrome-Anbindung (Nachweis in `testlauf.md`). Der Skill ist die Klammer darum. Alle Zahlen in den Beispielen sind erfunden, ausgenommen die ausdrücklich als gemessen bezeichneten.

**Die tragende Arbeitsteilung.** Die Instanz **deutet und ordnet zu**, das Skript **zählt und vergleicht**. Eine Aufzählung von Projektnamen mit Tippfehlern auf die echte Liste abbilden oder auf „zeig mir einfach alle" sinnvoll reagieren — das kann eine Instanz besser als jedes Skript. Einträge einer JSON-Datei aufsummieren kann sie nicht verlässlich; an diesem Vorhaben gemessen nannte sie zehn, wo neun standen (Doku 1.4). Der ganze Ablauf unten folgt dieser Trennung.

---

## 1 Voraussetzungen

Drei Punkte, davon zwei einmalig und einer bei jedem Lauf:

1. **Claude in Chrome** ist installiert.
2. **Chrome läuft.** Das ist die einzige Bedingung, die bei **jedem** Lauf neu gilt: Die Verbindung geht über die Erweiterung, und die lebt nur in einem geöffneten Browser. Fehlt er, meldet die Anbindung „Browser extension is not connected" — unabhängig davon, wie richtig alles andere eingestellt ist. Ein Fenster genügt; claude.ai selbst muss nicht offen sein, weil der Skill sich seinen eigenen Tab anlegt. Die Anmeldung bleibt im Chrome-Profil erhalten und muss nicht wiederholt werden.
3. **In Chrome unter *Einstellungen → Downloads*: „Speicherort für jede Datei vor dem Download abfragen" ausschalten.** Sonst öffnet der erste Download einen Dateidialog, und ein Dialog legt die Browser-Anbindung vollständig lahm — sie empfängt dann keine Kommandos mehr, und der Dialog muss von Hand weggeklickt werden.
4. Der Skill liegt im Zielprojekt unter `.claude/skills/chat-export/`, zusammen mit `chat_export_convert.py` und seiner `README.md`. Die jeweils aktuelle Fassung holt der Nutzer sich aus `chat-export/` des Repositories; dort und nur dort wird sie gepflegt.

**Was hier ausdrücklich nicht steht:** die Anweisung, sich vorher bei claude.ai anzumelden. Der Skill nennt zur Laufzeit, mit welchem Konto Chrome angemeldet ist (Abschnitt 2.3) — das ist verlässlicher als eine Zusicherung, die niemand prüft, und es fängt auch den Fall auf, dass gar keine Anmeldung besteht.

---

## 2 Der Durchgang

Ausgangslage: Eine Claude-Code-Sitzung im Zielprojekt, etwa `modellbahn-fahrpult`. Vor drei Wochen wurden die Chats aus dem claude.ai-Projekt „Modellbahn-Fahrpult" hierher geholt; seitdem wurde dort weitergechattet.

**Es gibt genau zwei Haltepunkte.** Der erste vor dem ersten Abruf, der zweite nach der Statistik. Alles dazwischen läuft ohne Rückfrage, weil es nur liest.

### 2.1 Der Aufruf

```
@browser /chat-export
```

Das `@browser` ist in der VS-Code-Erweiterung Pflicht: Ohne es hängen die Browser-Werkzeuge nicht an der Nachricht, und der Skill steht ohne Browser da. Im CLI genügt einmal `claude --chrome` beim Start.

Fehlen die Werkzeuge, bricht der Skill sofort ab und sagt genau das — er versucht nicht, sich anders zu behelfen:

> Die Browser-Werkzeuge sind dieser Nachricht nicht angehängt. Ruf mich mit `@browser /chat-export` auf, oder starte Claude Code mit `claude --chrome`.

Der Aufruf muss kein Slash-Kommando sein. „Hol die neuen Chats aus dem Modellbahn-Projekt" oder „ich will Projekte aus meinem Claude-Konto importieren" trifft ihn genauso.

### 2.2 Erster Haltepunkt: er erklärt und fragt

```
  Ich hole Chats aus claude.ai-Projekten in dieses Repo — als durchsuchbare
  JSON-Dateien, nicht als fortsetzbare Chats. Dafür lese ich über Deinen
  angemeldeten Chrome die Projekt- und Chatlisten Deines Kontos und
  vergleiche sie mit dem, was hier schon liegt.

  Erst danach entscheidest Du, was geholt wird. Soll ich anfangen?
```

Ein Ja ist die Zustimmung für **alles Lesende**: Kontoauskunft, Projektliste, Chatlisten, Abgleich. Es ist nicht die Zustimmung zum Holen der Chats — die kommt am zweiten Haltepunkt.

### 2.3 Er nennt das Konto

Der erste Abruf gilt der Kontoauskunft und der Projektliste. Was er zurückgibt, legt der Skill unverlangt vor:

```
  Chrome ist bei claude.ai angemeldet als: Frank <herbrand@gmx.de>
  Dort suche ich die Projekte. 45 Projekte gefunden.
```

Das steht hier und nicht in einer Vorbedingung, weil es der einzige Punkt ist, an dem sich das Konto **zeigen** lässt, statt es zu verlangen. Denselben Projektnamen kann es in einem zweiten Konto geben; ein Abgleich nur über den Namen würde das nicht bemerken. Ist es das falsche Konto, wechselt der Nutzer es jetzt. Besteht gar keine Anmeldung, fällt es an derselben Stelle auf:

> In Chrome besteht keine Anmeldung bei claude.ai. Melde Dich in dem Konto an, dem die Projekte gehören, und sag Bescheid.

### 2.4 Er ordnet die Projektwahl zu

Hier arbeitet die Instanz, nicht das Skript. Drei Fälle, und alle drei enden an derselben Stelle:

**Der Nutzer hat die Projekte schon genannt.** Dann fragt der Skill nicht mehr — er ordnet zu und macht weiter. Passt eine Nennung nur ungefähr, fragt er einmal nach:

```
  „Modelbahn Fahrpult" und „Freecad" finde ich so nicht wörtlich.
  Gemeint sind wohl:
    • Modellbahn-Fahrpult
    • FreeCAD-Bedienung
  Richtig?
```

**Der Nutzer will erst sehen, was es gibt.** Dann zeigt der Skill die Projekte als Vorlage, aus der sich auswählen lässt — nach letzter Änderung sortiert, mit dem, was hier schon liegt:

```
  Projekte im Konto (45), die zwölf jüngsten:

    Modellbahn-Fahrpult          zuletzt 18.08.   Archiv hier: 34 Chats
    FreeCAD-Bedienung            zuletzt 06.08.   Archiv hier: 22 Chats
    mcu-slotring                 zuletzt 03.08.   kein Archiv
    Dachluken                    zuletzt 26.06.   kein Archiv
    ...

  Welche?
```

**Es liegt hier nur ein Archiv und der Nutzer sagt nichts weiter.** Dann nimmt der Skill dieses und sagt, dass er es nimmt.

### 2.5 Er holt die Statistik

Je gewähltes Projekt die Chatliste über alle Seiten, dann der Vergleich gegen `protokoll.json`. Das rechnet das Skript. Bei mehreren Projekten steht **eine** Tabelle mit einer Zeile je Projekt — damit die Zahlen scharf bleiben und die Haltepunkte bei zwei:

```
  Stand 19.08.2026

  Projekt                 Archiv  Quelle   neu  gewachsen  verschw.  Umfang   Empfehlung
  Modellbahn-Fahrpult         34      39     5          2         1   ~310 N.  Web
  FreeCAD-Bedienung           22      23     1          0         0    ~40 N.  Web

  Verschwunden in „Modellbahn-Fahrpult": „Fahrstufen-Kennlinie".
  Bleibt liegen — siehe unten.
```

Der verschwundene Chat wird **gemeldet und nie automatisch entfernt**; seine Dateien bleiben. Der Grund steht als Vorgabe 2.4 fest: Von hier aus lässt sich Löschung an der Quelle nicht von einem Verschieben in ein anderes Projekt unterscheiden, und beides nicht von einer Liste, die der Nutzer nicht bis zum Ende geblättert hat. Jede automatische Entfernung wäre im dritten Fall Datenverlust aus einem Bedienfehler.

### 2.6 Zweiter Haltepunkt: der Nutzer wählt den Weg

```
  Web-Weg     Abruf über die Weboberfläche, gebremst auf 4–12 s Abstand.
              Für die 9 Chats gut zwei Minuten. Sofort, kein Warten.
              Belastet die Weboberfläche; deshalb die Bremse.

  Export-Weg  Ein Kontoexport, der bis zum 24.07.2026 zurückreichen muss.
              Antrag, E-Mail, Download — die Wartezeit bestimmt claude.ai.
              Trägt alles in einem Zug, ohne Last je Chat.

  Empfehlung hier: Web-Weg für beide Projekte. Wenige Chats, kleine Anhänge.
  Was soll ich tun?
```

Er sagt „Empfehlung", nicht „ich mache jetzt". Die Wahl zwischen Wartezeit und Serverlast ist eine Abwägung, und die trifft der Nutzer (Doku 1.2). Eine Antwort genügt für alle Projekte; sie darf sie auch trennen („Export für Modellbahn, Web für FreeCAD"). Kippt die Empfehlung, nennt er den Grund:

```
  Empfehlung: Export-Weg.
  61 Chats, davon 18 mit Anhängen (geschätzt 40 MB). Über den Web-Weg
  wären das 61 gebremste Abrufe, gut zehn Minuten Dauerlast.
```

### 2.7 Der Hinweis, was nun geschieht

Kein Haltepunkt mehr, sondern die Ansage vor dem Lauf. Sie **nennt das Ersetzen mit Zahlen**, weil dabei Dateien entfernt werden und das in einem allgemeinen Satz untergehen würde:

```
  Ich hole 9 Chats über den Web-Weg, Abstand 4–12 s zufällig, etwa 2 Minuten.
  Alles kommt als eine Datei in Deinen Download-Ordner.

  Beim Umwandeln werden 2 Chats ersetzt; ihre bisherigen 3 Dateien
  entferne ich vorher und nenne sie einzeln.

  Los.
```

### 2.8 Web-Weg

```
  [1/9] Bremsen-Simulation kalibrieren        12 Nachr.   ✓   (8,3 s)
  [2/9] PWM-Frequenz und Motorgeräusch        48 Nachr.   ✓   (5,1 s)
  ...
  [9/9] Sound-Sampling aus Aufnahmen          22 Nachr.   ✓

  Heruntergeladen: chats_2026-08-19.json (1,4 MB)
```

Danach die lokale Hälfte — dasselbe Skript wie beim Export-Weg, dieselbe Baumlogik, dieselben Dateien:

```
  Modellbahn-Fahrpult: 7 Chats umgewandelt

    5 neu geschrieben
    2 ersetzt — vorherige Dateien entfernt:
        2026-07-14_pwm-frequenz-und-motorgeraeusch_9c3f21a8.json
        2026-07-14_pwm-frequenz-und-motorgeraeusch_9c3f21a8.thinking.json
        2026-07-02_bremsen-simulation-kalibrieren_4a71ce09.json

    Dateien: 7 Gespräch, 3 Denkschritte, 4 Anhänge, 2 Erzeugnisse
    Nebenzweige: 2 (zusammen 6 Nachrichten)
    Waisen im Verzeichnis: keine

  FreeCAD-Bedienung: 1 Chat umgewandelt, 1 neu geschrieben

  Protokolle fortgeschrieben.
```

Das Ersetzen **nennt** die entfernten Dateien; stilles Löschen wäre die nächste Fehlerquelle. Aufgeräumt wird vor dem Schreiben, weil sich der Dateistamm geändert haben kann: Wurde ein Chat umbenannt, entstünde sonst ein zweiter Stamm, und ein `grep` fände beide Fassungen (Vorgabe 2.6).

Zum Schluss, als **Bemerkung und nicht als Frage** — sonst wäre es ein dritter Haltepunkt:

```
  Hinweis: In der CLAUDE.md dieses Projekts steht kein Verweis auf das
  Archiv. Ohne ihn liegt es hier und wird nie gelesen. Der einzusetzende
  Block steht in der README des Skills; sag Bescheid, wenn ich ihn
  einsetzen soll.
```

### 2.9 Export-Weg

```
  Der Export muss bis zum 24.07.2026 zurückreichen.
  Grund: „Bremsen-Simulation kalibrieren" ist am 24.07. entstanden und
  seitdem gewachsen. Der Zeitraumfilter greift auf das Erstelldatum,
  nicht auf die letzte Änderung — ein kürzeres Fenster ließe ihn ganz aus,
  und nichts würde das melden.

  Soll ich den Antrag im Browser ausfüllen? Ich trage den 24.07. ein und
  lege den Absenden-Knopf vor.
```

Das ist der eigentliche Gewinn dieses Weges: Bisher muss der Nutzer diesen Satz lesen und das Datum von Hand in den Datumswähler übertragen. Die Rechnung dahinter ist die heikelste des ganzen Werkzeugs — ein zu knappes Fenster meldet nichts, es liefert einfach weniger.

Dann reißt die Kette, und der Skill sagt es geradeheraus:

```
  Angefordert. Der Link kommt per E-Mail und gilt 24 Stunden.
  In das Postfach gehe ich nicht — das ist ein anderer Dienst.
  Lade die ZIP herunter und sag Bescheid; ich finde sie im
  Download-Ordner von selbst.
```

Sobald die Datei da ist, läuft alles Weitere automatisch — mit derselben Ausgabe wie in 2.8. Weil beide Wege denselben Konverter benutzen, ist das Ergebnis nicht *ähnlich*, sondern dasselbe.

---

## 3 Wenn etwas schiefgeht

**Cloudflare oder ein Captcha.** Die Anbindung hält an und fragt. Der Skill umgeht das nicht und soll es nicht — er merkt sich, welche Chats schon geholt sind, und setzt nach dem Wegklicken fort.

**Der Download öffnet einen Dialog.** Dann war die Einstellung aus Abschnitt 1, Punkt 3 nicht gesetzt. Der Skill kann das dann nicht mehr melden, weil die Anbindung blockiert ist — deshalb steht die Einstellung ganz vorn und wird beim Aufruf einmal geprüft, solange das noch möglich ist.

**Ein Chat ohne Datumsgrenze.** Bei einer Erstmigration ohne Protokoll kennt niemand den Projektbeginn. Dann rät der Skill nicht, sondern fordert an: *„4 wartende Chats haben keinerlei Datumsgrenze. Ich kann nicht sagen, wie weit ein Export zurückreichen muss."* Über den Web-Weg ist das erledigt, denn dort steht `created_at` je Chat in der Liste — genau deshalb wird der Sondierungsexport aus Doku 1.5 Schritt 0 überflüssig.

**Die Zahlen wirken falsch.** Dann liegt der Verdacht zuerst beim Protokoll, nicht beim Verzeichnis: Bei Widerspruch gilt das Protokoll (Vorgabe 2.4). `diff` meldet als Einziges auch ein Zuviel — Dateien, die kein Protokolleintrag beansprucht (Vorgabe 2.6).

---

## 4 Was der Skill nie tut

- **Er entscheidet nicht, welcher Weg genommen wird.** Er legt beide mit ihrem Preis vor.
- **Er zählt nicht selbst.** Jede Zahl kommt aus einem Skript, das die JSON parst.
- **Er entfernt nichts, was verschwunden scheint.** Er meldet es und lässt es liegen.
- **Er fasst nichts zusammen.** Chattext wird kopiert, nie nacherzählt — der Web-Weg liefert JSON, das nie durch einen Kontext läuft. Genau darin ist dieser Weg dem entfallenen Lese-Weg überlegen: Dort ging jeder Turn durch die Instanz, hier geht die Datei am Modell vorbei (Vorgabe 2.8).
- **Er ruft nicht ungebremst ab.** 4 bis 12 Sekunden, gleichverteilt gewürfelt, damit kein regelmäßiges Muster entsteht.
- **Er geht nicht in das E-Mail-Postfach.**
- **Er verlangt keine Zusicherung, die er selbst prüfen kann.** Das Konto wird genannt, nicht erfragt.

---

## 5 Was sich dadurch still auflöst

Zwei Dinge, die bisher nötig waren, verschwinden ersatzlos. Beide sind im Fahrplanpunkt 27 als Folge vermerkt und gehören beim Umsetzen in Kapitel 1 der Doku.

**Der Wegwerfchat für die Chatliste.** Bisher muss die Liste in einem eigens angelegten Chat geholt und dieser danach gelöscht werden — weil `recent_chats` den laufenden Chat nicht mitlistet und er sonst lautlos aus dem Archiv fiele (Doku 1.5, 1.6). Der Web-Weg listet ohne Chat und übergeht nichts.

**Der Rückweg des Protokolls ins Projektwissen.** Der trug den Lese-Weg, den es nicht mehr gibt. Als Selbstauskunft des Quellprojekts bleibt er nützlich — als Pflichtschritt entfällt er.
