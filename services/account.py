# Contains all functions to deal with accounts


# 1.
# Creates a new user account
def create_account(form, dao):
    # fetches all the accounts and verify if there is not already one having the email someone entered in the ui
    accounts = dao.get_all('user')
    if accounts:
        for account in accounts:
            if account:
                if form['email'] == account['email']:
                    return False

    # extract the list of genre the user selected
    # using form.getlist as there are several input having name = 'genre'
    # https://stackoverflow.com/questions/32633051/get-multiple-values-from-one-html-input-through-python-flask
    user_genre = []
    for genre in form.getlist('genre'):
        user_genre.append(genre)

    # Creates a dictionary gathering all the data of the current user
    # set the id to table totalcount + 1
    count = dao.get_table_count('user') + 1
    user = {'id': count,
            'email': form['email'],
            'name': form['fullname'],
            'password': form['password'],
            'genre': user_genre
            }
    dao.update('user', count, user)
    return user


# 2.
# Calls DAO function #3 in order to get the user having the given account_id (used to get the logged user)
def get_account_by_id(account_id, dao):
    return dao.get_id_from_table('user', account_id)


# 3.
# Retrieves the account which have the given email
def get_account_by_email(email, dao):
    return dao.get_object_by_property('user', 'email', email)
