from pytube import YouTube
from pytube import Playlist
import time
import os
import re

playlist = Playlist("https://www.youtube.com/playlist?list=PLXCoHsJ9oLef1c83KIbl9_h7tYyodL15J")

print("Playlist Name: "+playlist.title)

#print urls
playlist.video_urls
for url in playlist:
    print(url)

#prints address of each YouTube object in the playlist
for vid in playlist.videos:
    print(vid)

# Sanitize playlist title for folder name
safe_title = re.sub(r'[<>:"/\\|?*]', '_', playlist.title)
download_path = f"C:/Users/mkaro/Desktop/python/Youtube/PlaylistMp3Download/{safe_title}"
os.makedirs(download_path, exist_ok=True)

for url in playlist:
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
        if stream:
            print(f"Downloading: {yt.title}")
            stream.download(download_path)
            print(f"Downloaded: {yt.title}")
        else:
            print(f"No suitable stream found for: {yt.title}")
        time.sleep(2)  # Add delay to avoid rate limiting
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        continue