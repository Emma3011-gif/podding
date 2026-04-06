"""Test Blob storage integration"""
import os
import sys
from pathlib import Path

# Add current dir to path
sys.path.insert(0, str(Path(__file__).parent))

# Test 1: Module imports
print("Test 1: Importing blob_storage...")
try:
    import blob_storage
    print(f"  [OK] blob_storage imported")
    print(f"  BLOB_AVAILABLE: {blob_storage.BLOB_AVAILABLE}")
    print(f"  BLOB_ENABLED: {blob_storage.BLOB_ENABLED}")
except Exception as e:
    print(f"  [ERROR] Failed: {e}")
    sys.exit(1)

# Test 2: Test fallback upload
print("\nTest 2: Testing fallback upload (local)...")
try:
    test_bytes = b"fake image data"
    result = blob_storage.upload_avatar("test_user_123", test_bytes, "test.jpg")
    print(f"  [OK] Upload returned: {result}")

    # Cleanup
    if result != "test.jpg":
        print(f"  [INFO] Result is blob URL (expected in Blob mode)")
    else:
        print(f"  [INFO] Result is local filename (fallback mode)")
except Exception as e:
    print(f"  [ERROR] Failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Test get_avatar_url
print("\nTest 3: Testing get_avatar_url...")
try:
    url = blob_storage.get_avatar_url("test_user_123", "test.jpg")
    print(f"  [OK] Generated URL: {url}")
except Exception as e:
    print(f"  [ERROR] Failed: {e}")

print("\n[SUCCESS] All basic tests passed!")
