#!/usr/bin/python3
"""scdl allow you to download music from soundcloud

Usage:
	scdl.py -l <track_url> [--hidewarnings]
	scdl.py --me [--hidewarnings]
	scdl.py -h | --help
	scdl.py --version


Options:
	-h --help		Show this screen.
	--version		Show version.
	-l [url]		Necessary. URL is the url of the soundcloud's page.
	--hidewarnings	Hide Warnings.
"""
from docopt import docopt
import configparser

import warnings
import os
import signal
import sys

import soundcloud
import wget

token = ''
client = soundcloud.Client(client_id='b45b1aa10f1ac2941910a7f0d10f8e28')
filename = ''

def main():
	"""
	Main function, call parse_url
	"""
	print("Soundcloud Downloader")

	arguments = docopt(__doc__, version='0.1')
	print(arguments)

	get_config()

	if arguments["--hidewarnings"]:
		warnings.filterwarnings("ignore")

	if arguments["-l"]:
		parse_url(arguments["<track_url>"])
	elif arguments["--me"]:
		mystream()

def get_config():
	"""
	read the path where to store music
	"""
	global token
	config = configparser.ConfigParser()
	config.read('scdl.cfg')
	token = config['scdl']['auth_token']
	path = config['scdl']['path']
	os.chdir(path)

def mystream():
	client = soundcloud.Client(access_token=token)
	# make an authenticated call
	current_user = client.get('/me')
	print('Hello',current_user.username, '!')
	activities = client.get('/me/activities')
	print(activities.type)


def settags(track):
	"""
	Set the tags to the mp3
	"""
	print("Settings tags...")
	user = client.get('/users/' + str(track.user_id), allow_redirects=False)
	audiofile = my_eyed3.load(filename)
	audiofile.tag.artist = user.username
	audiofile.tag.album = track.title
	audiofile.tag.title = track.title

	audiofile.tag.save()

def get_item(track_url):
	"""
	Fetches metadata for an track or playlist
	"""
	# Fetches metadata from soundcloud
	try:
		item = client.get('/resolve', url=track_url)
	except Exception as e:
		print("Could not resolve url " + track_url)
		print(e, exc_info=True)
		return False
	return item

def parse_url(track_url):
	"""
	Detects if the URL is a track or playlists, and parses the track(s) to the track downloader
	"""

	item = get_item(track_url)
	if not item:
		return
	if item.kind == 'track':
		print("Found a track")
		download_track(item)

	if item.kind == 'user':
		print("Found an user profile")
		download_user(item)

	elif item.kind == "playlist":
		print("Found a playlist")
		for track_raw in item.tracks:
			mp3_url = get_item(track_raw["permalink_url"])
			if item:
				download_track(mp3_url)
			else:
				print("Could not find track " + track_raw["title"])
	else:
		print("Unknown item type")

def download_user(user):
	"""
	Fetch users data
	"""
	offset = 0
	end_of_tracks = False
	songs = client.get('/users/' + str(user.id) + '/favorites', limit = 10, offset = offset)
	while not end_of_tracks:
		for track in songs:
			if track.kind == 'track':
				print("")
				download_track(track)
			else:
				print("End of favorites")
				end_of_tracks =True
		offset += 10

def download_track(track):
	"""
	Downloads a track
	"""

	stream_url = client.get(track.stream_url, allow_redirects=False)
	url = stream_url.location

	title = track.title
	print("Downloading " + title)

	global filename
	filename = title +'.mp3'

	if not os.path.isfile(filename):
		wget.download(url, filename)
	else:
		print("Music already exists ! (exiting)")
		sys.exit(0)
	#settags(track)

	print('')
	print(title + ' Downloaded.')

def signal_handler(signal, frame):
	"""
	handle keyboardinterrupt
	"""
	files = os.listdir()
	for f in files:
		if not os.path.isdir(f) and ".tmp" in f:
			os.remove(f)

	print('')
	print('Good bye!')
	sys.exit(0)

if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal_handler)
	main()