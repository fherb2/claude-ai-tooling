# in-depth-online-literature-research — Recherche, die nicht zu früh aufgibt

*Stand: 2026-08-30*

**✅☑ Fertig und nutzbar.** Anweisungen vollständig, Frontmatter gesetzt, deutsche und englische Fassung vorhanden. Kein stiller Trigger nötig (Begründung unter „Details"). — Keine inhaltlichen Unterschiede zwischen der Version für Claude.ai / Claude Desktop (Chat + Cowork) sowie Claude Code.

**Macht aus einer Websuche ein Verfahren: Claude wechselt systematisch Suchbegriffe, Kanäle und Suchebenen, prüft jede Behauptung an der Primärquelle und meldet statt „nichts gefunden" die noch offenen Suchwege.** Der Anlass ist eine wiederkehrende Erfahrung: Die allgemeine Websuche findet Massenseiten zuverlässig, aber gerade Fachartikel, Vereinsschriften und regionale Quellen verschwinden hinter dem, was oft verlinkt ist — und die von Suchmaschinen mitgelieferten Zusammenfassungen erfinden dabei Details, die auf keiner der verlinkten Seiten stehen.

Dagegen setzt der Skill drei Dinge. Erstens die **Verifikationspflicht**: Was nur in einer Suchzusammenfassung steht, gilt als unbestätigt, bis die tragende Seite abgerufen und die Aussage dort gesehen wurde; jeder Fund wird als *belegt*, *unbestätigt* oder *eigenes Modellwissen* gekennzeichnet. Zweitens **sechs Suchoperatoren** als Pflichtrepertoire — umformulieren (auch in andere Sprachen), auf eine ergiebige Website eingrenzen, die Ebene wechseln (nicht das Dokument suchen, sondern das Register, das es listet), Entitäten wie Autoren und Zeitschriften verfolgen, den Kanal wechseln, verifizieren. Drittens den **Frontier-Bericht**: Bleibt die Suche erfolglos, ist „nichts gefunden" als Antwort unzulässig; stattdessen listet Claude, was versucht wurde und welche Suchwege noch offen sind — die Entscheidung über den Abbruch liegt damit beim Nutzer, nicht bei Claudes Ermüdung.

Dazu kommen drei Bequemlichkeiten: Vor größeren Recherchen wird die **Suchtiefe** verabredet (Schnellauskunft, gründlich, erschöpfend), weil eine erschöpfende Suche spürbar Zeit und Kontext kostet. Eine optionale **Quellenkarte** im Projekt sammelt Nischenquellen, die sich bewährt haben. Und das **Ergebnis** wird zuerst im Chat vorgelegt; ob und wo es gespeichert wird, entscheidet der Nutzer.

Der Skill gilt für **jede Art von Recherche** — Literatur, Fakten, Dokumente, Belege —, nicht nur für Software-Themen. **Nicht** gemeint ist er als Beschaffer für Unerreichbares: Was hinter einer Paywall liegt, offline ist oder nie erfasst wurde, findet auch dieses Verfahren nicht; es benennt solche Fälle nur sauber, statt sie zu überspielen. Ebenso wenig regelt er, ob und wo Rechercheergebnisse dauerhaft abgelegt werden — das entscheidet der Nutzer von Fall zu Fall.

## Installation

### Claude Code

1. **Paket herunterladen.** `downloads/in-depth-online-literature-research_de_local.zip`

2. **Entpacken.** Das Archiv enthält einen Ordner `in-depth-online-literature-research/` mit allen Dateien. Entpacke ihn nach `~/.claude/skills/` — dann gilt der Skill für alle Projekte — oder nach `.claude/skills/` im Projekt, dann nur dort. Ein vorhandener Ordner gleichen Namens wird ersetzt; es bleibt nichts Altes liegen.

### claude.ai und Claude Desktop (Chat + Cowork)

1. **Paket herunterladen.** `downloads/in-depth-online-literature-research_de_web.zip`

2. **Hochladen.** Im dafür vorgesehenen Verwaltungsfeld für Skills der Anwendung das Archiv hochladen. Der Skill gilt danach für Dein Konto — nicht für Deine Organisation, und nicht gleichzeitig in Claude Code.

Ein stiller Trigger entfällt hier: Der Skill löst über seine `description` aus oder wird mit `/in-depth-online-literature-research` aufgerufen; die Begründung steht unter „Details“. Beide Pakete tragen denselben Inhalt — getrennt sind sie allein, damit der Name sagt, wohin das Archiv gehört. Die Quellenkarte entfällt dort, wo kein Dateizugriff besteht.

## Details

**Die Verifikationspflicht ist der Kern, nicht ein Zusatz.** Sie gilt auf jeder Tiefenstufe, auch bei der Schnellauskunft. Wer sie beim Anpassen des Skills abschwächt, bekommt genau das zurück, wogegen der Skill gebaut wurde: überzeugend klingende Zahlen und Zitate, die in keiner Quelle stehen.

**Der Selbsttest vor der Abgabe.** Unmittelbar vor der Antwort geht Claude jeden als *belegt* markierten Fund durch und prüft, ob die tragende Quelle in diesem Lauf tatsächlich abgerufen wurde; sonst wird nachgeholt oder auf *unbestätigt* herabgestuft. Das ist kein Zierrat: Bei einer Sammelrecherche mit über zwanzig Funden ließ sich messen, wie die Kennzeichnungsdisziplin nachlässt — mehrere Einträge trugen „belegt", obwohl ihre Quelle nie abgerufen worden war. Bei Einzelfragen greift die Regel selten, bei Listen fast immer.

**Warum es keine feste Zahl von Suchversuchen gibt.** Niemand weiß im Voraus, wie viele Anläufe nötig sind. Deshalb ist das Abbruchkriterium kein Zähler, sondern ein Zustand: Die Suche endet, wenn gefunden wurde, wenn die Frontier leer ist oder wenn der Nutzer abbricht. Die Pflicht, die Liste der offenen Suchwege überhaupt hinzuschreiben, erzwingt nebenbei, dass die Strategien durchdacht werden — die Rechenschaftsform erzeugt das Suchverhalten. Wird sie zu „gib Dir Mühe" vereinfacht, bleibt nichts davon übrig.

**Der Ebenenwechsel ist der ergiebigste Operator** und zugleich der, der ohne ausdrückliche Anweisung nicht stattfindet: nicht den Artikel suchen, sondern das Register der Zeitschrift, die Schriftenreihe der Fachgesellschaft, den Bibliothekskatalog. In der Erprobung war das der Zug, der eine Quelle fand, die über die allgemeine Suche selbst mit exaktem Titel nicht auffindbar war.

**Die Quellenkarte gehört ins Projekt, nicht in den Skill-Ordner.** Eine global wachsende Karte trüge fachfremde Quellen in jede neue Recherche und verwässerte sie; nach einer Installation gäbe es zudem zwei Fassungen, die auseinanderdriften. Durch die Projektbindung ist sie automatisch themenrein. Der Preis ist bewusst in Kauf genommen: kein automatischer Lerntransfer zwischen Projekten.

**Warum kein stiller Trigger.** Der Auslöser steht in aller Regel in der Anfrage selbst („recherchiere", „finde eine Quelle", „belege"), und in der Erprobung feuerte der Skill auf Sonnet — dem unempfindlichsten Zielmodell — ohne jeden Zusatz in der `CLAUDE.md`. Eine Lücke bleibt: Eine Frage, die zunächst harmlos klingt und sich erst mitten in der Bearbeitung als schwierig erweist, erwischt der Trigger möglicherweise nicht, weil die Skill-Auswahl am Anfang eines Turns stattfindet. Wem das im Alltag auffällt, der ergänzt einen `CLAUDE.md`-Absatz, der an die erste Websuche als Handlung bindet.

**Was die Umgebung nicht kann.** Das Abrufwerkzeug rüstet `http://`-Adressen zwingend auf `https://` auf. Reine HTTP-Altseiten — bei Vereins- und Privatseiten keine Seltenheit — sind damit unerreichbar. Der Skill verliert solche Funde nicht, stuft sie aber korrekt auf *unbestätigt* herab und benennt den Grund; ein Blick mit dem eigenen Browser klärt sie dann in Sekunden.

## Stand und Offenes

**Status:** Fertig und einsatzbereit. Die deutsche Fassung ist am 23. August 2026 entstanden und in zwei Inhaltstests erprobt worden — einem Auffinde-Härtefall (Fachartikel, den die allgemeine Suche nicht liefert) und einer offenen Sammelrecherche in fremdem Fachgebiet und fremder Sprache; beide bestanden, aus dem zweiten stammt der Selbsttest gegen nachlassende Kennzeichnungsdisziplin. Die englische Fassung ist am 24. August 2026 als Übersetzung der deutschen entstanden.

**Offen:** Zwei Erprobungen stehen noch aus — die Nachmessung des Selbsttests und der claude.ai-Zweig der Ergebnisübergabe. Die Schritte dazu stehen im [Fahrplan](../../work-plan.md). Beide betreffen die Absicherung, nicht die Benutzbarkeit: Der Skill ist fertig und einsatzbereit.

**Bewusst offen gelassen:** Ob eine Quellenkarte geführt wird, wo sie im Projekt liegt und ob ein Projekt mehrere führt, entscheidet der Nutzer im Zielprojekt — der Skill schreibt weder Ablageort noch Zuschnitt vor. Eine Aufspaltung in mehrere Karten lohnt erst, wenn ein Projekt nachweislich zwei fachfremde Recherchestränge beherbergt.
