from flask import  jsonify, flash 
from werkzeug.utils import secure_filename # usato per la sicurezza dei file caricati dall'utente
import os # usato per uplodare il file caricato nell'utente, nel server 

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} # estensioni permesse dei file caricati dall'utente (da definire)


# funzione che controlla se l'utente ha caricato un file con estensione permessa 
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def uploadImmaggineProfilo(file, server, session):
    
    print("debug")
    server.config['UPLOAD_FOLDER'] = f"static/utenti/{session['IDUtente']}/ImmagineProfilo" # imposto la cartella di upload per l'immagine profilo

    # controllo se l'utente ha inserito effettivamente un file (i browser di solito se non viene isnerito un file, ne agigungono uno vuoto senza nome)
    if file.filename == '':
        print('Nessun file Selezionato') # debug
        return jsonify({'error': 'Nessun file Selezionato'}), 400
    if file and allowed_file(file.filename): # se è stato caricato il file lo carico della giusta cartella 
        print(f'File caricato: {file.filename}') # debug 
        filename = secure_filename(file.filename)
        file.save(os.path.join(server.config['UPLOAD_FOLDER'], filename))
        return  os.path.join(server.config['UPLOAD_FOLDER'], filename) # ritorno il path dell'immagine profilo poi da aggiornare nel db 
    
