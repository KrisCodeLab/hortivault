# HortiVault
Smart greenhouse monitoring and automation

Ziel dieses Projekts ist die kontinuierliche Erfassung, Verarbeitung und Analyse von Umweltdaten innerhalb eines Gewächshauses. 

Verschiedene Sensoren erfassen relevante Messgrößen wie Temperatur, Luftfeuchtigkeit, Bodenfeuchte, Lichtintensität und Wasserstand. Diese Daten werden durch einen Microcontroller (ESP32) aufgenommen und an ein zentrales Backend-System übermittelt. 

Im Backend erfolgt die Speicherung der Rohdaten in einer SQL-Datenbank sowie deren Weiterverarbeitung. Auf Basis definierter Grenzwerte und Analysen werden Zustände und Ereignisse (z. B. „Boden zu trocken“ oder „Wassertank leer“) erkannt. 

Zusätzlich werden auf Grundlage historischer Daten Prognosen und weiterführende Analysen durchgeführt. Die aufbereiteten Daten sowie berechneten Ergebnisse werden über ein Webfrontend visualisiert und können remote abgerufen werden. 

Das System soll modular aufgebaut sein und perspektivisch um Funktionen wie Bildverarbeitung sowie automatisierte Steuerungsprozesse erweitert werden. 