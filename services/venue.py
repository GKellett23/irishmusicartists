# 1. Retrieve all venues from firebase
def get_all_venue(dao):
    return dao.get_all('venue')


# 2. add the matching venue to each event contained in the event_list
def populate_venue_for_event(event_list, dao):
    all_venues = get_all_venue(dao)
    for event in event_list:
        for venue in all_venues:
            if int(event['venue_id']) == int(venue['id']):
                event['venue_name'] = venue['name']
