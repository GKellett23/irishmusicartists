# 1. transforms the array of int into an array of string type objects
# private function that won't be accessible from other files
# http://effbot.org/pyfaq/tutor-how-do-i-make-public-and-private-attributes-and-methods-in-my-classes.htm
def __get_str_array(array):
    result = []
    if array and len(array) > 0 and type(array[0]) == int:
        for val in array:
            result.append(str(val))
    else:
        return array
    return result


# 2. returns all the genre from the firebase genre table
def get_all_genres(dao):
    return dao.get_all('genre')


# 3. gets the genre objects from the genre ids in genre_list
def get_genre_for_list(genre_list, dao):
    all_genres = get_all_genres(dao)
    result = []
    for genre in all_genres:
        if str(genre['id']) in __get_str_array(genre_list):
            result.append(genre)
    return result


# 4. update the genre array of the given user_id
def update_user_genres(user_id, form, dao):
    new_genre = []
    for genre in form.getlist('genre'):
        new_genre.append(str(genre))

    dao.update('user/{0}'.format(user_id), 'genre', new_genre)
