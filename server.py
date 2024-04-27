from flask import Flask, request, render_template, url_for, redirect, session   # usato per flask
from datetime import timedelta                                                  # usato nel tempo per la sessione
import credentials                                                              # usato per importare credenziali utili
server = Flask(__name__)


#   con questo comando noi impostiamo la modalità del server in modalità
#   di debug avendo quindi il vantaggio che non servirà ricaricare le varie
#   pagine del browser per visualizzare i cambiamenti nel codice
server.config["DEBUG"] = True

#   con questo comando impostiamo la durata di ogni sessione per 5 minuti
#   (al termine di quest'ultimi la sessione verrà chiusa automaticamente)
server.permanent_session_lifetime = timedelta(minutes=5)

#   valore ripreso da un file esterno
#   imposto una chiave segreta per l'invio di cookie crittati da Flask al browser
server.secret_key = credentials.chiave_segreta


# ---------- sezione delle route -----------

@server.route('/')
def home():
    return render_template("about_storygram.html", title = "About storygram")

# si accettano solo i metodi HTTP GET e POST
@server.route('/login/', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        return "<h1> login fatto </h1>"

# per registrare un utente
@server.route('/singup/', methods=["GET", "POST"])
def singup():
    if request.method == "GET":
        return render_template("singup.html")
    if request.method == "POST":
        return "<h1> singup fatto </h1>"

# per effettuare il logout
@server.route('/logout/', methods=["POST"])
def logout():
    return "<h1> logout fatto </h1>"

# per visualizzare il profilo dell'utente
@server.route('/profile/my/')
def profile():
    return "<h1> profile </h1>"

# per visualizzare il profilo di un utente
@server.route('/profile/<username>/')
def profile_username(username):
    return f"<h1> profile {username} </h1>"

# per visualizzare un post 
@server.route('/post/<int:id>/')
def post_id(id):
    return f"<h1> post {id} </h1>"

# per visualizzare i commenti di un post
@server.route('/post/<int:id>/comment/')
def post_id_comment(id):
    return f"<h1> post {id} comment </h1>"

# per visualizzare o mettere un  like di un post
@server.route('/post/<int:id>/like/')
def post_id_like(id):
    return f"<h1> post {id} like </h1>"

# per unlike di un post
@server.route('/post/<int:id>/unlike/')
def post_id_unlike(id):
    return f"<h1> post {id} unlike </h1>"

# per  mettere like ad un commento
@server.route('/post/<int:id>/comment/<int:comment_id>/like/')
def post_id_comment_id_like(id, comment_id):
    return f"<h1> post {id} comment {comment_id} like </h1>"

# per unlike di un commento
@server.route('/post/<int:id>/comment/<int:comment_id>/unlike/')
def post_id_comment_id_unlike(id, comment_id):
    return f"<h1> post {id} comment {comment_id} unlike </h1>"

# per eelimianre un commento
@server.route('/post/<int:id>/comment/<int:comment_id>/delete/')
def post_id_comment_id_delete(id, comment_id):
    return f"<h1> post {id} comment {comment_id} delete </h1>"

# per creare un post
@server.route('/post/create/')
def post_create():
    return "<h1> post create </h1>"

# menu impostazioni
@server.route('/settings/')
def settings():
    return "<h1> settings </h1>"


#  -------- sezione di avvio server --------

if __name__ == "__main__":
    # avviamo l'applicazione in modalità debug
    server.run(debug=True)
