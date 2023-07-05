class Video:
    def __init__(self):
        self.__url = ""
        self.__duration = 0
        self.__current_time = 0
        self.__progress = 0
        self.__is_playing = False

    @property
    def duration(self):
        return self.__duration

    @duration.setter
    def duration(self, duration):
        self.__duration = duration

    @property
    def current_time(self):
        return self.__current_time

    @current_time.setter
    def current_time(self, current_time):
        self.__current_time = current_time

    @property
    def progress(self):
        return self.__progress

    @progress.setter
    def progress(self, progress):
        self.__progress = progress

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, url):
        self.__url = url
        
    @property
    def is_playing(self):
        return self.__is_playing

    @is_playing.setter
    def is_playing(self, is_playing):
        self.__is_playing = is_playing