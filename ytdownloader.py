from pytube import YouTube
from sys import argv

link = argv[0]
yt = YouTube('https://www.youtube.com/watch?v=dQw4w9WgXcQ') #change this to the video you wish to download

print("Title: ", yt.title)

print("view: ", yt.views)

yd = yt.streams.get_highest_resolution()

yd.download('C:/Users/Donkey/Videos/Youtube') #change this to wherever you want the video file to be downloaded to.
# Remember to use forward slashes in Python