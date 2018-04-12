from flask_login import UserMixin


# User class from https://stackoverflow.com/questions/37148414/updating-a-single-value-in-firebase-with-python
class User(UserMixin):
    def __init__(self, id, name, password, email, genre):
        self.id = id
        self.name = name
        self.password = password
        self.email = email
        self.is_artist = False
        self.id_artist = None
        if genre:
            self.genre = genre
        else:
            self.genre = []

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)

    def set_artist_id(self, id_artist):
        self.id_artist = id_artist
