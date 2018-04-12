# 1. returns all the city objects in the DB
def get_all_cities(dao):
    return dao.get_all('city')


# 2. gets the city from firebase which have city_id
def get_city_for_id(city_id, dao):
    all_cities = get_all_cities(dao)

    for city in all_cities:
        if city['id'] == int(city_id):
            return city
    return None
