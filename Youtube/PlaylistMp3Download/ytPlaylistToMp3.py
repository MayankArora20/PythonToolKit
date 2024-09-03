import os
import re
from pytube import YouTube
from pytube import Playlist
import moviepy.editor as mp #to convert the mp4 to wavv then mp3
from http.client import IncompleteRead

def writeErrorsToFile(location, errorMessage) :
    f = open(location+"tyMp3ErrorLog.txt", "a")
    f.write(errorMessage+"\n")
    f.close()

playlists = [
   "https://www.youtube.com/playlist?list=PLxPkKPLAAOxlTdF2XOJWhnnBI53ear3CN"
#    "https://www.youtube.com/playlist?list=PLxPkKPLAAOxlgT_R64kvtDbqETYlsiJ0d",
#    "https://www.youtube.com/playlist?list=PLxPkKPLAAOxm2Uli5PWBOZ4Z-dIXEY4cU",
#    "https://www.youtube.com/playlist?list=PLxPkKPLAAOxm_VTxT2x3kXAI0rX5xjw30",
#    "https://www.youtube.com/playlist?list=PLxPkKPLAAOxm8eTbRV9Dehw2500E7YZCW",
#    "https://www.youtube.com/playlist?list=PLxPkKPLAAOxnS0K2E-W8qbx-gBH5H44ZT",
#    "https://www.youtube.com/playlist?list=PLxPkKPLAAOxn3wrzvRvjewYOQ4j8GpEg_",
#    "https://www.youtube.com/playlist?list=PLCXtDNGOKg9uMxGmhyjWlR1BrjEoIhCiA"
]

errorLog = ["Errors:"]

for list in playlists:
    print("\nytLink: "+list)
    playlist = Playlist(list)

    print("Playlist Name: "+playlist.title)
    dirLocation = "C:/Users/mkaro/Desktop/python/Youtube/PlaylistMp3Download/"
    folder = dirLocation + playlist.title
    print("storage location: "+folder)

    
    for url in playlist:
        try:
            YouTube(url).streams.filter().first().download(folder)
        except Exception as e:
            writeErrorsToFile(dirLocation, "error: "+url+" "+ YouTube(url).streams[0].default_filename)
            os.remove(os.path.join(folder, YouTube(url).streams[0].default_filename))
            continue
    
    for file in os.listdir(folder):
        if re.search('mp4', file):
            print("Converting : " + file)
            try:
                mp4_path = os.path.join(folder,file)
                mp3_path = os.path.join(folder,os.path.splitext(file)[0]+'.mp3')
                new_file = mp.AudioFileClip(mp4_path)
                new_file.write_audiofile(mp3_path)
                os.remove(mp4_path)
            except Exception as e:
                writeErrorsToFile(dirLocation, "Error occur while converting "+file)
                continue
