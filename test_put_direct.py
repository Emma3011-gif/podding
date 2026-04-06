"""Direct test of vercel-blob put with environment token"""
import os

# Set the environment variable
os.environ['BLOB_READ_WRITE_TOKEN'] = 'vercel_blob_rw_hGPlra2V0I98FmvU_FG5gKM97Z81vHJztVWA7ssUtxASMbL'

from vercel_blob import put

# Test without passing token in options (let SDK read from env)
try:
    result = put('test_avatar.jpg', b'test image data', {'access': 'private'}, verbose=True)
    print('SUCCESS:', result)
except Exception as e:
    print('ERROR:', e)
    import traceback
    traceback.print_exc()
