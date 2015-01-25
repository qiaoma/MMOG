# Author: Ryan Myers
# Models: Jeff Styers, Reagan Heller


# Last Updated: 6/13/2005
#
# This tutorial provides an example of creating a character
# and having it walk around on uneven terrain, as well
# as implementing a fully rotatable camera.

import direct.directbase.DirectStart
from panda3d.core import CollisionTraverser,CollisionNode
from panda3d.core import CollisionHandlerQueue,CollisionRay
from panda3d.core import Filename,AmbientLight,DirectionalLight
from panda3d.core import PandaNode,NodePath,Camera,TextNode
from panda3d.core import Vec3,Vec4,BitMask32
from direct.gui.OnscreenText import OnscreenText
from direct.actor.Actor import Actor
from direct.showbase.DirectObject import DirectObject
import random, sys, os, math


from direct.showbase.ShowBase import ShowBase
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

from panda3d.core import ConnectionWriter
from panda3d.core import NetDatagram
from panda3d.core import QueuedConnectionListener
from panda3d.core import QueuedConnectionManager
from panda3d.core import QueuedConnectionReader


from Player import Player
from PlayerObject import PlayerObject
from PandaObject import PandaObject
from threading import Timer

SPEED = 0.5


LOGIN = "1"
REGISTER = "2"
UPDATE_PLAYER_MOVE = "4"
PANDA_ATTACK_REQUEST = "5"

USERNAME_EXIST = "111"
REGISTER_SUCCESSFUL = "110"

LOGIN_SUCCESSFUL = "100"
LOGIN_FAIL = "101"
ADD_NEW_PLAYER = "102"

LOGOUT = "120"

UPDATE_PLAYER_MOVE_RESPONSE = "130"

PANDA_ATTACK = "140"

PANDA_ATTACK_RANGE = 10

# Function to put instructions on the screen.
def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1),
                        pos=(-1.3, pos), align=TextNode.ALeft, scale = .05)

# Function to put title on the screen.
def addTitle(text):
    return OnscreenText(text=text, style=1, fg=(1,1,1,1),
                        pos=(1.3,-0.95), align=TextNode.ARight, scale = .07)

class World(DirectObject):

    def __init__(self):
               
        self.cManager = QueuedConnectionManager()
        self.cListener = QueuedConnectionListener(self.cManager, 0)
        self.cReader = QueuedConnectionReader(self.cManager, 0)
        self.cWriter = ConnectionWriter(self.cManager, 0)
        
        host = "localhost"
        port = 9898
        self.connection = self.cManager.openTCPClientConnection(host, port, 10000)
        #self.received = 1
        
        #store a dictionary of active players with username player as key value pair
        #the dictionary also contain a special player named panda
        self.players = {}
        
        #for display the list on the screen
        self.temp = []
        
        #store a dictionary of playerObject
        self.playerObjects = {}
        self.render = render
        self.loginSuccessful = False
        self.isMoving = False
        self.justStoping = False
        self.targetPlayer = None        
        
        if self.connection:
            self.cReader.addConnection(self.connection)
            taskMgr.add(self.updateRoutine, 'updateRoutine')
            #taskMgr.doMethodLater(0.5, self.updateRoutine, 'updateRoutine')
            #taskMgr.add(self.updatePandaAttack, 'updatePandaAttack')
            #taskMgr.doMethodLater(3, self.updatePandaAttack, 'updatePandaAttack')
            self.loginRegister()
            

    #################Communication Method################
    
    def loginRegister(self):
        print "1. Login"
        print "2. Register"
        userInput = str(raw_input("Enter 1 or 2: "))
        if userInput == "1":
            self.login()
        elif userInput == "2":
            self.register();
        else:
            print "Invalid input"
            self.loginRegister()
    
    def register(self):
        print "Please enter your username: "
        username = str(raw_input())
        print "Please enter your password: "
        password = str(raw_input())
        
        msg = "{} {} {}".format(REGISTER, username, password)
        self.sendRequest(msg)
    
    #define self.username to specify the username for this object   
    def login(self):
        print "Please enter your username: "
        self.username = str(raw_input())
        print "Please enter your password: "
        password = str(raw_input())
        msg = "{} {} {}".format(LOGIN, self.username, password)            
        self.sendRequest(msg)
  
    #user need to press esc key to logout       
    def logout(self, x, y, z, h):
        print "logout called"
        player = self.players[self.username]
        
        msg = "{} {},{},{},{},{}".format(LOGOUT, self.username, 
                        player.getX(), player.getY(), player.getZ(), player.getH())         
        print msg          
        self.sendRequest(msg)
        sys.exit()  
    
    def updateMovement(self, isMove, x, y, z, h):
        #send code username,ismove,x,y,z,h to the server according to the protocol
        msg = "{} {},{},{},{},{},{}".format(UPDATE_PLAYER_MOVE, self.username, isMove, x, y, z, h)
        self.sendRequest(msg)
    
    def possibleAttackRequest(self, distance):
        msg = "{} {},{}".format(PANDA_ATTACK_REQUEST, self.username, distance)
        self.sendRequest(msg)
        
    def composeStringMessage(self, msg):
        myPyDatagram = PyDatagram()
        myPyDatagram.addString(msg)
        return myPyDatagram
                
    def retrieveStringMessage(self,datagram):
        myIterator = PyDatagramIterator(datagram)
        msg = myIterator.getString()
        #print msg, " received"
        return msg
            
#     def sendRequest(self):
#         if(self.received):
#             print "->Client request:"
#             # Send a request to the server
#         mylist = ["apple", "ball", "cat", "dog"] 
#         
#         msg = random.choice(mylist)
#         request = self.composeStringMessage(msg)
#         ack = self.cWriter.send(request,self.connection)                
#         print msg, " sent"
#         self.received = 0

    def sendRequest(self, msg):
        request = self.composeStringMessage(msg)
        ack = self.cWriter.send(request,self.connection)                
        #print msg, " sent"
        #self.received = 0
        
    def receiveResponse(self):
        #print "<-Server response:"
        while self.cReader.dataAvailable():
            datagram = NetDatagram()
            # Retrieve the contents of the datagram.
            if self.cReader.getData(datagram):
                msg = self.retrieveStringMessage(datagram)
                msgs = msg.split(' ')
                #print msgs[0]
                
                if msgs[0] == REGISTER_SUCCESSFUL:
                    self.registerSuccessfulResponse()
                elif msgs[0] == USERNAME_EXIST:
                    self.usernameExistResponse()
                elif msgs[0] == LOGIN_SUCCESSFUL:
                    self.loginSuccessfulResponse(msgs[1])
                elif msgs[0] == ADD_NEW_PLAYER:
                    self.addNewPlayerResponse(msgs[1])
                elif msgs[0] == LOGIN_FAIL:
                    self.loginFailResponse()
                elif msgs[0] == LOGOUT:
                    self.logoutResponse(msgs[1])
                elif msgs[0] == UPDATE_PLAYER_MOVE_RESPONSE:
                    self.updateMoveResponse(msgs[1])
                elif msgs[0] == PANDA_ATTACK:
                    self.pandaAttackResponse(msgs[1])
                #self.received = 1
                
#     def communicate(self):
#         #print "communicate"
#         #self.sendRequest()
#         self.receiveResponse()
        
    def updateRoutine(self,task):
        #self.communicate()
        self.receiveResponse()
        return task.again;
    
    def registerSuccessfulResponse(self):
        print "You have successfully registered. Please login to start the game."
        self.login()
    
    def usernameExistResponse(self):
        print "Username already exist. Please choose another username."
        self.register()
    
    #initail a dictionary of players
    def loginSuccessfulResponse(self, playerListMsg):
        actorsMsg = playerListMsg.split(":")
        #the dictionary also adds a special player named panda
        for aMsg in actorsMsg:
            elements = aMsg.split(",")
            actor = Player(elements[0], float(elements[1]), float(elements[2]), float(elements[3]), 
                           float(elements[4]))
            self.players[elements[0]] = actor
            
        print "login successful"
        
        #display other players' Ralph
        for username, value in self.players.iteritems():
            if username == self.username:
                #display this player's Ralph
                self.showRalph(value)      
            elif username != self.username and username != "panda":
                self.createActor(self.render, value)
            elif username == "panda":
                self.createPanda(self.render, value)
            else:
                pass
        
        self.loginSuccessful = True       
    
    #add new player to the players dictionary
    def addNewPlayerResponse(self, msg):
        elements = msg.split(",")
        actor = Player(elements[0], float(elements[1]), float(elements[2]), float(elements[3]), 
                       float(elements[4]))
        self.players[elements[0]] = actor        
        print "add new player: ", self.players[elements[0]].getUsername(), self.players[elements[0]].getX()
        self.createActor(self.render, actor)
        
        ###Line's Added###
        textMsg = elements[0]+" has logged in"
        self.notifyPlayer(textMsg)
        
    def loginFailResponse(self):
        print "Username and password does not match, please re-login or register."
        self.loginRegister()
        
    def logoutResponse(self, username):
        if username in self.players:
            del self.players[username]
        
        if username in self.playerObjects:
            playerObject = self.playerObjects[username]
            playerObject.getActor().delete()
        
            del self.playerObjects[username]
        #self.playerObjects
        print "{} logout".format(username)
        
        ###Lines Added###
        msg = username+" has logged out"
        self.notifyPlayer(msg)
        
    def notifyPlayer(self,msg):
        #label = DirectLabel(text=msg)
        label = OnscreenText(text=msg, style=1, fg=(1,1,1,1),
                        pos=(1.3,-0.95), align=TextNode.ARight, scale = .07)
        taskMgr.doMethodLater(5, self.destroyLabel, 'destroyLabel', extraArgs=[label])
        
    def destroyLabel(self,label):
        label.destroy()
        
    def updateMoveResponse(self, msg):
        if self.loginSuccessful:
            #msg contain username,isMoving,x,y,z,h
            msgs = msg.split(",")
            username = msgs[0]
            if username == self.username:
                #self already move, no need to update
                pass
            else:
                if username in self.playerObjects.keys(): 
                    player = self.players[username]
                    player.setX(float(msgs[2]))
                    player.setY(float(msgs[3]))        
                    player.setZ(float(msgs[4]))    
                     
                    actor = self.playerObjects[username].getActor()
                    actor.setPos(float(msgs[2]), float(msgs[3]), float(msgs[4]))
                    actor.setH(float(msgs[5]))
                    self.playerObjects[username].move(msgs[1])
    
    def pandaAttackResponse(self, msg):
        #msg contain targetUsername
        #print "pan Att: ", msg
        #msgs = msg.split(",")
        
        targetUsername = msg
        targetPlayer = self.players[targetUsername]

        pandaActor = self.pandaObject.getActor()
        pandax = pandaActor.getX()
        panday = pandaActor.getY()
        pandaz = pandaActor.getZ()        
         
        x = targetPlayer.getX()
        y = targetPlayer.getY()
        z = targetPlayer.getZ()
         
        distance = self.getDistance(pandax, panday, pandaz, x, y, z)
      
        if distance < PANDA_ATTACK_RANGE:
            if pandax > x and panday > y:
                self.pandaObject.setH(135)
            elif pandax > x and panday < y:
                self.pandaObject.setH(180)
            elif pandax < x and panday > y:
                self.pandaObject.setH(135)
            else:
                self.pandaObject.setH(90)
            #self.pandaObject.turn(180)         
            self.pandaObject.move(x-0.5, y-0.5, z)
            
            panda = self.players["panda"]
            panda.setX(pandax);
            panda.setY(panday);
            panda.setZ(pandaz);
        
        #self.setTargetPlayer(msg)
        
    def setTargetPlayer(self, username):
        self.targetPlayer = self.players[username]
        
    def getTargetPlayer(self):
        return self.targetPlayer        
                    
    def createActor(self, render, actor):
        playerObject = PlayerObject(render, actor)
        self.playerObjects[actor.getUsername()] = playerObject
#         nameplate = TextNode('textNode username_' + str(actor.username))
#         nameplate.setText(actor.username)
#         npNodePath = actor.actor.attachNewNode(nameplate)
#         npNodePath.setScale(1.0)
#         npNodePath.setBillboardPointEye()
#         npNodePath.setZ(8.0)
        
    def createPanda(self, render, actor):
        self.pandaObject = PandaObject(render, actor)
        
    def checkPossibleAttack(self, x, y, z):
        panda = self.players["panda"]
        pandax = panda.getX();
        panday = panda.getY();
        pandaz = panda.getZ();
        
        distance = self.getDistance(pandax, panday, pandaz, x, y, z)
        
        if distance < PANDA_ATTACK_RANGE:
            self.possibleAttackRequest(distance)
            
    def getDistance(self, pandax, panday, pandaz, x, y, z):
        
        return math.sqrt( math.pow(pandax-x, 2) + math.pow(panday-y, 2) + math.pow(pandaz-z, 2) )
        
    #################################################################
    
    ################Ralph code ##################### 
       
    def showRalph(self, player):        
        
#         self.render = render
         
        self.keyMap = {"left":0, "right":0, "forward":0, "cam-left":0, "cam-right":0}
        base.win.setClearColor(Vec4(0,0,0,1))
 
        # Post the instructions
 
        #self.title = addTitle("Panda3D Tutorial: Roaming Ralph (Walking on Uneven Terrain)")
        self.inst1 = addInstructions(0.95, "[ESC]: Quit")
        self.inst2 = addInstructions(0.90, "[Left Arrow]: Rotate Ralph Left")
        self.inst3 = addInstructions(0.85, "[Right Arrow]: Rotate Ralph Right")
        self.inst4 = addInstructions(0.80, "[Up Arrow]: Run Ralph Forward")
        self.inst6 = addInstructions(0.70, "[A]: Rotate Camera Left")
        self.inst7 = addInstructions(0.65, "[S]: Rotate Camera Right")
        
        self.inst8 = addInstructions(0.60, "[l] Show Players on the right corner")
         
        # Set up the environment
        #
        # This environment model contains collision meshes.  If you look
        # in the egg file, you will see the following:
        #
        #    <Collide> { Polyset keep descend }
        #
        # This tag causes the following mesh to be converted to a collision
        # mesh -- a mesh which is optimized for collision, not rendering.
        # It also keeps the original mesh, so there are now two copies ---
        # one optimized for rendering, one for collisions.  
         
        self.environ = loader.loadModel("models/world")      
        self.environ.reparentTo(render)
        self.environ.setPos(0,0,0)
        
        # Create the main character, Ralph

        ralphStartPos = self.environ.find("**/start_point").getPos()
        self.ralph = Actor("models/ralph",
                                 {"run":"models/ralph-run",
                                  "walk":"models/ralph-walk"})
        self.ralph.reparentTo(render)
        self.ralph.setScale(.2)
        #self.ralph.setPos(ralphStartPos)
        
        self.ralph.setPos(player.getX(), player.getY(), player.getZ())
        self.ralph.setH(player.getH())
        
        #####################################


        # Create a floater object.  We use the "floater" as a temporary
        # variable in a variety of calculations.
        
        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(render)

        # Accept the control keys for movement and rotation

        #self.accept("escape", sys.exit)
        self.accept("escape", self.logout, [self.ralph.getX(), self.ralph.getY(), self.ralph.getZ(), self.ralph.getH()])
        self.accept("arrow_left", self.setKey, ["left",1])
        self.accept("arrow_right", self.setKey, ["right",1])
        self.accept("arrow_up", self.setKey, ["forward",1])
        self.accept("a", self.setKey, ["cam-left",1])
        self.accept("s", self.setKey, ["cam-right",1])
        self.accept("arrow_left-up", self.setKey, ["left",0])
        self.accept("arrow_right-up", self.setKey, ["right",0])
        self.accept("arrow_up-up", self.setKey, ["forward",0])
        self.accept("a-up", self.setKey, ["cam-left",0])
        self.accept("s-up", self.setKey, ["cam-right",0])

        taskMgr.add(self.move,"moveTask")

        # Game state variables
        self.isMoving = False

        # Set up the camera
        
        base.disableMouse()
        base.camera.setPos(self.ralph.getX(),self.ralph.getY()+10,2)
        
        # We will detect the height of the terrain by creating a collision
        # ray and casting it downward toward the terrain.  One ray will
        # start above ralph's head, and the other will start above the camera.
        # A ray may hit the terrain, or it may hit a rock or a tree.  If it
        # hits the terrain, we can detect the height.  If it hits anything
        # else, we rule that the move is illegal.

        self.cTrav = CollisionTraverser()

        self.ralphGroundRay = CollisionRay()
        self.ralphGroundRay.setOrigin(0,0,1000)
        self.ralphGroundRay.setDirection(0,0,-1)
        self.ralphGroundCol = CollisionNode('ralphRay')
        self.ralphGroundCol.addSolid(self.ralphGroundRay)
        self.ralphGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.ralphGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.ralphGroundColNp = self.ralph.attachNewNode(self.ralphGroundCol)
        self.ralphGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.ralphGroundColNp, self.ralphGroundHandler)

        self.camGroundRay = CollisionRay()
        self.camGroundRay.setOrigin(0,0,1000)
        self.camGroundRay.setDirection(0,0,-1)
        self.camGroundCol = CollisionNode('camRay')
        self.camGroundCol.addSolid(self.camGroundRay)
        self.camGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.camGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.camGroundColNp = base.camera.attachNewNode(self.camGroundCol)
        self.camGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.camGroundColNp, self.camGroundHandler)

        # Uncomment this line to see the collision rays
        #self.ralphGroundColNp.show()
        #self.camGroundColNp.show()
       
        # Uncomment this line to show a visual representation of the 
        # collisions occuring
        #self.cTrav.showCollisions(render)
        
        # Create some lighting
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor(Vec4(.3, .3, .3, 1))
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection(Vec3(-5, -5, -5))
        directionalLight.setColor(Vec4(1, 1, 1, 1))
        directionalLight.setSpecularColor(Vec4(1, 1, 1, 1))
        render.setLight(render.attachNewNode(ambientLight))
        render.setLight(render.attachNewNode(directionalLight))


    #Records the state of the arrow keys
    def setKey(self, key, value):
        self.keyMap[key] = value
        
    '''method to show player list'''
    def showPlayers(self, set):
        for i in self.temp:
            i.destroy()
        self.temp = []
        y=[]
        i = 0
        while(i!=set.__len__()):
            y.append(0.95-(i*0.05))
            i=i+1
        i = 0
        while(i!=y.__len__()):
            if set[i] == "panda":
                pass
            else:
                self.temp.append(OnscreenText(text=set[i], style=1, fg=(1,1,1,1),
                        pos=(1.3, y[i]), align=TextNode.ARight, scale = .07))
            i=i+1  

    # Accepts arrow keys to move either the player or the menu cursor,
    # Also deals with grid checking and collision detection
    def move(self, task):
        
        '''Call to Show player list'''
        x = self.players.keys()
        self.accept("l", self.showPlayers, [x])
        ''' call end '''

        # If the camera-left key is pressed, move camera left.
        # If the camera-right key is pressed, move camera right.

        base.camera.lookAt(self.ralph)
        if (self.keyMap["cam-left"]!=0):
            base.camera.setX(base.camera, -20 * globalClock.getDt())
        if (self.keyMap["cam-right"]!=0):
            base.camera.setX(base.camera, +20 * globalClock.getDt())

        # save ralph's initial position so that we can restore it,
        # in case he falls off the map or runs into something.

        startpos = self.ralph.getPos()

        # If a move-key is pressed, move ralph in the specified direction.

        if (self.keyMap["left"]!=0):
            self.ralph.setH(self.ralph.getH() + 300 * globalClock.getDt())
        if (self.keyMap["right"]!=0):
            self.ralph.setH(self.ralph.getH() - 300 * globalClock.getDt())
        if (self.keyMap["forward"]!=0):
            self.ralph.setY(self.ralph, -25 * globalClock.getDt())

        # If ralph is moving, loop the run animation.
        # If he is standing still, stop the animation.

        if (self.keyMap["forward"]!=0) or (self.keyMap["left"]!=0) or (self.keyMap["right"]!=0):
            if self.isMoving is False:
                self.ralph.loop("run")
                self.isMoving = True
                self.justStoping = False
        else:
            if self.isMoving:
                self.ralph.stop()
                self.ralph.pose("walk",5)
                self.isMoving = False
                self.justStoping = True
                
        
        #print self.ralph.getX(), self.ralph.getY(), self.ralph.getZ(), self.ralph.getH()
        if(self.isMoving or self.justStoping):       
            self.updateMovement(self.isMoving, self.ralph.getX(), self.ralph.getY(), 
                                self.ralph.getZ(), self.ralph.getH())
            
            #check if in panda attach range
            self.checkPossibleAttack(self.ralph.getX(), self.ralph.getY(), self.ralph.getZ())
            
            player = self.players[self.username]
            player.setX(self.ralph.getX())
            player.setY(self.ralph.getY())
            player.setZ(self.ralph.getZ())
            player.setH(self.ralph.getH())
            self.justStoping = False
        
        # If the camera is too far from ralph, move it closer.
        # If the camera is too close to ralph, move it farther.

        camvec = self.ralph.getPos() - base.camera.getPos()
        camvec.setZ(0)
        camdist = camvec.length()
        camvec.normalize()
        if (camdist > 10.0):
            base.camera.setPos(base.camera.getPos() + camvec*(camdist-10))
            camdist = 10.0
        if (camdist < 5.0):
            base.camera.setPos(base.camera.getPos() - camvec*(5-camdist))
            camdist = 5.0

        # Now check for collisions.

        self.cTrav.traverse(render)

        # Adjust ralph's Z coordinate.  If ralph's ray hit terrain,
        # update his Z. If it hit anything else, or didn't hit anything, put
        # him back where he was last frame.

        entries = []
        for i in range(self.ralphGroundHandler.getNumEntries()):
            entry = self.ralphGroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
            self.ralph.setZ(entries[0].getSurfacePoint(render).getZ())
        else:
            self.ralph.setPos(startpos)

        # Keep the camera at one foot above the terrain,
        # or two feet above ralph, whichever is greater.
        
        entries = []
        for i in range(self.camGroundHandler.getNumEntries()):
            entry = self.camGroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
            base.camera.setZ(entries[0].getSurfacePoint(render).getZ()+1.0)
        if (base.camera.getZ() < self.ralph.getZ() + 2.0):
            base.camera.setZ(self.ralph.getZ() + 2.0)
            
        # The camera should look in ralph's direction,
        # but it should also try to stay horizontal, so look at
        # a floater which hovers above ralph's head.
        
        self.floater.setPos(self.ralph.getPos())
        self.floater.setZ(self.ralph.getZ() + 2.0)
        base.camera.lookAt(self.floater)

        return task.cont
    
    
#     def updatePandaAttack(self,task):
#         
#         if self.targetPlayer != None and "panda" in self.players.keys():
#             panda = self.players["panda"]
#             pandax = panda.getX()
#             panday = panda.getY()
#             pandaz = panda.getZ()
#             
#             x = self.targetPlayer.getX()
#             y = self.targetPlayer.getY()
#             z = self.targetPlayer.getZ()
#             
#             distance = self.getDistance(pandax, panday, pandaz, x, y, z)
#          
#             if distance < PANDA_ATTACK_RANGE:               
#                 print "panda attack"
#                 
#                 pandax = pandax - (pandax - x)/6
#                 panday = panday - (panday - y)/6
#                 pandaz = pandaz - (pandaz - z)/6
#                 
#                 self.pandaObject.move(pandax, panday, pandaz)
#                 
#                 panda.setX(pandax)
#                 panda.setY(panday)
#                 panda.setZ(pandaz)                
#          
#         return task.cont

w = World()
run()

