import sqlite3
import datetime
import logging

logger = logging.getLogger(__name__)

DB_NAME = 'scamlingbot.db'
INITIAL_INTERNAL_BALANCE = 1000.0 # Startguthaben für neue Nutzer (simulierter SCAMCOIN)
BOT_OWNER_ID = 5096684838 # Deine ADMIN_USER_ID, um Gebühren gutzuschreiben

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Tabelle für Benutzer (existiert bereits, wird aber erweitert)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            language TEXT DEFAULT 'en',
            registered_at TEXT DEFAULT CURRENT_TIMESTAMP,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            internal_balance REAL DEFAULT 0.0 -- NEU: Für internes Währungssystem
        )
    ''')

    # Tabelle für Feedback (existiert bereits)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            feedback_text TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabelle für Wallets (existiert bereits)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wallets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            currency TEXT NOT NULL,
            address TEXT NOT NULL,
            UNIQUE(user_id, currency, address)
        )
    ''')

    # Tabelle für Pools (existiert bereits)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            pool_type TEXT NOT NULL,
            pool_address TEXT NOT NULL,
            UNIQUE(user_id, pool_type, pool_address)
        )
    ''')

    # Tabelle für News (existiert bereits)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            link TEXT PRIMARY KEY,
            title TEXT,
            published TEXT,
            sent_to_telegram INTEGER DEFAULT 0
        )
    ''')

    # NEU: Tabelle für Marktplatz-Produkte
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            currency TEXT NOT NULL, -- Z.B. 'SCAMCOIN' für internes System
            category TEXT DEFAULT 'General', -- NEU: Produktkategorie
            file_id TEXT, -- Telegram file_id des hochgeladenen Gutes
            status TEXT DEFAULT 'active', -- 'active', 'sold', 'deleted'
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (seller_id) REFERENCES users(id)
        )
    ''')

    # NEU: Tabelle für Marktplatz-Transaktionen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            buyer_id INTEGER NOT NULL,
            seller_id INTEGER NOT NULL,
            amount REAL NOT NULL, -- Preis des Produkts (ohne Gebühr)
            fee_amount REAL NOT NULL, -- Gebühr für den Bot
            total_paid REAL NOT NULL, -- Gesamtbetrag, den der Käufer zahlt
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'completed', -- 'completed', 'failed', 'refunded'
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (buyer_id) REFERENCES users(id),
            FOREIGN KEY (seller_id) REFERENCES users(id)
        )
    ''')

    # Füge eine interne Bot-Owner-Wallet hinzu, falls nicht vorhanden, um Gebühren zu sammeln
    # Dies ist eine spezielle Nutzer-ID, die nur für Gebühren existiert
    cursor.execute("INSERT OR IGNORE INTO users (id, username, internal_balance) VALUES (?, ?, ?)", 
                   (BOT_OWNER_ID, "ScamlingBotOwner", 0.0))

    conn.commit()
    conn.close()

def add_user_to_db(user_id: int, username: str = None, first_name: str = None, last_name: str = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (id, username, first_name, last_name, internal_balance)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, username, first_name, last_name, INITIAL_INTERNAL_BALANCE)) # Gib neuem Nutzer Startguthaben
    conn.commit()
    conn.close()

def set_user_language(user_id: int, lang: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET language = ? WHERE id = ?', (lang, user_id))
    conn.commit()
    conn.close()

def get_user_language_from_db(user_id: int) -> str:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT language FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 'en' # Default to English if not found

def add_feedback(user_id: int, username: str, feedback_text: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO feedback (user_id, username, feedback_text)
        VALUES (?, ?, ?)
    ''', (user_id, username, feedback_text))
    conn.commit()
    conn.close()

def get_feedback():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT username, feedback_text, timestamp FROM feedback ORDER BY timestamp DESC LIMIT 10')
    feedbacks = cursor.fetchall()
    conn.close()
    return feedbacks

def get_user_stats():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(DISTINCT id) FROM users')
    total_users = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM feedback')
    users_with_feedback = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM products') # NEU: Anzahl der Produkte
    total_products = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM transactions WHERE status = "completed"') # NEU: Anzahl der Transaktionen
    total_transactions = cursor.fetchone()[0]

    conn.close()
    return {
        'total_users': total_users,
        'users_with_feedback': users_with_feedback,
        'total_products': total_products,
        'total_transactions': total_transactions
    }

def get_all_user_ids():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users')
    user_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return user_ids

def add_user_wallet(user_id: int, currency: str, address: str) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO wallets (user_id, currency, address)
            VALUES (?, ?, ?)
        ''', (user_id, currency, address))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        logger.warning(f"Wallet for user {user_id} with currency {currency} and address {address} already exists.")
        return False
    finally:
        conn.close()

def get_user_wallets(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, currency, address FROM wallets WHERE user_id = ?', (user_id,))
    wallets = cursor.fetchall()
    conn.close()
    return wallets

def remove_user_wallet(wallet_id: int, user_id: int) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM wallets WHERE id = ? AND user_id = ?', (wallet_id, user_id))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

def add_user_pool(user_id: int, pool_type: str, pool_address: str) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO pools (user_id, pool_type, pool_address)
            VALUES (?, ?, ?)
        ''', (user_id, pool_type, pool_address))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        logger.warning(f"Pool for user {user_id} with type {pool_type} and address {pool_address} already exists.")
        return False
    finally:
        conn.close()

def get_user_pools(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, pool_type, pool_address FROM pools WHERE user_id = ?', (user_id,))
    pools = cursor.fetchall()
    conn.close()
    return pools

def remove_user_pool(pool_id: int, user_id: int) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM pools WHERE id = ? AND user_id = ?', (pool_id, user_id))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

def mark_news_item_as_sent(link: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE news SET sent_to_telegram = 1 WHERE link = ?', (link,))
    conn.commit()
    conn.close()

def check_if_news_item_sent(link: str) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT sent_to_telegram FROM news WHERE link = ?', (link,))
    result = cursor.fetchone()
    conn.close()
    return result[0] == 1 if result else False

# NEU: Marktplatz-spezifische Datenbankfunktionen

def add_product(seller_id: int, name: str, description: str, price: float, currency: str, file_id: str, category: str = 'General') -> int | None:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO products (seller_id, name, description, price, currency, category, file_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (seller_id, name, description, price, currency, category, file_id))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Error adding product: {e}")
        return None
    finally:
        conn.close()

def get_all_active_products(category: str = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if category:
        cursor.execute('SELECT id, seller_id, name, description, price, currency, file_id, status FROM products WHERE status = "active" AND category = ? ORDER BY created_at DESC', (category,))
    else:
        cursor.execute('SELECT id, seller_id, name, description, price, currency, file_id, status FROM products WHERE status = "active" ORDER BY created_at DESC')
    products = cursor.fetchall()
    conn.close()
    return products

def get_product_by_id(product_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, seller_id, name, description, price, currency, file_id, status FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    conn.close()
    return product

def get_user_products(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, seller_id, name, description, price, currency, file_id, status FROM products WHERE seller_id = ? ORDER BY created_at DESC', (user_id,))
    products = cursor.fetchall()
    conn.close()
    return products

# NEU: Funktionen für das interne Währungssystem
def get_user_internal_balance(user_id: int) -> float:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT internal_balance FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    # Wenn der Nutzer noch nicht in der DB ist, oder internal_balance NULL ist, initialisiere mit 0.0 oder DEFAULT
    if result is None:
        add_user_to_db(user_id) # Stelle sicher, dass der User existiert und balance initialisiert ist
        return INITIAL_INTERNAL_BALANCE
    return result[0] if result[0] is not None else 0.0

def update_user_internal_balance(user_id: int, amount: float) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        # Füge den Betrag hinzu (kann auch negativ sein für Abzug)
        cursor.execute('UPDATE users SET internal_balance = internal_balance + ? WHERE id = ?', (amount, user_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f"Error updating internal balance for user {user_id}: {e}")
        return False
    finally:
        conn.close()

def process_transaction(product_id: int, buyer_id: int, seller_id: int, price: float, fee_percentage: float) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        # Start transaction (ACID properties)
        cursor.execute("BEGIN TRANSACTION")

        # 1. Käufer belasten
        total_paid = price * (1 + fee_percentage)
        
        # Prüfe zuerst, ob der Käufer genug Guthaben hat
        cursor.execute('SELECT internal_balance FROM users WHERE id = ?', (buyer_id,))
        buyer_current_balance = cursor.fetchone()
        if buyer_current_balance is None or buyer_current_balance[0] < total_paid:
            raise ValueError("Insufficient funds for buyer or buyer not found.")

        cursor.execute('UPDATE users SET internal_balance = internal_balance - ? WHERE id = ?',
                       (total_paid, buyer_id))
        

        # 2. Verkäufer gutschreiben (abzüglich Gebühr)
        seller_receives = price * (1 - fee_percentage)
        cursor.execute('UPDATE users SET internal_balance = internal_balance + ? WHERE id = ?',
                       (seller_receives, seller_id))

        # 3. Bot-Owner Gebühr gutschreiben
        fee_amount = price * fee_percentage
        cursor.execute('UPDATE users SET internal_balance = internal_balance + ? WHERE id = ?',
                       (fee_amount, BOT_OWNER_ID)) # Deine ADMIN_USER_ID

        # 4. Produkt als verkauft markieren
        cursor.execute('UPDATE products SET status = "sold" WHERE id = ? AND status = "active"', (product_id,))
        if cursor.rowcount == 0:
            raise ValueError("Product not found or already sold.") # Product might have been sold concurrently

        # 5. Transaktion loggen
        cursor.execute('''
            INSERT INTO transactions (product_id, buyer_id, seller_id, amount, fee_amount, total_paid)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (product_id, buyer_id, seller_id, price, fee_amount, total_paid))

        conn.commit()
        return True
    except ValueError as ve:
        logger.warning(f"Transaction failed (ValueError): {ve}")
        conn.rollback()
        return False
    except sqlite3.Error as e:
        logger.error(f"Database error during transaction: {e}")
        conn.rollback() # Rollback in case of any other DB error
        return False
    finally:
        conn.close()

