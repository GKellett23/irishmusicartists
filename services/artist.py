from werkzeug.utils import secure_filename
import os

def create_artist_account(request, dao):
    count = dao.get_table_count('band') + 1
    id_artist = 0
    if count:
        id_artist = count

    genres = []

    for genre in request.form['genre']:
        genres.append(genre)

    banner = ''
    if 'banner' in request.files:
        f = request.files['banner']
        if not os.path.exists("static/medias/artist-details/{0}/banner".format(id_artist)):
            os.makedirs("static/medias/artist-details/{0}/banner/".format(id_artist))
        banner = secure_filename(f.filename)
        filepath = "static/medias/artist-details/{0}/banner/{1}".format(id_artist, banner)
        f.save(filepath)

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


def link_user_to_artist(user, artist, dao):
    user_db = dao.get_id_from_table('user', user.id)
    key = user.id

    if user_db:
        user_db['is_artist'] = True
        user_db['artist_id'] = artist['id']
        dao.update('user', key, user_db)

    return None


def get_artist(id_artist, dao):
    result = dao.get_id_from_table('band', id_artist)
    if result and result.get('banner'):
        result['banner'] = "static/medias/artist-details/{0}/banner/{1}".format(id_artist, result['banner'])
    return result


def get_all_artist(dao):
    all_artists = dao.get_all('band')
    result = []
    for artist in all_artists:
        if artist:
            result.append(artist)

    return result


def get_all_artists_for_genre(genre_list, dao):
    all_artist = get_all_artist(dao)
    result = []
    for artist in all_artist:
        if len(artist['genre']) < len(genre_list):
            for genre in artist['genre']:
                if int(genre) in genre_list:
                    result.append(artist)
        else:
            for genre in genre_list:
                if genre in artist['genre']:
                    result.append(artist)
    return result


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
