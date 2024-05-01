-- Seguiti di un profilo 
SELECT Profilo.IDProfilo, Profilo.Nome, Profilo.Cognome
FROM Profilo
JOIN Segue ON Profilo.IDProfilo = Segue.Seguito
WHERE Segue.Seguace = 'ID_DEL_TUO_PROFILO';

-- Follower di un profilo 
SELECT Profilo.IDProfilo, Profilo.Nome, Profilo.Cognome
FROM Profilo
JOIN Segue ON Profilo.IDProfilo = Segue.Seguito
WHERE Segue.Seguace = 'ID_DEL_TUO_PROFILO';

-- Effettuare una registrazione 
INSERT INTO Utente (CodiceUtente, Password, PeriodoStorico, CodiceDiRecupero)
VALUES (123456, 'password123', 'Medievale', 789012);

-- Creazione Nuovo Post
INSERT INTO Post (Descrizione, Data, PercorsoFile, IDProfiloProvenienza)
VALUES ('Descrizione del post', CURDATE(), '/path/to/file', 'ID_DEL_PROFILO');

-- Creazione Commento 
INSERT INTO Commento (Commento, Data, IDProfiloProvenienza, IDPostDestinazione)
VALUES ('Testo del commento', GETDATE(), IDProfiloProvenienza_Value, IDPostDestinazione_Value);

-- Aggiungere MiPiace ad un post 
INSERT INTO MiPiace (IDProfiloProvenienza, IDPostDestinazione)
VALUES (IDProfiloProvenienza_Value, IDPostDestinazione_Value);

-- Rimuovere MiPiace ad un post
INSERT INTO MiPiace (IDProfiloProvenienza, IDPostDestinazione)
VALUES (IDProfiloProvenienza_Value, IDPostDestinazione_Value);

-- Inserimento di  nuovo messaggio direct
INSERT INTO Messaggio (Messaggio, Data, Ora, Mittente, Destinatario)
VALUES ('Testo del messaggio', GETDATE(), GETDATE(), IDMittente, IDDestinatario);

-- Caricamento/Aggiornamento immagine profilo utente
UPDATE Profilo
SET PathImmagineProfilo = 'nuovo_percorso_immagine.jpg'
WHERE IDProfilo = IDUtenteDesiderato;

-- Iniziare a seguire un utente
INSERT INTO Segue (Seguace, Seguito)
VALUES (IDSeguace, IDSeguito);

-- Smettere di seguire un utente 
DELETE FROM Segue
WHERE Seguace = IDSeguace AND Seguito = IDSeguito;

-- Aggiornare descrizione del profilo 
UPDATE Profilo
SET Descrizione = 'Nuova descrizione del profilo'
WHERE IDProfilo = IDProfiloDesiderato;

-- Post delle persone che seguo (dai più recenti ai meno) 
UPDATE Profilo
SET Descrizione = 'Nuova descrizione del profilo'
WHERE IDProfilo = IDProfiloDesiderato;

-- Visualizzare i post con più interazioni (postati negli ultimi 30 giorni)
SELECT Post.*, COUNT(MiPiace.IDPostDestinazione) AS NumMiPiace, COUNT(Commento.IDPostDestinazione) AS NumCommenti
FROM Post
LEFT JOIN MiPiace ON Post.IDPost = MiPiace.IDPostDestinazione
LEFT JOIN Commento ON Post.IDPost = Commento.IDPostDestinazione
WHERE Post.Data >= DATEADD(day, -30, GETDATE())
GROUP BY Post.IDPost
ORDER BY (COUNT(MiPiace.IDPostDestinazione) + COUNT(Commento.IDPostDestinazione)) DESC;

-- Impostare il profilo come pubblico 
UPDATE Profilo
SET Privacy = 0
WHERE IDProfilo = IDProfiloDesiderato;

-- Impostare il profilo come privato 
UPDATE Profilo
SET Privacy = 1
WHERE IDProfilo = IDProfiloDesiderato;





