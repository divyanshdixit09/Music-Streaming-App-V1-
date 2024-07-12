from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
db = SQLAlchemy()
class User(db.Model,UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False, server_default='')
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(16))
    role=db.Column(db.String(12), default='user')
    playlist = db.relationship('Playlist', backref = 'user')
    blacklist = db.Column(db.Boolean(), default=False)

class Song(db.Model):
    __tablename__="songs"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50) , unique=True)
    artist = db.Column(db.String(30))
    genre = db.Column(db.String(30))
    text = db.Column(db.Text())
    rating = db.Column(db.Float())
    creator_id = db.Column(db.String(2) , nullable=False , default = '')
    nor = db.Column(db.Integer , default=0)
    flag = db.Column(db.Boolean(), default=False)
    

class Playlist(db.Model):
    __tablename__ = "playlists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"), nullable=False , default='')

    songs = db.relationship('Song', secondary='playlist_songs', backref='playlists')

playlist_songs = db.Table('playlist_songs',
    db.Column('playlist_id', db.String(36), db.ForeignKey('playlists.id'), primary_key=True),
    db.Column('song_id', db.String(36), db.ForeignKey('songs.id'), 
    primary_key=True))


class Album(db.Model):
    __tablename__ = "albums"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40),unique=True)
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"), nullable=False , default='')

    songs = db.relationship('Song', secondary='album_songs', backref='albums')

album_songs = db.Table('album_songs',
    db.Column('album_id', db.String(36), db.ForeignKey('albums.id'), primary_key=True),
    db.Column('song_id', db.String(36), db.ForeignKey('songs.id'), primary_key=True)
    )


    




    
    

    
