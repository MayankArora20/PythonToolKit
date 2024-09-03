import os
import re
import yt_dlp
import moviepy.editor as mp  # to convert the mp4 to mp3
from http.client import IncompleteRead

def writeErrorsToFile(location, errorMessage):
    with open(location + "ytMp3ErrorLog.txt", "a") as f:
        f.write(errorMessage + "\n")

playlists = [
    "https://www.youtube.com/playlist?list=PLxPkKPLAAOxnqCGRrFP0k0NNRr3QvuRgm"
]

errorLog = ["Errors:"]

for list in playlists:
    print("\nytLink: " + list)

    # yt-dlp does not have a direct Playlist object, so we'll get the URLs manually
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        playlist_info = ydl.extract_info(list, download=False)
        playlist_title = playlist_info.get('title', 'Untitled Playlist')
        video_urls = [entry['url'] for entry in playlist_info['entries']]

    print("Playlist Name: " + playlist_title)
    dirLocation = "C:/Users/mkaro/Desktop/python/Youtube/PlaylistMp3Download/"
    folder = os.path.join(dirLocation, playlist_title)
    os.makedirs(folder, exist_ok=True)
    print("Storage location: " + folder)

    for url in video_urls:
        try:
            # Set yt-dlp options for downloading video
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        except Exception as e:
            video_info = yt_dlp.YoutubeDL().extract_info(url, download=False)
            video_title = video_info.get('title', 'Unknown Title')
            writeErrorsToFile(dirLocation, f"Error: {url} {video_title}")
            continue

    # Convert any remaining MP4 files in the folder to MP3
    for file in os.listdir(folder):
        if re.search(r'\.mp4$', file):
            print("Converting : " + file)
            try:
                mp4_path = os.path.join(folder, file)
                mp3_path = os.path.join(folder, os.path.splitext(file)[0] + '.mp3')
                new_file = mp.AudioFileClip(mp4_path)
                new_file.write_audiofile(mp3_path)
                os.remove(mp4_path)
            except Exception as e:
                writeErrorsToFile(dirLocation, f"Error occurred while converting {file}")
                continue
