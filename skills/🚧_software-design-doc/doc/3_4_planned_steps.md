## 3.4 Geplante Schritte und Umbauziel

Stand (2026-09-24): Entschieden sind der Begriff des geplanten Schritts, die Syntax des Umbauziels, und — vormals Q-12 — der Inhalt eines geplanten Schritts sowie die Ablageorte einer Planung (der frühere Punkt T2); die Entscheidung steht in Kapitel 1.7.3, die Einzelheiten hier in 3.4.3.

### 3.4.1 Geplante Schritte

> Ein geplanter Schritt ist ein noch offener Schritt der Projektplanung — wo immer er steht: in einer Fahrplandatei, im Abschnitt „Offen" einer README, in einer Notiz. Der Skill setzt keine Fahrplandatei voraus. Er liest geplante Schritte aus Abschnitten mit der Rolle `plan` (Kapitel 1.3.3) und aus den Dateien, die der Skill-Parameter `planned_steps` nennt (Kapitel 3.5). Ein Schritt ist der Text unter einer Überschrift bis zur nächsten Überschrift gleicher oder höherer Ordnung. Erledigte Schritte verlassen die Planung; die Nummern der übrigen werden nicht neu vergeben, neue zählen hoch — ein Rückblick auf „Schritt n" bleibt so eindeutig.

### 3.4.2 Umbauziel

> Ein Schritt, der eine Festlegung oder ein Kapitel umbauen will, sagt das in einer Zeile `target:`. Diese Zeile lesen die Prüfungen R2 und R5 der Härteliste (Kapitel 3.1); ohne sie öffnet Planung nichts.
>
> | Fall | Zeile |
> |---|---|
> | ein Register im Spiel | `target: D-0042, D-0057` |
> | mehrere Register | `target: docs/pipeline/decisions.md:D-0042, :D-0057` — der Qualifier vor dem Doppelpunkt ist der Registerpfad; ein führender Doppelpunkt heißt „gleiches Register wie zuvor" |
> | ein Kapitel als Ziel | `target: chapter docs/3_2_pipeline.md` |
>
> Der Qualifier ist das Register, nicht die Kapiteldatei, weil IDs je Register global sind und Kapiteldateien sich umbenennen. Das Kapitelziel ist das Einzige, was an einem Dateinamen hängt; wird die Datei umbenannt, meldet `check` das zerbrochene Ziel. Mehrere `target:`-Zeilen je Schritt sind erlaubt.
>
> Fehlt in einem bestehenden Fahrplan jedes Umbauziel — der Normalfall bei Einführung —, fragt die Instanz einmal, wenn ein Schritt erkennbar den berührten Bereich betrifft, ob er als Umbau gemeint ist, und trägt das Ziel nach. Der Fahrplan kommt so am Berührungspunkt ins Schema, wie die Doku selbst.

### 3.4.3 Inhalt eines geplanten Schritts und Ablageorte einer Planung

> Ein geplanter Schritt beschreibt das Ziel, den Grund seiner Dringlichkeit, sein Umbauziel und, wo vorhanden, den Verweis auf die Planung. Er beschreibt nicht den Weg — außer der Entwickler fordert das für einen Schritt ausdrücklich ein.

Die frühere Formulierung „in aufgabenangemessener Detaillierung" (Anhang A) war die Wurzel eines Missverständnisses: Gemeint war die Präzision des Ziels, gelesen wurde die Ausbreitung des Weges — deshalb die schärfere Fassung oben.

> Wo eine Planung steht, entscheidet sich bei jeder Planung einzeln nach Länge und Haltbarkeit, nicht einmal je Projekt:
>
> 1. **Bis etwa zehn Sätze** — geschätzt beim Eintragen — steht die Planung im Schritt selbst. Für den kurzen Fall ist ein Verweis teurer als der Inhalt.
> 2. **Trägt die Planung Festlegungen über das System** — Verhalten, Schnittstellen, Struktur, Begründungen, die den Code überdauern —, gehört sie in die Doku, an das zuständige Kapitel; der Schritt verweist darauf. Das ist der Regelfall für alles, was nach der Ausführung noch gelesen werden muss.
> 3. **Beschreibt sie nur den Arbeitsweg** — Befehlsfolgen, Reihenfolgen, Fallstricke, Nachweisproben — und ist nach der Ausführung wertlos, entsteht eine eigene Planungsdatei im Projekt; der Schritt verweist mit Datei und Abschnitt.
>
> Wächst eine Planung beim Ausarbeiten über die zehn Sätze hinaus, bleibt sie nicht im Schritt, sondern wandert an einen der beiden anderen Orte und hinterlässt einen Verweis. Nach der Ausführung wandert, was zur Beurteilung nötig bleibt, in die Doku — Kapitel oder Anhang, nach der Grenze, die der Vorläufer dafür kennt (Anhang A, Abschnitt A.9) —; die Planungsdatei wird gelöscht, und die Zeile in der Statusdatei nennt sie. Es steht höchstens eine unausgeführte Planung je Schritt.
>
> Wird der Kontext knapp, ist die nächste Handlung nicht „den Fahrplan detaillieren", sondern „die Planung an ihrem Ort vertiefen und im Schritt darauf verweisen". Der Review-Anhang behält seine Funktion, verliert aber den Sonderstatus: Die Bearbeitung eines Befundes ist der Anwendungsfall von Ort 2, eine Planung, deren Begründung überdauern muss.
>
> Die Statusdatei trägt ausschließlich abgearbeitete Schritte in der Reihenfolge des Abschlusses; Entscheidungen gehören sofort in das zuständige Kapitel.

Die Kontext-Haushalt-Regel oben ersetzt für dieses Vorhaben die gleichnamige Regel der globalen Anweisungsdatei (Arbeitsanweisungen §1.9), die dort nicht aus dem Vorläufer stammte, sondern eigens für Softwareprojekte galt.

### 3.4.4 Entscheidungsgrundlagen

> **[Q-13] Entscheidungsgrundlage — Kapitel als Umbauziel über den Dateipfad**
> Kontext: `target: chapter docs/3_2_pipeline.md` ist das Einzige im Verfahren, das an einem Dateinamen hängt; Umnummerierung benennt Dateien um, `check` meldet das zerbrochene Ziel.
> Optionen: (a) Dateipfad, Bruch wird gemeldet und über den Plan repariert; (b) Kapitel bekommen eine eigene stabile Kennung, etwa im Rollenmarker `[DS:runtime C-03]`; (c) kein Kapitelziel — nur IDs, ein Umbau nennt die betroffenen Festlegungen einzeln.
> Vorschlag: (a) — selten, billig zu reparieren; (b) führt eine zweite Kennungsart ein.
> Gewicht: mittel · Blockiert: Fahrplanschritt 2
> Antwort:

> **[Q-14] Entscheidungsgrundlage — Eigene Kennungen für geplante Schritte**
> Kontext: `upheld`-Zeilen und Registerzeilen könnten auf den Schritt verweisen, in dem eine Idee verworfen wurde. Dafür bräuchten Schritte eine stabile Kennung über die Nummer hinaus, die je Planungsdatei gilt.
> Optionen: (a) nein — Schrittnummer und Dateiname genügen im Freitext der Zeile; (b) ja — Schritte tragen `S-0007` nach demselben Zählerprinzip.
> Vorschlag: (a).
> Gewicht: klein · Blockiert: Fahrplanschritt 2
> Antwort:
