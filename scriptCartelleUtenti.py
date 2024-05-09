import os

# funzione per creare la cartella dedicata al nuovo utente al momento della registrazione 
def creaCartella(IDUtente):
    try:
        IDUtente_str = str(IDUtente) # traformo il codice dell'utente in una stringa
        current = os.getcwd() # recupero la directory di lavoro dove creerò la cartella dedicata al nuovo utente 
        os.makedirs(os.path.join(current, "static/utenti", IDUtente_str, "media"))  # cartella per i media in generale (post/storie)
        os.makedirs(os.path.join(current, "static/utenti", IDUtente_str, "ImmagineProfilo")) # cartella per l'immagine profilo dell'utente
    except Exception as e:
        print(e)
