# Road2Music

Front end: https://road2music.herokuapp.com/

Theoretically, with the help of this app, users enter their route information (origin and destination) and get a playlist on Spotify that takes their route information into consideration (see the app's prototype under app/route2music/route2music.py).

What does not work yet:
1. The main part of my app is under https://road2music.herokuapp.com/createplaylist. The first step, getting a user's Spotify cache token saved into the designated folder ".spotify_caches", does not seem to work yet. Therefore, the following steps (accessing the Spotify account as well as creating and filling a playlist) also do not work. 
2. In case the fundamentals of this app will not work, I created a plan b so that I can at least meet the requirements in the assessment guidelines (specifically "a database to store data from user input"). In the contact.html, I created an input field where users can make suggestions. These inputs get shown as variables in the URL (for example "https://road2music.herokuapp.com/config.php?songname=Bohemian+Rhapsody&artistname=Queen"), but I have not found a way to set up a database and store these inputs yet.

