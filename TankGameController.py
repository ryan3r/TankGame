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
		
class TransferGoldRule(ABC):
	
	@abstractmethod
	def CanTransferGold(self, actor, target, amount):
		pass
		
	@abstractmethod
	def PerformTransferGold(self, actor, target, amount):
		pass
		
class TaxedGoldTransferRule(TransferGoldRule):

	def __init__(self, tax_amt, council):
		self.tax = tax_amt
		self.council_ref = council
		
	def CanTransferGold(self, actor, target, amount):
		dist = Distance(actor.position, target.position)
		if dist > actor.GetRange(): return False
		return actor.HasGold(amount + self.tax)
		
	def PerformTransferGold(self, actor, target, amount):
		actor.SpendGold(amount + self.tax)
		target.GainGold(amount)
		self.council_ref.coffer += self.tax
		
class NoGoldTransferRule(TransferGoldRule):

	def __init__(self):
		return
		
	def CanTransferGold(self, actor, target, amount):
		return False
		
	def PerformTransferGold(self, actor, target, amount):
		raise Exception("Rules forbid Gold Transfer")

class GiveApRule(ABC):
	
	@abstractmethod
	def CanGiveAp(self, actor, target, amount):
		pass
		
	@abstractmethod
	def PerformGiveAp(self, actor, target, amount):
		pass
		
	@abstractmethod
	def OnStartOfDay(self):
		pass
		
class OncePerDayGiveApRule(GiveApRule):

	def __init__(self, list_ref):
		self.actorList = list_ref
	
	def CanGiveAp(self, actor, target, amount):
		if amount is not 1: raise Exception("May only give one AP per day")
		if actor in self.actorList: return False
		if not actor.HasAp(): return False
		dist = Distance(actor.position, target.position)
		if dist > actor.range: return False
		return True
		
	def PerformGiveAp(self, actor, target, amount):
		self.actorList.append(actor)
		actor.SpendAp(1)
		target.GainAp(1)
		
	def OnStartOfDay(self):
		self.actorList = []
		
class NoGiveApRule(GiveApRule):

	def __init__(self):
		return
	
	def CanGiveAp(self, actor, target, amount):
		return False
		
	def PerformGiveAp(self, actor, target, amount):
		raise Exception("The rules forbid giving AP")
		
	def OnStartOfDay(self):
		return
		
class GiveLifeRule(ABC):
	
	@abstractmethod
	def CanGiveLife(self, actor, target, amount):
		pass
		
	@abstractmethod
	def PerformGiveLife(self, actor, target, amount):
		pass
		
	@abstractmethod
	def OnStartOfDay(self):
		pass
		
class OncePerDayGiveLifeRule(GiveLifeRule):

	def __init__(self, list_ref):
		self.actorList = list_ref
	
	def CanGiveLife(self, actor, target, amount):
		if amount is not 1: raise Exception("May only give one Life per day")
		if actor in self.actorList: return False
		if not actor.HasLife(): return False
		dist = Distance(actor.position, target.position)
		if dist > actor.range: return False
		return True
		
	def PerformGiveLife(self, actor, target, amount):
		self.actorList.append(actor)
		actor.LoseLife()
		target.GainLife()
		
	def OnStartOfDay(self):
		self.actorList = []
		
class NoGiveLifeRule(GiveApRule):

	def __init__(self):
		return
	
	def CanGiveLife(self, actor, target, amount):
		return False
		
	def PerformGiveLife(self, actor, target, amount):
		raise Exception("The rules forbid giving Lives")
		
	def OnStartOfDay(self):
		return

class TradeGoldRule(ABC):

	@abstractmethod
	def CanTradeGold(self, actor, amount):
		pass
		
	@abstractmethod
	def PerformTradeGold(self, actor, amount):
		pass
		
class FlatRateTradeGoldRule(ABC):
	
	def __init__(self, goldPerAp):
		self.goldPerAp = goldPerAp
		
	def CanTradeGold(self, actor, amount):
		try:
			apValue = self._DetermineTradeValue(amount)
			return actor.HasGold(amount)
		except:
			return False
			
	def PerformTradeGold(self, actor, amount):
		apValue = self._DetermineTradeValue(amount)
		actor.SpendGold(amount)
		actor.GainAp(apValue)
	
	def _DetermineTradeValue(self, amount):
		if amount % self.goldPerAp != 0: raise Exception(f'Must trade gold in multiples of {self.goldPerAp}')
		return amount // self.goldPerAp
		
class TableRateTradeGoldRule(ABC):
	
	def __init__(self, tradeTable):
		self.tradeTable = tradeTable
		
	def CanTradeGold(self, actor, amount):
		try:
			apValue = self._DetermineTradeValue(amount)
			return actor.HasGold(amount)
		except:
			return False
			
	def PerformTradeGold(self, actor, amount):
		apValue = self._DetermineTradeValue(amount)
		actor.SpendGold(amount)
		actor.GainAp(apValue)
	
	def _DetermineTradeValue(self, amount):
		if amount not in self.tradeTable: raise Exception(f'Trade amount {amount} is not in trade table keys: {self.tradeTable.keys()}')
		return self.tradeTable[amount]

class GameRules:
	
	def __init__(self, startingGold, maxAp, fireApCost, apPerTurn, wallDur, rangeIncreasePolicy, moveRule, goldTransferRule, giveApRule, giveLifeRule, tradeGoldRule):
		self._fireApCost = fireApCost
		self._maxAp = maxAp
		self._startingGold = startingGold
		self._apPerTurn = apPerTurn
		self._wallDurability = wallDur
		self.rangeIncreasePolicy = rangeIncreasePolicy
		self.moveRule = moveRule
		self.goldTransferRule = goldTransferRule
		self.giveApRule = giveApRule
		self.giveLifeRule = giveLifeRule
		self.tradeGoldRule = tradeGoldRule
		
	def OnStartOfDay(self):
		self.giveApRule.OnStartOfDay()
		self.giveLifeRule.OnStartOfDay()
		
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
		self.council = Council()

	def AddWall(self, position):
		newWall = Wall(position, self.gameRules.GetDefaultWallDurability())
		self.board.AddEntity(newWall)
		self.walls.append(newWall)

	def AddTank(self, position, owner, **tankArgs):
		newTank = Tank(position, owner, **tankArgs)
		newTank._gold = self.gameRules.GetStartingGold(newTank)
		newTank.maxAp = self.gameRules.GetMaxAp(newTank)
		self.board.AddEntity(newTank)
		self.tanks.append(newTank)

	def StartOfTurn(self):
		self.gameRules.OnStartOfDay()
		
		for tank in self.tanks:
			if tank.lives > 0: tank.GainAp(self.gameRules.GetApPerTurn(tank))

		if not self.goldMines: return
		for mine in self.goldMines:
			mine.AwardGold(self.tanks, self.council)

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
		if self.gameRules.giveApRule.CanGiveAp(actor, target, amount):
			self.gameRules.giveApRule.PerformGiveAp(actor, target, amount)

	def PerformShareLife(self, owner, targetOwner, amount = 1):
		target = self._GetTankByOwner(targetOwner)
		actor = self._GetTankByOwner(owner)
		if self.gameRules.giveLifeRule.CanGiveLife(actor, target, amount):
			self.gameRules.giveLifeRule.PerformGiveLife(actor, target, amount)

	def PerformTradeGold(self, owner, amount):
		actor = self._GetTankByOwner(owner)
		if self.gameRules.tradeGoldRule.CanTradeGold(actor, amount):
			self.gameRules.tradeGoldRule.PerformTradeGold(actor, amount)

	def PerformUpgrade(self, owner):
		actor = self._GetTankByOwner(owner)
		if not self.gameRules.rangeIncreasePolicy.CanIncreaseRange(actor): raise Exception("Cannot increase range.")
		self.gameRules.rangeIncreasePolicy.PerformRangeIncrease(actor)
		
	def PerformTransferGold(self, owner, targetOwner, amount):
		actor = self._GetTankByOwner(owner)
		target = self._GetTankByOwner(targetOwner)
		if self.gameRules.goldTransferRule.CanTransferGold(actor, target, amount):
			self.gameRules.goldTransferRule.PerformTransferGold(actor, target, amount)
		
	def _GiveTankAttackDrops(self, tank, attackDrops):
		tank.GainAp(attackDrops.AP)
		tank.GainGold(attackDrops.gold)
		tank.kills += attackDrops.kills
		tank.lives += attackDrops.lives
		
	def _GetTankByOwner(self, owner):
		for tank in self.tanks:
			if owner == tank.owner or owner == tank.tile:
				return tank
		raise Exception("No tank found with owner name: " + owner + "!")
		
def Distance(posA, posB):
	xDiff = abs(posA.x - posB.x)
	yDiff = abs(posA.y - posB.y)
	return max(xDiff, yDiff)