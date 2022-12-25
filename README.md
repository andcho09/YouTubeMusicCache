# YouTube Music Cache

A helper module for [ytmusicapi](https://ytmusicapi.readthedocs.io/en/latest/index.html) that introduces:

* Cache for reducing the number of network calls made to YouTube Music
* Rate-limiting so we can be nice to YouTube's API
* Fuzzy matching to check whether search queries are returning "useful" results
* Helper methods


## Usage

1. In the project that you want to use this module...

1. Install the module in development mode (since this isn't published anywhere official), e.g.

	From a local directory (which makes modifying this code easier):

	```
	$ pip install -e <local path to the folder containing this README.md>
	```

	Or from Git:

	```
	$ pip install -e git+https://github.com/andcho09/YouTubeMusicCache.git
	```

1. Set up the ``headers_auth.json`` as per these [instructions](https://ytmusicapi.readthedocs.io/en/latest/setup.html)

1. Then import and use the module:

		from ytmusicapi import YTMusic
		from youtubemusiccache import youtube_music_cache

		yt = youtube_music_cache.YTMCache(YTMusic('headers_auth.json'))
		track = yt.get_track('Tribute', 'Tenacious D')


## TODO

* Figure out how to mock ytmusicapi for unit tests


## References

https://python-packaging-tutorial.readthedocs.io/en/latest/setup_py.html