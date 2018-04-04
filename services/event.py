def add_event(form, dao):
    count = dao.get_table_count('event') + 1
    event = {
        'id': count,
        'venue_id': form['venue'],
        'band_id': form['band_id'],
        'date': form['date']
    }
    dao.update('event', count, event)


def get_all_events(dao):
    all_evts = dao.get_all('event')
    result = []
    for evt in all_evts:
        if evt:
            result.append(all_evts.get(evt))

    return result


def get_artist_events(artist_id, dao):
    all_evts = get_all_events(dao)
    result = []
    for evt in all_evts:
        if int(evt['band_id']) == int(artist_id):
            result.append(evt)
    return result


def populate_artist_events(artist, dao):
    artist['events'] = get_artist_events(artist['id'], dao)
