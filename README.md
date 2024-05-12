# StoryGram

StoryGram è un social network PWA che aha come obiettivo far incontrare i pensieri e le abitudini delle diverse generazioni e dei diversi periodi storici. Il social prevede le seguenti funzioni base: 

- Registrazione, Login e Logout alla piattaforma
- Pubblicazione di un Post con Immagine e Descrizione
- Possibilità do seguire un utente
- Possibilità di visualizzare seguiti e seguaci
- Possibilità di mettere “Mi piace” ai post
- Pagina home dove vedere i post dei profili seguiti e le tendenze
- Possibilità di modificare il profilo personale (descrizione, immagine profilo e la privacy del profilo)
- Possibilità di inviare e ricevere i messaggi dagli utente che seguo e che mi seguono
- Tema chiaro e tema scuro del sito
- Ricercare gli utenti nel social, con una barra di ricerca
- PWA del social
- Permettere di visualizzare la home in offline

## Infrastruttura utilizzata

### host VPS

per il nostro social network abbiamo deciso di affittare un VPS su cui hostare sia il stio vero e proprio che  il database e le risorse multimediali archiviate, in modo da poter rendere il sito disponibile h24 e avere un sistema completamente dedicato (oltre che isolato) per esso. Avendo un budget molto basso dedicato all’acquisto di risorse software e hardware abbiamo optato per una VPS che fosse ottima a livello qualità-prezzo, senza dover sostenere costi aggiuntivi e optando anche per supporti e optional software gratuiti e open-source quali sistema operativo Debian 12 e database MariaDB, compatibile con mySQL 

### Dominio storygram.it

per permettere agli utenti di raggiungere il nostro sito abbiamo scelto di acquistare anche un domino, ovvero “storygram.it”, insieme a un servizio di mail integrato, rimanendo sempre entro dei costi molto limitati. Grazie al servizio mail integrato abbiamo creato anche una casella di posta dedicata alle richieste di assistenza che gli utenti, possono utilizzare, in caso di Domande e Problemi da segnalarci 

### Certificato SSL, HTTPS e Sicurezza

per rendere il nostro sito sicuro e renderla una PWA abbiamo utilizzato il Certificato SSL Certificato DV Let’s Encrypt gratuito fornito dal fornitore della VPS che abbiamo affittato e installato automaticamente da loro, il servizio comprende anche una protezione  Anti-DDoS: L4 avanzato che assicura la protezione dai seguenti attacchi: 

- ICMP Echo Request Flood
- IP Packet Fragment Attack
- SMURF
- IGMP Flood
- Ping of Death
- TCP SYN Flood
- TCP Spoofed SYN Flood
- TCP SYN ACK Reflection Flood
- TCP ACK Flood
- TCP Fragmented Attack

In questo modo possiamo garantire un grado di sicurezza maggiore ai nostri  servizi e a chi gli utilizza. 

## Back-End

### Database

lo schema del database utilizzando per il nostro social è il seguente: 

```sql
CREATE TABLE Utente (
    IDUtente int PRIMARY KEY AUTO_INCREMENT,
    CodiceUtente int NOT NULL UNIQUE,
    Password varchar(200) NOT NULL,
    PeriodoStorico varchar(10) NOT NULL,
    CodiceDiRecupero varchar(200) NOT NULL
    );

CREATE TABLE Profilo (
    IDProfilo int PRIMARY KEY AUTO_INCREMENT,
    Nome varchar(25) NOT NULL,
    Cognome varchar(25) NOT NULL,
    Descrizione text(200) NOT NULL DEFAULT "",
    NumeroDiPost int NOT NULL DEFAULT 0,
    PathImmagineProfilo varchar(100) NOT NULL DEFAULT "utenti/default/ImmagineProfiloBase.jpg",
    Seguaci int NOT NULL DEFAULT 0,
    Seguiti int NOT NULL DEFAULT 0,
    Privacy BIT(1) NOT NULL DEFAULT 0, -- 0 PROFILO PUBBLICO, 1 PROFILO PRIVATO --> i computer sono più veloci coi numeri che con le stringhe
    CONSTRAINT FK_UtenteProfilo FOREIGN KEY (IDProfilo) REFERENCES Utente(IDUtente) ON DELETE CASCADE ON UPDATE CASCADE
    );

CREATE TABLE Messaggio (
    IDMessaggio int PRIMARY KEY AUTO_INCREMENT,
    Messaggio text(500) NOT NULL,
    Data date NOT NULL,
    Ora time NOT NULL,
    Mittente int NOT NULL,
    Destinatario int NOT NULL,
    CONSTRAINT FK_MittenteMessaggio FOREIGN KEY (Mittente) REFERENCES Profilo(IDProfilo) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT FK_DestinatarioMessaggio FOREIGN KEY (Destinatario) REFERENCES Profilo(IDProfilo) ON DELETE CASCADE ON UPDATE CASCADE
    );

CREATE TABLE Segue (
    IDSeguito int PRIMARY KEY AUTO_INCREMENT,
    Seguace int NOT NULL,
    Seguito int NOT NULL,
    CONSTRAINT FK_Seguace FOREIGN KEY (Seguace) REFERENCES Profilo(IDProfilo) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT FK_Seguito FOREIGN KEY (Seguito) REFERENCES Profilo(IDProfilo) ON DELETE CASCADE ON UPDATE CASCADE
    );

CREATE TABLE Post (
    IDPost int PRIMARY KEY AUTO_INCREMENT,
    Descrizione text(200) NOT NULL DEFAULT "",
    Data date NOT NULL,
    PercorsoFile varchar(100) NOT NULL,
    IDProfiloProvenienza int NOT NULL,
    CONSTRAINT FK_PostProfilo FOREIGN KEY (IDProfiloProvenienza) REFERENCES Profilo(IDProfilo) ON DELETE CASCADE ON UPDATE CASCADE
    );

CREATE TABLE MiPiace (
    IDProfiloProvenienza int NOT NULL,
    IDPostDestinazione int NOT NULL,
    PRIMARY KEY (IDProfiloProvenienza, IDPostDestinazione), -- la coppia è la chiave primaria ("non posso mettere like allo stesso post con lo stesso account")
    CONSTRAINT FK_MiPiaceProfiloProvenienza FOREIGN KEY (IDProfiloProvenienza) REFERENCES Profilo(IDProfilo) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT FK_MiPiacePostDestinazione FOREIGN KEY (IDPostDestinazione) REFERENCES Post(IDPost) ON DELETE CASCADE ON UPDATE CASCADE
    );

CREATE TABLE Commento (
    IDCommento int PRIMARY KEY AUTO_INCREMENT,
    Commento text(300) NOT NULL,
    Data date NOT NULL,
    IDProfiloProvenienza int NOT NULL,
    IDPostDestinazione int NOT NULL,
    CONSTRAINT FK_CommentoProfiloProvenienza FOREIGN KEY (IDProfiloProvenienza) REFERENCES Profilo(IDProfilo) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT FK_CommentoPostDestinazione FOREIGN KEY (IDPostDestinazione) REFERENCES Post(IDPost) ON DELETE CASCADE ON UPDATE CASCADE
    );

CREATE TABLE Storia (
    IDStoria int PRIMARY KEY AUTO_INCREMENT,
    PercorsoFile varchar(100) NOT NULL,
    IDProfiloProvenienza int NOT NULL,
    CONSTRAINT FK_StoriaProfilo FOREIGN KEY (IDProfiloProvenienza) REFERENCES Profilo(IDProfilo) ON DELETE CASCADE ON UPDATE CASCADE
    );
```

### Connessione al Database

per la connessione al db e l’esecuzione delle query, essendo il sito nello stesso server del database, accediamo direttamente il [localhost](http://localhost), utilizzando il seguente script in Python che utilizza la libreria pymysql:

```python
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

```

attraverso la funzione executeQuery eseguiamo tutte le interrogazioni fatte al db dal nostro sito per gestire i vari dati. 

### Gestione delle route tramite il micro-framework Flask

per la gestione delle route e del sito storygram abbiamo utilizzato il framework Flask, visto in classe, combinato con Jinja2 per in render dei vari templates e pagine del sito.

Ogni route gestita verifica che se l’utente è autorizzato ad effettuare una richiesta alla specifica route e se la richiesta è stata effettuata con un metodo valido.

 Le varie route gestite sono le seguenti:

- `@server.route('/')`

che definisce la home di Storygram, gestisce solo le gestisce di tipo GET e renderizza la pagina home con le varie informazioni richieste, inclusi i post propri e degli unteti seguiti, combinati con i post in tendenza di storygram degli ultimi 30 giorni, in sequenza 3-1-

I post in tendenza degli ultimi 30 giorni vengono calcolati attraverso le varie interazioni (commenti e mi piace) con diversi valori di peso a seconda del tipo di interazione: 1,5 per i commenti, essendo un interazione più rilevante, e 1 per i mi piace. La query al db che permette di ottenere i post in tendenza è la seguente: 

```sql
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
LIMIT 50
```

nella query per i post in tendenza da far visualizzare all’utente escludiamo gli eventuali suoi post e di chi segue e ovviamente dei profili che hanno il profilo privato.

- `@server.route('/login/', methods=["GET", "POST"])`

la route login gestisce appunto il login a storygram , al momento del login l’utente deve inserire il proprio codice utente e la propria password, se le informazioni sono correte verrà permesso l’accesso al social e portato automaticamente alla pagina home del sito 

- `@server.route('/register/', methods=['GET', 'POST'])`

la route di registrazione permette a un nuovo utente di registrarsi al social, le informazioni necessarie per inscriversi  sono: nome, cognome, password, periodo storico. richiesta la registrazione il sito genera automaticamente un codice utente con cui l’utente eseguirà gli accessi futuri. Il codice di recupero inserito dall’utente serve in caso di smarrimento della password. Non è stato implementato un recupero attraverso indirizzo email, ipotizzando che gli utenti di periodi storici molto passati non dispongono di un indirizzo email da fornire durante la registrazione. Infine per garantire la sicurezza, la password e il codice di recupero non sono salvati in chiaro del db ma viene salvato l’hash relativo attraverso l’algoritmo sha256 come mostrato qua sotto: 

```sql
# Codifica la password in codice hash e il relativo codice di recupero
password_hash = hashlib.sha256(password.encode()).hexdigest()
codice_di_recupero_hash = hashlib.sha256(codice_di_recupero.encode()).hexdigest()
```

- `@server.route('/recovery/', methods=['GET', 'POST'])` e `@server.route('/recovery/reset/', methods=['GET', 'POST'])`

queste due route gestiscono il reset della password in caso di smarrimento, una volta fornito il codice utente e il codice di recupero, verrà permesso di inserire una nuova password che verrà aggiornata  nel db. In caso di smarrimento anche del codice di recupero è presente un link che permette di contattare via email il servizio clienti per richiedere assistenza, per un reset manuale della password, garantendo comunque che il richiedente  sia l’effettivo proprietario del profilo di cui sono state perse le credenziali. 

- `@server.route('/logout/', methods=["GET"])`

questa route gestisce semplicemente il logout di un utente, eliminando i dati di sessione

- `@server.route('/profile/<int:id>/', methods=['GET'])`

questa route gestisce la visualizzazione  di un profilo utente e a seconda se un utente ha il permesso di visualizzare i post dell’utente, vengono richiesti al db le info dei psot di quell’utente. Se l’utente è il proprietario del profilo invece, viene permessa anche la possibilità di accedere alla pagine di modifica del profilo 

- `@server.route('/profile/<int:id>/modify', methods=['GET', 'POST'])`

questa route gestisce appunto la modifica del proprio profilo, ovvero la modifica dell’immagine profilo, della descrizione e la possibilità di rendere pubblico o privato il profilo 

- `@server.route('/profile/<int:id>/followers/', methods=['GET'])`

questa route permette di visualizzare i follower  di un determinato profilo 

- `@server.route('/profile/<int:id>/following/', methods=['GET'])`

questa route permette di visualizzare i seguiti  di un determinato profilo 

- `@server.route('/search/', methods=['GET', 'POST'])`

questa route permette di ricercare gli utenti presenti in storygram, effettua una ricerca per nome, cognome ma anche periodo storico, per rendere più semplice ed efficace la ricerca di un utente, di cui magari si ricorda solo il periodo storico ma non il nome completo, o viceversa 

- `@server.route('/post/create/', methods=['GET', 'POST'])`

route che permette la creazione di un nuovo post, al momento della creazione viene chiesto di inserire un immagine e un eventuale descrizione. La gestione delle immagini e dei tipi di file permessi, viene descritta successivamente, in questa documentazione, nell’apposita sezione “gestione delle imagini uplodate”

- `@server.route('/post/<int:post_id>/comments/', methods=['GET', 'POST'])`

questa route permette di visualizzare i commenti di un determinato post oppure di aggiungerne uno nuovo 

- `@server.route('/post/<int:post_id>/like/', methods=['GET', 'POST'])`

questa route invece permette di mettere o togliere un like ad un post 

- `@server.route('/messages/', methods=['GET', 'POST'])`

questa route permette la gestione della ricezione e dell’invio dei messaggi tra utenti 

- `@server.route('/segui/<int:id_profilo_da_seguire>', methods=['GET', 'POST'])` e `@server.route('/stop_segui/<int:id_profilo_da_stop_seguire>', methods=['GET', 'POST'])`

queste due route infine, permettono di seguire e smettere di seguire un profilo 

### Gestione delle immagini uplodate

per quanto riguarda la gestione dei file multimediali (imagini profilo e immagini dei post) abbiamo deciso di salvare nel server le risorse, in cartelle divise per utenti e successivamente per media e immagini profilo, per rendere l’archiviazione delle risorse più chiara e ordinata. LA creazione delle cartelle dedicate per ogni utente avviene al momento della registrazione attraverso il seguente script in python: 

```python
import os

# funzione per creare la cartella dedicata al nuovo utente al momento della registrazione 
def creaCartella(IDUtente):
    try:
        IDUtente_str = str(IDUtente) # traformo il codice dell'utente in una stringa
        current = os.getcwd() # recupero la directory di lavoro dove creerò la cartella dedicata al nuovo utente 
        os.makedirs(os.path.join(current, "static/utenti", IDUtente_str, "media"))  # cartella per i media in generale (post/storie)
        os.makedirs(os.path.join(current, "static/utenti", IDUtente_str, "ImmagineProfilo")) # cartella per l'immagine profilo dell'utente
    except Exception as e:
        print(e)

```

Nel momento in cui un utente carica una nuova immagine profilo o un nuovo post, l’immagine viene salvata nel server attraverso il seguente script: 

```python
from flask import  jsonify, flash 
from werkzeug.utils import secure_filename # usato per la sicurezza dei file caricati dall'utente
import os # usato per uplodare il file caricato nell'utente, nel server 

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} # estensioni permesse dei file caricati dall'utente (da definire)

# funzione che controlla se l'utente ha caricato un file con estensione permessa 
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def uploadImmagineProfilo(file, server, session):
    
    print("debug")
    server.config['UPLOAD_FOLDER'] = f"static/utenti/{session['IDUtente']}/ImmagineProfilo" # imposto la cartella di upload per l'immagine profilo

    # controllo se l'utente ha inserito effettivamente un file (i browser di solito se non viene isnerito un file, ne agigungono uno vuoto senza nome)
    if file.filename == '':
        print('Nessun file Selezionato') # debug
        return jsonify({'error': 'Nessun file Selezionato'}), 400
    if file and allowed_file(file.filename): # se è stato caricato il file lo carico della giusta cartella 
        print(f'File caricato: {file.filename}') # debug 
        filename = secure_filename(file.filename)
        file.save("./" + os.path.join(server.config['UPLOAD_FOLDER'], filename))
        return  os.path.join(server.config['UPLOAD_FOLDER'], filename) # ritorno il path dell'immagine profilo poi da aggiornare nel db 

def uploadImmaginePost(file, server, session):
    
    server.config['UPLOAD_FOLDER'] = f"static/utenti/{session['IDUtente']}/media"

    if file.filename == '':
        print('Nessun file Selezionato') # debug
        return jsonify({'error': 'Nessun file Selezionato'}), 400
    if file and allowed_file(file.filename): # se è stato caricato il file lo carico della giusta cartella 
        print(f'File caricato: {file.filename}') # debug 
        filename = secure_filename(file.filename)
        file.save("./" + os.path.join(server.config['UPLOAD_FOLDER'], filename))
        return  os.path.join(server.config['UPLOAD_FOLDER'], filename)

```

seguendo le linee guida presenti nella documentazione ufficiale del Framework Flask. come si vede dallo script i tipi di file che accettiamo sono: 

- png
- jpg
- jpeg
- gif

questo per motivi di compatibilità del sito e di sicurezza, per evitare che non vengano caricati file dannosi. Il path di tutti i file multimediali vengono salvati del db, negli attributi delle tabelle apposite, descritte nei punti precedenti della documentazione, al fine di poterle recuperare in modo semplice e veloce.

## Front-End

## Progettazione del progetto
