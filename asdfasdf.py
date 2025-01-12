import os
import spotipy
import tkinter as tk
import requests
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from PIL import Image, ImageTk, ImageOps
from io import BytesIO


# Load environment variables from the .env file
load_dotenv()


# Spotify API credentials
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

# Configuration Section--------------

# Fonts
FONT_TITLE = ("Circular Std Black", 20)
FONT_BUTTON = ("Circular Std Black", 14)

# Colors
COLOR_BACKGROUND = "#1DB954"  
COLOR_BUTTON_BACKGROUND = "black"
COLOR_BUTTON_FORGROUND = "white"
COLOR_BUTTON_ACTIVE = "black"

# Dimensions
BUTTON_WIDTH = 20
BUTTON_HEIGHT = 4

#-------------------------------------

# Scope for controlling playback
SCOPE = 'user-read-playback-state user-modify-playback-state'

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=SCOPE))

# Determine the initial playback state
def get_playback_state():
    playback = sp.current_playback()
    return playback and playback['is_playing']

# Track playback state
is_playing = get_playback_state()

# Function to get current song and album cover URL
def get_current_song():
    playback = sp.current_playback()
    if playback and playback['item']:
        song_name = playback['item']['name']
        artists = ', '.join(artist['name'] for artist in playback['item']['artists'])
        album_cover_url = playback['item']['album']['images'][0]['url']  # Album cover URL
        return f"{song_name} by {artists}", album_cover_url
    return "No song playing", None

# Function to update the album cover
def update_album_cover(album_cover_url):
    if album_cover_url:
        response = requests.get(album_cover_url)
        img_data = Image.open(BytesIO(response.content))

        # Ensure the image is square by padding
        desired_size = 300  # Desired dimensions (300x300)
        img_data = ImageOps.pad(img_data, (desired_size, desired_size), method=Image.LANCZOS)

        # Create a PhotoImage for tkinter
        img = ImageTk.PhotoImage(img_data)
        album_label.config(image=img)
        album_label.image = img  # Keep a reference to avoid garbage collection
    else:
        album_label.config(image="")

# Function to update the song label and album cover immediately
def update_song_label_immediately():
    song, album_cover_url = get_current_song()
    song_label.config(text=song)
    update_album_cover(album_cover_url)

# Toggle Play and Pause
def toggle_play_pause():
    global is_playing
    if is_playing:
        sp.pause_playback()
        play_pause_button.config(text="Play")
    else:
        sp.start_playback()
        play_pause_button.config(text="Pause")
    is_playing = not is_playing

# Skip and Previous Button Functions
def skip_song():
    sp.next_track()
    update_song_label_immediately()

def previous_song():
    sp.previous_track()
    update_song_label_immediately()

def create_gui():
    root = tk.Tk()
    root.title("Spotify Controller")
    root.geometry("1024x600")  # Set window size explicitly
    root.attributes('-fullscreen', True)
    root.config(bg=COLOR_BACKGROUND)
    root.config(cursor="none")
    root.bind(
        "<Escape>",
        lambda event: root.attributes('-fullscreen', False))

    global song_label, artist_label, album_label, play_pause_button

#-----------------------------

    # Album Cover
    album_label = tk.Label(
        root,
        bg=COLOR_BACKGROUND)
    album_label.place(x=50, y=50, width=300, height=300)  

    # Song Title Label
    song_label = tk.Label(
        root,
        text="No song playing",
        font=FONT_TITLE,
        bg=COLOR_BACKGROUND,
        fg="white",
        anchor="w")
    song_label.place(x=400, y=100, width=500, height=50)  

    # Artist Label
    artist_label = tk.Label(
        root,
        text="",
        font=("Circular Std Book", 16),
        bg=COLOR_BACKGROUND,
        fg="white",
        anchor="w")
    artist_label.place(x=400, y=180, width=500, height=30)  

#-----------------------------

    # Common Button Style
    button_style = {
        "font": FONT_BUTTON,
        "activebackground": COLOR_BUTTON_ACTIVE,
        "bg": COLOR_BUTTON_BACKGROUND,
        "fg": COLOR_BUTTON_FORGROUND,
        "highlightthickness": 0}

    # Previous Button
    previous_button = tk.Button(
        root,
        text="Previous",
        command=previous_song
        **button_style)
    previous_button.place(
        x=50, y=400, width=150, height=50)

    # Play/Pause Button
    play_pause_button = tk.Button(
        root,
        text="Pause" if is_playing else "Play",
        command=toggle_play_pause,
        **button_style)
    play_pause_button.place(
        x=250, 
        y=400, 
        width=150, 
        height=50)

    # Skip Button
    skip_button = tk.Button(
        root,
        text="Next",
        command=skip_song,
        **button_style)
    skip_button.place(
        x=450, 
        y=400, 
        width=150, 
        height=50)

#-----------------------------

    # Function to poll for song changes
    def update_song():
        song, album_cover_url = get_current_song()
        if song_label["text"] != song:
            song_label.config(text=song.split(" by ")[0])  
            artist_label.config(text=song.split(" by ")[1])  
            update_album_cover(album_cover_url)
        root.after(1000, update_song)

    # Start updating song
    update_song()

    root.mainloop()

create_gui()