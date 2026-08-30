# Die Entscheidung des Nutzers über die Kennzeichnung

Du arbeitest über den Nutzer: Jede Debug-Zeile, die entsteht, trägt **er** ein, und er baut sie später wieder aus. Ob dabei markiert wird, entscheidet deshalb er.

## Erst nachsehen, dann fragen

Steht die Antwort schon im Kontext — als Vorgabe des Projekts oder weil der Nutzer es in diesem Chat bereits gesagt hat —, gilt sie. **Dann wird nicht gefragt.**

Sonst legst Du ihm die Wahl einmal vor. Halte Dich dabei kurz: Er soll entscheiden können, nicht die Regeln lernen.

## Was Du ihm zeigst

Ein Satz zum Zweck und ein kurzes Beispiel:

> Ich kann die Debug-Zeilen mit einer Marke versehen. Dann findest Du sie später mit einer einzigen Suche wieder, und stillgelegter Originalcode steht zum Wiederherstellen daneben — ohne dass einer von uns sich erinnern muss.

```python
    # @@~DEBUG: ORIGINAL >>parse-fail<< ~@@ config = parse(raw)
    config = parse(raw, strict=False)  # @@~DEBUG >>parse-fail<< ~@@
```

Mehr nicht. Keine vollständige Markenübersicht, keine Fallunterscheidung — das käme erst, wenn er zustimmt.

## Die drei Ausgänge

- **Er stimmt zu.** Es gilt die Kennzeichnung dieses Skills.
- **Er lehnt ab.** Frag ihn dann, ob er eine einfachere Markierung möchte und wie sie aussehen soll. Was er vorschlägt, gilt — unverändert und ohne Prüfung. Du beurteilst seinen Vorschlag nicht und kommst nicht darauf zurück.
- **Er will gar keine Markierung.** Dann wird nicht markiert.

Die Antwort gilt für den laufenden Chat. Möchte er sie dauerhaft festlegen, gehört sie in die Vorgaben des Projekts; dann stellt sich die Frage künftig nicht mehr.

## Danach

Lies in jedem Fall `rules-handover.de.md` aus dem Ordner dieses Skills und arbeite danach. Dort steht, wie Du die Probe wählst und dem Nutzer übergibst — das gilt unabhängig davon, wie er sich entschieden hat. Die Kennzeichnung selbst wird dort nur nachgeladen, wenn er ihr zugestimmt hat.

Sollte der Nutzer im weiteren Verlauf die Entscheidung rückgängig machen bzw. eine andere Lösung vorgeben, um Debug-Stellen zu markieren, orientierst Du Dich an den Festlegungen des Nutzers und übernimmst seine Vorgaben ohne Rückfragen oder eigene Vorschläge.
