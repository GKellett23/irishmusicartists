# 1. add a new event in firebase
def add_event(form, dao):
    count = dao.get_table_count('event') + 1
    event = {
        'id': count,
        'venue_id': form['venue'],
        'band_id': form['band_id'],
        'date': form['date']
    }
    dao.update('event', count, event)


# 2. returns all the events from firebase event table
def get_all_events(dao):
    all_evts = dao.get_all('event')
    result = []
    for evt in all_evts:
        if evt:
            result.append(evt)

    return result


# 3. gets all the event objects from firebase for the given artist_id
def get_artist_events(artist_id, dao):
    all_evts = get_all_events(dao)
    result = []
    for evt in all_evts:
        if int(evt['band_id']) == int(artist_id):
            result.append(evt)
    return result


# 4. does the same work than 3. with an artist object rather than only its id
def populate_artist_events(artist, dao):
    artist['events'] = get_artist_events(artist['id'], dao)
