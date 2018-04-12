from werkzeug.utils import secure_filename
import os


# 1.
# Creates an artist account
def create_artist_account(request, dao):
    # Gets the count of the band table and add 1 to generate the id of the future account
    count = dao.get_table_count('band') + 1
    id_artist = 0
    if count:
        id_artist = count

    genres = []

    for genre in request.form['genre']:
        genres.append(genre)

    banner = ''
    # saves the banner in the filesystem to store artist's picture
    # http://www.pythonforbeginners.com/files/reading-and-writing-files-in-python
    if 'banner' in request.files:
        f = request.files['banner']
        # using makedirs function in order to create the structure if it does not exists
        # https://docs.python.org/2/library/os.html#os.makedirs
        if not os.path.exists("static/medias/artist-details/{0}/banner".format(id_artist)):
            os.makedirs("static/medias/artist-details/{0}/banner/".format(id_artist))
        # uses secure_filename in order to prevent the user to put weird characters like / that may harm the system
        # replaces all those characters by _ char instead
        banner = secure_filename(f.filename)
        filepath = "static/medias/artist-details/{0}/banner/{1}".format(id_artist, banner)
        f.save(filepath)

    # creates a dictionary to store the band information
    artist_account = {
        'id': id_artist,
        'name': request.form['name'],
        'bio': request.form['biography'],
        'genre': genres,
        'locality': request.form['city'],
        'spot': request.form.get('spot'),
        'facebook': request.form.get('facebook'),
        'website': request.form.get('website'),
        'banner': banner
    }
    dao.update('band', count, artist_account)
    return artist_account


# 2.
# allows to link the current user to its artist account
# add a new entry artist_id to the user to store the newly generated artist id  in the user
def link_user_to_artist(user, artist, dao):
    user_db = dao.get_id_from_table('user', user.id)
    key = user.id

    if user_db:
        user_db['is_artist'] = True
        user_db['artist_id'] = artist['id']
        dao.update('user', key, user_db)

    return None


# 3.
# returns the artist for the given id
def get_artist(id_artist, dao):
    result = dao.get_id_from_table('band', id_artist)
    # generates the banner link from the user id and the user's banner attribute to display in the UI
    if result and result.get('banner'):
        result['banner'] = "static/medias/artist-details/{0}/banner/{1}".format(id_artist, result['banner'])
    return result


# 4.
# returns all the artists from the band table
def get_all_artist(dao):
    all_artists = dao.get_all('band')
    result = []
    for artist in all_artists:
        if artist:
            result.append(artist)

    return result


# 5.
# Returns the list of artists having one of the genre in the genre_list
def get_all_artists_for_genre(genre_list, dao):
    all_artist = get_all_artist(dao)
    result = []
    for artist in all_artist:
        # optimise the time taken to check if an artist is having the given genre
        # if the artist genre's list is less than the genre list in parameter
        # then use the artist genre otherwise use the parameterized genre list
        # allows to do less iterations while joining
        if len(artist['genre']) < len(genre_list):
            for genre in artist['genre']:
                if genre in genre_list:
                    result.append(artist)
        else:
            for genre in genre_list:
                if genre in artist['genre']:
                    result.append(artist)
    return result


# 6.
# Does the same job than function 5 but excludes the artist having id_artist value in parameter
def get_artist_for_genre(id_artist, genre_list, dao):
    all_artist = get_all_artist(dao)
    result = []
    for artist in all_artist:
        if not artist['id'] == id_artist:
            if len(artist['genre']) < len(genre_list):
                for genre in artist['genre']:
                    if int(genre) in genre_list:
                        result.append(artist)
            else:
                for genre in genre_list:
                    if genre in artist['genre']:
                        result.append(artist)
    return result
