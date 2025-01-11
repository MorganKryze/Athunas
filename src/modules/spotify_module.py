import spotipy
import os
import logging
from settings import Settings
from enums.variable_importance import Importance


class SpotifyModule:
    def __init__(self):
        """
        Initialize the SpotifyModule with the given configuration.
        """
        self.enabled = Settings.read_variable("Spotify", "enabled", Importance.REQUIRED)
        if not self.enabled:
            logging.info("[Spotify Module] Disabled")
            return

        logging.debug("[Spotify Module] Initializing")

        client_id = Settings.read_variable("Spotify", "client_id", Importance.REQUIRED)
        client_secret = Settings.read_variable(
            "Spotify", "client_secret", Importance.REQUIRED
        )
        redirect_uri = Settings.read_variable(
            "Spotify", "redirect_uri", Importance.REQUIRED
        )

        if client_id and client_secret and redirect_uri:
            try:
                os.environ["SPOTIPY_CLIENT_ID"] = client_id
                os.environ["SPOTIPY_CLIENT_SECRET"] = client_secret
                os.environ["SPOTIPY_REDIRECT_URI"] = redirect_uri

                scope = "user-read-currently-playing, user-read-playback-state, user-modify-playback-state"
                self.auth_manager = spotipy.SpotifyOAuth(scope=scope)
                logging.info(
                    f"[Spotify Module] Authorization URL: {self.auth_manager.get_authorize_url()}"
                )
                self.sp = spotipy.Spotify(
                    auth_manager=self.auth_manager, requests_timeout=10
                )
                self.isPlaying = False
            except Exception as e:
                logging.error(f"[Spotify Module] Initialization error: {e}")
                self.enabled = False
        else:
            logging.error(
                "[Spotify Module] Missing or invalid configuration parameters"
            )
            self.enabled = False

    def getCurrentPlayback(self):
        """
        Get the current playback information.

        Returns:
            tuple: A tuple containing artist, title, art_url, is_playing, progress_ms, and duration_ms.
        """
        if not self.enabled:
            logging.warning("[Spotify Module] Module is disabled")
            return None

        try:
            track = self.sp.current_user_playing_track()
            if track and track["item"]:
                artist = track["item"]["artists"][0]["name"]
                if len(track["item"]["artists"]) >= 2:
                    artist = f"{artist}, {track['item']['artists'][1]['name']}"
                title = track["item"]["name"]
                art_url = track["item"]["album"]["images"][0]["url"]
                self.isPlaying = track["is_playing"]
                return (
                    artist,
                    title,
                    art_url,
                    self.isPlaying,
                    track["progress_ms"],
                    track["item"]["duration_ms"],
                )
            else:
                logging.info("[Spotify Module] No track is currently playing")
                return None
        except Exception as e:
            logging.error(f"[Spotify Module] Error getting current playback: {e}")
            return None

    def resume_playback(self):
        """
        Resume playback.
        """
        if self.enabled:
            try:
                self.sp.start_playback()
            except spotipy.exceptions.SpotifyException:
                logging.warning(
                    "[Spotify Module] No active device, trying specific device"
                )
                devices = self.sp.devices()
                if "devices" in devices and len(devices["devices"]) > 0:
                    try:
                        self.sp.start_playback(device_id=devices["devices"][0]["id"])
                    except Exception as e:
                        logging.error(
                            f"[Spotify Module] Error resuming playback on specific device: {e}"
                        )
            except Exception as e:
                logging.error(f"[Spotify Module] Error resuming playback: {e}")

    def pause_playback(self):
        """
        Pause playback.
        """
        if self.enabled:
            try:
                self.sp.pause_playback()
            except spotipy.exceptions.SpotifyException:
                logging.warning("[Spotify Module] Problem pausing playback")
            except Exception as e:
                logging.error(f"[Spotify Module] Error pausing playback: {e}")

    def next_track(self):
        """
        Skip to the next track.
        """
        if self.enabled:
            try:
                self.sp.next_track()
            except spotipy.exceptions.SpotifyException:
                logging.warning(
                    "[Spotify Module] No active device, trying specific device"
                )
                devices = self.sp.devices()
                if "devices" in devices and len(devices["devices"]) > 0:
                    self.sp.next_track(device_id=devices["devices"][0]["id"])
            except Exception as e:
                logging.error(f"[Spotify Module] Error skipping to next track: {e}")

    def previous_track(self):
        """
        Go to the previous track.
        """
        if self.enabled:
            try:
                self.sp.previous_track()
            except spotipy.exceptions.SpotifyException:
                logging.warning(
                    "[Spotify Module] No active device, trying specific device"
                )
                devices = self.sp.devices()
                if "devices" in devices and len(devices["devices"]) > 0:
                    self.sp.previous_track(device_id=devices["devices"][0]["id"])
            except Exception as e:
                logging.error(f"[Spotify Module] Error going to previous track: {e}")

    def increase_volume(self):
        """
        Increase the volume.
        """
        if self.enabled and self.isPlaying:
            try:
                devices = self.sp.devices()
                curr_volume = devices["devices"][0]["volume_percent"]
                self.sp.volume(min(100, curr_volume + 5))
            except Exception as e:
                logging.error(f"[Spotify Module] Error increasing volume: {e}")

    def decrease_volume(self):
        """
        Decrease the volume.
        """
        if self.enabled and self.isPlaying:
            try:
                devices = self.sp.devices()
                curr_volume = devices["devices"][0]["volume_percent"]
                self.sp.volume(max(0, curr_volume - 5))
            except Exception as e:
                logging.error(f"[Spotify Module] Error decreasing volume: {e}")
