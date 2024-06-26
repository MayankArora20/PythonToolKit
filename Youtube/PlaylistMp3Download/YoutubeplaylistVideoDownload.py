from pytube import YouTube
from pytube import Playlist

playlist = Playlist("https://www.youtube.com/playlist?list=PLxPkKPLAAOxlTdF2XOJWhnnBI53ear3CN")

print("Playlist Name: "+playlist.title)

#print urls
playlist.video_urls
for url in playlist:
    print(url)

#prints address of each YouTube object in the playlist
for vid in playlist.videos:
    print(vid)

for url in playlist:
   YouTube(url).streams.filter().first().download("C:/Users/mkaro/Desktop/python/Youtube/PlaylistMp3Download/"+playlist.title)