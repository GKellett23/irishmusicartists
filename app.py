from flask import Flask, redirect, request, abort, render_template
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from dao import firebase_dao
from models.user import User
from services import account, city, genre, artist, event, venue
import json

firebase_dao = firebase_dao.FirebaseDAO()
app = Flask(__name__)

# config
app.config.update(
    DEBUG=True,
    SECRET_KEY='secret_xxx'
)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    user = account.get_account_by_id(user_id, firebase_dao)
    logged_user = User(user['id'], user['name'], user['password'], user['email'], user.get('genre'))
    if user.get('is_artist'):
        logged_user.is_artist = True
        logged_user.set_artist_id(user.get('artist_id'))
    return logged_user


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/createAccount', methods=["POST"])
def create_account():
    form = request.form
    user_dict = account.create_account(form, firebase_dao)
    user = User(user_dict['id'], user_dict['name'], user_dict['password'], user_dict['email'], user_dict.get('genre'))
    login_user(user)
    return redirect(request.args.get("next"))


@app.route('/createArtistAccount', methods=['GET', 'POST'])
@login_required
def create_artist_account():
    if request.method == 'POST':
        artistaccount = artist.create_artist_account(request, firebase_dao)
        artist.link_user_to_artist(current_user, artistaccount, firebase_dao)
    else:
        if current_user:
            if not current_user.is_artist:
                cities = city.get_all_cities(firebase_dao)
                genres = genre.get_all_genres(firebase_dao)
                return render_template('artists_form.html', cities=cities, genres=genres)
    return redirect('/dashboard')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']
        user_account = account.get_account_by_email(username, firebase_dao)
        if user_account:
            if user_account['password'] == password:
                user = User(user_account.get('id'),
                            user_account.get('name'),
                            user_account.get('password'),
                            user_account.get('email'),
                            user_account.get('genre'))
                login_user(user)
                return redirect(request.args.get("next"))
            else:
                return render_template("login.html", error="Wrong login/password")
        else:
            return abort(401)
    else:
        genres = genre.get_all_genres(firebase_dao)
        return render_template("login.html", genres=genres)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')


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


@app.route('/addEvent', methods=['POST', 'GET'])
@login_required
def add_event():
    if request.method == 'POST':
        event.add_event(request.form, firebase_dao)
    else:
        venues = venue.get_all_venue(firebase_dao)
        return render_template('add_event.html', venues=venues)

    return redirect('/dashboard')


@app.route('/recommendations', methods=['GET'])
@login_required
def recommendations():
    return render_template('views/recommendations.html')


@app.route('/eventsAround', methods=['GET'])
@login_required
def events_around():
    return render_template('views/map.html')


@app.route('/getEvents', methods=['POST'])
@login_required
def get_events():
    all_events = event.get_all_events(firebase_dao)
    all_venue = venue.get_all_venue(firebase_dao)
    all_bands = artist.get_all_artist(firebase_dao)
    return json.dumps({'venues': all_venue, 'events': all_events, 'artists': all_bands})


@app.route('/showArtist/<id_artist>')
@login_required
def show_artist(id_artist):
    res = artist.get_artist(id_artist, firebase_dao)
    artist_genre = genre.get_genre_for_list(res['genre'], firebase_dao)
    artist_events = event.get_artist_events(res['id'], firebase_dao)
    venue.populate_venue_for_event(artist_events, firebase_dao)
    related = artist.get_artist_for_genre(res['id'], res['genre'], firebase_dao)
    return render_template('views/artist_details.html',
                           artist=res,
                           genres=artist_genre,
                           events=artist_events,
                           related=related)


@app.route('/artistSuggest')
@login_required
def artist_suggest():
    user_genre = current_user.genre
    artists = artist.get_all_artists_for_genre(user_genre, firebase_dao)

    for current_artist in artists:
        event.populate_artist_events(current_artist, firebase_dao)
        venue.populate_venue_for_event(current_artist['events'], firebase_dao)
        current_artist['genres'] = genre.get_genre_for_list(current_artist['genre'], firebase_dao)

    return render_template('views/recommendations.html', artists=artists)


@app.route('/updateUserGenres', methods=['POST'])
@login_required
def update_user_genres():
    genre.update_user_genres(current_user.id, request.form, firebase_dao)
    return redirect('/dashboard')


if __name__ == '__main__':
    app.run()
