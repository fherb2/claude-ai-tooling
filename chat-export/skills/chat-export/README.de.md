# chat-export — Chats aus claude.ai in dein Projekt holen

**Dieser Skill holt Chats aus deinen claude.ai-Projekten und legt sie als durchsuchbare JSON-Dateien in dem Projekt ab, in dem Claude Code gerade läuft.** Gedacht sind sie zum Wiederfinden früheren Zusammenhangs: Was in einem Chat einmal besprochen wurde, steht danach im Projekt und ist auffindbar, statt nur im Konto zu liegen.

Auch weiter wachsende Chats und neue Chats können aktualisiert / ergänzt werden.

Was dabei entsteht, sind Archivdateien, keine fortsetzbaren Chats. Ein importierter Chat lässt sich lesen und durchsuchen, aber nicht an dieser Stelle weiterführen.

## Installation

Kopiere den Ordner `skills/chat-export/` mit seinem gesamten Inhalt an einen der beiden Orte:


| Ort         | Pfad                                    | Gilt für           |
| ----------- | --------------------------------------- | ------------------- |
| Persönlich | `~/.claude/skills/chat-export/`         | alle deine Projekte |
| Projekt     | `<projekt>/.claude/skills/chat-export/` | nur dieses Projekt  |

Der Ordner enthält zwei Sprachfassungen der Anweisungsdatei, `SKILL.de.md` und `SKILL.en.md`. Übertrage die gewünschte Fassung an den Zielort und benenne **dort** genau diese eine in `SKILL.md` um — Claude Code erkennt nur diesen Namen, die jeweils andere Fassung lässt du liegen oder löschst sie. Der Rest — das Hilfsskript und diese README zur Dokumentation für dich — bleibt unverändert.

## Bedienung

### Voraussetzungen

> Hinweis zur Claude Chrome Extension:
>
> Der hier beschriebene Vorgang mit der Extension ist in 08/2026 mit der Beta-Version getestet und bis zum Erfolg, die Bridge (s.u.) herzustellen, manchmal stressig. Hoffnung besteht, dass Anthropic hier noch etwas nutzerfreundlicher entwickelt.

**Einmalig einzurichten:**

Punkt 1 und 3 entsprechen dabei der vollständigen Installation der Claude Chrome Extension und sind eine Voraussetzung, die du vielleicht schon für andere Zwecke geschaffen hast.

1. **Claude Extension in Chrome installieren** und die Verbindung zu Claude Code einmal herstellen: im Terminal `claude --chrome` aufrufen. Das legt die Datei an, über die Claude Code mit der Erweiterung spricht. **Chrome danach einmal vollständig neu starten** — die Datei wird nur beim Start gelesen.
2. **In Chrome die Download-Nachfrage abschalten:** *Einstellungen → Downloads → „Speicherort für jede Datei vor dem Download abfragen"* aus. Bleibt sie an, öffnet der erste Download ein Dateifenster, und das legt die Verbindung zum Browser lahm ([warum](#warum-ein-browser-gebraucht-wird)).
3. **Auf claude.ai den Connector einschalten:** *Einstellungen → Connectors → „Claude in Chrome"*. Das gilt je Konto und wirkt nicht rückwirkend auf bereits geöffnete Tabs.

**Bei jedem Lauf:**

4. **Chrome läuft.** Ein Fenster genügt; claude.ai selbst muss nicht offen sein, der Skill legt sich seinen eigenen Tab an.
5. **Claude Code läuft in dem Projekt, in das importiert werden soll.** Das Ziel ist immer das Projekt, in dem du gerade arbeitest — der Skill holt die Chats dorthin, wo die Sitzung steht. Du kannst auch die VSCode Claude Code Extension dazu verwenden.
6. Du musst zuerst **die Bridge zwischen Claude Code und der Chrome Claude Extension herstellen**. Zu diesem Zweck musst du dich zuerst *in Chrome mit dem gleichen Konto anmelden wie in Claude Code*. Rufe dann in Chrome mal das Claude Chat Fenster der Claude Chrome Extension auf: Wenn es startet und nicht meldet, dass noch eine Anmeldung stattfinden muss, ist es ok. Wenn es auch erst eine Anmeldung benötigt, melde es an. Spätestens jetzt ist die Claude Chrome Extension wirklich mit dem Konto verbunden. Ausführlich protokollierte Fehlerbilder beim Herstellen dieser Bridge und was jeweils geholfen hat, stehen in [`chrome-zugriff.de.md`](../../chrome-zugriff.de.md).
7. **Stelle jetzt aus Claude Code die Bridge her**, indem du am Prompt "@browser" übergibst. (Den meist angehängten Vorschlag kannst du abwenden, indem du hinter @browser noch ein Leerzeichen setzt.)
8. **Frage abschließend Claude Code**, ob es einen Tab in Chrome öffnen kann. Erst wenn das funktioniert, steht die Bridge tatsächlich.
9. Falls Du **aus einem anderen Claude-Account Chats importieren** möchtest, kannst du dich jetzt in einem neuen Tab in Chrome bei Claude.ai abmelden und mit dem anderen Konto anmelden. Ein E-Mail-Turn ist dabei wahrscheinlich fällig. Die Bridge bricht dabei nicht.

   ---

   **Wenn Du das erreicht hast, kann Claude Code, wo du die Chats hin importieren möchtest, mit dem Claude.ai-Konto auf Chrome, mit dem du zu diesem Zeitpunkt angemeldet bist, arbeiten, um die Chats dort zu exportieren.**

   ---
10. Du wechselst nun zu **Claude Code in dem Projekt, in das importiert werden soll.** Der Skill holt die Chats hierhin, wo die Sitzung steht und nutzt den Zugriff über Chrome, um an die Quelldaten zu kommen.

### Der erste Prompt zum Ex- und Import

Wie gesagt: Du bist in der Claude Instanz im Zielprojekt. Dort muss der Skill bekannt sein.

Du hast in den Schritten oben bereits `@browser` an diesem Prompt übergeben, was über dem Prompt weiterhin angezeigt wird. Wenn du der Meinung bist, dass diese Bridge gestört ist, kannst du die Instanz direkt über den Prompt danach fragen oder sie wird es von sich aus melden. Ohne diese Bridge hat der Skill keinen Zugriff auf Chrome und damit die Quelle. **Jetzt kannst du beginnen:**

```
Ich möchte Chats aus einem Projekt exportieren und hierher importieren. Mit der Quelle bist du bereits über Chrome verbunden. Bitte gib mir zuerst eine Liste aller Projekte dort, dann sage ich dir genauer, um welches Projekt es sich handelt.
```

In diesem Sinne hast du relativ freie Gestaltungsmöglichkeit der Anfrage. Du kannst auch sofort das Projekt benennen oder sogar mehrere Projekte angeben. Lasse dich von Claude durch die weitere Sitzung führen.

Wenn die Quelle kein Team-Account ist, hast du die Möglichkeit, den Export über einen Download zu machen. Claude wird dich hierzu beraten. In Team-Konten gibt es diese Möglichkeit nicht, und Claude bleibt dann nur der Export über den Browser übrig, den er in Chrome bedient.

### Der Ablauf

Per Skill führt dich Claude durch den Export und fragt, wo er eine Entscheidung oder schreibende Zugriffsrechte benötigt. Alles dazwischen läuft durch, weil er nur liest.

**Claude nennt das Konto.** Ungefragt, sobald er es kennt:

```
Chrome ist bei claude.ai angemeldet als: maxebaumann@gmx.de's Organization
Dort suche ich die Projekte.
```

Ist das nicht das Konto, aus dem du importieren wolltest, wechselst du spätestens jetzt in Chrome und lässt ihn neu anfangen ([warum er es nennt](#warum-der-skill-das-konto-nennt-statt-danach-zu-fragen)).

**Claude klärt, welche Projekte gemeint sind.** Drei Fälle, je nachdem, was du gesagt hast:

- Du hast die Projekte **genannt** — er ordnet sie der echten Liste zu und macht weiter. Passt ein Name nur ungefähr, fragt er einmal kurz nach („*Projekt ABC* finde ich so nicht wörtlich — gemeint ist wohl *Projekt A-B-C*?").
- Du willst **erst sehen, was es gibt** — dann legt er die Projekte des Kontos vor, nach letzter Änderung sortiert, mit dem Vermerk, was davon schon im Ziel-Projekt liegt. Du wählst aus.
- Es liegt nur **ein einziges Archiv** im Projekt und du sagst nichts weiter — dann nimmt er dieses und sagt, dass er es nimmt.

**Claude holt die Statistik und legt sie vor.** Je Projekt eine Zeile:

```
Projekt                 Archiv  Quelle   neu  gewachsen  verschw.  Empfehlung
Projekt A-B-C              34      39     5          2         1  Web
Auch-ein Projekt           22      23     1          0         0  Web
```

*Archiv* ist der Stand im Projekt, *Quelle* der im Konto. *Neu* sind Chats, die noch nie geholt wurden, *gewachsen* sind solche, die seit dem letzten Mal weitergeführt wurden, *verschwunden* sind welche, die das Konto nicht mehr führt ([was damit geschieht](#warum-ein-verschwundener-chat-liegen-bleibt)). Bis hierher ist nichts geholt und nichts geschrieben worden ([warum erst gezählt wird](#warum-zuerst-nur-gezählt-wird)).

**Du wählst den Weg.** Das ist der zweite und letzte Haltepunkt. Der Skill legt beide Wege (Export per Archiv und Downloadlink per Mail, Export direkt über die Web-Schnittstelle in Chrome) mit ihren Kosten vor und **empfiehlt** einen, entscheidet aber nicht ([warum nicht](#warum-du-den-weg-wählst-und-nicht-der-skill)). Eine Antwort genügt für alle Projekte; du darfst sie auch trennen („Export für A-B-C, Web für alle anderen").

**Claude sagt an, was nun geschieht** — mit Zahlen, weil dabei auch Dateien ersetzt und entfernt werden. Das ist kein Haltepunkt mehr, sondern die letzte Ansage vor dem Lauf.

**Claude läuft und berichtet.** Beim Web-Weg siehst du den Fortschritt Chat für Chat. Am Ende steht, was geschrieben und was ersetzt wurde — ersetzte Dateien einzeln benannt —, und ein ausdrücklicher Schlusssatz, dass er fertig ist ([was dann im Ordner liegt](#was-am-ende-im-ordner-liegt)).

### Die zwei Wege

Beide liefern **dasselbe Ergebnis**: dieselben Dateien, derselbe Inhalt — auch dieselben Lücken ([was grundsätzlich nicht mitkommt](#was-nicht-mitkommt)). Sie unterscheiden sich nur darin, wie die Chats aus dem Konto herauskommen.

**Web-Weg** — der Skill liest die Chats direkt über deinen angemeldeten Chrome-Browser. Kein Warten, es geht sofort los. Dafür ruft er gebremst ab, mit vier bis zwölf Sekunden Abstand je Chat; bei vielen Chats summiert sich das. Die richtige Wahl für **einige wenige Chats**, etwa wenn du regelmäßig nachträgst.

**Export-Weg** — du beantragst bei claude.ai einen Datenexport deines Kontos. Der Skill füllt den Antrag im Browser aus und legt dir den Absenden-Knopf vor; er nennt dabei das Datum, bis zu dem der Export zurückreichen muss, und begründet es. Danach **reißt die Kette**: Der Download-Link kommt per E-Mail und gilt 24 Stunden. In dein Postfach geht der Skill nicht — du lädst die Datei herunter und sagst Bescheid, den Rest findet er von selbst. Die richtige Wahl für **viele Chats oder große Anhänge**, weil alles in einem Zug kommt, ohne Last je Chat.

> **In Team- und Enterprise-Konten gibt es diesen Export-Weg nicht** — dort kann nur der Primary Owner der Organisation exportieren. Für ein gewöhnliches Mitglied ist der Web-Weg damit nicht die bequemere, sondern die **einzige** Möglichkeit.

### Wenn etwas klemmt

**„Die Browser-Werkzeuge sind dieser Nachricht nicht angehängt."** Das `@browser` am Anfang der Nachricht fehlt.

**„Browser extension is not connected."** Klingt nach einem kaputten Aufbau, heißt aber meist nur, dass Chrome gerade nicht läuft — oder dass die Erweiterung selbst nicht angemeldet ist. Das ist von der Anmeldung auf der claude.ai-Seite getrennt: Prüfen kannst du es, indem du in der Erweiterung selbst einen Chat öffnest.

**„Claude in Chrome is turned off in your settings."** Der Connector ist für dieses Konto nicht eingeschaltet (Voraussetzung 3). Nach dem Einschalten musst du den betroffenen Tab neu laden — die Einstellung wirkt nicht auf bereits offene Tabs.

**Ein Dateifenster geht auf und nichts geht mehr weiter.** Dann war die Download-Nachfrage doch noch an (Voraussetzung 2). Klick das Fenster weg, schalte die Einstellung ab und lass den Skill neu anfangen.

**Eine Sicherheitsabfrage von claude.ai.** Der Skill umgeht sie nicht und soll das auch nicht. Er hält an, du klickst sie weg, er setzt dort fort, wo er war — bereits geholte Chats holt er nicht noch einmal.

### Der Zielordner – Die importierten Chats nutzen

Claude wird dir einen Zielordner im Projekt vorschlagen. Achte darauf, ob du diesen Ordner in ein remote-Repo übertragen willst.

Wenn du in Claude Code im Projekt darauf hinweisen willst, dass er frühere Chats mal nach etwas durchsuchen soll, sag ihm einfach, wo die Chats liegen. Die Chats sind so formatiert, dass Claude sich bestens darin auskennt.

Was leider nicht geht: Diese Chats in Claude Code fortzusetzen. Aber sag einfach Claude, was er lesen soll und dass du den Chat hier wieder aufgreifen möchtest. So kennt Claude den Kontext des alten Chats und du kannst unmittelbar darauf aufbauen.

## Hintergrund

Dieser Teil erklärt, warum der Skill wonach fragt und was er aus deinen Angaben macht. Zum Bedienen brauchst du ihn nicht.

### Warum ein Browser gebraucht wird

Deine Chats liegen in deinem claude.ai-Konto, nicht auf deiner Festplatte. Claude Code allein kommt dort nicht heran: Es hat keinen Zugang zu deinem Konto und kann sich auch keinen verschaffen. Was es hat, ist der Weg über **deinen** Browser — dort bist du bereits angemeldet, und der Skill benutzt genau diese bestehende Anmeldung, um die Chats zu lesen. Er meldet sich nirgends an und kennt kein Passwort von dir.

Daraus folgt der Rest: Chrome muss laufen, weil eine Verbindung zu einem geschlossenen Browser nicht besteht. Und ein Dateifenster im Browser blockiert alles, weil der Browser währenddessen keine Befehle mehr annimmt — deshalb die Einstellung mit der Download-Nachfrage, noch bevor der erste Download stattfindet.

### Warum der Skill das Konto nennt, statt danach zu fragen

Zusicherungen prüft niemand nach. Wenn der Skill dich fragte „bist du im richtigen Konto angemeldet?", wäre deine Antwort bestenfalls eine Vermutung — und der häufigste Fehler wäre der, den beide nicht bemerken: **Denselben Projektnamen kann es in einem zweiten Konto geben.** Ein Abgleich, der nur über den Namen läuft, würde stillschweigend das falsche Archiv fortschreiben.

Deshalb nennt der Skill, was er tatsächlich vorfindet, sobald er es weiß. Das fängt zugleich den Fall auf, dass gar keine Anmeldung besteht.

Dass Chrome und Claude Code an verschiedenen Konten hängen dürfen, ist dabei kein Versehen, sondern geprüft: Der Skill sieht immer die Sitzung, die im Browser gerade aktiv ist. Für dich heißt das, dass du das Quellkonto durch einen Kontowechsel in Chrome bestimmst — nicht dadurch, mit welchem Konto du Claude Code benutzt.

### Warum zuerst nur gezählt wird

Bevor irgendein Chat geholt wird, vergleicht der Skill die Chatliste des Kontos mit dem, was im Projekt schon liegt. Das kostet nichts und beantwortet die Frage, die du für deine Entscheidung brauchst: **wie viel** überhaupt fehlt. Fünf nachzutragende Chats sind eine Sache von Minuten, zweihundert eine ganz andere — und erst mit dieser Zahl lässt sich der Weg sinnvoll wählen.

Der zweite Grund ist Verlässlichkeit. Alles, was gezählt und verglichen wird, rechnet ein Skript, das die Dateien tatsächlich liest — nicht die Claude-Instanz aus dem Gedächtnis. Beim Aufsummieren vertut sich ein Sprachmodell, und zwar lautlos: In einem Versuch nannte es zehn Einträge, wo neun standen. Jede Zahl, die du zu sehen bekommst, stammt deshalb aus einem Skriptlauf.

### Warum du den Weg wählst und nicht der Skill

Die beiden Wege unterscheiden sich in einer Abwägung, die niemand für dich treffen kann: **Wartezeit gegen Belastung.** Der Web-Weg fängt sofort an, ruft aber Chat für Chat über die normale Weboberfläche ab — bei vielen Chats ist das eine spürbare Dauerlast auf einem Dienst, den du mit anderen teilst. Deshalb die Bremse von vier bis zwölf Sekunden, zufällig gestreut: Sie hält die Last niedrig und vermeidet das gleichmäßige Muster, an dem ein Massenabruf erkennbar wäre.

Der Export-Weg belastet nichts, weil er ein einziges Paket erzeugt — aber wann es fertig ist, bestimmt claude.ai, nicht du, und der Link läuft nach 24 Stunden ab.

Was davon besser passt, hängt an deiner Lage: wie eilig es ist, wie viele Chats fehlen, wie groß deren Anhänge sind. Der Skill rechnet dir das aus und empfiehlt; entscheiden sollst du.

### Warum ein verschwundener Chat liegen bleibt

Führt das Konto einen Chat nicht mehr, den das Projekt kennt, meldet der Skill das — und **entfernt nichts**. Der Grund: Von außen sind drei völlig verschiedene Ursachen nicht voneinander zu unterscheiden.

Der Chat kann an der Quelle **gelöscht** worden sein. Er kann in ein **anderes Projekt verschoben** worden sein und dort unverändert weiterleben. Oder die Liste wurde schlicht **nicht bis zum Ende durchgeblättert**. Im dritten Fall wäre ein automatisches Löschen Datenverlust aus einem Bedienfehler — und ausgerechnet der stille, der niemandem auffällt.

Deshalb bleibt die Entscheidung bei dir. Der Skill sagt dir, welcher Chat betroffen ist; ob seine Dateien verschwinden sollen, entscheidest du und niemand sonst.

### Was am Ende im Ordner liegt

Die Chats landen unter `<projekt>/.claude/imported_chats/<quellprojekt>/` — ein flacher Ordner je claude.ai-Projekt, ohne Unterordner. Willst du sie woanders haben, sag es beim Aufruf; der Skill nimmt dann diesen Ort.

Je Chat entsteht eine **Gesprächsdatei** mit den Redebeiträgen, benannt nach Datum, Titel und Kennung des Chats — so ist sie über den Dateinamen auffindbar, bevor sie überhaupt geöffnet wird. Daneben liegen, sofern der Chat sie hergibt, bis zu drei Zusatzdateien: eine mit den **Überlegungen**, die zu den Antworten führten, eine mit dem **Inhalt hochgeladener Dateien** und eine mit dem, was **die KI erzeugt hat** — Artefakte, Dateien, Codeänderungen.

Getrennt liegen sie, weil sie den Umfang sonst vervielfachen würden: Die Überlegungen allein sind fast so lang wie das Gespräch selbst. Wer einen Chat nachliest, will in aller Regel das Gespräch — die Zusatzdateien sind da, wenn man sie braucht, und stören nicht, wenn nicht.

Dazu kommt eine `protokoll.json`. Sie merkt sich, welche Chats geholt wurden und auf welchem Stand sie waren. Nur deshalb kann ein späterer Lauf sagen, was neu ist und was gewachsen — ohne sie wäre jeder Import ein Neuanfang.

Wird ein gewachsener Chat erneut geholt, **ersetzt** seine neue Fassung die alte vollständig; die alten Dateien werden vorher entfernt und dabei einzeln genannt. Stilles Löschen gäbe es hier nicht.

### Was nicht mitkommt

Nicht alles, was in einem Chat zu sehen war, steht hinterher auch im Archiv — teils, weil Anthropic es nicht herausgibt, teils, weil es das Archiv unbrauchbar aufblähen würde.

**Bilder und andere nicht-textliche Anhänge** kommen nur als Dateiname. Ihr Inhalt ist in dem, was das Konto herausgibt, schlicht nicht enthalten. Textdateien dagegen kommen vollständig mit.

**Werkzeugaufrufe und ihre Ergebnisse** werden gezählt, aber nicht gespeichert. Das ist der weitaus größte Posten und besteht überwiegend aus Material, das ohnehin woanders steht — Dateiinhalte, Suchergebnisse, Zwischenschritte.

**Die Überlegungen können fehlen.** Das ist keine Eigenheit dieses Skills: Claude legt sie manchmal offen und manchmal nicht, und zwar in derselben Quelle — gemessen wechselte es innerhalb eines einzigen Chats von Tag zu Tag. Woran es hängt, ist nicht bekannt. Praktisch heißt das: Ein Archiv ohne Überlegungen ist eine Stichprobe, kein Defekt des Werkzeugs, und mehr als vorhanden ist kann niemand holen. Anhänge und Erzeugnisse sind davon unberührt.

**Gelöschte Chats** erscheinen im Export noch als leere Hülle, ohne Text. Der Skill erkennt und kennzeichnet sie; wiederherstellen kann sie niemand.
