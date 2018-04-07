def create_account(form, dao):
    accounts = dao.get_all('user')
    if accounts:
        for account in accounts:
            if account:
                if form['email'] == account['email']:
                    return False

    user_genre = []
    for genre in form.getlist('genre'):
        user_genre.append(genre)

    count = dao.get_table_count('user') + 1
    user = {'id': count,
            'email': form['email'],
            'name': form['fullname'],
            'password': form['password'],
            'genre': user_genre
            }
    dao.update('user', count, user)
    return user


def get_account_by_id(account_id, dao):
    return dao.get_id_from_table('user', account_id)


def get_account_by_email(email, dao):
    return dao.get_object_by_property('user', 'email', email)
