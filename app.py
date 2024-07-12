from flask import Flask , request , redirect , render_template ,flash , url_for 
from flask_login import login_user,logout_user,LoginManager,current_user,login_required
from models import *
from sqlalchemy import or_
from graph import *
#from models import *
app = Flask(__name__)
login_manager=LoginManager()


app.config['SECRET_KEY'] = "MY SECRET KEY"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///MusicData.sqlite3"

db.init_app(app)
app.app_context().push()
login_manager.init_app(app)
login_manager.login_view = '/'
@login_manager.user_loader

def load_user(id):
    return User.query.get(int(id))
#####################################################  LOGOUT  ###################################################################################
@app.route("/logout")
def logout():
    if current_user.role=="admin":
        logout_user()
        flash("Admin Logged out Successfully","success")
        return redirect("/adminlogin")
    else:
        logout_user()
        flash("Logged out successfully!","success")
        return redirect(url_for('login'))
    
   
################################################################## HOME  ###########################################################################
@app.route("/")
def home():
    return render_template("home.html")
#########################################################   REGISTER  #########################################################################################################################################################################################################
@app.route("/register",methods =["GET", "POST"])
def register():
    user=current_user
    if request.method == "GET" :
        return render_template("register.html")
    if request.method == "POST" :
        email=request.form["email"]
        password=request.form["password"]
        username=request.form["username"]
        exist1 = User.query.filter_by(username=username).first()
        exist2=User.query.filter_by(email=email).first()
        #print(f"Email: {email}, Password: {password}, Username: {username}")
        if len(password) <5:
                flash('Password should be at least 5 characters' , "danger")
                return redirect('/register')
        if exist1 is None and exist2 is None:
                    a = User(username=username, email=email, password=password)
                    db.session.add(a)
                    db.session.commit()
                    flash('You have been registered successfully! Please login to continue', 'success')
                    return redirect('/login')
        else:
            if exist1:
                flash("Username already exists! Please try another one.","danger")
                return redirect(url_for("register"))
            if exist2:
                flash("Email has already been used! Please try with different Email ID.","warning")
                return redirect(url_for("register"))
            

###################################################  LOGIN   #############################################################################################################################################################################################################    

@app.route("/login" ,  methods =["GET", "POST"])
def login():
    if request.method == "GET" :
        return render_template("login.html")
    if request.method == "POST" :
        password=request.form["password"]
        username=request.form["username"]
        User(username=username, password=password)
        user=db.session.query(User).filter(User.username==username, User.password==password ).first()
        if user==None:
           flash ("Invalid Credentials" , "danger")
           return redirect ('/login')
        else :
            if user.role=="admin":
                flash('Invalid credentials','danger')
                return redirect('/login')
            
            login_user(user)
            flash('Welcome','success')
            return redirect("/dashboard")
            
    
###############################################    ADMIN LOGIN    #########################################################################################################################################################################################################

@app.route("/adminlogin" , methods =["GET", "POST"])
def adminlogin():
    if request.method == "GET" :
        return render_template("adminlogin.html")
    if request.method=="POST":
        password=request.form["password"]
        username=request.form["adminname"]
        User( username=username , password=password)
        acc=db.session.query(User).filter(User.username==username, User.password==password , User.role=='admin' ).first()
        if acc==None:
            flash('Acess denied wrong credentials','danger')
            return redirect('/adminlogin')
        else :
            login_user(acc)
            pie_chart()
            bar_graph()
            flash('Admin Dashboard','success')
            return redirect("/dashboard")
        
################################################## DASHBOARD ##################################################################################

@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "user":
        song=Song.query.all()
        king=User.query.all()
        album=Album.query.all()
        user=current_user
        return render_template('user_dash.html',user=user,song=song,king=king , album=album)
    if current_user.role=="creator":
        flash('Welcome Creator' , 'success')
        album=Album.query.all()
        king=User.query.all()
        user= current_user
        song=Song.query.all()
        return render_template('creator_dash.html',user=user , song=song,king=king,album=album)
    if current_user.role == "admin":
        user=current_user
        u = User.query.filter_by(role="user").all()
        user_count = len(u)
        c= User.query.filter_by(role="creator").all()
        creator_count = len(c)
        a= Song.query.all()
        song_count = len(a)
        al= Album.query.all()
        album_count =len(al)
        ##====================top 3 songs==============######
        top_song = Song.query.order_by(Song.rating.desc()).limit(3).all()
        
        return render_template('admin_dash.html',user=user , user_count=user_count,creator_count=creator_count,top_song=top_song,song_count=song_count,album_count=album_count)
################################################# creator ##################################################################################################
@app.route("/creator/<int:id>")
@login_required
def creator(id):
    album=Album.query.all()
    king=User.query.all()
    user=current_user
    user.role = 'creator'
    db.session.commit()
    flash("successfully registered as creator","success")
    return redirect("/dashboard")

#########################################     SONGS   #########################################################################################################################################################################    

@app.route("/song", methods = ["GET","POST"])
@login_required
def song():
    user= current_user
    if user.role == 'user' :
        song = Song.query.all()
        return render_template("song.html", song=song , user=user)
    elif user.role =='creator':
        song = Song.query.all()
        return render_template("creator_song.html", song=song ,user=user, user_id=current_user.id)
    

#============================== PLAY ==========================================================================================================
@app.route("/play")
@login_required
def play():
    return render_template("play.html")

#############################################  UPLOAD SONGS ################################################################################################
@app.route("/upload_song", methods=['GET', 'POST'])
@login_required
def upload_song():
    songs = Song.query.all()
    user = current_user

    if request.method == "GET":
        return render_template('upload_song.html' , user=user)

    if request.method == "POST":
        title = request.form["title"]
        artist = request.form["artist"]
        genre = request.form["genre"]
        text = request.form["text"]

        for song in songs:
            if song.title == title:
                flash("This song is already uploaded", "danger")
                return redirect('/upload_song')

        # If the loop completes without finding a matching title, add the new song
        s = Song(title=title, artist=artist, genre=genre, text=text, rating=0.0, creator_id=user.id)
        db.session.add(s)
        db.session.commit()
        flash("Song added successfully","success")
        return redirect("/dashboard")

    
############################################# Delete SONG  ###########################################################################################
@app.route("/delete_song/<int:id>")
@login_required
def delete_song(id):
    song = Song.query.filter_by(id=id).first()
    db.session.delete(song)
    db.session.commit()
    flash("Successfully delete the song!","success")
    if current_user.role == "admin":
        return redirect("/management")
    return redirect('/song')

###########################################       Lyrics           ############################################################################################

@app.route("/lyrics/<int:id>", methods = ["GET","POST"] )
@login_required
def lyrics(id):
    c= Song.query.get(id)
    song = Song.query.all()
    return render_template("song_lyrics.html",c=c, song=song , user=current_user )

################################################## edit song  ################################################################################################
@app.route("/edit_song/<int:id>" , methods = ["GET","POST"])
@login_required
def edit_song(id):
    user=current_user
    c= Song.query.get(id)
    if request.method=='GET':
        return render_template("edit_song.html" ,user=user, c=c)
    if request.method=='POST':
        c.title=request.form["title"]
        c.text=request.form["text"]
        db.session.commit()
        return redirect("/dashboard")

##############################################  RATING   #############################################################################################

@app.route("/rating/<int:id>", methods=["POST"])
@login_required
def rating(id):
    if request.method=="POST":  
        song = Song.query.get(id) 
        new_rating = round(float(request.form['rating']), 1)
    if song.rating == 0.0 :
                song.rating = new_rating
                song.nor = song.nor + 1
                db.session.commit()
                return redirect("/dashboard")
    else: 
                song.rating = round(((song.rating*song.nor) + new_rating) /(song.nor+1) , 1)
                song.nor = song.nor+1
                db.session.commit()
                return redirect("/dashboard")


########################################### PLaylist ###################################################################################################
@app.route("/playlist", methods = ["GET","POST"])
@login_required
def playlist():
    user = current_user
    playlist = Playlist.query.all()
    return render_template("playlist.html", playlist=playlist,user=user)

####################################### Playlist Song ###########################################################################################
@app.route("/playlist_song/<int:id>")
@login_required
def playlist_song(id):
    song=Song.query.all()
    p=Playlist.query.filter_by(id=id).first()
    return render_template("playlist_song.html",song=song,p=p,user=current_user)



################################################# Add playlist #######################################################################################
@app.route("/add_playlist/<int:user_id>" , methods = ["GET","POST"])
@login_required
def add_playlist(user_id):
    user = current_user
    if request.method == "GET":
        return render_template("add_playlist.html",user=user)
    if request.method == "POST":
        name = request.form['playlist']
        playlist = Playlist.query.filter_by(user_id=user.id).all()
        if playlist :
            for p in playlist :
                if name == p.name :
                    flash ("This playlist already exists! Please enter a different one.", 'danger')
                    return redirect("/playlist")
                else:
                    c = Playlist(name=name,user_id=current_user.id)
                    db.session.add(c)
                    db.session.commit()
                    flash("playlist added successfully!" , 'success')
                    return redirect("/playlist")
        else:
            c = Playlist(name=name,user_id=user_id)
            db.session.add(c)
            db.session.commit()
            flash("playlist added successfully!", 'success')
            return redirect("/playlist") 

#################################### ADD SONG TO PLAYLIST ##################################################################################

@app.route("/add_song_playlist/<int:user_id>/<int:playlist_id>", methods=["GET", "POST"])
@login_required
def add_song_playlist(user_id, playlist_id):
    if request.method == "GET":
        user = current_user
        p = Playlist.query.get(playlist_id)
        song = Song.query.all()
        return render_template("add_song_playlist.html", song=song, user=user, p=p)

    if request.method == "POST":
        song_id = request.form.get("song_id")
        playlist = Playlist.query.get(playlist_id)
        song = Song.query.get(song_id)

        # Check if the song is not already in the playlist
        if song not in playlist.songs:
            # Associate the song with the playlist
            playlist.songs.append(song)
            db.session.commit()

            flash("Song has been added to the playlist.", 'success')
            return redirect(url_for('playlist', user_id=user_id, playlist_id=playlist_id))
        else:
            flash("Song is already in the playlist." , 'danger')
            return redirect(url_for('playlist', user_id=user_id, playlist_id=playlist_id))

    # Add a default return statement to handle unexpected cases
    return "Invalid request"

########################################## REMOVE SONG PLAYLIST ################################################################################


@app.route('/remove_song/<int:id>', methods=["GET", "POST"])
@login_required
def remove_song(id):
    p = Song.query.get(id)
    playlist = Playlist.query.filter(Playlist.songs.contains(p)).first()

    if playlist:
        playlist.songs.remove(p)
        db.session.commit()
        flash("Song removed from playlist" , 'success')
    else:
        flash("Error: Playlist not found" , 'danger')

    return redirect("/playlist")


    
############################################ DELETE PLAYLIST #############################################################################################
@app.route("/delete_playlist/<int:playlist_id>" , methods=["GET","POST"])
@login_required
def delete_playlist(playlist_id):
    if request.method=="GET":
        pl=Playlist.query.filter_by(id=playlist_id).first()
        db.session.delete(pl)
        db.session.commit()
        flash("Deleted Successfully" , 'success')
        return  redirect('/playlist' )

################################################## ALBUM  ###############################################################################################
@app.route("/album")
@login_required
def album():
    user= current_user
    album=Album.query.all()
    return render_template("album.html",album=album,user=user)
############################################### Add ALBUM ####################################################################################

@app.route("/add_album" , methods = ["GET","POST"])
@login_required
def add_album():
    album = Album.query.all()
    user = current_user
    if request.method == "GET":
        return render_template("add_album.html",user=user)
    if request.method == "POST":
        name = request.form['album']
        a = Album.query.filter_by(name=name).first()
        if a is None :
            n = Album(name=name,user_id = current_user.id)
            db.session.add(n)
            db.session.commit()
            flash('Added Succesfully','success')
            return redirect('/album')
        else:
            flash('This album already exists!','warning')
            return redirect("/add_album")

#################################################### ALBUM SONGS ########################################################################################
@app.route("/album_song/<int:id>")
@login_required
def album_song(id):
    song = Song.query.all()
    a = Album.query.filter_by(id=id).first()
    return render_template("album_song.html", song=song, a=a,user=current_user)

####===================================ALBUM DETAILS==================================================================================#
@app.route('/album_details/<int:id>')
@login_required
def album_details(id):
    song = Song.query.all()
    a = Album.query.filter_by(id=id).first()
    return render_template("album_details.html", song=song, a=a,user=current_user)


################################################## Add Song Album ########################################################################################

@app.route("/add_song_album/<int:user_id>/<int:album_id>", methods=["GET", "POST"])
@login_required
def add_song_album(user_id, album_id):
    if request.method == "GET":
        user = current_user
        a = Album.query.get(album_id)
        song = Song.query.all()
        return render_template("add_song_album.html", song=song, user=user, a=a)

    if request.method == "POST":
        song_id = request.form.get("song_id")
        album = Album.query.get(album_id)
        song = Song.query.get(song_id)

        # Check if the song is not already in the album
        if song not in album.songs:
            # Associate the song with the album
            album.songs.append(song)
            db.session.commit()

            flash("Song has been added to the album.","success")
            return redirect(url_for('album', user_id=user_id, album_id=album_id))
        else:
            flash("Song is already in the album.","warning")
            return redirect(url_for('album', user_id=user_id, album_id=album_id))
        
################################################# REMOVE SONG ALBUM ##############################################################################
@app.route('/remove_song_album/<int:id>', methods=["GET", "POST"])
@login_required
def remove_song_album(id):
    p = Song.query.get(id)
    album = Album.query.filter(Album.songs.contains(p)).first()

    if album:
        album.songs.remove(p)
        db.session.commit()
        flash("Song removed from album","success")
    else:
        flash("Error: album not found", "danger")

    return redirect("/album")


################################################## DELETE ALBUM  #######################################################################################

@app.route("/delete_album/<int:id>" , methods=["GET","POST"])
@login_required
def delete_album(id):
        album = Album.query.filter_by(id=id).first()
        db.session.delete(album)
        db.session.commit()
        flash("Deleted Successfully","success")
        return redirect('/album')


#============================================ SEARCH ================================================================================================================#

@app.route("/search" , methods=["GET" , "POST"])
@login_required
def search():
    query = request.form['query']
    query = f"%{query}%"
    
    results = Song.query.filter( or_(
                    Song.title.contains(query),
                    Song.artist.contains(query),
                    Song.genre.contains(query)
                )).all()
    song=Song.query.all()
    king=User.query.all()
    album=Album.query.all()
    user=current_user
    if user.role == "user":
        return render_template('user_dash.html',user=user,song=song,king=king , album=album,results=results)
    if user.role == "creator":
          return render_template('creator_dash.html',user=user , song=song,king=king,album=album,results=results)
    if user.role == "admin":
        user=User.query.all()
        return render_template("admin_manage.html" , song=song , user=user,results=results)
#====================================== ADMIN ========================================================================================================#

@app.route("/management" , methods = ["GET" , "POST"])

def management():
    user=User.query.all()
    song=Song.query.all()
    return render_template("admin_manage.html",song=song,user=user)
#================================== FLAG SONG =====================================================================================================
@app.route('/flag_song/<int:song_id>', methods=['POST'])
def flag_song(song_id):
    action = request.form.get('flagsong')
    song = Song.query.get(song_id)
    if song:
        if action == 'flag':
            song.flag = True
        else:
            song.flag = False 
        db.session.commit()
    return redirect("/management")
#============================== BLACKLISTING CREATOR ====================================================================================================
@app.route('/blacklist/<int:id>', methods=["POST"])
def blacklist(id):
    user = User.query.get(id)
    action = request.form.get('blacklist')
    if user :
        if action == 'blacklist':
            user.blacklist = True
        else:
            user.blacklist = False
        db.session.commit()
    return redirect("/management")

if __name__=="__main__":
    app.run( )