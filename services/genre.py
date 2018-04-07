def __get_str_array(array):
    result = []
    if array and len(array) > 0 and type(array[0]) == int:
        for val in array:
            result.append(str(val))
    else:
        return array
    return result


def get_all_genres(dao):
    return dao.get_all('genre')


def get_genre_for_list(genre_list, dao):
    all_genres = get_all_genres(dao)
    result = []
    for genre in all_genres:
        if str(genre['id']) in __get_str_array(genre_list):
            result.append(genre)
    return result


def update_user_genres(user_id, form, dao):
    new_genre = []
    for genre in form.getlist('genre'):
        new_genre.append(str(genre))

    dao.update('user/{0}'.format(user_id), 'genre', new_genre)
