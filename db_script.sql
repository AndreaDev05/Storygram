CREATE TABLE Utente (
    IDUtente int PRIMARY KEY AUTO_INCREMENT,
    CodiceUtente int NOT NULL UNIQUE,
    Password varchar(200) NOT NULL,
    PeriodoStorico varchar(10) NOT NULL,
    CodiceDiRecupero int NOT NULL
    );

CREATE TABLE Profilo (
    IDProfilo int PRIMARY KEY,
    Nome varchar(25) NOT NULL,
    Cognome varchar(25) NOT NULL,
    Descrizione text(200) NOT NULL DEFAULT "",
    NumeroDiPost int NOT NULL DEFAULT 0,
    PathImmagineProfilo varchar(100) NOT NULL DEFAULT "PATH DA DEFINIRE",
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
    IDPost int PRIMARY KEY,
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
