#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, jsonify, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db) 
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column("genres", db.ARRAY(db.String()), nullable=False)
    website_link = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres =db.Column("genres", db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
    start_time = db.Column(db.DateTime, nullable=False)
    
#db.create_all()
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
      # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  cities = Venue.query.with_entities(Venue.city, Venue.state).all()  # we fetch the cities
  for city, state in set(cities):
      info = {
          "city": city,
          "state": state,
          "venues": [{
              "id": venue.id,
              "name": venue.name,
              "num_upcoming_shows": len(Show.query.filter(Show.start_time > datetime.utcnow(), Show.venue_id==venue.id).all())
          } for venue in Venue.query.filter_by(city=city).all()
          ]
      }

      # adding info to data
      data.append(info)
  #printing data in console to see if its correct
  #print("The json data is "+ str(data), flush=True) 
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  if search_term == '':
    response = {
    "count": 0,
    "data": []
    }
  else:
    venues = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()
    response = {
        "count": len(venues),
        "data": [
            {
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": 0,
            } for venue in venues
        ]
    }
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  form = VenueForm()
  specificVenue=Venue.query.filter(Venue.id==venue_id).all()
  for venue in specificVenue:
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link
    }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  try:
    venue_input = Venue()
    venue_input.name = request.form['name']
    venue_input.city = request.form['city']
    venue_input.state = request.form['state']
    venue_input.address = request.form['address']
    venue_input.phone = request.form['phone']
    venue_input.genres = request.form.getlist('genres')
    venue_input.facebook_link = request.form['facebook_link']
    db.session.add(venue_input)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('venues'))
  except:
    flash('An error occurred. Venue ' +  request.form['name']+ ' could not be listed.')
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    #Delete the child elements then delete the venue
    db.session.query(Show).filter(Show.artist_id==venue_id).delete() 
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('The venue ' + venue.name + 'has beem deleted successfully.')
  except:
      db.session.rollback()
      print(sys.exc_info(),flush=True)
      flash('Venue was not deleted successfully.')
  finally:
      db.session.close()
  return redirect(url_for("index"))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  artistsList = Artist.query.all()
  for artist in artistsList:
    info = {
            "id": artist.id,
            "name": artist.name
    }
    data.append(info)
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form.get('search_term', '')
  if search_term == '':
    response = {
        "count": 0,
        "data": []
    }
  else:
    artists = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()
    response = {
        "count": len(artists),
        "data": [
            {
                "id": artist.id,
                "name": artist.name,
                "num_upcoming_shows": len(Show.query.filter(Show.start_time > datetime.utcnow(), Show.artist_id==artist.id).all()) ,
            } for artist in artists
        ]
    }
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first()
  shows = Show.query.join(Artist,Venue).filter(artist_id == Show.artist_id,Show.venue_id == Venue.id).all()
  upcoming_shows = []
  past_shows = []
  
  for show in shows:
    info = {
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'venue_image_link': show.venue.image_link,
      'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
    if show.start_time < datetime.now():
      past_shows.append(info)
    else:
      upcoming_shows.append(info)


  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  specificArtist=Artist.query.filter(Artist.id==artist_id).all()
  for item in specificArtist:
    artist = {
          "id":   item.id,
          "name": item.name,
          "genres": item.genres,
          "city": item.city,
          "state": item.state,
          "phone": item.phone,
          "website": item.website_link,
          "facebook_link": item.facebook_link,
          "seeking_venue": item.seeking_venue,
          "seeking_description": item.seeking_description,
          "image_link": item.image_link
      }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.website = request.form['website_link']
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.seeking_description = request.form['seeking_description']
    db.session.add(artist)
    db.session.commit()
    flash("Successfully Edited Artist Info")
  except:
    flash("Error Editing Artist info")
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
 
  form = VenueForm()
  specificVenue=Venue.query.filter(Venue.id==venue_id).all()
  for item in specificVenue:
    venue = {
          "id": item.id,
          "name": item.name,
          "genres": item.genres,
          "address": item.address,
          "city": item.city,
          "state": item.state,
          "phone": item.phone,
          "website": item.website_link,
          "facebook_link": item.facebook_link,
          "seeking_talent": item.seeking_talent,
          "seeking_description": item.seeking_description,
          "image_link": item.image_link
      }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  
  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form['facebook_link']
    db.session.add(venue)
    db.session.commit()
    flash("Successfully Edited Venue")
  except:
    print("Error occured while editing Venue",flush=True)
    flash("Error occured while editing Venue")
  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

  try:
    artist = Artist()
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.website_link = request.form['website_link']
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.seeking_description = request.form['seeking_description']
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('artists'))
  except:
    flash('An error occurred. Artist ' + request.form['name']+ ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.all()

  data = []
  for item in shows:
      data.append({
          'venue_id': item.venue.id,
          'venue_name': item.venue.name,
          'artist_id': item.artist.id,
          'artist_name': item.artist.name,
          'artist_image_link': item.artist.image_link,
          'start_time': item.start_time.isoformat()
      })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    show = Show()
    show.artist_id = request.form['artist_id']
    show.start_time = request.form['start_time']
    show.venue_id = request.form['venue_id']
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  # on successful db insert, flash success
  except:
    db.session.rollback()
    print(sys.exc_info(),flush=True)
    flash('An error occurred. Requested show could not be listed.')
    return redirect(url_for("create_shows"))
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
