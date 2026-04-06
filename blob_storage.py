"""
Vercel Blob Storage integration for persistent avatar storage.
Falls back to local file system when Blob is not configured.
"""

import os
from pathlib import Path

# Import get_avatar_path from models (safe: models only imports blob_storage inside functions)
from models import get_avatar_path

# Global flag for Blob availability
BLOB_AVAILABLE = False
BLOB_ENABLED = False

try:
    from vercel_blob import put, delete as blob_delete, download_file
    BLOB_AVAILABLE = True
    # Enable Blob if running on Vercel (or force with USE_BLOB_STORAGE=1)
    if os.getenv('VERCEL') or os.getenv('USE_BLOB_STORAGE') == '1':
        BLOB_ENABLED = True
        print("[BLOB] Vercel Blob Storage enabled for avatars")
    else:
        print("[BLOB] Vercel Blob Storage available but not enabled (set USE_BLOB_STORAGE=1 or run on Vercel)")
except ImportError:
    print("[BLOB] Vercel Blob SDK not installed - using local file storage")
    BLOB_AVAILABLE = False
    BLOB_ENABLED = False
    # Set to None to avoid NameError later
    put = None
    blob_delete = None
    download_file = None


def upload_avatar(user_id, file_bytes, filename):
    """
    Upload avatar to storage (Blob or local).

    Args:
        user_id: User identifier
        file_bytes: Image file bytes
        filename: Original filename (used for extension)

    Returns:
        Stored filename (for local) or blob URL (for Blob)
    """
    ext = Path(filename).suffix.lower()
    stored_filename = f"avatar{ext}"

    if BLOB_ENABLED:
        # Upload to Vercel Blob
        blob_path = f"avatars/{user_id}_{stored_filename}"
        try:
            # Use BLOB_READ_WRITE_TOKEN if provided, otherwise use default Vercel integration
            token = os.getenv('BLOB_READ_WRITE_TOKEN')
            # Note: The vercel-blob SDK (v0.4.2) always sends 'access: public' header.
            # For this to work, your Blob Store must be configured as PUBLIC in Vercel.
            # If you need PRIVATE storage, you must either:
            #   - Use direct API calls instead of the SDK
            #   - Or wait for SDK support (as of v0.4.2, private is not supported)
            options = {}
            if token:
                options['token'] = token
            blob = put(blob_path, file_bytes, options)
            print(f"[BLOB] Uploaded avatar to: {blob.url}")
            # Return the blob URL as the "filename" - we'll store this in DB
            return blob.url
        except Exception as e:
            print(f"[BLOB] Upload failed: {e}, falling back to local storage")
            # Fallback to local storage
            fallback_to_local(user_id, file_bytes, stored_filename)
            return stored_filename
    else:
        # Local file storage (development)
        fallback_to_local(user_id, file_bytes, stored_filename)
        return stored_filename


def fallback_to_local(user_id, file_bytes, stored_filename):
    """Save avatar to local file system (fallback)"""
    avatar_path = get_avatar_path(user_id, stored_filename)
    avatar_path.parent.mkdir(parents=True, exist_ok=True)
    with open(avatar_path, 'wb') as f:
        f.write(file_bytes)
    print(f"[BLOB] Saved avatar locally: {avatar_path}")


def get_avatar_url(user_id, avatar_filename):
    """
    Get avatar URL for display.

    Args:
        user_id: User identifier
        avatar_filename: Stored filename (local) or blob URL

    Returns:
        URL string (blob URL or Flask route)
    """
    if not avatar_filename:
        return None

    # If it's a blob URL (starts with http), use it directly
    if avatar_filename.startswith('http'):
        # For private blobs, we need to generate a signed URL or proxy through our app
        # For simplicity, if blob URL is already public, return it
        # For private blobs, we should proxy through /user/avatar/<user_id>
        # For now, check if we're using Blob and return our route to handle fetching
        if BLOB_ENABLED or avatar_filename.startswith('https://'):
            # Use our Flask route to serve the avatar from Blob
            return f"/user/avatar/{user_id}?blob=true"
        return avatar_filename

    # Local filename - use Flask route
    return f"/user/avatar/{user_id}"


def delete_avatar(user_id, avatar_filename):
    """
    Delete avatar from storage.

    Args:
        user_id: User identifier
        avatar_filename: Stored filename (local) or blob URL
    """
    if not avatar_filename:
        return

    if BLOB_ENABLED and avatar_filename.startswith('http'):
        # Delete from Vercel Blob
        try:
            blob_delete(avatar_filename)
            print(f"[BLOB] Deleted avatar blob: {avatar_filename}")
        except Exception as e:
            print(f"[BLOB] Failed to delete blob {avatar_filename}: {e}")
    else:
        # Delete local file
        try:
            avatar_path = get_avatar_path(user_id, avatar_filename)
            if avatar_path.exists():
                avatar_path.unlink()
                print(f"[BLOB] Deleted local avatar: {avatar_path}")
        except Exception as e:
            print(f"[WARN] Failed to delete avatar: {e}")


def get_blob_file(user_id, avatar_filename):
    """
    Retrieve blob content for serving via Flask route.

    Args:
        user_id: User identifier
        avatar_filename: Blob URL

    Returns:
        file_bytes or None
    """
    if not BLOB_ENABLED or not avatar_filename.startswith('http'):
        return None

    try:
        # Fetch blob content using download_file
        # The download_file function expects the blob URL
        result = download_file(avatar_filename)
        # download_file returns content as bytes
        return result
    except Exception as e:
        print(f"[BLOB] Failed to fetch blob: {e}")
        return None
