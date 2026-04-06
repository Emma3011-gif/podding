"""
Database models and operations for user profiles, documents, and chat history.
Supports both SQLite (local development) and PostgreSQL (production).
"""

import os
import json
from datetime import datetime
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash

# Detect environment
IS_VERCEL = os.getenv('VERCEL') == '1' or os.getenv('VERCEL_ENV') is not None
DATABASE_URL = os.getenv('DATABASE_URL')

# Import appropriate database library
if DATABASE_URL:
    # Production: Use PostgreSQL with psycopg2
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        DB_TYPE = 'postgres'
    except ImportError:
        raise ImportError("psycopg2-binary is required for PostgreSQL. Install it first.")
else:
    # Local development: Use SQLite
    import sqlite3
    DB_TYPE = 'sqlite'

    # Database configuration for SQLite
    if IS_VERCEL:
        # Use /tmp for serverless (ephemeral but writable)
        DB_DIR = Path('/tmp')
        DATABASE_PATH = DB_DIR / 'app.db'
    else:
        # Local development: use data/ directory
        DB_DIR = Path(__file__).parent / 'data'
        DB_DIR.mkdir(exist_ok=True)
        DATABASE_PATH = DB_DIR / 'app.db'

# Avatar storage
if DATABASE_URL:
    # For PostgreSQL on Vercel/production, use /tmp for avatar files (ephemeral)
    AVATAR_DIR = Path('/tmp') / 'avatars'
else:
    # Local development: use data/avatars
    AVATAR_DIR = DB_DIR / 'avatars'

# Create avatar directory with proper handling for Windows/NTFS
try:
    AVATAR_DIR.mkdir(parents=True, exist_ok=True)
except Exception as e:
    print(f"[WARN] Could not create avatar directory at {AVATAR_DIR}: {e}")
    # Try temp directory as fallback
    AVATAR_DIR = Path(os.getenv('TEMP', '/tmp')) / 'pdf-qa-avatars'
    try:
        AVATAR_DIR.mkdir(parents=True, exist_ok=True)
        print(f"[INFO] Using fallback avatar directory: {AVATAR_DIR}")
    except Exception as e2:
        print(f"[WARN] Could not create fallback avatar directory: {e2}")

def get_db_connection():
    """Create a database connection (SQLite or PostgreSQL)"""
    if DB_TYPE == 'postgres':
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        return conn
    else:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # Return dict-like rows
        return conn

def row_to_dict(row, cursor):
    """Convert a database row to a dictionary, handling both SQLite and PostgreSQL"""
    if row is None:
        return None
    if DB_TYPE == 'postgres':
        # psycopg2 returns tuples by default, need to use description to get column names
        return dict(zip([desc[0] for desc in cursor.description], row))
    else:
        # SQLite with Row factory already behaves like a dict
        return dict(row)

def init_db():
    """Initialize database tables (SQLite or PostgreSQL)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            display_name TEXT,
            avatar_filename TEXT,
            google_id TEXT UNIQUE,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')

    # Documents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            file_type TEXT NOT NULL,
            upload_date TEXT NOT NULL,
            full_text TEXT NOT NULL,
            text_preview TEXT,
            file_size INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')

    # Chat history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id SERIAL PRIMARY KEY,
            doc_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (doc_id) REFERENCES documents (id) ON DELETE CASCADE
        )
    ''')

    # Embeddings table for document chunks (persist across serverless invocations)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS embeddings (
            id SERIAL PRIMARY KEY,
            doc_id TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            chunk_text TEXT NOT NULL,
            embedding TEXT NOT NULL,  -- JSON string of the embedding vector
            FOREIGN KEY (doc_id) REFERENCES documents (id) ON DELETE CASCADE,
            UNIQUE(doc_id, chunk_index)
        )
    ''')

    # Indexes for performance (only create if not exists)
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_doc_id ON chat_messages(doc_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_embeddings_doc_id ON embeddings(doc_id)')
    except Exception as e:
        # Some databases might not support IF NOT EXISTS, ignore errors
        print(f"[DB] Index creation note: {e}")

    conn.commit()
    conn.close()
    if DB_TYPE == 'postgres':
        print("[DB] PostgreSQL database initialized")
    else:
        print(f"[DB] SQLite database initialized at {DATABASE_PATH}")

# ==================== USER OPERATIONS ====================

def create_user(user_id, email, password=None, display_name=None, google_id=None):
    """Create a new user in the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()

    password_hash = generate_password_hash(password) if password else None

    # Use appropriate placeholder for database type
    placeholder = '%s' if DB_TYPE == 'postgres' else '?'
    sql = f'''
        INSERT INTO users (id, email, password_hash, display_name, google_id, created_at, updated_at)
        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
    '''
    cursor.execute(sql, (user_id, email.lower(), password_hash, display_name, google_id, now, now))

    conn.commit()
    conn.close()
    return user_id

def get_user_by_email(email):
    """Get user by email"""
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholder = '%s' if DB_TYPE == 'postgres' else '?'
    cursor.execute(f'SELECT * FROM users WHERE email = {placeholder}', (email.lower(),))
    row = cursor.fetchone()
    conn.close()
    return row_to_dict(row, cursor)

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholder = '%s' if DB_TYPE == 'postgres' else '?'
    cursor.execute(f'SELECT * FROM users WHERE id = {placeholder}', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row_to_dict(row, cursor)

def update_user_name(user_id, display_name):
    """Update user's display name"""
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    placeholder = '%s' if DB_TYPE == 'postgres' else '?'
    sql = f'UPDATE users SET display_name = {placeholder}, updated_at = {placeholder} WHERE id = {placeholder}'
    cursor.execute(sql, (display_name, now, user_id))
    conn.commit()
    conn.close()

def update_user_avatar(user_id, avatar_filename):
    """Update user's avatar filename"""
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    placeholder = '%s' if DB_TYPE == 'postgres' else '?'
    sql = f'UPDATE users SET avatar_filename = {placeholder}, updated_at = {placeholder} WHERE id = {placeholder}'
    cursor.execute(sql, (avatar_filename, now, user_id))
    conn.commit()
    conn.close()

def verify_password(password, password_hash):
    """Verify a password against its hash"""
    return check_password_hash(password_hash, password)

# ==================== DOCUMENT OPERATIONS ====================

def create_document(doc_id, user_id, filename, file_type, full_text, file_size=0):
    """Store a document in the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    text_preview = full_text[:500] if full_text else ''

    placeholder = '%s' if DB_TYPE == 'postgres' else '?'
    sql = f'''
        INSERT INTO documents (id, user_id, filename, file_type, upload_date, full_text, text_preview, file_size)
        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
    '''
    cursor.execute(sql, (doc_id, user_id, filename, file_type, now, full_text, text_preview, file_size))

    conn.commit()
    conn.close()

def get_document(doc_id, user_id=None):
    """Get document by ID. If user_id provided, verify ownership."""
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholder = '%s' if DB_TYPE == 'postgres' else '?'

    if user_id:
        cursor.execute(f'SELECT * FROM documents WHERE id = {placeholder} AND user_id = {placeholder}', (doc_id, user_id))
    else:
        cursor.execute(f'SELECT * FROM documents WHERE id = {placeholder}', (doc_id,))

    row = cursor.fetchone()
    conn.close()
    return row_to_dict(row, cursor)

def get_user_documents(user_id):
    """Get all documents for a user, ordered by upload date descending"""
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholder = '%s' if DB_TYPE == 'postgres' else '?'
    cursor.execute(f'''
        SELECT id, filename, file_type, upload_date, text_preview, file_size
        FROM documents
        WHERE user_id = {placeholder}
        ORDER BY upload_date DESC
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [row_to_dict(row, cursor) for row in rows]

def delete_document(doc_id, user_id):
    """Delete a document (and its chats) by ID, verifying ownership"""
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholder = '%s' if DB_TYPE == 'postgres' else '?'

    # Verify ownership and delete
    cursor.execute(f'DELETE FROM documents WHERE id = {placeholder} AND user_id = {placeholder}', (doc_id, user_id))
    # Chat messages will cascade delete due to FOREIGN KEY constraint

    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

# ==================== CHAT HISTORY OPERATIONS ====================

def save_chat_message(doc_id, role, content):
    """Save a chat message to history"""
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    placeholder = '%s' if DB_TYPE == 'postgres' else '?'
    sql = f'''
        INSERT INTO chat_messages (doc_id, role, content, timestamp)
        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})
    '''
    cursor.execute(sql, (doc_id, role, content, now))
    conn.commit()
    conn.close()

def get_chat_history(doc_id, user_id=None):
    """Get all chat messages for a document, ordered by timestamp"""
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholder = '%s' if DB_TYPE == 'postgres' else '?'

    if user_id:
        cursor.execute(f'''
            SELECT cm.* FROM chat_messages cm
            JOIN documents d ON cm.doc_id = d.id
            WHERE cm.doc_id = {placeholder} AND d.user_id = {placeholder}
            ORDER BY cm.timestamp ASC
        ''', (doc_id, user_id))
    else:
        cursor.execute(f'SELECT * FROM chat_messages WHERE doc_id = {placeholder} ORDER BY timestamp ASC', (doc_id,))

    rows = cursor.fetchall()
    conn.close()
    return [row_to_dict(row, cursor) for row in rows]

def clear_chat_history(doc_id, user_id=None):
    """Clear chat history for a document (optional, if user_id provided verify ownership)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholder = '%s' if DB_TYPE == 'postgres' else '?'

    if user_id:
        cursor.execute(f'''
            DELETE FROM chat_messages
            WHERE doc_id = {placeholder} AND doc_id IN (
                SELECT id FROM documents WHERE user_id = {placeholder}
            )
        ''', (doc_id, user_id))
    else:
        cursor.execute(f'DELETE FROM chat_messages WHERE doc_id = {placeholder}', (doc_id,))

    conn.commit()
    conn.close()

# ==================== EMBEDDING OPERATIONS ====================

def save_embeddings(doc_id, embeddings):
    """Save document chunk embeddings to database

    Args:
        doc_id: Document ID
        embeddings: List of tuples [(chunk_text, embedding_vector), ...]
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholder = '%s' if DB_TYPE == 'postgres' else '?'

    # Delete existing embeddings for this doc (if any)
    cursor.execute(f'DELETE FROM embeddings WHERE doc_id = {placeholder}', (doc_id,))

    # Insert new embeddings
    for idx, (chunk_text, embedding) in enumerate(embeddings):
        # Serialize embedding vector to JSON
        embedding_json = json.dumps(embedding)
        sql = f'INSERT INTO embeddings (doc_id, chunk_index, chunk_text, embedding) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})'
        cursor.execute(sql, (doc_id, idx, chunk_text, embedding_json))

    conn.commit()
    conn.close()

def load_embeddings(doc_id):
    """Load document chunk embeddings from database

    Returns:
        List of tuples [(chunk_text, embedding_vector), ...] or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholder = '%s' if DB_TYPE == 'postgres' else '?'

    cursor.execute(f'''
        SELECT chunk_text, embedding FROM embeddings
        WHERE doc_id = {placeholder}
        ORDER BY chunk_index ASC
    ''', (doc_id,))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return None

    # Deserialize embedding vectors
    embeddings = []
    for row in rows:
        row_dict = row_to_dict(row, cursor) if DB_TYPE == 'postgres' else row
        embedding = json.loads(row_dict['embedding'] if DB_TYPE == 'postgres' else row['embedding'])
        chunk_text = row_dict['chunk_text'] if DB_TYPE == 'postgres' else row['chunk_text']
        embeddings.append((chunk_text, embedding))

    return embeddings

def delete_embeddings(doc_id):
    """Delete embeddings for a document (called when document is deleted)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholder = '%s' if DB_TYPE == 'postgres' else '?'
    cursor.execute(f'DELETE FROM embeddings WHERE doc_id = {placeholder}', (doc_id,))
    conn.commit()
    conn.close()

# ==================== AVATAR OPERATIONS ====================

def get_avatar_path(user_id, filename):
    """Get full path to avatar file (local storage only)"""
    return AVATAR_DIR / f"{user_id}_{filename}"

def save_avatar(user_id, file_bytes, filename):
    """Save avatar file and return the stored filename or blob URL"""
    try:
        import blob_storage
        # Use Vercel Blob storage if available, otherwise fallback to local
        return blob_storage.upload_avatar(user_id, file_bytes, filename)
    except ImportError:
        # Fallback to local storage if blob_storage not available
        import os
        ext = Path(filename).suffix.lower()
        stored_filename = f"avatar{ext}"
        avatar_path = get_avatar_path(user_id, stored_filename)
        avatar_path.parent.mkdir(parents=True, exist_ok=True)
        with open(avatar_path, 'wb') as f:
            f.write(file_bytes)
        return stored_filename

def delete_avatar(user_id):
    """Delete user's current avatar if exists"""
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholder = '%s' if DB_TYPE == 'postgres' else '?'
    cursor.execute(f'SELECT avatar_filename FROM users WHERE id = {placeholder}', (user_id,))
    row = cursor.fetchone()
    conn.close()

    row_dict = row_to_dict(row, cursor) if DB_TYPE == 'postgres' else row
    if row_dict and row_dict.get('avatar_filename'):
        avatar_ref = row_dict['avatar_filename']
        try:
            import blob_storage
            blob_storage.delete_avatar(user_id, avatar_ref)
        except ImportError:
            # Fallback to local deletion
            try:
                avatar_path = get_avatar_path(user_id, avatar_ref)
                if avatar_path.exists():
                    avatar_path.unlink()
            except Exception as e:
                print(f"[WARN] Failed to delete avatar: {e}")

def get_avatar_url(user_id, avatar_filename):
    """Generate URL for avatar (to be served via Flask route)"""
    if not avatar_filename:
        return None
    # Check if it's a blob URL (starts with http)
    if avatar_filename.startswith('http'):
        return f"/user/avatar/{user_id}?blob=true"
    # Local filename - use Flask route
    return f"/user/avatar/{user_id}"

def get_avatar_blob_url(user_id, avatar_filename):
    """Get the actual blob URL for direct access (if stored)"""
    if avatar_filename and avatar_filename.startswith('http'):
        return avatar_filename
    return None

# ==================== UTILITY ====================

def migrate_from_json():
    """Optional: migrate existing JSON data to SQLite (if you had data)"""
    # This could read from data/users.json etc and insert into DB
    # For now, not needed since we're starting fresh
    pass

if __name__ == '__main__':
    init_db()
    print("Database models initialized.")
