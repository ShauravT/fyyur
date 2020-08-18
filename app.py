#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
import re
from operator import itemgetter
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))

    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))

    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete="CASCADE"), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete="CASCADE"), nullable=False)

  def __repr__(self):
    return f'<Show {self.id} {self.start_time} artist_id={artist_id} venue_id={venue_id}>'


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#----------------------------------------------------------------------------#
# Venues
#----------------------------------------------------------------------------#

# Create
# ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm()

  name = form.name.data.strip()
  city = form.city.data.strip()
  state = form.state.data.strip()
  address = form.address.data.strip()
  phone = form.phone.data
  image_link = form.image_link.data.strip()
  facebook_link = form.facebook_link.data.strip()
  website = form.website.data.strip()
  genres = form.genres.data
  seeking_talent = True if(form.seeking_talent =='Yes') else False
  seeking_description = form.seeking_description.data.strip()

  if not form.validate():
    flash(form.errors)
    return redirect(url_for('create_venue_submission'))
  else:
    error_in_insert = False

    # try insert form data into db
    try:
      new_venue = Venue(name=name, city=city, state=state, address=address, phone=phone, \
                seeking_talent=seeking_talent, seeking_description=seeking_description, image_link=image_link, \
                website=website, facebook_link=facebook_link, genres=genres)

      db.session.add(new_venue)
      db.session.commit()

    except Exception as e:
      error_in_insert = True
      print(f'Exception "{e}" in create_venue_submission()')

    finally:
      db.session.close()

    if not error_in_insert:
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')
    else:
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Venue ' + name +  ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      print("Error in create_venue_submission()")
      # internal server error
      abort(500)

# Read
# ----------------------------------------------------------------
@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.all()
  data = []
  city_states_set = set()
  for venue in venues:
    city_states_set.add((venue.city, venue.state))

  city_states_set = list(city_states_set)
  city_states_set.sort(key=itemgetter(1,0))

  current_datetime = datetime.now()
  for location in city_states_set:
    venue_list = []
    for venue in venues:
      if (venue.city == location[0]) and (venue.state == location[1]):
        venue_shows = Show.query.filter_by(venue_id=venue.id).all()
        num_upcoming_shows = 0
        for show in venue_shows:
          if show.start_time > current_datetime:
            num_upcoming_shows += 1

        venue_list.append({
          "id":venue.id,
          "name":venue.name,
          "num_upcoming_shows": num_upcoming_shows
        })

    data.append({
      "city": location[0],
      "state": location[1],
      "venues": venue_list
      })
  print(data)
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  # }]
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # search for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '').strip()
  search_word = '%' + search_term +'%'
  venues = Venue.query.filter(Venue.name.ilike(search_word)).all()
  venue_list = []
  current_datetime = datetime.now()
  for venue in venues:
    venue_show = Show.query.filter_by(venue_id=venue.id).all()
    num_upcoming_shows = 0
    for show in venue_show:
      if show.start_time > current_datetime:
        num_upcoming_shows += 1

    venue_list.append({
      "id":venue.id,
      "name":venue.name,
      "num_upcoming_shows":num_upcoming_shows
    })

  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  response = {
    "count": len(venues),
    "data": venue_list
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  print(venue)
  if not venue:
    return redirect(url_for('index'))
  else:
    genres = ((venue.genres.replace('{','')).replace('}','')).split(',')
    past_shows = []
    past_shows_count = 0
    upcoming_shows = []
    upcoming_shows_count = 0
    current_datetime = datetime.now()
    for show in venue.shows:
      if show.start_time < current_datetime:
        past_shows_count += 1
        past_shows.append({
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": format_datetime(str(show.start_time))
          })
      if show.start_time > current_datetime:
        upcoming_shows_count += 1
        upcoming_shows.append({
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": format_datetime(str(show.start_time))
          })
    data = {
      "id": venue_id,
      "name": venue.name,
      "genres": genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": (venue.phone),
      "image_link":venue.image_link,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "past_shows": past_shows,
      "past_shows_count": past_shows_count,
      "upcoming_shows": upcoming_shows,
      "upcoming_shows_count": upcoming_shows_count
      }
  # data={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  return render_template('pages/show_venue.html', venue=data)

# Update
# ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  if not venue:
    return redirect(url_for('index'))
  else:
    form = VenueForm(obj=venue)
    genres = ((venue.genres.replace('{','')).replace('}','')).split(',')
    venue={
    "id": venue_id,
    "name": venue.name,
    "genres": genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }
  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()

  name = form.name.data.strip()
  city = form.city.data.strip()
  state = form.state.data.strip()
  address = form.address.data.strip()
  city = form.city.data.strip()
  phone = form.phone.data
  genres = form.genres.data
  image_link = form.image_link.data.strip()
  facebook_link = form.facebook_link.data.strip()
  website = form.website.data.strip()
  seeking_talent = True if (form.seeking_talent.data == 'Yes') else False
  seeking_description = form.seeking_description.data.strip()

  if not form.validate():
    flash(form.errors)
    return redirect(url_for('edit_venue_submission',venue_id=venue_id))
  else:
    error_in_update = False

    try:
      venue = Venue.query.get(venue_id)
      venue.name = name
      venue.city = city
      venue.state = state
      venue.address = address
      venue.city = city
      venue.phone = phone
      venue.genres = genres
      venue.image_link = image_link
      venue.facebook_link = facebook_link
      venue.website = website
      venue.seeking_talent =seeking_talent
      venue.seeking_description = seeking_description

      db.session.commit()

    except Exception as e:
      error_in_update = True
      print(f'Exception "{e}" in edit_venue_submission()')
      db.session.rollback()

    finally:
      db.session.close()

    if not error_in_update:
      flash('Venue ' + request.form['name'] + ' was successfully updated')
      return redirect(url_for('show_venue', venue_id=venue_id))
    else:
      flash('An error occurred! Venue '+ name + 'could not be updated.')
      print("Error in edit_venue_submission()")
      abort(500)

# Delete
# ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/delete', methods=['GET', 'POST'])
def delete_venue(venue_id):

  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue = Venue.query.get(venue_id)
  if not venue:
    return redirect(url_for('venues'))
  else:
    error_on_delete = False
    venue_name = venue.name
    try:
      db.session.delete(venue)
      db.session.commit()
    except:
      error_on_delete = True
      db.session.rollback()
    finally:
      db.session.close()
    if not error_on_delete:
      flash(f'{venue_name} deleted successfully!')
      return redirect(url_for('venues'))
    else:
      flash(f'An error occurred deleting venue {venue_name}.')
      print("Error in delete_venue()")
      abort(500)

#----------------------------------------------------------------------------#
# Artists
#----------------------------------------------------------------------------#

# Create
# ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm()

  name = form.name.data.strip()
  city = form.city.data.strip()
  state = form.state.data.strip()
  phone = form.phone.data
  genres = form.genres.data
  image_link = form.image_link.data.strip()

  facebook_link = form.facebook_link.data.strip()
  website = form.website.data.strip()
  seeking_venue = True if (form.seeking_venue.data == 'Yes') else False
  seeking_description = form.seeking_description.data.strip()

  if not form.validate():
    flash(form.errors)
    return redirect(url_for('create_artist_submission'))
  else:
    error_in_insert = False

    # try insert form data into db
    try:
      new_artist = Artist(name=name, city=city, state=state, phone=phone, \
                seeking_venue=seeking_venue, seeking_description=seeking_description, image_link=image_link, \
                website=website, facebook_link=facebook_link, genres=genres)

      db.session.add(new_artist)
      db.session.commit()

    except Exception as e:
      error_in_insert = True
      print(f'Exception "{e}" in create_artist_submission()')
      db.session.rollback()

    finally:
      db.session.close()

    if not error_in_insert:
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')
    else:
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Artist ' + request.form['name'] +  ' could not be listed.')
      print("Error in create_artist_submission()")
      #internal server error
      abort(500)

# Read
# ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.order_by(Artist.name).all()

  data = []
  for artist in artists:
    data.append({
      "id":artist.id,
      "name":artist.name
    })
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '').strip()
  search_word = '%' + search_term +'%'
  artists = Artist.query.filter(Artist.name.ilike(search_word)).all()
  artist_list = []
  current_datetime = datetime.now()
  for artist in artists:
    artist_show = Show.query.filter_by(artist_id=artist.id).all()
    num_upcoming_shows = 0
    for show in artist_show:
      if show.start_time > current_datetime:
        num_upcoming_shows += 1

    artist_list.append({
      "id":artist.id,
      "name":artist.name,
      "num_upcoming_shows":num_upcoming_shows
    })
    response = {
    "count": len(artists),
    "data": artist_list
  }
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.get(artist_id)
  if not artist:
    return redirect(url_for('index'))
  else:
    genres = ((artist.genres.replace('{','')).replace('}','')).split(',')
    past_shows = []
    past_shows_count = 0
    upcoming_shows = []
    upcoming_shows_count = 0
    current_datetime = datetime.now()
    for show in artist.shows:
      if show.start_time < current_datetime:
        past_shows_count += 1
        past_shows.append({
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": format_datetime(str(show.start_time))
          })
      if show.start_time > current_datetime:
        upcoming_shows_count += 1
        upcoming_shows.append({
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": format_datetime(str(show.start_time))
          })
    data = {
      "id": artist_id,
      "name": artist.name,
      "genres": genres,
      "city": artist.city,
      "state": artist.state,
      "phone": (artist.phone),
      "image_link":artist.image_link,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "past_shows": past_shows,
      "past_shows_count": past_shows_count,
      "upcoming_shows": upcoming_shows,
      "upcoming_shows_count": upcoming_shows_count
      }

  # data={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  return render_template('pages/show_artist.html', artist=data)

# Update
# ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  artist = Artist.query.get(artist_id)
  if not artist:
    return redirect(url_for('index'))
  else:
    form = ArtistForm(obj=artist)
    genres = ((artist.genres.replace('{','')).replace('}','')).split(',')
    artist={
      "id": artist_id,
      "name": artist.name,
      "genres": genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_venue,
      "image_link": artist.image_link
    }
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm()

  name = form.name.data.strip()
  city = form.city.data.strip()
  state = form.state.data.strip()
  phone = form.phone.data
  genres = form.genres.data
  image_link = form.image_link.data.strip()
  facebook_link = form.facebook_link.data.strip()
  website = form.website.data.strip()
  seeking_venue = True if (form.seeking_venue.data == 'Yes') else False
  seeking_description = form.seeking_description.data.strip()

  if not form.validate():
    flash(form.errors)
    return redirect(url_for('edit_artist_submission',artist_id=artist_id))
  else:
    error_in_update = False

    try:
      artist = Artist.query.get(artist_id)
      artist.name = name
      artist.city = city
      artist.state = state
      artist.phone = phone
      artist.genres = genres
      artist.image_link = image_link
      artist.facebook_link = facebook_link
      artist.website = website
      artist.seeking_venue = seeking_venue
      artist.seeking_description = seeking_description

      db.session.commit()

    except Exception as e:
      error_in_update = True
      print(f'Exception "{e}" in edit_artist_submission()')
      db.session.rollback()

    finally:
      db.session.close()

    if not error_in_update:
      flash('Artist ' + request.form['name'] + 'was successfully updated!')
      return redirect(url_for('show_artist', artist_id=artist_id))
    else:
      flash('An error occurred! Artist '+ name + ' could not be updated.')
      print("Error in edit_artist_submission()")
      abort(500)

# Delete
# ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/delete', methods=['GET', 'POST'])
def delete_artist(venue_id):

  artist = Artist.query.get(venue_id)
  if not artist:
    return redirect(url_for('artists'))
  else:
    error_on_delete = False
    artist_name = artist.name
    try:
      db.session.delete(artist)
      db.session.commit()
    except:
      error_on_delete = True
      db.session.rollback()
    finally:
      db.session.close()
    if not error_on_delete:
      flash(f'{artist_name} deleted successfully!')
      return redirect(url_for('artist'))
    else:
      flash(f'An error occurred deleting venue {artist}.')
      print("Error in delete_artist()")
      abort(500)

#----------------------------------------------------------------------------#
# Shows
#----------------------------------------------------------------------------#

# Create
# ----------------------------------------------------------------
@app.route('/shows/create', methods=['GET'])
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  form.artist_id.choices =[(artist.id, artist.name) for artist in Artist.query.order_by(Artist.id).all()]
  form.venue_id.choices =[(venue.id, venue.name) for venue in Venue.query.order_by(Venue.id).all()]
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form =ShowForm()

  artist_id = form.artist_id.data.strip()
  venue_id = form.venue_id.data.strip()
  start_time = form.start_time.data

  error_in_insert = False

  try:
    new_show = Show(start_time=start_time, artist_id=artist_id, venue_id=venue_id)
    db.session.add(new_show)
    db.session.commit()

  except:
    error_in_insert = True
    print(f'Exception "{e}" in create_show_submission()')
    db.session.rollback()

  if not error_in_insert:
    # on successful db insert, flash success
    flash('Show was successfully listed!')
    return render_template('pages/home.html')
  else:
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
    print("Error in create_show_submission")
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

# Read
# ----------------------------------------------------------------
@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  shows = Show.query.all()

  for show in shows:
    data.append({
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": format_datetime(str(show.start_time))
    })
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=data)

#----------------------------------------------------------------------------#
# Error Handlers
#----------------------------------------------------------------------------#

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
