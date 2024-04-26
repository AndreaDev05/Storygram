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



#  -------- sezione di avvio server --------

if __name__ == "__main__":
    # avviamo l'applicazione in modalità debug
    server.run(debug=True)