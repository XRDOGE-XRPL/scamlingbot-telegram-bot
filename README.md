
ScamlingBot - Projektbeschreibung & Verlauf
Dies ist die zentrale Dokumentation für den ScamlingBot, ein multifunktionaler Telegram-Bot. Das Projekt wurde mit dem Ziel entwickelt, eine leistungsstarke, aber einfach zu bedienende Schnittstelle für eine Vielzahl von digitalen Diensten und Werkzeugen direkt in Telegram bereitzustellen.
Kernfunktionen & Anwendungen
Der Bot bietet eine breite Palette an Funktionen, die in folgende Anwendungsbereiche unterteilt sind:
🛒 Marktplatz & Digitaler Handel
 * Verkauf digitaler Güter: Nutzer können eigene digitale Produkte (Bilder, Dokumente, etc.) mit Preis und Beschreibung auf dem Marktplatz einstellen.
 * Kauf von Produkten: Angebote können durchstöbert und sicher über ein internes Währungssystem erworben werden.
 * Integriertes Wallet-System: Jeder Nutzer verfügt über eine SCAMCOIN-Wallet, deren Guthaben für Transaktionen auf dem Marktplatz verwendet wird. Ein- und Auszahlungen werden derzeit simuliert und sind für eine zukünftige Anbindung an reale Kryptowährungen vorbereitet.
💰 Krypto-Finanzinstrumente
 * Echtzeit-Kursabfragen: Abfrage aktueller Preise und prozentualer 24h-Veränderungen für diverse Kryptowährungen wie BTC, ETH und XRP.
 * Wechselkurs-Rechner: Ermittelt Wechselkurse zwischen zwei beliebigen Kryptowährungen über die CoinGecko-API.
 * Persönliches Dashboard:
   * Wallet-Verwaltung: Speichern und Verwalten externer Krypto-Wallet-Adressen mit der Möglichkeit, deren Guthaben über die Blockchair-API abzufragen.
   * Mining-Pool-Verwaltung: Hinterlegen von Adressen für Mining-Pools (ETH, ETC, KAS) zur Abfrage persönlicher Mining-Statistiken (Hashrate, unbezahltes Guthaben etc.).
   * Öffentliche Pool-Daten: Anzeige allgemeiner Statistiken von großen öffentlichen Mining-Pools.
 * XRPL-Analyse: Detaillierte Abfrage von Informationen zu jeder Adresse im XRP-Ledger, inklusive Guthaben, Sequenz und Owner-Count.
🛠️ Allgemeine Werkzeuge & Dienste
 * Globale Wetter-Abfrage: Liefert aktuelle Wetterdaten für jeden beliebigen Ort weltweit.
 * Interaktiver Taschenrechner: Führt grundlegende arithmetische Berechnungen im Chat durch.
 * Automatischer News-Dienst: Überwacht einen RSS-Feed (U.Today) und postet neue Krypto-Nachrichten automatisch und zuverlässig in eine vordefinierte Telegram-Gruppe.
 * Crypto Hodler Spiel: Ein unterhaltsames Simulationsspiel, in dem Nutzer ein Krypto-Portfolio durch zufällige Marktereignisse navigieren.
🔒 Administration & Nutzer-Interaktion
 * Passwortgeschützter Admin-Bereich: Bietet exklusiven Zugriff auf Bot-Statistiken.
 * Broadcast-System: Ermöglicht den Versand von Nachrichten an alle registrierten Nutzer des Bots.
 * Feedback-System: Nutzer können direkt über einen Befehl Feedback oder Fehlermeldungen an den Administrator senden.
Changelog & Update-Verlauf
Hier ist eine Übersicht der wichtigsten Entwicklungsstufen und Updates des Projekts.
Version 13.x - Das Marktplatz-Update
 * Hinzugefügt: Vollständige Marktplatz-Funktionalität zum Kaufen und Verkaufen digitaler Güter.
 * Hinzugefügt: Internes SCAMCOIN-Währungssystem und persönliche Wallets für alle Nutzer.
 * Hinzugefügt: Neue Datenbank-Tabellen (products, transactions) zur Verwaltung von Angeboten und zur Protokollierung von Verkäufen.
 * Hinzugefügt: process_transaction-Funktion mit atomaren Datenbank-Operationen (ACID) für sichere Käufe.
 * Hinzugefügt: Neue Menüs und ConversationHandler zur Steuerung des Kauf- und Einstellprozesses.
 * Hinzugefügt: Simulierte Ein- und Auszahlungsfunktionen als Vorbereitung für echte Krypto-Transaktionen.
 * Geändert: Admin-Statistiken um Produkt- und Transaktionszähler erweitert.
Version 10.x - 12.x - Das Architektur-Refactoring
 * Geändert: Komplette Umstrukturierung des Codes von einer monolithischen main.py in eine modulare Architektur.
 * Hinzugefügt: Separate Module für database.py, services.py, keyboards.py, localization.py und news_service.py.
 * Hinzugefügt: Mehrsprachigkeit (Deutsch & Englisch) durch das localization-Modul.
 * Geändert: Der Bot wird nun aus Sicherheitsgründen unter einem eingeschränkten Benutzer (scamling) statt root betrieben.
 * Verbessert: Fehlerbehandlung und Stabilität durch klare Trennung der Zuständigkeiten.
Version 5.x - 9.x - Funktionserweiterungen
 * Hinzugefügt: Persönlicher Dashboard-Bereich (/dashboard).
 * Hinzugefügt: Funktionen zur Verwaltung von Krypto-Wallets und Mining-Pools.
 * Hinzugefügt: XRPL-Kontoabfrage.
 * Hinzugefügt: Wetter-API-Anbindung.
 * Hinzugefügt: Taschenrechner und Krypto-Simulationsspiel.
 * Hinzugefügt: Admin-Bereich mit Broadcast-Funktion und Feedback-Anzeige.
Version 1.x - 4.x - Grundsteinlegung
 * Hinzugefügt: Basis-Bot-Struktur mit python-telegram-bot.
 * Hinzugefügt: Erste Befehle wie /start und /help.
 * Hinzugefügt: Erste API-Integration zur Abfrage von Krypto-Kursen.
 * Hinzugefügt: Automatischer News-Job, der in eine Gruppe postet.
Technische Architektur
Das Projekt basiert auf Python 3 und nutzt eine Reihe von spezialisierten Bibliotheken:
 * Telegram-Anbindung: python-telegram-bot
 * Datenpersistenz: SQLite3
 * Externe API-Kommunikation: httpx
 * RSS-Feed-Verarbeitung: feedparser
Alle sensiblen Daten wie API-Schlüssel und Token werden extern in einer environment_vars.conf-Datei verwaltet und sind nicht Teil des Repositorys.
(Ende des zu kopierenden Textes)
