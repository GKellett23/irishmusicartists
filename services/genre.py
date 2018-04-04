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
