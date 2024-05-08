SLIDE Uitlizzo FLask 

Scritto con Flask, micro-framework Web scritto in Python, basato sullo strumento Werkzeug WSGI e con il motore di template Jinja2

pezzo di codice interattivo (da definire) per spiegare oralmente il funzionamento di flask 

server = Flask(__name__)

# set del timeout della sessione 
server.permanent_session_lifetime = timedelta(minutes=20)

#   imposto una chiave segreta per l'invio di cookie crittati da Flask al browser
server.secret_key = credentials.chiave_segreta
 
# gestione del sito web tramite route 
@server.route('/')
def home():
    if session.get('logged_in'):
        return render_template("home.html")
    else:
        return render_template('login.html')  

if __name__ == "__main__":
    # avvio dell'applicaizone web
    server.run(host='0.0.0.0',debug=False, port=80)

---------------------------------------------------------------------------------------------

SLIDE creazione nuovo utente  (cartelle e dati di sessione)


pezzo di codice interattivo (da definire) per spiegare oralmente la creaizone delle cartelle dell'utente

import os

# funzione per creare la cartella dedicata al nuovo utente al momento della registrazione 
def creaCartella(IDUtente):
    try:
        IDUtente_str = str(IDUtente) # traformo il codice dell'utente in una stringa
        current = os.getcwd() # recupero la directory di lavoro dove creerò la cartella dedicata al nuovo utente 
        os.makedirs(os.path.join(current, "utenti", IDUtente_str, "media"))  # cartella per i media in generale (post/storie)
        os.makedirs(os.path.join(current, "utenti", IDUtente_str, "ImmagineProfilo")) # cartella per l'immagine profilo dell'utente
    except Exception as e:
        print(e)
    


---------------------------------------------------------------------------------------------

SLIDE tendenze

calcolo delle tendenze con diversi pesi

Inserire pezzo codice  (da aggiornare non è questo il definitivo) interattivo della query di calcol odel trending:
@server.route('/trending/', methods=['GET'])
def trending():
    if session['logged_in'] == True:
        if request.method == 'GET':
            # Query per ottenere i post con più interazioni (postati negli ultimi 30 giorni) (aggiugnere gestione errori)
            query = """
                    SELECT Post.*, 
                        COUNT(MiPiace.IDPostDestinazione) AS NumMiPiace, 
                        COUNT(Commento.IDPostDestinazione) AS NumCommenti
                    FROM Post
                    LEFT JOIN MiPiace ON Post.IDPost = MiPiace.IDPostDestinazione
                    LEFT JOIN Commento ON Post.IDPost = Commento.IDPostDestinazione
                    WHERE Post.Data >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                    GROUP BY Post.IDPost
                    ORDER BY (COUNT(MiPiace.IDPostDestinazione) + COUNT(Commento.IDPostDestinazione) * 1.5) DESC
            """

( a voce spiegare il peso diverso commenti-like)

---------------------------------------------------------------------------------------------



