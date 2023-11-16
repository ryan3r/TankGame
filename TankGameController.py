from Entities import *

class GameController:

	def __init__(self, width, height):
		self.board = Board(width, height)
		self.walls = []
		self.tanks = []
		self.goldMines = []

	def AddWall(self, position):
		newWall = Wall(position)
		self.board.AddEntity(newWall)
		self.walls.append(newWall)

	def AddTank(self, position, owner, **tankArgs):
		newTank = Tank(position, owner, **tankArgs)
		self.board.AddEntity(newTank)
		self.tanks.append(newTank)

	def StartOfTurn(self):
		for tank in self.tanks:
			if tank.lives > 0: tank.GainAP(AP_PER_TURN)

		if not self.goldMines: return
		for mine in self.goldMines:
			mine.AwardGold(self.tanks)

	def PerformMove(self, owner, targetPosition):
		actor = self._GetTankByOwner(owner)
		dist = Distance(actor.position, targetPosition)
		if dist > 1: raise Exception("Must only move 1 space at a time.")
		if self.board.IsSpaceOccupied(targetPosition): raise Exception("targetPosition position is occupied.")
		if actor.AP < MOVE_AP_COST: raise Expection("Not enough AP to move.")
		self.board.RemoveEntity(actor)
		actor.PerformMove(targetPosition)
		self.board.AddEntity(actor)

	def PerformFire(self, owner, targetPosition, doesHit=True):
		actor = self._GetTankByOwner(owner)
		dist = Distance(actor.position, targetPosition)
		if dist > actor.range: raise Exception("targetPosition is out of range.")
		if actor.AP < FIRE_AP_COST: raise Expection("Not enough AP to Fire.")
		targetObject = self.board.grid[targetPosition.x][targetPosition.y]
		if not self.board.DoesLineOfSightExist(actor, targetObject): raise Exception("No line of sight on targetPosition.")
		
		actor.PerformFire()
		if doesHit:
			remove_from_board, attack_drops = targetObject.TakeDamage(actor, FIRE_DAMAGE)
			actor.GainAttackDrops(attack_drops)
			if remove_from_board:
				self.board.RemoveEntity(targetObject)
				# TODO: add TankWall if necessary

	def PerformShareActions(self, owner, targetOwner, amount):
		target = self._GetTankByOwner(targetOwner)
		actor = self._GetTankByOwner(owner)
		dist = Distance(actor.position, target.position)
		if dist > actor.range: raise Exception("target is out of range.")
		cost = self._DetermineShareCost(amount)
		if actor.AP < (amount + cost): raise Exception("Not enough AP to Share.")
		# TODO: check if player has done share today
		actor.AP -= (amount + cost)
		target.GainAP(amount)

	def PerformShareLife(self, owner, targetOwner):
		target = self._GetTankByOwner(targetOwner)
		actor = self._GetTankByOwner(owner)
		dist = Distance(actor.position, target.position)
		if dist > actor.range: raise Exception("target is out of range.")
		# TODO: check if player has done share today
		actor.lives -= 1
		# TODO: check if player is dead now
		if target.lives != 3: target.lives += 1

	def PerformTradeGold(self, owner, amount):
		actor = self._GetTankByOwner(owner)
		if actor.gold < amount: raise Exception("Not enough gold.")
		ap_value = self._DetermineTradeValue(amount)
		actor.gold -= amount
		actor.GainAP(ap_value)

	def PerformUpgrade(self, owner):
		actor = self._GetTankByOwner(owner)
		if actor.AP < UPGRADE_AP_COST: raise Exception("Not enough AP to Upgrade.")
		actor.PerformUpgrade()

	def _DetermineTradeValue(self, amount):
		if amount % 3 != 0: raise Exception("Must trade gold in multiples of three")
		return amount // 3

	def _DetermineShareCost(self, amount):
		return 0
		
	def _GetTankByOwner(self, owner):
		for tank in self.tanks:
			if owner == tank.owner or owner == tank.tile:
				return tank
		raise Exception("No tank found with owner name: " + owner + "!")
		
def Distance(posA, posB):
	xDiff = abs(posA.x - posB.x)
	yDiff = abs(posA.y - posB.y)
	return max(xDiff, yDiff)