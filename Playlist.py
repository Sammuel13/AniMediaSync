from ListaSequencial import Lista

class Playlist:
    def __init__(self):
        self.playlist = Lista()

    def is_empty(self):
        return self.playlist.estaVazia()

    def add_media(self, media, position=None):
        if position is not None:
            self.playlist.inserir(media, position)
        else:
            self.playlist.inserir(media)

    def remove_media(self, position):
        self.playlist.remover(position)

    def clear_playlist(self):
        self.playlist.clear()

    def shuffle_playlist(self):
        self.playlist.shuffle()

    def remove_duplicates(self):
        self.playlist.removeDupps()

    def realocate_media(self, current_position, new_position):
        self.playlist.realocate(current_position, new_position)

    def get_current_media(self):
        return self.playlist.elemento(1)

    def get_next_media(self):
        return self.playlist.next()

    def get_playlist_length(self):
        return self.playlist.tamanho()

    def get_all_media(self):
        return self.playlist.iterable()