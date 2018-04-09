from flask import Flask, redirect, request, abort, render_template
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from dao import firebase_dao
from models.user import User
from services import account, city, genre, artist, event, venue
import json

# instantiate the firebaseDAO that will help talking with firebase
firebase_dao = firebase_dao.FirebaseDAO()
app = Flask(__name__)

# config
app.config.update(
    DEBUG=True,
    SECRET_KEY='secret_xxx'
)

# initialize the login manager from flask_login module and add it to the map
login_manager = LoginManager()
login_manager.init_app(app)
# set the page to be displayed as login.html
login_manager.login_view = "login"


# 4. method that allows to add the current user in the browser's session (this is used by flask login)
# see https://stackoverflow.com/questions/12075535/flask-login-cant-understand-how-it-works
@login_manager.user_loader
def load_user(user_id):
    user = account.get_account_by_id(user_id, firebase_dao)
    logged_user = User(user['id'], user['name'], user['password'], user['email'], user.get('genre'))
    if user.get('is_artist'):
        logged_user.is_artist = True
        logged_user.set_artist_id(user.get('artist_id'))
    return logged_user


# 1. Entry point of the application, the user entered the website
@app.route('/')
def index():
    # Takes the index.html page in order to translate it and send it to the user's browser
    return render_template("index.html")


@app.route('/createAccount', methods=["POST"])
def create_account():
    form = request.form
    user_dict = account.create_account(form, firebase_dao)
    user = User(user_dict['id'], user_dict['name'], user_dict['password'], user_dict['email'], user_dict.get('genre'))
    # using the support of flask_login in order to register the current user
    # who just created its account using the builtin login_user function
    login_user(user)
    return redirect(request.args.get("next"))


# 6. function that allows to create an artist page linked to the current logged user
@app.route('/createArtistAccount', methods=['GET', 'POST'])
@login_required
def create_artist_account():
    # as per login, POST means, the user submitted an html form, we need to validate the information
    # attempting to create the artist page for the user
    if request.method == 'POST':
        # sends the request to firebase to create the account, the full request is sent to be able to get
        # the <input type="file" />
        artistaccount = artist.create_artist_account(request, firebase_dao)
        # user just created an artist page, linking the newly created artist to the current logged user
        artist.link_user_to_artist(current_user, artistaccount, firebase_dao)
    else:
        # otherwise, display the html form to the user so he can enter his information and create his artist account
        if current_user:
            # checks if the user is not already an artist so he cannot create several artists accounts
            if not current_user.is_artist:
                # gets all the cities and genres in order to allow the user to choose which ones he wants
                cities = city.get_all_cities(firebase_dao)
                genres = genre.get_all_genres(firebase_dao)
                return render_template('artists_form.html', cities=cities, genres=genres)
    return redirect('/dashboard')


# 3. Login page. Handles both kind of requests GET and POST. If GET, the user access the page from the browser
# if POST, the user submitted the login form, the app validates the inputs from the form
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Gets all the genres in order to diplay them on the login page at the end
    genres = genre.get_all_genres(firebase_dao)
    # the user has submitted the login form, trying to login the user
    if request.method == 'POST':
        # request is the object representing all information coming from the user browser
        # getting the value inserted in the login form which has the name email and the name password
        # corresponds to the <input name="email" /> and <input name="password" />
        username = request.form['email']
        password = request.form['password']
        # tries to fetch a user from its email address in firebase
        user_account = account.get_account_by_email(username, firebase_dao)
        # if a user have been found (it is different to None)
        if user_account:
            # checks the values corresponding to the user found in firebase matches the value entered in the
            # form password
            if user_account['password'] == password:
                # if the passwords matches, creating a User object (custom made) that flask_login will use to keep
                # the user logged in the application until the user closes the application
                user = User(user_account.get('id'),
                            user_account.get('name'),
                            user_account.get('password'),
                            user_account.get('email'),
                            user_account.get('genre'))
                # calls the custom function load_user (4) to add it to the session
                login_user(user)
                # redirects the user to the parameter ?next=value (dashboard)
                return redirect(request.args.get("next"))
            else:
                # in the rest of the case, the user is redirected to the login page and an error message is shown
                return render_template("login.html", error="Wrong login/password", genres=genres)
        else:
            return render_template("login.html", error="Wrong login/password", genres=genres)
    else:
        return render_template("login.html", genres=genres)


# 5. logout the user, removes the current logged user from the session and redirect him to the index.html page
# https://github.com/shekhargulati/flask-login-example/blob/master/flask-login-example.py
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')


# 2. the user's dashboard access (account management etc..). The user needs to be logged in order to access
# See 3.
@app.route('/dashboard')
@login_required
def dashboard():
    artist_account = None
    if current_user.is_artist:
        artist_account = artist.get_artist(current_user.id_artist, firebase_dao)
        artist_account['city'] = city.get_city_for_id(artist_account['locality'], firebase_dao)
        artist_account['genres'] = genre.get_genre_for_list(artist_account['genre'], firebase_dao)
    genres = genre.get_all_genres(firebase_dao)
    return render_template("views/dashboard.html", artist_account=artist_account, genres=genres)


# 7. function that allows to add an event for the user's band
@app.route('/addEvent', methods=['POST', 'GET'])
@login_required
def add_event():
    # if the request comes from an html form, insert the event in firebase
    if request.method == 'POST':
        event.add_event(request.form, firebase_dao)
    else:
        # otherwise, gets all the venues from firebase and display the html form to the user
        venues = venue.get_all_venue(firebase_dao)
        return render_template('add_event.html', venues=venues)

    return redirect('/dashboard')


# function that is not used (see 8)
# @app.route('/recommendations', methods=['GET'])
# @login_required
# def recommendations():
#    return render_template('views/recommendations.html')


# 9. displays the google maps to the user
@app.route('/eventsAround', methods=['GET'])
@login_required
def events_around():
    return render_template('views/map.html')


# 10. function which gets all the events, venues and bands in order to display the venues markers and the events
@app.route('/getEvents', methods=['POST'])
@login_required
def get_events():
    all_events = event.get_all_events(firebase_dao)
    all_venue = venue.get_all_venue(firebase_dao)
    all_bands = artist.get_all_artist(firebase_dao)
    # the bands contains an array of integers, in order to show something more meaningful to the user
    # fetching all the genres that in the band's genre array and transform from id to actual band object
    for band in all_bands:
        genres = genre.get_genre_for_list(band['genre'], firebase_dao)
        band['genres'] = []
        for current_genre in genres:
            band['genres'].append(current_genre['name'])
    # uses dumps function from json module in order to transform a python dictionary into a json string
    return json.dumps({'venues': all_venue, 'events': all_events, 'artists': all_bands})


# 11. function that allows to display the information of an artist
# the <id_artist> is fetched from the frontend such as showArtist/1 will display the information of band -> id = 1
@app.route('/showArtist/<id_artist>')
@login_required
def show_artist(id_artist):
    # gets the artist having id = id_artist from firebase
    res = artist.get_artist(id_artist, firebase_dao)
    # gets the genre array from the artist that is coming from firebase
    artist_genre = genre.get_genre_for_list(res['genre'], firebase_dao)
    # gets all the artist gigs
    artist_events = event.get_artist_events(res['id'], firebase_dao)
    # the artist_event dictionary will only contains the band id, and the venue_id.
    # transforming the venue_id into venue name so the user can understand it
    venue.populate_venue_for_event(artist_events, firebase_dao)
    # retrieve all the artists that have the same genre that the user previously retrieved
    related = artist.get_artist_for_genre(res['id'], res['genre'], firebase_dao)
    # same as previous, for each related artist transform the list of genre from id to actual stirng values
    # that a user can understand
    for related_artist in related:
        related_artist['genres'] = []
        genres = genre.get_genre_for_list(related_artist['genre'], firebase_dao)
        for related_genre in genres:
            related_artist['genres'].append(related_genre['name'])
    # displays the artist_details page and sends all the variables needed to display the page (artist, genres..)
    # so it is possible to access them from the html page using jinja
    return render_template('views/artist_details.html',
                           artist=res,
                           genres=artist_genre,
                           events=artist_events,
                           related=related)


# 8. artist suggestions, shows a list of artist that are related to genres the current logged user likes
@app.route('/artistSuggest')
@login_required
def artist_suggest():
    # gets all the genres of the logged user from the current_user variable of flask_login module
    user_genre = current_user.genre
    # gets all the artist that have one of the genre the user likes
    artists = artist.get_all_artists_for_genre(user_genre, firebase_dao)

    # for each artists gets the events that are going to be played
    for current_artist in artists:
        # inserts the events inside the current_artist (if any)
        event.populate_artist_events(current_artist, firebase_dao)
        # after the events have been inserted into the current_artist dictionary
        # inserts the venues related to the events
        venue.populate_venue_for_event(current_artist['events'], firebase_dao)
        # transforms the genre ids contained inside the genre array into actual genres object that contains more info
        # that the user will see
        current_artist['genres'] = genre.get_genre_for_list(current_artist['genre'], firebase_dao)

    return render_template('views/recommendations.html', artists=artists)


# 12. update the list of genres of the user, so he can add and remove some genres as he needs
@app.route('/updateUserGenres', methods=['POST'])
@login_required
def update_user_genres():
    genre.update_user_genres(current_user.id, request.form, firebase_dao)
    return redirect('/dashboard')


if __name__ == '__main__':
    app.run()
