# Fahrplan Chats-Export

**Keine offenen Aufgaben.** Das Werkzeug ist fertig, erprobt und produktiv; die Anwenderdokumentation liegt beim Skill, alle Fakten und Prüfpunkte in `implementation_doku.md`. Diese Datei bleibt als Ort für den nächsten Schritt, sobald einer ansteht.

## Erledigt am 22. August 2026 — Aufräumen nach dem Produktivwerden

Beides ohne Änderung an der eigentlichen Implementierung: Der Konverter, der Skill und das Dateiformat sind unangetastet.

**Die Implementierungsdoku ist ausgemistet.** Sie beschreibt jetzt ausschließlich den implementierten Stand. Alles, was nur den Entwicklungsweg erklärte, ist entfernt; die versuchten und nicht tragfähigen Wege stehen zusammengefasst in **1.7 Misslungene Ansätze und Versuche** — beschreibend, nicht als Protokoll ihrer damaligen Umsetzung. Kapitel 3 ist neu durchnummeriert (3.1 Konverter, 3.2 `inspect_export.py`, 3.3 Skill), die Vorgaben 2.5 und 2.9 sind auf den heutigen Stand gebracht, und die Prüfliste in Kapitel 4 führt keine Punkte mehr zu Werkzeugen, die der Entwurf nicht benutzt. Von 704 Zeilen sind 659 geblieben, bei rund 15.000 Zeichen entferntem Entwicklungsdetail.

**Die Reste des entfallenen Lese-Wegs sind aufgelöst.** `chat_crawl_store.py` und `chat_read_store.py` samt ihren Tests sind gelöscht — zusammen 2.758 Zeilen für Wege, die niemand mehr geht. Was davon gebraucht wurde, steckt in `tests/wegegleichheit_referenz.py`: 605 Zeilen, die **allein** dem Zweck dienen, Vorgabe 2.5 zu messen. Der Grund für ihre Existenz steht in ihrem Docstring — ein Maßstab, der Code mit dem Gemessenen teilt, bestätigt jede Formatänderung von selbst.

**Der Prüfumfang ist dabei vollständig erhalten:** `test_wegegleichheit.py` läuft mit denselben 73 Prüfungen wie vorher, nur ohne Subprozess-Aufrufe einer Kommandozeile, die es nicht mehr gibt. Alle vier Testsuiten sind grün, auch unter `-O`.
