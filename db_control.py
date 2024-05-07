from flask import jsonify
import pymysql
import credentials

# funzione per eseguire una query su database
def executeQuery(query):
    #   creo una connessione al database
    connection = pymysql.connect(
        host=credentials.host,
        user=credentials.user,
        password=credentials.password,
        db=credentials.database,
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(query) # esegue la query
                connection.commit() # permette di salvare le modifiche fatte al database
                res = cursor.fetchall() # restituisce i risultati della query eseguita
                return res
    except Exception as e: # se avviene un errore ritorno -1 come codice di errore
        print(e)
        return jsonify({"message": "Errore durante l'esecuzione della query"}), 500

# Query per verificare se l'utente sta seguendo il profilo
def is_following(user_id, profile_id):
    
    follow_query = f"""
                        SELECT COUNT(*) AS cnt
                        FROM Seguaci
                        WHERE IDFollower = {user_id} AND IDSeguito = {profile_id};
                    """
    result = executeQuery(follow_query)
    return result[0]['cnt'] > 0
