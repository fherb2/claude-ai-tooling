# system-access — Regeln für das Arbeiten auf einem laufenden System

*Stand: 2026-09-15*

*[English version](https://github.com/fherb2/claude-ai-tooling/blob/master/skills/system-access/README.en.md)*

**Inhaltlich fertig, noch ohne Installationspaket.** Anweisungen vollständig, Frontmatter gesetzt, stiller Trigger vorhanden, deutsche und englische Fassung. Was zur Installation per Paket noch fehlt, steht unter „Stand und Offenes". — Nur für Claude Code.

---

## Überblick

**Der Skill regelt, was zwischen dem Auftrag und dem ersten Befehl auf einem laufenden System geschieht — und was danach den Rückweg offenhält.** Er ist für die Wartung gebaut: einen Server betreuen, Software aktualisieren, eine Fehlkonfiguration suchen, eine Schwachstelle finden. Also für Arbeit, deren Fehler sofort wirksam und für andere sichtbar sind, statt wie in der Softwareentwicklung erst einmal privat und rücknehmbar.

Er beantwortet vier Fragen, und zwar in dieser Reihenfolge: **Welches System** ist überhaupt gemeint — der eigene Rechner, ein Container darauf, ein verbundener oder ein gar nicht verbundener fremder? **Welcher Bereich** darin ist freigegeben, und wo verlaufen seine Grenzen, auch die unsichtbaren aus Einhängungen, Verweisen und Netzwerkzielen? **Was ist über die Wirkung bekannt**, bevor eingegriffen wird — aus lesender Erkundung und aus der Dokumentation der tatsächlich installierten Version, nicht aus gelerntem Wissen? Und **wie kommt man zurück**, wenn die Maßnahme etwas anderes tut als erwartet?

Dazu kommen drei Lagen, die in der Softwareentwicklung nicht vorkommen und deshalb leicht übersehen werden: Änderungen, die den eigenen Zugang kappen können; fremde Menschen, deren Arbeit an einem Dienst hängt; und das Scheitern eines Zugriffs an einem Schutz, das kein Defekt ist und nicht umgangen werden darf.

**Wofür er nicht gilt:** für die gewöhnliche Arbeit im freigegebenen Projektordner. Die Grenze „keine Änderungen außerhalb der Projektwurzel" ist Sache der Arbeitsanweisungen und bleibt dort; dieser Skill setzt erst an, wo die Arbeit den Projektordner verlässt oder in laufende Programme, Dienste und Container eingreift. Er gilt außerdem nur für Claude Code: Auf claude.ai gibt es keinen Zugriff auf den Rechner des Nutzers, und die Regeln hätten dort keinen Gegenstand.

## Installation

1. **Paket herunterladen.** `downloads/system-access_de_local.zip`

2. **Entpacken.** Das Archiv enthält einen Ordner `system-access/` mit allen Dateien. Entpacke ihn nach `~/.claude/skills/` — dann gilt der Skill für alle Projekte — oder nach `.claude/skills/` im Projekt, dann nur dort. Ein vorhandener Ordner gleichen Namens wird ersetzt; es bleibt nichts Altes liegen.

3. **Stillen Trigger übernehmen.** Das musst Du händisch tun. Claude erkennt dann leichter aus dem Kontext heraus, ob der Skill geladen werden soll. Dazu: Aus `CLAUDE-snippet.md` kommt **alles unterhalb der Trennlinie** in die `CLAUDE.md` des gewählten Orts. Der kursive Text darüber bleibt zurück; die Datei selbst bleibt im Skill-Ordner liegen und zeigt an ihrer Datumszeile, von welchem Stand der übernommene Trigger ist.

   Ohne diesen Schritt wirkt der Skill nur beim ausdrücklichen Aufruf mit `/system-access`.

## Details

### Der stille Trigger trägt einen eigenen Regelkern

Sein letzter Absatz ist keine Kurzfassung des Skills, sondern die Regel, die wirkt, **solange der Skill nicht geladen ist**: Ein Auftrag gibt nicht die Mittel frei, eine Umgebung ohne Hindernis hat nichts erlaubt, vor jedem Zugriff einzeln fragen, nichts ändern ohne benennbaren Rückweg. Deshalb ist dieser Trigger mit rund 1200 Zeichen der längste des Repositories, während die übrigen zwischen 540 und 800 liegen.

Der Grund ist der Zeitversatz: Zwischen dem Moment, in dem eine Aufgabe ankommt, und dem Moment, in dem der Skill tatsächlich im Kontext steht, liegt eine Strecke — nach einer Kompaktierung ebenso wie am Anfang einer Sitzung. Auf dieser Strecke ist der Absatz das Einzige, was schützt. **Wer ihn beim Kürzen für eine Dopplung hält und streicht, nimmt dem Skill genau die Wirkung, für die er gebaut wurde.** Die Kopfnotiz der Snippet-Datei sagt das noch einmal an Ort und Stelle.

### Vier Auslöser statt einem

Der Trigger nennt Themen (Server, Rechner, Dienst, Paket, Konfiguration, Netz), eine ankommende Frage, die eigene Handlung und den Regelkern. Der zweite ist der früheste und der wichtigste: Bei einer bloßen Frage nach einem Computer gibt es noch gar keinen Zugriff, den man abwägen könnte — die Falle ist das Losforschen, und zwar auf dem Rechner, der zufällig erreichbar ist. Ein Anker, der an der eigenen Handlung hängt, greift dafür zu spät.

Dieselben Auslöser stehen zusätzlich in der `description`. Das ist Absicht und keine Dopplung: Die `description` ist der von Anthropic vorgesehene Weg und wirkt ohne Zutun des Nutzers; der stille Trigger überlebt dafür eine Kompaktierung, die die Skill-Liste nicht übersteht. Die beiden ergänzen sich, und nach den Messungen des Entwicklers ist der stille Trigger auf den weniger empfindlichen Modellen der wichtigere.

### Regeln, deren Vereinfachung die Funktion zerstört

- **Der Bereich wird benannt, nicht umschrieben.** „Die Konfiguration des Dienstes X und seine Protokolle" ist eine Bereichsangabe, „ich schaue mal, woran es liegt" nicht. Ohne benannte Grenze kann der Nutzer nicht erkennen, wozu er zustimmt.
- **Der Rückweg gehört zur Maßnahme, nicht zur Nachbereitung.** Der Satz „Kannst Du den Rückweg nicht benennen, ist die Maßnahme nicht vorbereitet" gilt ausdrücklich **auch gegen eine bereits erteilte Freigabe**. Eine sorgfältige Freigabe schützt vor dem Übergriff, nicht vor der unerwarteten Wirkung — und je gründlicher beide Seiten abgewogen haben, desto weniger rechnet jemand damit.
- **Beim Scheitern an einem Schutz wird nicht ausgewichen.** Weder auf einen anderen technischen Weg noch auf eine Lockerung. Erlaubt ist genau ein Eingrenzungsschritt bei mehrdeutiger Fehlermeldung, und der darf den geschützten Bereich nicht berühren.
- **Der Zeitpunkt ist Teil der Freigabe.** Die Zustimmung zu einem Neustart ist keine Zustimmung dazu, ihn jetzt auszuführen.

### Herkunft

Der Skill fasst zwei ältere Entwürfe des Repositories zusammen, die dadurch entfallen sind: `safety_rules` (Bereichsgrenzen, „auto"-Rechte sind keine Freigabe, keine implizite Projekteröffnung) und `pc-configuration-maintaining` (lesende Erkundung vor dem Eingriff, Belege statt gelerntem Wissen). Dazu kommen die Posten T29 und T30 aus dem Inventar der bisherigen Arbeitsanweisungen.

**Eine Abweichung von `safety_rules` ist bewusst:** Dort waren Prozesse ausgenommen, die innerhalb des gerade bearbeiteten Projekts laufen. Der Skill kennt diese Ausnahme nicht. Stattdessen hängt die Regel an der Art der Handlung — ein Blick auf einen Prozess löst sie nicht aus, ein Eingriff schon. Grund: Ob ein Prozess „zum Projekt gehört", steht im Moment der Handlung oft nicht fest, und ein projekteigener Dienst kann derselbe sein, an dem auf einem Server die Arbeit anderer hängt.

## Stand und Offenes

**Status.** Der Skill ist inhaltlich vollständig und in beiden Sprachen benutzbar; wer den Ordner von Hand nach `~/.claude/skills/` kopiert und den Trigger überträgt, kann ihn sofort einsetzen.

**Offen.**

- Die Installationspakete unter `downloads/` fehlen noch. Bis dahin trägt Schritt 1 der Installationsanleitung ins Leere; installiert wird von Hand.
- Ein Eintrag in der Übersichtstabelle der Gesamt-README von `skills/` steht aus, samt des Statussymbols, das der Statushinweis oben dann spiegelt.
- Ob der Skill eine Erprobung am lebenden Objekt braucht, bevor er als fertig gilt, ist nicht entschieden. Seine Regeln sind aus Vorfällen und aus zwei Entwürfen abgeleitet, nicht in einer Wartungssitzung gemessen.

**Bewusst offen gelassene Entscheidungen.**

- **Wo das Eingriffsprotokoll geführt wird**, legt der Skill nicht fest — er verlangt nur, dass es geführt und der Ort zu Beginn mit dem Nutzer geklärt wird. Auf einem Server gibt es keine naheliegende Entsprechung zur Git-Historie, und der richtige Ort hängt davon ab, wem das System gehört.
- **Was „der Projektordner" im Trigger genau umfasst**, entscheidet das Zielprojekt. Der Begriff ist bewusst konkret und damit beobachtbar gewählt statt präzise-aber-unbestimmt („der freigegebene Bereich"): Eine Instanz, die den Skill noch nicht geladen hat, weiß nicht, was der Bereich ist, aber sie weiß, wo sie arbeitet.
- **Ein Hook als garantierter Auslöser** ist nicht vorgesehen. Er wäre die einzige Konstruktion, die das Laden sicher erzwingt, kostet aber bei jedem Werkzeugaufruf. Ob sich das lohnt, zeigt erst der Einsatz.
