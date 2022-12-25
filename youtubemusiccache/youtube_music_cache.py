import fuzzywuzzy.fuzz
import shelve
import time
from typing import Dict, List
import ytmusicapi

"""
Disk cached and helper functions for https://ytmusicapi.readthedocs.io/en/latest/index.html
"""
class YTMCache:

	def __init__(self, ytmusic: ytmusicapi.YTMusic, sleep_interval=0.1, track_cache='cache/tracks.dat'):
		self.ytmusic = ytmusic
		self.sleep_interval = sleep_interval
		self.track_cache = shelve.open(track_cache, 'c')
		self.last_time_sec = time.time() - 1 # Last time we interacted with YouTube Music API, this implements rate limiting

	"""
	Find a track in YouTube Music using the given track, artist, and album.

	Returns a dict {
		"id": "bjGppZKiuFE",
		"track": "Lost",
		"artists": [
			{
				"name": "Guest Who",
				"id": "UCkgCRdnnqWnUeIH7EIc3dBg"
			},
			{
				"name": "Kate Wild",
				"id": "UCwR2l3JfJbvB6aq0RnnJfWg"
			}
		],
		"album": {
			"name": "Lost",
			"id": "MPREb_PxmzvDuqOnC"
		},
		"score": <match score out of 100>
	}
	or None if no track can be found
	"""
	def get_track(self, track, artist, album=''):
		track_key = f"{track} | {artist} | {album}"
		if track_key in self.track_cache:
			return self.track_cache[track_key]

		# Rate limiting, be nice to YouTube Music API
		sleep_time = self.last_time_sec + self.sleep_interval - time.time()
		if sleep_time > 0:
			time.sleep(sleep_time)
		search_result = self.ytmusic.search(f"{track} {artist} {album}", 'songs') # TODO this search string gets dumb with self-titled albums or songs named after albums
		self.last_time_sec = time.time()

		if len(search_result) > 0:
			hit = search_result[0]
			result = {'id': hit['videoId'], 'track': hit['title'], 'album': hit['album'], 'artists': hit['artists']}
			result['score'] = self.calculate_track_diff(result, track, artist, album)
			result['add'] = self.extract_add_feedback_token(hit)

			if len(search_result) > 1 and not hit['isExplicit']: # Check the next hit if the first hit isn't explicit
				hit = search_result[1]
				result_alt = {'id': hit['videoId'], 'track': hit['title'], 'album': hit['album'], 'artists': hit['artists']}
				result_alt['score'] = self.calculate_track_diff(result_alt, track, artist, album)
				result_alt['add'] = self.extract_add_feedback_token(hit)
				if hit['isExplicit'] and result_alt['score'] >= result['score']: # Use second hit if it's explicit and has better score
					result = result_alt

			self.track_cache[track_key] = result
			return result
		else:
			self.track_cache[track_key] = None
			return None

	"""
	Retrieve the current user's playlists
	"""
	def get_playlists(self):
		return self.ytmusic.get_library_playlists()

	"""
	Create a playlist
	"""
	def create_playlist(self, title, description, video_ids):
		return self.ytmusic.create_playlist(title, description, video_ids=video_ids)

	def calculate_track_diff(self, search_result, track, artist=None, album=None):
		s1 = f"{track} {artist} {album}"
		result_artists = ' '.join(map(lambda x: x['name'], search_result['artists']))
		result_album = '' if search_result['album'] is None else search_result['album']['name']
		s2 = f"{search_result['track']} {result_artists} {result_album}"
		return fuzzywuzzy.fuzz.token_set_ratio(s1, s2)

	def extract_add_feedback_token(self, hit):
		token = ''
		if 'feedbackTokens' in hit and 'add' in hit['feedbackTokens']:
			add_token = hit['feedbackTokens']['add']
			if add_token is not None and len(add_token) > 0:
				token = add_token
		return token

	def edit_song_library_status(self, feedback_tokens: List[str]) -> Dict:
		return self.ytmusic.edit_song_library_status(feedback_tokens)

	"""
	Retrieve songs from the current user's library limiting the size of the return to the given limit
	"""
	def get_library_songs(self, limit: int, validate_responses: bool):
		return self.ytmusic.get_library_songs(limit, validate_responses)

	"""
	Rate a song specified by the videoId ('LIKE', 'DISLIKE', 'INDIFFERENT')
	"""
	def rate_song(self, videoId: str, rating: str = 'INDIFFERENT') -> Dict:
		sleep_time = self.last_time_sec + self.sleep_interval - time.time() # Be nice to YouTube Music API
		if sleep_time > 0:
			time.sleep(sleep_time)
		result =  self.ytmusic.rate_song(videoId, rating)
		self.last_time_sec = time.time()
		return result

	"""
	Closes cache files to prevent corruption. Should be called before the program exits.
	"""
	def close(self):
		self.track_cache.close()
