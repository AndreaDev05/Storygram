from flask import jsonify
import pymysql
import static.credentials as credentials

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

