# Progettazione

## Idea

Storygram è una web-app scaricabile (PWA???) dove diversi utenti da diversi periodi storici potranno iscriversi e fare post inerenti al proprio operato.
Gli utenti possibili possono essere:

- Personaggi storici conosciuti (es. politici, poeti ecc.)
- Persone del popolo che mostraranno accordo o disaccordo e potranno fare post, comuqnue sempre in relazione al proprio periodo storico

Le dinamiche saranno simili a quelle di qualsiasi social, quindi gli utenti potranno fare:

- registrazione
- login
- caricare post (chi fa un post non può cambiare il proprio periodo storico)
- commentare post
- mettere mi piace
- mandare messaggi agli utenti
- verificato ??? (gli utenti col verificato non possono cambiare il proprio periodo storico)
- cambio dei propri dati, possibile se l'account non è stato mai attivo
- immagine profilo con quello che ne consegue, quindi la possibilità di caricarla e cambiarla
- seguire gli altri utenti
- poter vedere chi seguo o chi mi segue
- possibilità di visualizzare gli ultimi post da offline (implementazione di una cache)
- pagina tendenze dove saranno visualizzati i post con più interazioni
- descrizione del profilo con la possibilità di cambiarla quando si vuole
- pagina home dove vedo i post delle persone che seguo
- Profili pubblici/privati ???
- tema chiaro e scuro
- storie visualizzabili solo per 24h ???

L'applicazione sarà ospitata su un server, dominio storygram.it ??? + server ??? + certificazione https per la PWA ???

## Registrazione

L'utente protrà registrarsi dando le seguenti informazioni:

- Nome
- Cognome
- Password
- Periodo storico in cui è vissuto
- Codice di sicurezza personale per il recupero delle credenziali

Dopo la registrazione all'utente sarà fornito un codice univoco per permettere l'accesso usato nel login, così da permettere persone con lo stesso nome e cognome nello stesso periodo storico.

## Login

Per accedere l'utente dovrà fornire il suo codice univoco e la sua password.
Sulla schermata di login sarà possibile anche andare alla registrazione oppure recuperare le credenziali.

## Caricare post

Per riuscire a caricare un'immagine l'utente deve aver fatto il login.

Per caricare dei post l'utente deve caricare un'immagine e potrà dare una descrizione (e un luogo ??? )

Il post sarà visibile da chi segue l'account ( se pubblico da tutti ???)

## Commentare post

Per commentare un post un utente deve aver fatto il login.

Dopo che qualcuno ha fatto un commento a un post questo potrà essere eliminato. Verrà indicato anche chi ha scritto il commento con la possibilità di vedere il profilo di chi l'ha scritto.

Il commento sarà visualizzabile da chiunque ha diritto di vedere il post commentato.

## Mettere mi piace

Mettendo mi piace la persona sarà visuallizzabile da gli altri utenti.
Inoltre il mi piace può esserer rimosso.

## Mandare messaggi

Un utente può mandare messaggi alle persone che segue (oppure ai profili pubblici)

## Verificato

Gli utenti che sono personaggi storici grandi possono ricevere il verificato (es. Mussolini può chiedere il verificato per certificare che sia lui)

## Cambio dei propri dati

Per gli utenti sarà possibile cambiare i propri dati se:

- Non ha attività (es. mi piace,post,commenti ecc.)
- E' verificato

## Immagine profilo

Ogni utente può scegliere di avere un'immagine profilo e questa potrà essere cambiata in un qualsiasi momento

## Seguire altri utenti

Un'utente può seguire un altro utente e questo potrà essere visualizzato dalla lista dei seguiti

## Visualizzazione di chi seguo e chi mi segue

Dimamica simile a instagram, quindi posso vedere chi segue e chi mi segue, anche gli altri utenti possono visualizzare le liste di chi segue ( e account pubblici ??)

## Visuallizzazione di post in modalità offline

Implementazione di una cache che permetta di visualizzare gli ultimi post in modalità offline.
Ulitmi 10 post che sono stati visualizzati dall'utente

## Pagina tendenze

Attraverso le interazioni che un post ha questo verrà caricato nella pagina delle tendenze.
Implementazione di un timer per creare una classifica settimanale, quindi tenere conto delle interazioni in una settimana

## Descrizione del profilo

Stesse dinamiche dell'immagine profilo solo che vengono applicate alla descrizione del profilo che avrà una lunghezza massima, quindi questa potrà essere cambiata in un qualsiasi momento

## Pagina home

Nella pagina home un'utente potrà visualizzare tutti gli ultimi post degli utenti che segue

## Profili privati e pubblici

Stesse dinamiche di instagram, quindi se un utente è privato il suo profilo potrà essere guardato solo da chi lo segue al contrario se un profilo è pubblico, allora anche chi non lo segue potrà visualizzarne i contenuti

## Tema chiaro e scuro

Progettazione dei temi.
Sarà possibile cambiare attraverso un'impostazione apposità

## Storie

Stesse dinamiche di instagram, visualizzabili solo da chi segue il profilo se è privato, visualizzabile da tutti se il profilo è pubblico

## Acquisto server e licenza http

Da discutere, anche se i prezzi sono bassi
