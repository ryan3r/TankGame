from abc import ABC, abstractmethod
from Entities import *

FIRE_DAMAGE = 1

class RangeIncreasePolicy(ABC):
	
	@abstractmethod
	def CanIncreaseRange(self, tank):
		pass
	
	@abstractmethod
	def PerformRangeIncrease(self, tank):
		pass
		
class ApCostRangeIncreasePolicy(RangeIncreasePolicy):
	
	def __init__(self, ap_cost):
		self.cost = ap_cost
		
	def CanIncreaseRange(self, tank):
		return tank.HasAp(self.cost)
		
	def PerformRangeIncrease(self, tank):
		tank.SpendAp(self.cost)
		tank.IncreaseRange()
		
class GoldCostRangeIncreasePolicy(RangeIncreasePolicy):
	
	def __init__(self, gold_cost):
		self.cost = gold_cost
		
	def CanIncreaseRange(self, tank):
		return tank.HasGold(self.cost)
		
	def PerformRangeIncrease(self, tank):
		tank.SpendGold(self.cost)
		tank.IncreaseRange()
		
class MoveRule(ABC):
	
	@abstractmethod
	def CanMove(self, board, tank, target):
		pass
	
	@abstractmethod
	def PerformMove(self, board, tank, target):
		pass
		
class ApCostMoveRule(MoveRule):

	def __init__(self, ap_cost):
		self.cost = ap_cost
		
	def CanMove(self, board, tank, target):
		dist = Distance(tank.position, target)
		if dist > 1:
			board.Render()
			raise Exception("Must only move 1 space at a time.")
		if board.IsSpaceOccupied(target):
			board.Render()
			raise Exception(f"targetPosition {target} is occupied.")
		if not tank.HasAp(self.cost): raise Expection("Not enough AP to move.")
		return True
	
	def PerformMove(self, board, tank, target):
		board.RemoveEntity(tank)
		tank.position = target
		board.AddEntity(tank)
		
class GameRules:
	
	def __init__(self, startingGold, maxAp, fireApCost, apPerTurn, wallDur, rangeIncreasePolicy, moveRule):
		self._fireApCost = fireApCost
		self._maxAp = maxAp
		self._startingGold = startingGold
		self._apPerTurn = apPerTurn
		self._wallDurability = wallDur
		self.rangeIncreasePolicy = rangeIncreasePolicy
		self.moveRule = moveRule
		
	def GetFireApCost(self, tank):
		return self._fireApCost
		
	def GetMaxAp(self, tank):
		return self._maxAp
		
	def GetStartingGold(self, tank):
		return self._startingGold
		
	def GetApPerTurn(self, tank):
		return self._apPerTurn
		
	def GetDefaultWallDurability(self):
		return self._wallDurability

class GameController:

	def __init__(self, width, height, game_rules):
		self.board = Board(width, height)
		self.walls = []
		self.tanks = []
		self.goldMines = []
		self.gameRules = game_rules

	def AddWall(self, position):
		newWall = Wall(position, self.gameRules.GetDefaultWallDurability())
		self.board.AddEntity(newWall)
		self.walls.append(newWall)

	def AddTank(self, position, owner, **tankArgs):
		newTank = Tank(position, owner, **tankArgs)
		newTank._gold = self.gameRules.GetStartingGold(newTank)
		self.board.AddEntity(newTank)
		self.tanks.append(newTank)

	def StartOfTurn(self):
		for tank in self.tanks:
			if tank.lives > 0: self._GiveTankAp(tank, self.gameRules.GetApPerTurn(tank))

		if not self.goldMines: return
		for mine in self.goldMines:
			mine.AwardGold(self.tanks)

	def PerformMove(self, owner, targetPosition):
		actor = self._GetTankByOwner(owner)
		try:
			self.gameRules.moveRule.CanMove(self.board, actor, targetPosition)
			self.gameRules.moveRule.PerformMove(self.board, actor, targetPosition)
		except Exception as e:
			print("An error ocurred: ", e)

	def PerformFire(self, owner, targetPosition, doesHit=True):
		actor = self._GetTankByOwner(owner)
		dist = Distance(actor.position, targetPosition)
		if dist > actor.range:
			raise Exception("targetPosition is out of range.")
		if actor.AP < self.gameRules.GetFireApCost(actor): 
			raise Expection("Not enough AP to Fire.")
		targetObject = self.board.grid[targetPosition.x][targetPosition.y]
		if not self.board.DoesLineOfSightExist(actor, targetObject):
			self.board.Render()
			raise Exception("No line of sight on targetPosition.")
		
		actor.AP -= self.gameRules.GetFireApCost(actor)
		if doesHit:
			remove_from_board, attack_drops = targetObject.TakeDamage(actor, FIRE_DAMAGE)
			self._GiveTankAttackDrops(actor, attack_drops)
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
		self._GiveTankAp(target, amount)

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
		if not actor.HasGold(amount):
			raise Exception("Not enough gold.")
		ap_value = self._DetermineTradeValue(amount)
		actor.SpendGold(amount)
		self._GiveTankAp(actor, ap_value)

	def PerformUpgrade(self, owner):
		actor = self._GetTankByOwner(owner)
		if not self.gameRules.rangeIncreasePolicy.CanIncreaseRange(actor): raise Exception("Cannot increase range.")
		self.gameRules.rangeIncreasePolicy.PerformRangeIncrease(actor)
		
	def _GiveTankAttackDrops(self, tank, attackDrops):
		self._GiveTankAp(tank, attackDrops.AP)
		tank.GainGold(attackDrops.gold)
		tank.kills += attackDrops.kills
		tank.lives += attackDrops.lives
		
	def _GiveTankAp(self, tank, amount):
		tank.AP = min(self.gameRules.GetMaxAp(tank), tank.AP + amount)

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