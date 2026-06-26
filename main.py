from bs4 import BeautifulSoup
import requests
from datetime import datetime
from ytmusicapi import YTMusic

# ============================================== Setup YT auth ==============================================
yt = YTMusic("./headers_auth.json")

# ============================================== Get Songs list with artists from billboard ==============================================
URL = 'https://www.billboard.com/charts/hot-100/'

response = requests.get(URL)
soup = BeautifulSoup(response.content, 'html.parser')

songs = []

for row in soup.select("ul.o-chart-results-list-row"):
    title_tag = row.select_one("h3")

    if not title_tag:
        continue

    song = title_tag.get_text(" ", strip=True)

    artist_span = title_tag.find_next(
        "span",
        class_=lambda x: x and "c-label" in x
    )

    if artist_span:
        artist = artist_span.get_text(" ", strip=True)

        songs.append({
            "song": song,
            "artist": artist
        })

# ============================================== Get Present a Yt Music Playlists ==============================================
playlists = yt.get_library_playlists()
print(f"Found {len(playlists)} playlists in your library.")
# pprint(playlists)

new_playlist_name = f"{datetime.now().strftime("%Y-%m-%d")} Billboard 100"
Check = False

# ============================================== Check for existing playlist id else create ==============================================
for playlist in playlists:
    if playlist['title'] == new_playlist_name:
        playlist_id = playlist['playlistId']
        Check = True

if Check:
    print("Playlist already exists. Skipping creation.\nPlaylist ID : ",playlist_id)
else:
    playlist_id = yt.create_playlist(new_playlist_name, "Billboard 100","PUBLIC")
    print("Playlist created successfully.\nPlaylist ID : ",playlist_id)

# ============================================== Search and add songs to the new playlist ==============================================
for music in songs:
    try:
        print(f"Searching {music['song']} by {music['artist']}")
        search_result = yt.search(f"{music["song"]} by {music["artist"]}", filter="songs", limit=1)
        print(f"Found {len(search_result)} songs in {music['song']},Adding to playlist.")
        yt.add_playlist_items(playlist_id , [search_result[0]['videoId']])
        print("Song Added to playlist.\n")

# ============================================== If search give 0 results ==============================================
    except IndexError:
        print(f"Skipping {music['song']} by {music['artist']}")
        continue

# ============================================== Print Final Song Count ==============================================
response = yt.get_playlist(playlist_id)
print("All Song Added to playlist.\n"
      "Song count : ", len(response['tracks']))