# Chats-Export

Derzeit (08/2026) unterstützt Anthropic den Umzug von einem Projekt / Konto zu einem anderen Projekt / Konto aber auch zwischen Claude.ai – Claude Desktop – Claude Code völlig unzureichend. Insbesondere lassen sich ganze Chats nicht verschieben. In diesem Ordner werden dafür Hilfsmittel erstellt.

# Anwendung

Lade chat_crawl_store.py in einem Chat innerhalb des Projekts hoch, wo die Chats exportiert werden sollen hoch. Das Script wird Claude anwenden, um bisherige Chats des Projekts so vollständig, wie möglich zu exportieren. Die Anweisungen zur Nutzung des Scripts findet Clkaudfe im Docstring des Scripts. Das Script allein kann dabei den Export nicht durchführen. Claude wird das Script als Hilfsmittel nutzen, auf Basis seiner beschränkten Such-Funktion in vergangenen Chats, diese im Wortlaut möglichst umfänglich für den Export aufzubereiten und Dir zum Download anzubieten.
