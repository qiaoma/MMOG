
1. How to run the game application?


(1) install jdbc driver on eclipse: In eclipse click Project, Properties, Java Build Path, Libraries, Add External JARs, 
choose location and then click OK.

(2) modify the username and password in DBConnection.java file, change them as your own username and password 
to connect the MySql server.

(3) run the database script provided in GameDBScript.txt

(4) run CapitalizerServer.java for server

(5) run ClientApplication.py for client

(6) press left, right or up arrow key to activate the game for that user.


2. Constrains

User should press ESC key to logout.

3. Files

files in client

ClientApplication.py 
Player.py
PandaObject.py 
PlayerObject.py


files in server

CapitalizerServer.java 
DBConnection.java

files in server/model

Player.java
Panda.java

