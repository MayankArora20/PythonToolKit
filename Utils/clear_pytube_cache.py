import os
import shutil

# Define the path to the pytube cache directory
cache_dir = os.path.join(os.path.expanduser('~'), '.pytube')

# Check if the cache directory exists and delete it if it does
if os.path.exists(cache_dir):
    shutil.rmtree(cache_dir)
    print("pytube cache cleared.")
else:
    print("Cache directory not found.")
