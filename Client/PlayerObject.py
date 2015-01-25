from panda3d.core import CollisionTraverser,CollisionNode
from panda3d.core import CollisionHandlerQueue,CollisionRay
from panda3d.core import Vec3,Vec4,BitMask32
from direct.actor.Actor import Actor

class PlayerObject():
	def __init__(self, render, player):
		self.username = player.getUsername()
		self.isMoving = False
		self.render = render

		self.keyMap = {"left":0, "right":0, "forward":0, "cam-left":0, "cam-right":0}

		self.actor = Actor("models/ralph", {"run":"models/ralph-run", "walk":"models/ralph-walk"})
		self.actor.reparentTo(render)
		self.actor.setScale(0.2)
		self.actor.setPos(player.getX(), player.getY(), player.getZ())
		self.actor.setH(player.getH())

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

# 	def getUsername(self):
# 		return self.username
	
	def getActor(self):
		return self.actor
	
	def setPos(self, x, y, z):
		self.actor.setPos(x, y, z)
		
	def setH(self, h):
		self.actor.setH(h)

	def move(self, isActorMove):
		if isActorMove == "True":
			if self.isMoving is False:
				self.actor.loop("run")
				self.isMoving = True
		else:
			if self.isMoving:
				self.actor.stop()
				self.actor.pose("walk",5)
				self.isMoving = False

