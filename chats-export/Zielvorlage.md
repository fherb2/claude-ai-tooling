# Zielvorlage: der Skill aus Sicht des Nutzers

**Was diese Datei ist.** Eine Beschreibung des angestrebten Verhaltens, geschrieben als Durchgang aus der Sicht dessen, der das Werkzeug benutzt. Sie dient dazu, den Entwurf zu beurteilen, bevor er gebaut wird, und ist später die Vorlage für die Anwenderdokumentation (Fahrplanpunkt 13).

**Was sie nicht ist.** Sie ist **kein Plan** im Sinne der Arbeitsanweisungen §1.3 und der Repo-`CLAUDE.md`. Der Plan des nächsten Schrittes steht ausdetailliert im Fahrplan, Punkt 27, und nur dort; eine neue Sitzung nimmt ihren Auftrag von dort, nicht von hier. Diese Datei beschreibt das Ziel, nicht den Weg dorthin.

**Stand.** Nichts hiervon existiert. Was existiert, sind die Skripte darunter — Baumlauf, Blockauswahl, Protokollführung, Fensterrechnung, Ersetzen samt Aufräumen — und der am 19. August 2026 belegte Zugriff auf beide claude.ai-Endpunkte über die Chrome-Anbindung (Nachweis in `testlauf.md`). Der Skill ist die Klammer darum. Alle Zahlen in den Beispielen sind erfunden, ausgenommen die ausdrücklich als gemessen bezeichneten.

---

## 1 Einmalig, bevor es losgeht

Drei Dinge, danach nie wieder:

1. **Claude in Chrome** ist installiert, und in Chrome besteht eine Anmeldung bei claude.ai — mit dem Konto, dem die Quellprojekte gehören.
2. **In Chrome unter *Einstellungen → Downloads*: „Speicherort für jede Datei vor dem Download abfragen" ausschalten.** Sonst öffnet der erste Download einen Dateidialog, und ein Dialog legt die Browser-Anbindung vollständig lahm — sie empfängt dann keine Kommandos mehr, und der Dialog muss von Hand weggeklickt werden.
3. Der Skill liegt im Zielprojekt unter `.claude/skills/`.

---

## 2 Der Normalfall: nachtragen

Ausgangslage: Eine Claude-Code-Sitzung im Zielprojekt, etwa `modellbahn-fahrpult`. Vor drei Wochen wurden die Chats aus dem claude.ai-Projekt „Modellbahn-Fahrpult" hierher geholt; seitdem wurde dort weitergechattet.

### 2.1 Der Aufruf

```
@browser /chats-nachtragen
```

Das `@browser` ist in der VS-Code-Erweiterung Pflicht: Ohne es hängen die Browser-Werkzeuge nicht an der Nachricht, und der Skill steht ohne Browser da. Im CLI genügt einmal `claude --chrome` beim Start.

Fehlen die Werkzeuge, bricht der Skill sofort ab und sagt genau das — er versucht nicht, sich anders zu behelfen:

> Die Browser-Werkzeuge sind dieser Nachricht nicht angehängt. Ruf mich mit `@browser /chats-nachtragen` auf, oder starte Claude Code mit `claude --chrome`.

### 2.2 Er stellt fest, worum es geht

Er sieht unter `.claude/imported_chats/` nach, welche Quellprojekte hier schon ein Archiv haben. Bei genau einem nimmt er es; bei mehreren fragt er:

> Hier liegen zwei Archive: `modellbahn-fahrpult` (34 Chats, zuletzt abgeglichen 28.07.) und `freecad-bedienung` (22 Chats, 06.08.). Welches?

Gibt es noch keines, ist es eine Erstmigration, und er sagt gleich dazu, dass dafür der Export-Weg der richtige ist (Abschnitt 2.6).

### 2.3 Er holt die Lage, ohne etwas zu verändern

Im Browser: ein Tab auf claude.ai, die Projektliste, dann die Chatliste des Projekts über alle Seiten. Das sind zwei bis drei Abrufe, keine Last. Die Liste lädt er als kleine Datei herunter und übergibt sie dem Skript.

**Das Skript rechnet, nicht der Skill.** Das ist keine Förmlichkeit: Eine Instanz kann einen Zeitstempel mikrosekundengenau vorlesen und sich im selben Atemzug bei neun Einträgen verzählen — beides ist an diesem Vorhaben gemessen worden (Doku 1.4). Also vergleicht das Skript die Liste gegen `protokoll.json` und gibt zurück, was Sache ist.

Dann legt der Skill vor:

```
Quellprojekt „Modellbahn-Fahrpult", Stand 19.08.2026

  34 Chats im Archiv, 39 in der Quelle

   5 neu            seit dem letzten Abgleich hinzugekommen
   2 gewachsen      weitergechattet, Archivstand veraltet
   1 verschwunden   „Fahrstufen-Kennlinie" — im Archiv, nicht mehr in der Liste
  32 unverändert

  Umfang der 7 zu holenden Chats: rund 310 Nachrichten, 4 mit Anhängen
```

Der verschwundene Chat wird **gemeldet und nie automatisch entfernt** — seine Dateien bleiben liegen. Der Grund steht als Vorgabe 2.4 fest: Von hier aus lässt sich Löschung an der Quelle nicht von einem Verschieben in ein anderes Projekt unterscheiden, und beides nicht von einer Liste, die der Nutzer nicht bis zum Ende geblättert hat. Jede automatische Entfernung wäre im dritten Fall Datenverlust aus einem Bedienfehler.

### 2.4 Er empfiehlt, der Nutzer entscheidet

```
  Empfehlung: Web-Weg.

  Web-Weg     7 Abrufe, gebremst auf 4–12 s Abstand → gut eine Minute.
              Sofort, kein Warten, keine E-Mail.
              Belastet die Weboberfläche; deshalb die Bremse.

  Export-Weg  Ein Kontoexport, der bis zum 24.07. zurückreichen muss
              (der ältere der beiden gewachsenen Chats entstand dann).
              Antrag, E-Mail, Download — die Wartezeit bestimmt claude.ai.
              Lohnt hier nicht: 7 Chats sind wenig, die Anhänge sind klein.

  Was soll ich tun?
```

Er sagt „Empfehlung", nicht „ich mache jetzt". Die Wahl zwischen Wartezeit und Serverlast ist eine Abwägung, und die trifft der Nutzer — so festgelegt in Doku 1.2. Kippt die Empfehlung, nennt er den Grund:

```
  Empfehlung: Export-Weg.
  61 Chats, davon 18 mit Anhängen (geschätzt 40 MB). Über den Web-Weg
  wären das 61 gebremste Abrufe, gut zehn Minuten Dauerlast auf der
  Weboberfläche. Ein Export erledigt das in einem Zug.
```

### 2.5 Web-Weg

Der Nutzer wählt den Web-Weg. Der Skill zeigt, was er vorhat, und fragt einmal:

```
  Ich hole 7 Chats, Abstand 4–12 s zufällig → etwa 1 Minute.
  Alles kommt als eine Datei in den Download-Ordner.
  Einverstanden?
```

Dann läuft es, mit sichtbarem Fortschritt:

```
  [1/7] Bremsen-Simulation kalibrieren        12 Nachr.   ✓   (8,3 s)
  [2/7] PWM-Frequenz und Motorgeräusch        48 Nachr.   ✓   (5,1 s)
  ...
  [7/7] Sound-Sampling aus Aufnahmen          22 Nachr.   ✓

  Heruntergeladen: chats_modellbahn-fahrpult_2026-08-19.json (1,2 MB)
```

Danach die lokale Hälfte — dasselbe Skript wie beim Export-Weg, dieselbe Baumlogik, dieselben Dateien:

```
  Umgewandelt: 7 Chats

    5 neu geschrieben
    2 ersetzt — vorherige Dateien entfernt und benannt:
        2026-07-14_pwm-frequenz-und-motorgeraeusch_9c3f21a8.json
        2026-07-14_pwm-frequenz-und-motorgeraeusch_9c3f21a8.thinking.json

    Dateien: 7 Gespräch, 3 Denkschritte, 4 Anhänge, 2 Erzeugnisse
    Nebenzweige: 2 (zusammen 6 Nachrichten)
    Waisen im Verzeichnis: keine

  Protokoll fortgeschrieben: 39 Chats, Stand 19.08.2026 21:12
```

Das Ersetzen **nennt** die entfernten Dateien; stilles Löschen wäre die nächste Fehlerquelle. Aufgeräumt wird vor dem Schreiben, weil sich der Dateistamm geändert haben kann: Wurde ein Chat umbenannt, entstünde sonst ein zweiter Stamm, und ein `grep` fände beide Fassungen (Vorgabe 2.6).

Zum Schluss, aber nur wenn nötig:

```
  In der CLAUDE.md dieses Projekts steht noch kein Hinweis auf das Archiv.
  Ohne ihn liegt es hier und wird nie gelesen. Soll ich den Block einsetzen?
```

### 2.6 Export-Weg

Der Nutzer wählt den Export. Hier bleibt Handarbeit:

```
  Der Export muss bis zum 24.07.2026 zurückreichen.
  Grund: „Bremsen-Simulation kalibrieren" ist am 24.07. entstanden und
  seitdem gewachsen. Der Zeitraumfilter greift auf das Erstelldatum,
  nicht auf die letzte Änderung — ein kürzeres Fenster ließe ihn ganz aus,
  und nichts würde das melden.

  Soll ich den Antrag im Browser ausfüllen? Ich trage den 24.07. ein und
  lege den Absenden-Knopf vor.
```

Das ist der eigentliche Gewinn dieses Schrittes: Bisher muss der Nutzer diesen Satz lesen und das Datum von Hand in den Datumswähler übertragen. Die Rechnung dahinter ist die heikelste des ganzen Werkzeugs — ein zu knappes Fenster meldet nichts, es liefert einfach weniger.

Dann reißt die Kette, und der Skill sagt es geradeheraus:

```
  Angefordert. Der Link kommt per E-Mail und gilt 24 Stunden.
  In das Postfach gehe ich nicht — das ist ein anderer Dienst.
  Lade die ZIP herunter und sag Bescheid; ich finde sie im
  Download-Ordner von selbst.
```

Sobald die Datei da ist, läuft alles Weitere automatisch — mit derselben Ausgabe wie in 2.5. Weil beide Wege denselben Konverter benutzen, ist das Ergebnis nicht *ähnlich*, sondern dasselbe.

---

## 3 Wenn etwas schiefgeht

**Cloudflare oder ein Captcha.** Die Anbindung hält an und fragt. Der Skill umgeht das nicht und soll es nicht — er merkt sich, welche Chats schon geholt sind, und setzt nach dem Wegklicken fort.

**Der Download öffnet einen Dialog.** Dann war die Einstellung aus Abschnitt 1 nicht gesetzt. Der Skill kann das dann nicht mehr melden, weil die Anbindung blockiert ist — deshalb steht die Einstellung ganz vorn und wird beim Aufruf einmal geprüft, solange das noch möglich ist.

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

---

## 5 Was sich dadurch still auflöst

Zwei Dinge, die bisher nötig waren, verschwinden ersatzlos. Beide sind im Fahrplanpunkt 27 als Folge vermerkt und gehören beim Umsetzen in Kapitel 1 der Doku.

**Der Wegwerfchat für die Chatliste.** Bisher muss die Liste in einem eigens angelegten Chat geholt und dieser danach gelöscht werden — weil `recent_chats` den laufenden Chat nicht mitlistet und er sonst lautlos aus dem Archiv fiele (Doku 1.5, 1.6). Der Web-Weg listet ohne Chat und übergeht nichts.

**Der Rückweg des Protokolls ins Projektwissen.** Der trug den Lese-Weg, den es nicht mehr gibt. Als Selbstauskunft des Quellprojekts bleibt er nützlich — als Pflichtschritt entfällt er.
