STARTING_LIVES = 3
STARTING_RANGE = 2
STARTING_GOLD = 0

WALL_STARTING_DURABILITY = 5

AP_PER_TURN = 2
AP_MAX = 9

FIRE_DAMAGE = 1

#AP COSTS
MOVE_AP_COST = 1
FIRE_AP_COST = 2
UPGRADE_AP_COST = 5

class Position():

	def __init__(self, x, y):
		self.x = x
		self.y = y

class Tank():

	def __init__(self, position, owner):
		self.position = position
		self.owner = owner
		self.lives = STARTING_LIVES
		self.AP = 0
		self.gold = STARTING_GOLD
		self.range = STARTING_RANGE
		self.kills = 0
		self._totalMoves = 0
		
	def PerformMove(self, targetPos):
		self.AP -= MOVE_AP_COST
		self.position = target
		self._totalMoves += 1
		
	def PerformFire(self):
		self.AP -= FIRE_AP_COST
		
	def PerformUpgrade(self):
		self.AP -= UPGRADE_AP_COST
		self.range += 1
		
	def DoesShotHit(self, actor):
		if random() > 0.333333333: return true
		return false
		
	def TakeDamage(self, amount):
		self.lives = max(0, self.lives - amount)
		if self.lives == 0:
			self.Die()
			return true
		return false
		
	def Die(self):
		self.AP = 0

class Wall():

	def __init__(self, position):
		self.position = position
		self.durability = WALL_STARTING_DURABILITY
		
	def DoesShotHit(self, actor):
		return true
		
	def TakeDamage(self, amount):
		self.durability = max(0, self.durability - amount)
		if self.durability == 0:
			self.Die()
			return true
		return false
		
	def Die(self):
		return
		
class Council():

	def __init__(self):
		self.councilors = []
		self.senators = []
		
class GoldMine():
	
	def __init__(self):
		self.spaces = []
		self.goldPerDay = 8
		
	def AddSpace(self, position):
		self.spaces.append(position)
		
	def AwardGold(self, tanksList):
		tanksInMine = []
		for tank in tanksList:
			for space in self.spaces:
				if tank.position.x == space.x and tank.position.y == space.y: tanksInMine.append(tank)
		
		awardPerTank = self.goldPerDay // len(tanksInMine)
		for tank in tanksInMine:
			tank.gold += awardPerTank
	
class Board():

	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.walls = []
		self.tanks = []
		self.grid = [ [ None for y in range( height ) ] for x in range( width ) ]
		self.goldMines = []
		
	def AddWall(self, position):
		if self.IsSpaceOccupied(position): raise Exception("Cannot add Wall there, the space is occupied")
		newWall = Wall(position)
		self.walls.append(newWall)
		self.grid[position.x][position.y] = newWall
		
	def AddTank(self, position, owner):
		if self.IsSpaceOccupied(position): raise Exception("Cannot add Tank there, the space is occupied")
		newTank = Tank(position, owner)
		self.tanks.append(newTank)
		self.grid[position.x][position.y] = newTank
		
	def StartOfTurn(self):
		for tank in self.tanks:
			if tank.lives > 0: tank.AP = min(AP_MAX, tank.AP + AP_PER_TURN)
		
		if not self.goldMines: return
		for mine in self.goldMines:
			mine.AwardGold(self.tanks)
		
	def PerformMove(self, actor, targetPosition):
		dist = Distance(actor.position, targetPosition)
		if dist > 1: raise Exception("Must only move 1 space at a time.")
		if self.IsSpaceOccupied(targetPosition): raise Exception("targetPosition position is occupied.")
		if actor.AP < MOVE_AP_COST: raise Expection("Not enough AP to move.")
		actor.PerformMove(targetPosition)
		
	def PerformFire(self, actor, targetPosition):
		dist = Distance(actor.position, targetPosition)
		if dist > actor.range: raise Exception("targetPosition is out of range.")
		if actor.AP < FIRE_AP_COST: raise Expection("Not enough AP to Fire.")
		if not self.DoesLineOfSightExist(actor.position, targetPosition): raise Exception("No line of sight on targetPosition.")
		actor.PerformFire()
		
		targetObject = self.grid[targetPosition.x][targetPosition.y]
		isHit = targetObject.DoesShotHit(actor)
		if isHit: isDestroyed = targetObject.TakeDamage(FIRE_DAMAGE)
		# TODO: finish this
		
	def PerformShareActions(self, actor, target, amount):
		dist = Distance(actor.position, target.position)
		if dist > actor.range: raise Exception("target is out of range.")
		cost = DetermineShareCost(amount)
		if actor.AP < (amount + cost): raise Exception("Not enough AP to Share.")
		actor.AP -= (amount + cost)
		target.AP += amount
		
	def PerformShareLife(self, actor, target):
		dist = Distance(actor.position, target.position)
		if dist > actor.range: raise Exception("target is out of range.")
		actor.lives -= 1
		if target.lives != 3: target.lives += 1
		
	def PerformTradeGold(self, actor, amount):
		if actor.gold < amount: raise Exception("Not enough gold.")
		ap_value = DetermineTradeValue(amount)
		actor.gold -= amount
		actor.AP += ap_value
		
	def PerformUpgrade(self, actor):
		if actor.AP < UPGRADE_AP_COST: raise Exception("Not enough AP to Upgrade.")
		actor.PerformUpgrade()
		
	def DetermineTradeValue(amount):
		if amount % 3 != 0: raise Exception("Must trade gold in multiples of three")
		return amount // 3
		
	def DetermineShareCost(amount):
		return 0
		
	def DoesLineOfSightExist(self, posA, posB):
		# TODO: implement this
		return true
		
	def IsSpaceOccupied(self, position):
		return (self.grid[position.x][position.y] != None)
	
def Distance(posA, posB):
	xDiff = abs(posA.x - posB.x)
	yDiff = abs(posA.y - posB.y)
	return max(xDiff, yDiff)
	
def RenderBoard(board):
	#for y in range(board.height):
	#	for x in range(board.width):
	#		if (board.grid[x][y] == None):
	return
	
def PrintTanks(board):
	for tank in board.tanks:
		PrintTank(tank)
		
def PrintTank(tank):
	print("{} -\tPosition: {},{}\tLives: {}\tRange: {}\tAP: {}\tGold: {}".format(tank.owner, tank.position.x, tank.position.y, tank.lives, tank.range, tank.AP, tank.gold))
	
if __name__ == "__main__":
	board = Board(9, 9)
	
	mine = GoldMine()
	mine.AddSpace(Position(2, 2))
	mine.AddSpace(Position(4, 1))
	board.goldMines.append(mine)
	
	board.AddTank(Position(2, 2), "Ryan")
	board.AddTank(Position(4, 1), "Beyer")
	print("INITIAL SETUP")
	PrintTanks(board)
	
	board.StartOfTurn()
	print("START OF DAY 1")
	PrintTanks(board)
		