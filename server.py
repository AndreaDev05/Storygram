from flask import Flask, jsonify, request, render_template, url_for, redirect, session   # usato per flask
from datetime import timedelta                                                  # usato nel tempo per la sessione
import credentials                                                              # usato per importare credenziali utili
import pymysql.cursors

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

# --------------------------------------------------
# funzione per eseguire una query su database
def executeQuery(query):
    connection = pymysql.connect(credentials.host,
                                credentials.user,
                                credentials.password,
                                credentials.database,
                                cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                res = cursor.fetchall()
                return res
    finally:
        connection.close()
# --------------------------------------------------


# ---------- sezione delle route -----------

@server.route('/')
def home():
    return render_template("about_storygram.html", title = "About storygram") # !! nome pagina poi da definire !!

# si accettano solo i metodi HTTP GET e POST
@server.route('/login/', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html") # !! nome pagina poi da definire !!
    if request.method == "POST":
        return "<h1> login fatto </h1>"

# Funzione per la registrazione dell'utente
@server.route('/register/', methods=['GET', 'POST'])
def register_user():
    if request.method == 'GET':
        return render_template('registration_form.html') # redirect alla pagina di registrazione
    elif request.method == 'POST':
        # Recupera i dati inviati dal form
        data = request.json
        codice_utente = data.get('codice_utente')
        password = data.get('password')
        periodo_storico = data.get('periodo_storico')
        codice_di_recupero = data.get('codice_di_recupero')

        # Esegui la query SQL per inserire l'utente nel database
        query = f"INSERT INTO Utente (CodiceUtente, Password, PeriodoStorico, CodiceDiRecupero) VALUES ('{codice_utente}', '{password}', '{periodo_storico}', '{codice_di_recupero}')"
        executeQuery(query)

        return jsonify({"message": "Utente registrato con successo"}), 200
    else:
        return jsonify({"message": "Metodo non consentito"}), 405
    
# per effettuare il logout
@server.route('/logout/', methods=["POST"])
def logout():
    return "<h1> logout fatto </h1>"

# per visualizzare il profilo dell'utente
@server.route('/profile/my/')
def profile():
    return "<h1> profile </h1>"

# per visualizzare il profilo di un utente
@server.route('/profile/<int:user_id>', methods=['GET'])
def profile(user_id):
    if request.method == 'GET':
        # Query per recuperare informazioni sul profilo dell'utente
        profile_query = f"""
            SELECT Profilo.*, 
                COUNT(Post.IDPost) AS NumPost,
                COUNT(Followers.IDUtenteSeguace) AS NumFollowers,
                COUNT(Following.IDUtenteSeguito) AS NumFollowing
            FROM Profilo
            LEFT JOIN Post ON Profilo.IDProfilo = Post.IDProfiloProvenienza
            LEFT JOIN Followers ON Profilo.IDProfilo = Followers.IDUtenteSeguito
            LEFT JOIN Following ON Profilo.IDProfilo = Following.IDUtenteSeguace
            WHERE Profilo.IDProfilo = {user_id}
        """
        profile_info = executeQuery(profile_query)

        # Query per recuperare i post dell'utente
        posts_query = f"""
            SELECT * FROM Post
            WHERE IDProfiloProvenienza = {user_id}
        """
        user_posts = executeQuery(posts_query)

        return render_template('profile.html', profile_info=profile_info[0], user_posts=user_posts) # !! nome pagina poi da definire !!
    else:
        return jsonify({"message": "Metodo non consentito"}), 405

# per visualizzare i post in tendenza delgi ultimi 30 giorni (da dfinire ul limite di post per la sezione)
@server.route('/trending', methods=['GET'])
def trending():
    if request.method == 'GET':
        # Query per ottenere i post con più interazioni (postati negli ultimi 30 giorni)
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
        return render_template('trending.html', trending_posts=trending_posts) # redirect alla pagina dei trending posts con i post in tendenza 
    else:
        return jsonify({"message": "Metodo non consentito"}), 405

# per visualizzare un post 
@server.route('/post/<int:id>/')
def post_id(id):
    return f"<h1> post {id} </h1>"

# funzione per visualizzare i commenti di un post o inserire un nuovo commento
@server.route('/post/<int:post_id>/comments/', methods=['GET', 'POST'])
def post_comment(post_id):
    if request.method == 'GET':
        query = f"SELECT * FROM Commento WHERE IDPost = '{post_id}'" # recupero i commenti del post relativo all'id
        comments = executeQuery(query, fetchall=True)

        return render_template('comments.html', comments=comments) # redirect alla pagina dei commenti

    elif request.method == 'POST':
        # Recupera i dati inviati dal form
        data = request.json
        comment_text = data.get('comment_text')
        profile_id = data.get('profile_id')

        # inserisco i dati del commento nel database
        query = f"INSERT INTO Commento (Commento, Data, IDProfiloProvenienza, IDPost) VALUES ('{comment_text}', NOW(), '{profile_id}', '{post_id}')"
        executeQuery(query)

        # aggiorno la pagina dei commenti
        return redirect(url_for('comments', post_id=post_id)) # !! nome pagina poi da definire !!
    else:
        return jsonify({"message": "Metodo non consentito"}), 405


# per visualizzare o mettere un  like di un post
@server.route('/post/<int:id>/like/')
def post_id_like(id):
    return f"<h1> post {id} like </h1>"

# per unlike di un post
@server.route('/post/<int:id>/unlike/')
def post_id_unlike(id):
    return f"<h1> post {id} unlike </h1>"

# per eelimianre un commento
@server.route('/post/<int:id>/comment/<int:comment_id>/delete/')
def post_id_comment_id_delete(id, comment_id):
    return f"<h1> post {id} comment {comment_id} delete </h1>"

@server.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        # prendo i dati del form
        descrizione = request.form['descrizione']
        percorso_file = request.form['percorso_file']
        id_profilo_provenienza = request.form['id_profilo_provenienza']

        # inserisco le informazioni del nuovo post nel db
        query = f"INSERT INTO Post (Descrizione, Data, PercorsoFile, IDProfiloProvenienza) VALUES ('{descrizione}', NOW(), '{percorso_file}', '{id_profilo_provenienza}')"
        executeQuery(query)

        # aggiorno lapplicaizone e rindirizzo alla pagina principale 
        return redirect(url_for('index')) # !! nome pagina poi da definire !!
    
    elif request.method == 'GET':
        # carico la pagina per la creazione di un nuovo post 
        return render_template('create_post.html') # !! nome pagina poi da definire !!
    else:
        return jsonify({"message": "Metodo non consentito"}), 405

# menu impostazioni
@server.route('/settings/')
def settings():
    return "<h1> settings </h1>"


#  -------- sezione di avvio server --------

if __name__ == "__main__":
    # avviamo l'applicazione in modalità debug
    server.run(debug=True)