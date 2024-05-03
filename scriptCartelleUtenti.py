import os

# funzione per creare la cartella dedicata al nuovo utente al momento della registrazione 
def creaCartella(username):
    try:
        current = os.getcwd() # recupero la directory di lavoro dove creerò la cartella dedicata al nuovo utente 
        os.makedirs(current + "/utenti/" + username + "/media")
        os.makedirs(current + "/utenti/" + username + "/ImmagineProfilo")
    except Exception as e:
        print(e)
