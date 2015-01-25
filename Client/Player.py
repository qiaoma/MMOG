
class Player:

    def __init__(self, username, x=0.0, y=0.0, z=0.0, h=0.0):
        self.username = username
        self.x = x
        self.y = y
        self.z = z
        self.h = h
    
    def getUsername(self):
        return self.username
    
    def setUsername(self, username):
        self.username = username
        
    def getX(self):
        return self.x
    
    def setX(self, x):
        self.x = x
    
    def getY(self):
        return self.y
    
    def setY(self, y):
        self.y = y 
    
    def getZ(self):
        return self.z
    
    def setZ(self, z):
        self.z = z
    
    def getH(self):
        return self.h
    
    def setH(self, h):
        self.h = h
    
        