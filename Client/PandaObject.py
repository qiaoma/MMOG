from panda3d.core import CollisionTraverser,CollisionNode
from panda3d.core import CollisionHandlerQueue,CollisionRay
from panda3d.core import Vec3,Vec4,BitMask32
from direct.actor.Actor import Actor
from panda3d.core import Point3
from direct.interval.IntervalGlobal import Sequence

class PandaObject():
	def __init__(self, render, player):
		self.username = player.getUsername()
		self.isMoving = False
		self.render = render

		self.keyMap = {"left":0, "right":0, "forward":0, "cam-left":0, "cam-right":0}

		#self.actor = Actor("models/ralph", {"run":"models/ralph-run", "walk":"models/ralph-walk"})
		self.actor = Actor("models/panda-model",
                                {"walk": "models/panda-walk4"})
		self.actor.reparentTo(render)
		self.actor.setScale(0.002, 0.002, 0.002)
		self.actor.setPos(player.getX(), player.getY(), player.getZ())
		self.actor.setH(player.getH())	
		
		#self.actor.loop("walk")
		
		self.cTrav = CollisionTraverser()
		self.GroundRay = CollisionRay()
		self.GroundRay.setOrigin(0,0,1000)
		self.GroundRay.setDirection(0,0,-1)
		self.GroundCol = CollisionNode('actorRay')
		self.GroundCol.addSolid(self.GroundRay)
		self.GroundCol.setFromCollideMask(BitMask32.bit(0))
		self.GroundCol.setIntoCollideMask(BitMask32.allOff())
		self.GroundColNp = self.actor.attachNewNode(self.GroundCol)
		self.GroundHandler = CollisionHandlerQueue()
		self.cTrav.addCollider(self.GroundColNp, self.GroundHandler)

	def getActor(self):
		return self.actor
	
	def setPos(self, x, y, z):
		self.actor.setPos(x, y, z)
		
	def setH(self, h):
		self.actor.setH(h)
		
	def move(self, endx, endy, endz):
		self.actor.loop("walk")
		
# 		pandaPosInterval1 = self.pandaActor.posInterval(13, Point3(0, -10, 0), startPos=Point3(0, 10, 0))
# 		pandaPosInterval2 = self.pandaActor.posInterval(13, Point3(0, 10, 0), startPos=Point3(0, -10, 0))
# 		pandaHprInterval1 = self.pandaActor.hprInterval(3, Point3(180, 0, 0), startHpr=Point3(0, 0, 0))
# 		pandaHprInterval2 = self.pandaActor.hprInterval(3, Point3(0, 0, 0), startHpr=Point3(180, 0, 0))
# 
# 		# Create and play the sequence that coordinates the intervals.
# 
# 		self.pandaPace = Sequence(pandaPosInterval1, pandaHprInterval1, pandaPosInterval2, pandaHprInterval2, name="pandaPace")

# 		pandaPosInterval1 = self.actor.posInterval(8, Point3(endx, endy, endz), 
# 													startPos=Point3(startx, starty, startz))
		
		#pandaHprInterval1 = self.actor.hprInterval(2, Point3(angle, 0, 0))
		pandaPosInterval1 = self.actor.posInterval(4, Point3(endx, endy, endz))
		#self.pandaPace = Sequence(pandaHprInterval1, pandaPosInterval1, name="pandaPace")
		#self.pandaPace.loop()
		#self.pandaPace.start()
		pandaPosInterval1.start()
		
	def turn(self, angle):
		pandaHprInterval1 = self.actor.hprInterval(2, Point3(angle, 0, 0))
		pandaHprInterval1.start()
