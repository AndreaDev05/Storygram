from flask import Flask, jsonify, request, render_template, redirect, session   # usato per flask
from datetime import timedelta # usato per impostare la durata di una sessione
import static.credentials as credentials # usato per importare credenziali utili
import hashlib # usato per la conversione della password in hash mediante l'algoritmo sha-256
from scriptCartelleUtenti  import creaCartella # usato per la conversione della password in hash mediante l'algoritmo sha-256
from scriptUpload import uploadImmagineProfilo, uploadImmaginePost # usato per uplodare nel server le immaigni profilo degli utenti 
from db_control import executeQuery, is_following # usato per la comunicazione con il db
import json # usato per manipolare i json (esempio last codice utente)
from random import randint
from datetime import datetime

server = Flask(__name__)

#   con questo comando noi impostiamo la modalità del server in modalità
#   di debug avendo quindi il vantaggio che non servirà ricaricare le varie
#   pagine del browser per visualizzare i cambiamenti nel codice
server.config["DEBUG"] = True

#   con questo comando impostiamo la durata di ogni sessione per 5 minuti
#   (al termine di quest'ultimi la sessione verrà chiusa automaticamente)
server.permanent_session_lifetime = timedelta(weeks=1)

#   valore ripreso da un file esterno
#   imposto una chiave segreta per l'invio di cookie crittati da Flask al browser
server.secret_key = credentials.chiave_segreta
 
# ---------- sezione delle route -----------

@server.route('/')
def home():
    if session.get('logged_in'):

        # query per calcolare i psot in tendenza 
        query_trending = f'''
SELECT Post.*, 
    Profilo.*,
    COUNT(MiPiace.IDPostDestinazione) AS NumMiPiace, 
    COUNT(Commento.IDPostDestinazione) AS NumCommenti
FROM Post
LEFT JOIN MiPiace ON Post.IDPost = MiPiace.IDPostDestinazione
LEFT JOIN Commento ON Post.IDPost = Commento.IDPostDestinazione
INNER JOIN Profilo ON Post.IDProfiloProvenienza = Profilo.IDProfilo
LEFT JOIN Segue ON Profilo.IDProfilo = Segue.Seguito AND Segue.Seguace = {session['IDUtente']}
WHERE (Post.Data >= DATE_SUB(CURDATE(), INTERVAL 30 DAY))
    AND (Profilo.Privacy = 0)
    AND (Post.IDProfiloProvenienza NOT IN (SELECT Seguito FROM Segue WHERE Seguace = {session['IDUtente']})
        AND Post.IDProfiloProvenienza != {session['IDUtente']})
GROUP BY Post.IDPost
ORDER BY (COUNT(MiPiace.IDPostDestinazione) + COUNT(Commento.IDPostDestinazione) * 1.5) DESC
LIMIT 50;

                        '''
        
        # ottengo  dal db i post che sono in tendenza 
        post_trending = executeQuery(query_trending)

        # query per ottenere i post della home dell'utente 
        query_seguiti = f'''
                        SELECT Post.*, Profilo.*
                        FROM Post
                        JOIN Profilo ON Post.IDProfiloProvenienza = Profilo.IDProfilo
                        LEFT JOIN Segue ON Post.IDProfiloProvenienza = Segue.Seguito
                        WHERE Profilo.IDProfilo = {session['IDUtente']} OR Segue.Seguace = {session['IDUtente']}
                        ORDER BY Post.Data DESC;
                        '''
        # query da tenere come debug per vedere anche i psot dei profili che non seguiamo 
        # post_seguiti  = executeQuery("SELECT * FROM Post JOIN Profilo ON (Post.IDProfiloProvenienza = Profilo.IDProfilo) ORDER BY Data DESC")
        
        # ottengo dal db i post degli utenti che l'utente segue 
        post_seguiti  = executeQuery(query_seguiti)

        # Combina i post seguiti e i post in tendenza in una lista alternata
        combined_posts = []
        seguiti_index = 0
        trending_index = 0
        while seguiti_index < len(post_seguiti) and trending_index < len(post_trending):
            for _ in range(3):  # Aggiungi 3 post seguiti
                if seguiti_index < len(post_seguiti):
                    combined_posts.append(post_seguiti[seguiti_index])
                    seguiti_index += 1
            if trending_index < len(post_trending): # Aggiungi 1 post in tendenza
                combined_posts.append(post_trending[trending_index])
                trending_index += 1

        # Aggiungi eventuali post seguiti e in tendenza rimanenti
        combined_posts.extend(post_seguiti[seguiti_index:])
        combined_posts.extend(post_trending[trending_index:])

        # carico la home con i relativi dati 
        return render_template("home.html", ID=session['IDUtente'], lista_post=combined_posts, names=["paolo", "bellofigo", "nano sporcaccione"], paths=["", "", ""], seen_s=[False, False, False])
    else:
        return render_template('login.html')  


# ------------- route per il login ---------------------- #
@server.route('/login/', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if session.get('logged_in'):
            return redirect("https://storygram.it", code=302)
        else:
            return render_template('login.html')
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
            session['IDUtente'] = risp[0]['IDUtente']

            return redirect("https://storygram.it", code=302)
        else:                                                           
            return render_template("login.html")

    else:
        return jsonify({"message": "Metodo non consentito"}), 405 # in caso di metodo non consentito do errore

# ---------------- route per la registrazione ---------------------- #
@server.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        if session.get('logged_in'):
            return redirect("https://storygram.it", code=302)
        else:
            UltimoCodiceUtente = None
            with open("permanent_data/UltimoCodiceUtente.json", "r") as file:
                diz = json.load(file)
                UltimoCodiceUtente = diz["UltimoCodiceUtente"] + 1
                file.close()
            return render_template('registrazione.html',codice=UltimoCodiceUtente)  # Redirect alla pagina di registrazione
    elif request.method == 'POST':
        # Recupera i dati inviati dal form
        nome = request.form['Nome']
        cognome = request.form['Cognome']
        password = request.form['Password']
        periodo_storico = request.form['PeriodoStorico']
        codice_di_recupero = request.form['CodiceDiRecupero']
        codice_utente = request.form['codiceUtente']    #DA INSERIRE NEL DATABASE

        # Codifica la password in codice hash e il relativo codice di recupero
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        codice_di_recupero_hash = hashlib.sha256(codice_di_recupero.encode()).hexdigest()

        # calcolo il codice utente
        # apro il file e leggo il codice, incremento di 1 e lo riscrivo nel file
        UltimoCodiceUtente = None
        with open("permanent_data/UltimoCodiceUtente.json", "r") as file:
            diz = json.load(file)
            UltimoCodiceUtente = diz["UltimoCodiceUtente"] + 1
            file.close()
        with open("permanent_data/UltimoCodiceUtente.json", "w") as file:
            file.write( json.dumps({"UltimoCodiceUtente" : UltimoCodiceUtente}, indent=4) )
            file.close()

        # Esegui la query SQL per inserire l'utente nel database (aggiungi gestione errori)
        try:
            executeQuery("START TRANSACTION") # essendo che devo fare più query atomiche uso le transazioni
            query = f"INSERT INTO Utente (CodiceUtente, Password, PeriodoStorico, CodiceDiRecupero) VALUES ('{UltimoCodiceUtente}', '{password_hash}', '{periodo_storico}', '{codice_di_recupero_hash}')"
            executeQuery(query)
            ris = executeQuery(f"SELECT IDUtente FROM Utente WHERE CodiceUtente = '{UltimoCodiceUtente}'")
            query = f"INSERT INTO Profilo (IDProfilo, Nome, Cognome) VALUES ('{ris[0]['IDUtente']}', '{nome}', '{cognome}')"
            executeQuery(query)
            executeQuery("COMMIT")

            # creo la cartella dove memorizzare i vari futuri media del nuovo utente
            creaCartella(ris[0]['IDUtente'])
            return redirect("http://storygram.it/login/", code=302)
        except:
            #executeQuery("ROLLBACK") # serve anche se da errore o il dbms fa il rollback in automatico ??????
            return jsonify({"message": "Errore interno al server. Riprovare più tardi"}), 500

# --------------- route il consentire il recupero della passowrd ---------------------- #
@server.route('/recovery/', methods=['GET', 'POST'])
def recovery():
    if request.method == 'GET':
            return render_template('recupero.html')
    elif request.method == 'POST':
        # Recupera i dati inviati dal form
        codice_utente = request.form['CodiceUtente']
        codice_di_recupero = request.form['CodiceDiRecupero']

        # codifico in hash il codice di recupero e lo ocnfronto con quello alvato nel db
        codice_di_recupero_hash = hashlib.sha256(codice_di_recupero.encode()).hexdigest()
        query = f"SELECT * FROM Utente WHERE CodiceUtente = {codice_utente} AND CodiceDiRecupero = '{codice_di_recupero_hash}' LIMIT 1"
        risp = executeQuery(query)

        # Se l'utente esiste e il codice di recupero è corretto permetto il reset della passowrd e avvio una sessione per permettere il cambio passowrd
        if risp:
            session['CodiceUtente'] = risp[0]['CodiceUtente']
            return redirect("/recovery/reset/", code=302)
        else:
            return jsonify({"message": "Codice utente o codice di recupero non corretti"}), 400

# --------------- route per il cambio della password vero e proprio ---------------------- #
@server.route('/recovery/reset/', methods=['GET', 'POST'])
def recovery_reset():
    if session['CodiceUtente']:
        if request.method == 'GET':
            return render_template('reset_password.html')
        elif request.method == 'POST':
            # Recupera i dati inviati dal form
            nuova_password = request.form['NuovaPassword']
            nuova_password_conferma = request.form['NuovaPasswordConferma']

            # controllo se le due password sono uguali 
            if nuova_password == nuova_password_conferma:
                # codifico la nuova passowrd in hash
                nuova_password_hash = hashlib.sha256(nuova_password.encode()).hexdigest()
                # eseguo la query per resettare la passowrd
                query = f"UPDATE Utente SET Password = '{nuova_password_hash}' WHERE CodiceUtente = '{session['CodiceUtente']}'"
                executeQuery(query)
                # elimino la sessione
                session.clear()
                # reindirizzo alla pagina di login
                return redirect("/login/", code=302)
            else:
                return jsonify({"message": "Le due password non coincidono"}), 400
        else:
                return redirect("metodo non consentito", code=405)
    else:
        return redirect("http://storygram.it/login/", code=302)
        
# ---------------- route per effettuare il logout ---------------------- #
@server.route('/logout/', methods=["GET"])
def logout():
    if session.get('logged_in') == True:
        if request.method == "GET":
            # elimino i dati di sessione 
            session.clear()
            # reindirizzo alla pagina principale
            return redirect("http://storygram.it/login/", code=302)
    else:
        return redirect("http://storygram.it/login/", code=302)


# ---------------- route per la visualizzare un profilo ---------------------- #
def _renderProfile(id : int, profile_info : list, is_owner : bool, is_following : bool):
    posts_query = f"SELECT * FROM Post WHERE IDProfiloProvenienza = {id} ORDER BY Data DESC"
    user_posts = executeQuery(posts_query)

    return render_template('profile.html', ID=id, session_userid=session['IDUtente'] , is_owner=is_owner, is_following=is_following, nomeUtente=profile_info[0]['Nome'] + " " + profile_info[0]['Cognome'], descrizione=profile_info[0]['Descrizione'], numeroDiPost=profile_info[0]['NumeroDiPost'], pathImmagineProfilo=profile_info[0]['PathImmagineProfilo'], seguaci=profile_info[0]['Seguaci'], seguiti=profile_info[0]['Seguiti'], privacy=profile_info[0]['Privacy'], posts=[user_posts])    


@server.route('/profile/<int:id>/', methods=['GET'])
def profile(id):
    if session.get('logged_in') == True:

        # Query per recuperare informazioni sul profilo dell'utente
        profile_query = f"SELECT * FROM Profilo WHERE IDProfilo = {id};"
        profile_info = executeQuery(profile_query)

        posts_query = f"SELECT * FROM Post WHERE IDProfiloProvenienza = {id} ORDER BY Data DESC"
        user_posts = executeQuery(posts_query)
        
        is_owner = True if(id == session['IDUtente']) else False
        is_private = True if(profile_info[0]['Privacy'] == 1) else False

        if is_owner:
            return _renderProfile(id, profile_info, is_owner, True)
        else:
            if is_private:
                
                following_query = executeQuery(f"SELECT * FROM Segue WHERE Seguace = {session['IDUtente']}")
                for riga in following_query:
                    if riga['Seguito'] == id:
                        return _renderProfile(id, profile_info, is_owner, is_following=True)
                return jsonify({"message" : "profilo privato"}) # METTERE BOTTONE PER RICHIESTA DI SEGUIRE IL PROFILO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            else: # profilo pubblico
                is_following = False
                following_query = executeQuery(f"SELECT * FROM Segue WHERE Seguace = {session['IDUtente']}")
                for riga in following_query:
                    if riga['Seguito'] == id:
                        is_following = True
                return _renderProfile(id, profile_info, is_owner, is_following)

    else:
        return redirect("http://storygram.it/login/", code=302)

# ---------------- route per la modifica del profilo ---------------------- #
@server.route('/profile/<int:id>/modify', methods=['GET', 'POST'])
def modifica_profilo(id):
    if session.get('logged_in') == True:
        if request.method == "GET":

            profile_info = executeQuery(f"SELECT * FROM Profilo JOIN Utente ON (IDutente = IDProfilo) WHERE IDProfilo = {id}")[0] # metto posizione 0 perche "id" è chiave primaria quindi sono sicuro di avere un solo record
            is_owner = True if(id == session["IDUtente"]) else False
            
            if is_owner:
                print(profile_info['PathImmagineProfilo'])
                return render_template("profile_modifica.html", ID=id, nome=profile_info['Nome'], cognome=profile_info['Cognome'], descrizione=profile_info['Descrizione'], pathImmagineProfilo=profile_info['PathImmagineProfilo'], privacy=profile_info['Privacy'], periodoStorico=profile_info['PeriodoStorico'])
            else:
                return jsonify({"message": "Forbidden"}), 403  # da definire poi !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        else:
            
            if request.form['Privacy'] == "on":
                Privacy = 1
            else:
                Privacy = 0

            file = request.files['file']
            if file.filename == '':
                try:
                    executeQuery("START TRANSACTION")
                    executeQuery(f"UPDATE Profilo SET Nome = '{request.form['Nome']}', Cognome = '{request.form['Cognome']}', Descrizione = '{request.form['Descrizione']}', Privacy = '{Privacy}' WHERE IDProfilo = '{id}'")
                    executeQuery(f"UPDATE Utente SET PeriodoStorico = '{request.form['PStorico']}' WHERE IDUtente = '{id}'")
                    executeQuery("COMMIT")
                except:
                    executeQuery("ROLLBACK")
            else:
                newpath = uploadImmagineProfilo(file,server,session)
                try:
                    executeQuery("START TRANSACTION")
                    executeQuery(f"UPDATE Profilo SET Nome = '{request.form['Nome']}', Cognome = '{request.form['Cognome']}', PathImmagineProfilo = '/{newpath}', Descrizione = '{request.form['Descrizione']}', Privacy = '{Privacy}' WHERE IDProfilo = '{id}'")
                    executeQuery(f"UPDATE Utente SET PeriodoStorico = '{request.form['PStorico']}' WHERE IDUtente = '{id}'")
                    executeQuery("COMMIT")
                except:
                    executeQuery("ROLLBACK")
            
            return redirect(f"http://storygram.it/profile/{id}", code=302)
      
            # mi aspetto dei dati da inserire nel db aggiornando i parametri del profilo
    else:
        return redirect("http://storygram.it/login/", code=302)

# ---------------- route per la visualizzare i follower di un profilo ---------------------- #
@server.route('/profile/<int:id>/followers/', methods=['GET'])
def followers(id):
    if session.get('logged_in') == True:
        
        # Recupera i follower del profilo
        query = f"""
                SELECT Profilo.*
                FROM Profilo
                INNER JOIN Segue ON Profilo.IDProfilo = Segue.Seguace
                WHERE Segue.Seguito = {id};
        """
        followers_info = executeQuery(query)
        return render_template('followers.html', followers=followers_info)
        
    else:
        return redirect("http://storygram.it/login/", code=302)

# ---------------- route per la visualizzare i seguiti di un profilo ---------------------- #
@server.route('/profile/<int:id>/following/', methods=['GET'])
def following(id):
    if session.get('logged_in') == True:
        if request.method == 'GET':
            # Recupera i seguiti del profilo
            query = f"""
                    SELECT Profilo.*
                    FROM Profilo
                    INNER JOIN Segue ON Profilo.IDProfilo = Segue.Seguito
                    WHERE Segue.Seguace = {id};
            """
            following_info = executeQuery(query)
            return jsonify({"message": "Seguiti trovati"}), 405  # !!  pagina poi da definire !!
        return jsonify({"message": "Metodo non consentito"}), 405
    else:
        return redirect("http://storygram.it/login/", code=302)


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
                    ORDER BY (COUNT(MiPiace.IDPostDestinazione) + COUNT(Commento.IDPostDestinazione) * 1.5) DESC
            """
            trending_posts = executeQuery(query) 

            # !! nome pagina poi da definire !!
            return jsonify({"message": "pagina trending"},trending_posts), 200 # !!  pagina poi da definire !!
        else:
            return jsonify({"message": "Metodo non consentito"}), 405
    else:
        return redirect("http://storygram.it/login/", code=302)

# ---------------- route per ricercare un utente ---------------------- #
@server.route('/search/', methods=['GET', 'POST'])
def search():
    if session['logged_in'] == True:
        if request.method == "GET":
            return render_template("cerca_utente.html", cerca=False, ID=session['IDUtente'])
        else:
            search_text = request.form['input_cerca_utente']
            profili = executeQuery("SELECT * FROM Utente JOIN Profilo ON IDUtente = IDProfilo WHERE Cognome LIKE '%{search_text}%' OR Nome LIKE '%{search_text}%' OR PeriodoStorico LIKE '%{search_text}%'")
            print("Profili trovati:\n")
            print(profili)
            return render_template("cerca_utente.html", cerca=True, ID=session['IDUtente'], profili_trovati=profili)
    else:
        return redirect("http://storygram.it/login/", code=302)
    
# ---------------- route per la creazione di un nuovo post ---------------------- #
@server.route('/post/create/', methods=['GET', 'POST'])
def create_post():
    if session.get('logged_in') == True:
        if request.method == 'POST':
            # prendo i dati del form
            descrizione = request.form['Descrizione']
            file = request.files['file_post']
            newpath = uploadImmaginePost(file,server,session)

            data_ora = datetime.now()
            data_ora = f"{data_ora.year}-{data_ora.month}-{data_ora.day} {data_ora.hour}:{data_ora.minute}:{data_ora.second}"

            # inserisco le informazioni del nuovo post nel db
            try:
                executeQuery("START TRANSACTION")
                query = f"INSERT INTO Post (Descrizione, Data, PercorsoFile, IDProfiloProvenienza) VALUES ('{descrizione}', '{data_ora}', '/{newpath}', {session['IDUtente']})"
                executeQuery(query)
                n_post = executeQuery(f"SELECT NumeroDiPost FROM Profilo WHERE IDProfilo = {session['IDUtente']}")[0]['NumeroDiPost']
                executeQuery(f"UPDATE Profilo SET NumeroDiPost = {n_post + 1}")
                executeQuery("COMMIT")
            except:
                executeQuery("ROLLBACK")
            finally:
                # aggiorno l'applicaizone e rindirizzo alla pagina principale 
                return redirect("http://storygram.it/", code=302)
        
        elif request.method == 'GET':
            # carico la pagina per la creazione di un nuovo post 
            return render_template("post_create.html", ID=session["IDUtente"])
        else:
            return jsonify({"message": "Metodo non consentito"}), 405
    else:
        return redirect("http://storygram.it/login/", code=302)
    
# ---------------- route per visualizzare i commenti di un post o aggiungere un commento al post ---------------------- #
@server.route('/post/<int:post_id>/comments/', methods=['GET', 'POST'])
def post_comment(post_id):
    if session['logged_in'] == True:
        if request.method == 'GET':

            # Recupero l'id del post relativo al commento (da implementare)
            post_id = -1 # debug

            query = f"SELECT * FROM Commento WHERE IDPost = '{post_id}'" # recupero i commenti del post relativo all'id
            comments = executeQuery(query)

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
        return redirect("http://storygram.it/login/", code=302)

# ---------------- route per visualizzare i like di un post o agigugnerne uno o toglierlo ---------------------- #
@server.route('/post/like/', methods=['GET', 'POST'])
def post_like():
    if session['logged_in'] == True:
        if request.method == 'GET':
            # Recupero l'id del post relativo al like 
            post_id = -1 # debug

            # Query per ottenere i like del post
            query = f"SELECT * FROM MiPiace WHERE IDPost = '{post_id}'"
            likes = executeQuery(query)

            return render_template('likes.html', likes=likes) # redirect alla pagina dei like (da definire)
        elif request.method == 'POST':
            # Recupera i dati inviati dal form
            like = request.form.get('like')
            post_id = request.form.get('post_id')
            id_provenienza = session['IDUtente']
            
            # a secoda se è un like o un un-like eseguo la giusta query
            if like == True:
                query = f"INSERT INTO MiPiace (Data, IDProfiloProvenienza, IDPostDestinazione) VALUES (NOW(), {id_provenienza}, {post_id})"
                executeQuery(query)
            elif like == False:
                query = f"DELETE FROM MiPiace WHERE IDProfiloProvenienza = {id_provenienza} AND IDPostDestinazione = {post_id}"
                executeQuery(query)

        else:
            return jsonify({"message": "Metodo non consentito"}), 405 # !!  pagina poi da definire !!
    else:
            return redirect("http://storygram.it/login/", code=302)
  
# ---------------- route per gestione messaggi ---------------------- #
@server.route('/messages/', methods=['GET', 'POST'])
def messages():
    return render_template("message_page_desktop.html", ID=1234)
    if session['logged_in'] == True:
        if request.method == 'GET':

            # Recupero l'id del profilo con cui è la chat (da implementare)
            id_amico = -1 # debug

            # Query per ottenere i messaggi ricevuti dal profilo loggato
            query = f"SELECT * FROM Messaggio WHERE (IDProfiloDestinatario = {session['codiceUtente']} AND  IDProfiloMittente ={id_amico}) OR (IDProfiloDestinatario = {id_amico} AND IDProfiloMittente = {session['codiceUtente']}) ORDER BY Data DESC"
            messages_received = executeQuery(query)
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
            return redirect("http://storygram.it/login/", code=302)

# ---------------- route per gestione delle storie ---------------------- #
@server.route('/story/<int:id>', methods=['GET', 'POST'])
def story():
    if(session.get("logged_in")):
        if request.method == 'GET':
            # Recupero i dati della storia (se non sono passate 24 ore)
            query= f'''
                    SELECT * FROM Storia
                    WHERE IDStoria = {id}
                    AND Data >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            '''
            story = executeQuery(query)
            return render_template("story.html", story=story) # !!  pagina poi da definire !!
        else:
            return jsonify({"message": "Metodo non consentito"}), 405
    else:
        return redirect("http://storygram.it/login/", code=302)

# ---------------- route per gestione del bottone per seguire ---------------------- #
@server.route('/segui/<int:id_profilo_da_seguire>', methods=['GET', 'POST'])
def segui(id_profilo_da_seguire):
    if(session.get("logged_in")):
        try:
            executeQuery("START TRANSACTION")
            executeQuery(f"INSERT INTO Segue (Seguace, Seguito) VALUES ('{session['IDUtente']}', '{id_profilo_da_seguire}')")
            seguiti = executeQuery(f"SELECT Seguiti FROM Profilo WHERE IDProfilo = '{session['IDUtente']}'")[0]['Seguiti']
            seguaci = executeQuery(f"SELECT Seguaci FROM Profilo WHERE IDProfilo = '{id_profilo_da_seguire}'")[0]['Seguaci']
            executeQuery(f"UPDATE Profilo SET Seguiti = {seguiti + 1} WHERE IDProfilo = '{session['IDUtente']}'")
            executeQuery(f"UPDATE Profilo SET Seguaci = {seguaci + 1} WHERE IDProfilo = '{id_profilo_da_seguire}'")
            executeQuery("COMMIT")
        except:
            executeQuery('ROLLBACK')
        finally:
            return redirect(f"http://storygram.it/profile/{id_profilo_da_seguire}", code=302)
    else:
        return redirect("http://storygram.it/login/", code=302)

@server.route('/stop_segui/<int:id_profilo_da_stop_seguire>', methods=['GET', 'POST'])
def stop_segui(id_profilo_da_stop_seguire):
    if(session.get("logged_in")):
        try:
            executeQuery("START TRANSACTION")
            executeQuery(f"DELETE FROM Segue WHERE Seguace = '{session['IDUtente']}' AND Seguito = '{id_profilo_da_stop_seguire}'")
            seguiti = executeQuery(f"SELECT Seguiti FROM Profilo WHERE IDProfilo = '{session['IDUtente']}'")[0]['Seguiti']
            seguaci = executeQuery(f"SELECT Seguaci FROM Profilo WHERE IDProfilo = '{id_profilo_da_stop_seguire}'")[0]['Seguaci']
            executeQuery(f"UPDATE Profilo SET Seguiti = {seguiti - 1} WHERE IDProfilo = '{session['IDUtente']}'")
            executeQuery(f"UPDATE Profilo SET Seguaci = {seguaci - 1} WHERE IDProfilo = '{id_profilo_da_stop_seguire}'")
            executeQuery("COMMIT")
        except:
            executeQuery('ROLLBACK')
        finally:
            return redirect(f"http://storygram.it/profile/{id_profilo_da_stop_seguire}", code=302)
    else:
        return redirect("http://storygram.it/login/", code=302)

if __name__ == "__main__":

    # avviamo l'applicazione in modalità debug
    server.run(host='0.0.0.0',debug=True, port=80)