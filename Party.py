from ChainingHashTable import ChainingHashTable
from Playlist import Playlist
from Video import Video

class Party:
    def __init__(self, size=10):
        self._name = ""
        self._size = size
        self._member_count = 0
        self.members = ChainingHashTable(size*4)
        self._video = Video()
        self._playlist = Playlist()
        self._status = self._video.is_playing

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def video_url(self):
        return self._video.url

    @video_url.setter
    def video_url(self, url):
        self._video.url = url

    @property
    def video_time(self):
        return self._video.current_time

    @video_time.setter
    def video_time(self, current_time):
        self._video.current_time = current_time

    @property
    def video_position(self):
        return self._video.progress

    @video_position.setter
    def video_position(self, position):
        self._video.progress = position

    @property
    def video_duration(self):
        return self._video.duration

    @video_duration.setter
    def video_duration(self, duration):
        self._video.duration = duration

    @property
    def playlist(self):
        return self._playlist

    def add_member(self, memberKey, member):
        self.members.put(memberKey, member)
        self._member_count += 1

    def remove_member(self, memberKey):
        self.members.remove(memberKey)
        self._member_count -= 1

    def get_members(self):
        return self.members.values()
    
    def get_member_count(self):
        return self._member_count
