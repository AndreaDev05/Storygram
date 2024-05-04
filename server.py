
# problema route setting: nella query se viene modificata la privacy il db da sempre errore di dato troppo lungo
# problema dell'attributo nel db????

from flask import Flask, jsonify, request, render_template, url_for, redirect, session   # usato per flask
from datetime import timedelta # usato per impostare la durata di una sessione
import credentials # usato per importare credenziali utili
import hashlib # usato per la conversione della password in hash mediante l'algoritmo sha-256
from scriptCartelleUtenti  import creaCartella # usato per la conversione della password in hash mediante l'algoritmo sha-256
from db_control import executeQuery, is_following # usato per la comunicazione con il db

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

#route di home storygram !!!!
@server.route('/')
def home():
    return render_template("about_storygram.html", title = "About storygram") # !!  pagina poi da definire !!

# ------------- route per il login ---------------------- #
@server.route('/login/', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html") # !! nome pagina poi da definire !!
    if request.method == "POST":
        # Recupera i dati inviati dal form
        codiceUtente = request.form['codiceUtente']
        password = request.form['password']

        # converto la passowrd inserita in hash 
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        #print(password_hash)

        # Esegui la query per verificare se l'utente esiste (aggiugnere gestione errori)
        query = f"SELECT * FROM Utente WHERE CodiceUtente = {codiceUtente} AND Password = '{password_hash}' LIMIT 1"
        risp = executeQuery(query)

        # Se l'utente esiste e la password è corretta, la sessione viene avviata
        if risp:
            session['logged_in'] = True
            session['codiceUtente'] = risp[0]['CodiceUtente']

            return jsonify({"message": "Utente Loggato con successo"}), 200
        else:                                                           
            return jsonify({"message": "Utente o Password errata"}), 404  # Se l'utente non esiste o la password è errata

    else:
        return jsonify({"message": "Metodo non consentito"}), 405 # in caso di metodo non consentito do errore
        
# ---------------- route per la registrazione ---------------------- #
@server.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('registration.html')  # Redirect alla pagina di registrazione
    elif request.method == 'POST':
        # Recupera i dati inviati dal form
        codice_utente = request.form['CodiceUtente']
        password = request.form['Password']
        periodo_storico = request.form['PeriodoStorico']
        codice_di_recupero = request.form['CodiceDiRecupero']

        # Codifica la password in codice hash
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Esegui la query SQL per inserire l'utente nel database (aggiungi gestione errori)
        query = f"INSERT INTO Utente (CodiceUtente, Password, PeriodoStorico, CodiceDiRecupero) VALUES ({codice_utente}, '{password_hash}', '{periodo_storico}', {codice_di_recupero})"
        res = executeQuery(query)
        
        # Se l'utente è gia registrato do errore
        if res==-1:
            return jsonify({"message": "Utente già registrato"}), 409
        else:
            # creo la cartella dove memorizzare i vari futuri media del nuovo utente
            creaCartella(codice_utente)
            return jsonify({"message": "Utente registrato con successo"}), 200  # !!  pagina poi da definire !!
        
    else:
        return jsonify({"message": "Metodo non consentito"}), 405 # in caso di metodo non consentito do errore 
    
# ---------------- route per effettuare il logout ---------------------- #
@server.route('/logout/', methods=["POST"])
def logout():
    if session['logged_in'] == True:
        if request.method == "POST":
            # elimino i dati di sessione 
            session.clear()
            # reindirizzo alla pagina principale
            return jsonify({"message": "logout effettuato"}), 200 # !!  pagina poi da definire !!
        else:
            return jsonify({"message": "Metodo non consentito"}), 405
    else:
        return jsonify({"message": "Utente non loggato"}), 401

# ---------------- route per la creazione di un nuovo post ---------------------- #
@server.route('/post/create/', methods=['GET', 'POST'])
def create_post():
    if session['logged_in'] == True:
        if request.method == 'POST':
            # prendo i dati del form
            descrizione = request.form['descrizione']
            percorso_file = request.form['percorso_file']

            # inserisco le informazioni del nuovo post nel db
            query = f"INSERT INTO Post (Descrizione, Data, PercorsoFile, IDProfiloProvenienza) VALUES ('{descrizione}', NOW(), '{percorso_file}', {session['codiceUtente']})"
            executeQuery(query)

            # aggiorno l'applicaizone e rindirizzo alla pagina principale 
            return jsonify({"message": "post creato con successo"}), 200 # !!  pagina poi da definire !!
        
        elif request.method == 'GET':
            # carico la pagina per la creazione di un nuovo post 
            return jsonify({"message": "pagina creaizone post"}), 200 # !!  pagina poi da definire !!
        else:
            return jsonify({"message": "Metodo non consentito"}), 405
    else:
        return jsonify({"message": "Utente non loggato"}), 401


# ---------------- route per la visualizzare un profilo ---------------------- #
@server.route('/profile/<int:id>/', methods=['GET'])
def profile(id):
    if session.get('logged_in') == True:
        if request.method == 'GET':
            # Verifica se l'utente corrente è il proprietario del profilo o lo sta seguendo
            is_owner_or_following = session['codiceUtente'] == id or is_following(session['codiceUtente'], id)
            
            # Query per recuperare informazioni sul profilo dell'utente
            profile_query = f"""
                                SELECT 
                                    IDProfilo, 
                                    Seguaci, 
                                    Seguiti, 
                                    NumeroDiPost, 
                                    Privacy
                                FROM 
                                    Profilo
                                WHERE 
                                    IDProfilo = {id};
                            """
            profile_info = executeQuery(profile_query)
            
            # Controlla se il profilo è privato
            is_private = profile_info[0]['Privacy'] == 1 

            # Se il profilo è privato e l'utente non è il proprietario né lo sta seguendo, restituisci solo un messaggio di profilo privato
            if is_private and not is_owner_or_following:
                return jsonify({"message": "Profilo privato"}), 200
            
            # Recupera i post solo se il profilo è pubblico o se l'utente è il proprietario o lo sta seguendo
            if not is_private or is_owner_or_following:
                posts_query = f"""
                    SELECT * FROM Post
                    WHERE IDProfiloProvenienza = {id}
                """
                user_posts = executeQuery(posts_query)

                # Restituisci le informazioni sul profilo e i post
                return jsonify({
                    "profile_info": profile_info,
                    "user_posts": user_posts
                }), 200
            
            return jsonify({"message": "Profilo privato"}), 200

        return jsonify({"message": "Metodo non consentito"}), 405
    else:
        return jsonify({"message": "Utente non loggato"}), 401

    
# ---------------- route per modificare il profilo e le varie impsotazioni ---------------------- #
@server.route('/settings/', methods=['GET', 'POST'])
def settings():
    if session['logged_in'] == True:
        if request.method == 'GET':
            # carico la pagina per la modifica delle impostazioni del profilo
            return jsonify({"message": "pagina impostazioni"}), 200 # !!  pagina poi da definire !!
        elif request.method == 'POST':
            # Prende i dati dal form
            pathImmagineProfilo = request.form.get('pathImmagineProfilo')
            descrizione = request.form.get('descrizione')
            privacy = request.form.get('privacy')

            # Query per aggiornare le informazioni sul profilo dell'utente
            query = f"UPDATE Profilo SET PathImmagineProfilo = '{pathImmagineProfilo}', Descrizione = '{descrizione}', Privacy = '{privacy}' WHERE IDProfilo = {session['codiceUtente']};"
            
            # Esegui l'aggiornamento nel database
            executeQuery(query)
            return jsonify({"message": "Impostazioni aggiornate"}), 200 # !!  pagina poi da definire !!

        else:
            return jsonify({"message": "Metodo non consentito"}), 405
    else:
        return jsonify({"message": "Utente non loggato"}), 401

# per visualizzare i post in tendenza delgi ultimi 30 giorni (da dfinire ul limite di post per la sezione)
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
                ORDER BY (COUNT(MiPiace.IDPostDestinazione) + COUNT(Commento.IDPostDestinazione)) DESC
            """
            trending_posts = executeQuery(query) 

            # !! nome pagina poi da definire !!
            return jsonify({"message": "pagina trending"},trending_posts), 200 # !!  pagina poi da definire !!
        else:
            return jsonify({"message": "Metodo non consentito"}), 405
    else:
        return jsonify({"message": "Utente non loggato"}), 401
    
# ---------------- route per visualizzare i commenti di un post o aggiungere un commento al post ---------------------- #
@server.route('/post/comments/', methods=['GET', 'POST'])
def post_comment():
    if session['logged_in'] == True:
        if request.method == 'GET':

            # Recupero l'id del post relativo al commento (da implementare)
            post_id = -1 # debug

            query = f"SELECT * FROM Commento WHERE IDPost = '{post_id}'" # recupero i commenti del post relativo all'id
            comments = executeQuery(query, fetchall=True)

            return render_template('comments.html', comments=comments) # redirect alla pagina dei commenti

        elif request.method == 'POST':
            # Recupera i dati inviati dal form
            Commento = request.form.get('Commento')
            
            # Recupero l'id del post relativo al commento (da implementare)
            post_id = -1 # debug 

            # inserisco i dati del commento nel database
            query = f"INSERT INTO Commento (Commento, Data, IDProfiloProvenienza, IDPostDestinazione) VALUES ('{Commento}', NOW(), {session['codiceUtente']}, {post_id})"
            executeQuery(query)

            return jsonify({"message": "Commento inserito"}), 200 # !!  pagina poi da definire !!
            
        else:
            return jsonify({"message": "Metodo non consentito"}), 405
    else:
        return jsonify({"message": "Utente non loggato"}), 401
    
# ---------------- route per gestione messaggi ---------------------- #
@server.route('/messages/', methods=['GET', 'POST'])
def messages():
    if session['logged_in'] == True:
        if request.method == 'GET':

            # Recupero l'id del profilo con cui è la chat (da implementare)
            id_amico = -1 # debug

            # Query per ottenere i messaggi ricevuti dal profilo loggato
            query = f"SELECT * FROM Messaggio WHERE (IDProfiloDestinatario = {session['codiceUtente']} AND  IDProfiloMittente ={id_amico}) OR (IDProfiloDestinatario = {id_amico} AND IDProfiloMittente = {session['codiceUtente']}) ORDER BY Data DESC"
            messages_received = executeQuery(query, fetchall=True)
        elif request.method == 'POST':

            # Recupera i dati inviati dal form
            Messaggio = request.form.get('Messaggio')

            # Recupero l'id del profilo con cui è la chat (da implementare)
            id_amico = -1 # debug

            # inserisco i dati del messaggio nel database
            query = f"INSERT INTO Messaggio (Messaggio, Data, IDProfiloMittente, IDProfiloDestinatario) VALUES ('{Messaggio}', NOW(), {session['codiceUtente']}, {id_amico})"
            executeQuery(query)

            return jsonify({"message": "Messaggio inserito"}), 200 # !!  pagina poi da definire !!
        else:
            return jsonify({"message": "Metodo non consentito"}), 405
    else:
            return jsonify({"message": "Utente non loggato"}), 401

if __name__ == "__main__":

    # avviamo l'applicazione in modalità debug
    server.run(host='0.0.0.0',debug=True, port=11125)

