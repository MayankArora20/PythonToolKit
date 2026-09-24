import os
import re
import yt_dlp
import moviepy.editor as mp  # to convert the mp4 to mp3
from http.client import IncompleteRead

def writeErrorsToFile(location, errorMessage):
    with open(location + "ytMp3ErrorLog.txt", "a") as f:
        f.write(errorMessage + "\n")

# Sometimes playlist title contains invalid characters, that we should handle
def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip().strip('.')

playlists = [
    # "https://www.youtube.com/playlist?list=PLxPkKPLAAOxnqCGRrFP0k0NNRr3QvuRgm",
    # "https://www.youtube.com/playlist?list=PLxPkKPLAAOxkk2rPqHkKIyQaMhGRYefMv",
    # "https://www.youtube.com/playlist?list=PLQ8Q-8-X18dmZwj53QMUBv0jyDzhzZSFU",
    # "https://www.youtube.com/playlist?list=PLQ8Q-8-X18dnONIdMCi60rCpPOlRDjDBW",
    # "https://www.youtube.com/playlist?list=PLQ8Q-8-X18dmOznjoG3yeqmHiF9Ne6osR",
    # "https://www.youtube.com/playlist?list=PLQ8Q-8-X18dlv1iIHy_y7nch7xIDgsXFK",
    # "https://www.youtube.com/playlist?list=PLQ8Q-8-X18dm9qo_bmxrQjf8AKIO5N_bp",
    # "https://www.youtube.com/playlist?list=PLQ8Q-8-X18dlOLRQQiqDSMJpgZ586to1o"
    # "https://www.youtube.com/playlist?list=PLxPkKPLAAOxln5v_Y91GIhD0GOJJeUVEq",
    "https://youtube.com/playlist?list=PLxPkKPLAAOxln5v_Y91GIhD0GOJJeUVEq&si=q_hpijCrQPmWfhlQ"
]

errorLog = ["Errors:"]

for list in playlists:
    print("\nytLink: " + list)

    dirLocation = "C:/Users/mkaro/Desktop/python/Youtube/PlaylistMp3Download/"

    try:
        # yt-dlp does not have a direct Playlist object, so we'll get the URLs manually
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'skip_download': True,
            'ignoreerrors': True,
            'noplaylist': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(list, download=False)

        if not playlist_info:
            print("No playlist info was returned; skipping this playlist.")
            continue

        playlist_title_raw = playlist_info.get('title', 'Untitled Playlist')
        playlist_title = sanitize_filename(playlist_title_raw)
        entries = playlist_info.get('entries') or []
        video_urls = []

        for entry in entries:
            if not entry:
                continue
            if isinstance(entry, dict):
                if entry.get('url'):
                    video_urls.append(entry['url'])
            elif isinstance(entry, str):
                video_urls.append(entry)

    except Exception as e:
        writeErrorsToFile(dirLocation, f"Playlist error: {list} :: {type(e).__name__}: {e}")
        continue

    print("Playlist Name: " + playlist_title)
    folder = os.path.join(dirLocation, playlist_title)
    os.makedirs(folder, exist_ok=True)
    print("Storage location: " + folder)

    for url in video_urls:
        video_title = "Unknown Title"

        try:
            info_opts = {
                'quiet': True,
                'skip_download': True,
                'noplaylist': True,
                'ignoreerrors': True,
            }
            video_info = yt_dlp.YoutubeDL(info_opts).extract_info(url, download=False)
            if isinstance(video_info, dict):
                video_title = video_info.get('title', 'Unknown Title')
        except Exception:
            pass

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
                'quiet': True,
                'noplaylist': True,
                'ignoreerrors': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        except Exception as e:
            writeErrorsToFile(dirLocation, f"Error: {url} {video_title} :: {type(e).__name__}: {e}")
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
