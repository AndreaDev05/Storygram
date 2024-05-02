import sshtunnel
from getpass import getpass # used to hide the input of the password
import mysql.connector as ms
from mysql.connector import Error
from threading import Lock

#   ----------------------------------------------------------------------------------
#           class tussh used to connect to the DB in the school's server
#           contabile via tunnel ssh
#   ----------------------------------------------------------------------------------

class tunnSSH:
    connSSH : sshtunnel.SSHTunnelForwarder = None
    connection = None
    mycursor = None
    lock : Lock = None

    #function that enable connectiot to the server via ssh
    def connect():
        #declaretion of global variables used in other functions
        global connSSH, connection, ps, us, lock
        lock = Lock()
        us = input("Utente dominio e-fermi: ")
        ps = getpass() #password input
        connSSH = sshtunnel.SSHTunnelForwarder(
            ("contabile.e-fermi.it", 2234), # tuple with the server address and port
            ssh_username = us,
            ssh_password = ps,
            remote_bind_address = ("127.0.0.1",3306) #database address and port
        )

        connSSH.start() # inizio ssh

    # function that connect to the database 
    def connDB():
        global connSSH,connection,mycursor,ps

        try:
            connection = ms.connect(
                user=us,
                passwd=ps[:-2],
                database=us,
                host="localhost",
                port=connSSH.local_bind_port
            )
            print(connection)
        except Error as err:
            print(f"Error: '{err}'")
        
        mycursor = connection.cursor()

        print("Successful connection to database!")

    # used to get data from database
    def comDBGet(str:str):
        global connection,mycursor,lock

        lock.acquire()
        mycursor.execute(str)
        myresult = mycursor.fetchall()
        lock.release()

        return myresult

    # used to set data from database
    def comDBSet(str:str):
        global connection,mycursor,lock

        lock.acquire()
        mycursor.execute(str)
        connection.commit()
        lock.release()

        return mycursor.lastrowid

    #used to call a sql procedure
    def comDBCallProc(str:str,args:tuple):
        global connection,mycursor,lock

        lock.acquire()
        mycursor.callproc(str,args)
        connection.commit()
        lock.release()
    
    # termino la connessione ssh
    def endSSH():
        global connSSH

        connSSH.close()