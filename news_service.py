import os
import asyncio
import logging
import datetime
import httpx
import feedparser
from typing import Final

# Import der Datenbankfunktionen, die vom News-Service benötigt werden
from database import mark_news_item_as_sent, check_if_news_item_sent

# Konfiguration des Loggers für dieses Modul
logger = logging.getLogger(__name__)

# =================================================================================
# NEWS FEED KONFIGURATION & AUTOMATISIERTE FUNKTIONEN
# =================================================================================

# HINWEIS: NEWS_FEED_URL ist hier als https://u.today/rss belassen, da es bei dir funktioniert.
# Falls es zu Problemen kommt, solltest du hier auf eine stabile RSS-Feed-Quelle umstellen (z.B. CoinDesk: "https://www.coindesk.com/feed/")
NEWS_FEED_URL: Final[str] = "https://u.today/rss"
NEWS_CHECK_INTERVAL_SECONDS: Final[int] = 60 * 30  # Alle 30 Minuten
NEWS_MAX_TO_POST_PER_CHECK: Final[int] = 3

# Die GROUP_CHAT_ID wird direkt aus den Umgebungsvariablen geladen,
# um news_service.py autark zu machen.
GROUP_CHAT_ID: Final[int] = int(os.environ.get("GROUP_CHAT_ID", -1000000000000)) # Fallback für den Fall, dass es nicht gesetzt ist

# Dateiname für den letzten News-Check-Zeitpunkt (bleibt lokal für dieses Modul)
LAST_NEWS_CHECK_TIME_FILE: Final[str] = 'last_news_check.txt' # Hier am besten einen absoluten Pfad oder einen Pfad relativ zum bot-Ordner verwenden

def get_last_news_check_time() -> datetime.datetime:
    """Liest den Zeitpunkt des letzten News-Checks aus einer Datei."""
    # Pfad relativ zum Bot-Ordner
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), LAST_NEWS_CHECK_TIME_FILE)
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                return datetime.datetime.fromisoformat(f.read().strip())
            except ValueError:
                logger.warning(f"Ungültiges Datumsformat in {file_path}. Setze auf Minimum.")
                return datetime.datetime.min
    logger.info(f"Keine letzte News-Check-Zeit gefunden in {file_path}. Setze auf Minimum.")
    return datetime.datetime.min

def set_last_news_check_time(dt: datetime.datetime):
    """Speichert den Zeitpunkt des letzten News-Checks in einer Datei."""
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), LAST_NEWS_CHECK_TIME_FILE)
    with open(file_path, "w") as f:
        f.write(dt.isoformat())

async def fetch_and_parse_news(url: str) -> list:
    """Holt und parst RSS-Nachrichten."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=15.0)
            response.raise_for_status()
            feed = feedparser.parse(response.text)
            if feed.bozo:
                logger.error(f"Fehler beim Parsen des RSS-Feeds '{url}': {feed.bozo_exception}")
                return []
            return feed.entries
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP-Fehler beim Abrufen des RSS-Feeds '{url}': {e.response.status_code} - {e.response.text}")
        return []
    except httpx.RequestError as e:
        logger.error(f"Netzwerkfehler beim Abrufen des RSS-Feeds '{url}': {e}")
        return []
    except Exception as e:
        logger.error(f"Unerwarteter Fehler beim Abrufen/Parsen des RSS-Feeds '{url}': {e}")
        return []

async def fetch_xrdoge_price() -> float:
    """Fetch the current XRdoge price from CoinGecko API."""
    url = "https://api.coingecko.com/api/v3/simple/price?ids=xrdoge&vs_currencies=usd"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            price = data.get("xrdoge", {}).get("usd")
            if price is None:
                logger.error("XRdoge price not found in API response.")
                return 0.0
            return price
    except Exception as e:
        logger.error(f"Error fetching XRdoge price: {e}")
        return 0.0

async def check_and_post_news(context): # ContextTypes.DEFAULT_TYPE ist hier nicht nötig
    """Überprüft auf neue Nachrichten und postet sie in die Gruppe."""
    logger.info("Job 'check_and_post_news' gestartet.")
    last_check_time = get_last_news_check_time()
    current_time = datetime.datetime.now()

    entries = await fetch_and_parse_news(NEWS_FEED_URL)
    
    # Sortiere Artikel, um die ältesten zuerst zu verarbeiten (sofern die RSS-Feed-Reihenfolge absteigend ist)
    entries.sort(key=lambda entry: datetime.datetime(*entry.published_parsed[:6]) if 'published_parsed' in entry and entry.published_parsed else datetime.datetime.min)
    
    new_articles_to_post = []

    for entry in entries:
        try:
            # Versuche, das Veröffentlichungsdatum zu parsen
            news_pub_date = None
            if 'published_parsed' in entry and entry.published_parsed:
                news_pub_date = datetime.datetime(*entry.published_parsed[:6])
            elif 'updated_parsed' in entry and entry.updated_parsed:
                news_pub_date = datetime.datetime(*entry.updated_parsed[:6])

            # Überspringe Artikel ohne gültiges Datum oder Artikel, die älter als der letzte Check sind
            if not news_pub_date or news_pub_date <= last_check_time + datetime.timedelta(seconds=5): # 5 Sekunden Toleranz
                continue

            item_id = entry.id if hasattr(entry, 'id') else entry.link
            if check_if_news_item_sent(item_id): # Prüfe, ob Artikel bereits in DB als gesendet markiert ist
                continue
            
            new_articles_to_post.append(entry)

        except Exception as e:
            logger.error(f"Fehler beim Vorsortieren eines News-Eintrags ({entry.get('title', 'N/A')}): {e}")

    if not new_articles_to_post:
        logger.info("Keine neuen News-Artikel gefunden, die gepostet werden müssen.")
    else:
        logger.info(f"Finde {len(new_articles_to_post)} neue Artikel. Poste bis zu {NEWS_MAX_TO_POST_PER_CHECK}.")
        for entry in new_articles_to_post[:NEWS_MAX_TO_POST_PER_CHECK]:
            try:
                item_id = entry.id if hasattr(entry, 'id') else entry.link
                title = getattr(entry, 'title', "Kein Titel verfügbar").strip()
                link = getattr(entry, 'link', "#").strip()
                
                message = f"📰 **Neue News von U.Today**\n\n**{title}**\n\n➡️ [Artikel lesen]({link})"
                
                await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=message, parse_mode="Markdown")
                mark_news_item_as_sent(item_id) # Artikel in DB als gesendet markieren
                logger.info(f"News gepostet: {title}")
                await asyncio.sleep(1) # Kurze Pause, um Telegram API Limits nicht zu reißen
            except Exception as e:
                logger.error(f"Fehler beim Posten eines News-Eintrags ({entry.get('title', 'N/A')}): {e}", exc_info=True)

    # Post XRdoge price
    price = await fetch_xrdoge_price()
    if price > 0:
        price_message = f"🚀 Aktueller XRdoge Preis: ${price:.6f} USD"
        try:
            await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=price_message)
            logger.info("XRdoge Preis gepostet.")
        except Exception as e:
            logger.error(f"Fehler beim Posten des XRdoge Preises: {e}")

    # Aktualisiere den Zeitpunkt des letzten Checks nur, wenn der aktuelle Check erfolgreich war.
    # Wichtig: Wir speichern den Zeitpunkt des Checks, nicht des letzten Artikels, um fehlgeschlagene Abrufe zu handhaben.
    set_last_news_check_time(current_time)
    logger.info(f"News-Check abgeschlossen. Letzter Check-Zeitpunkt aktualisiert auf: {current_time}.")
