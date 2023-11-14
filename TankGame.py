import logging
from collections import namedtuple

logger = logging.getLogger(__name__)

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

Position = namedtuple("Position", ["x", "y"])


class Tank:

	def __init__(self, position, owner, tile=None):
		self.position = position
		self.owner = owner
		self.lives = STARTING_LIVES
		self.AP = 0
		self.gold = STARTING_GOLD
		self.range = STARTING_RANGE
		self.kills = 0
		self._totalMoves = 0
		self.tile = tile if tile is not None else self.owner[:2]

	def PerformMove(self, targetPos):
		self.AP -= MOVE_AP_COST
		self.position = target
		self._totalMoves += 1

	def PerformFire(self):
		self.AP -= FIRE_AP_COST

	def PerformUpgrade(self):
		self.AP -= UPGRADE_AP_COST
		self.range += 1
		
	def GainAP(self, amount_to_gain):
		self.AP = min(AP_MAX, self.AP + amount_to_gain)

	def DoesShotHit(self, actor):
		if random() > 0.333333333: return True
		return False

	def TakeDamage(self, amount):
		self.lives = max(0, self.lives - amount)
		if self.lives == 0:
			self.Die()
			return True
		return False

	def Die(self):
		self.AP = 0

	def __str__(self):
		return f"{self.owner:15} - {self.position.x:2},{self.position.y:2} Lives: {self.lives} Range: {self.range} AP: {self.AP} Gold: {self.gold:2}"

class Wall:

	def __init__(self, position):
		self.position = position
		self.durability = WALL_STARTING_DURABILITY

	def DoesShotHit(self, actor):
		return True

	def TakeDamage(self, amount):
		self.durability = max(0, self.durability - amount)
		if self.durability == 0:
			self.Die()
			return True
		return False

	def Die(self):
		return

	@property
	def tile(self):
		return f"W{self.durability}"

class Council:

	def __init__(self):
		self.councilors = []
		self.senators = []

class GoldMine:

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

		if not tanksInMine: return
		awardPerTank = self.goldPerDay // len(tanksInMine)
		for tank in tanksInMine:
			tank.gold += awardPerTank


class Board:
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.grid = [ [ None for y in range(height) ] for x in range(width) ]

	def IsSpaceOccupied(self, position):
		return self.grid[position.x][position.y] != None

	def AddEntity(self, entity):
		if self.IsSpaceOccupied(entity.position):
			raise Exception(f"The space {entity.position} is already occupied can't add {entity}")

		self.grid[entity.position.x][entity.position.y] = entity

	def RemoveEntity(self, entity):
		gridSpace = self.grid[entity.position.x][entity.position.y]
		assert gridSpace != entity, \
			f"Entity's position does not match the board state (position = {entity.position}, boardEntity = {gridSpace})"
		self.grid[entity.position.x][entity.position.y] = None

	def Render(self):
		"""Render the game board to stdout using a series of 2 character tiles to represent each space."""
		for y in range(self.height):
			row = ""

			for x in range(self.width):
				tile = "  "
				if self.grid[x][y] is not None:
					tile = self.grid[x][y].tile

				if x > 0:
					row += "|"

				row += tile

			if y > 0:
				separator = self.width * "--+"
				print(separator[:-1])

			print(row)

		print()

	def DoesLineOfSightExist(self, initiator, target, ignoredEntities=[]):
		"""
		Check if the initiator can see the target.

		ignoredEntities - A list of types of entities that will not block line of sight
		"""
		# Vertical lines doesn't work for slow intercept form but we can simply walk the spaces between the target and initiator
		if target.position.x == initiator.position.x:
			direction = -1 if target.position.y - initiator.position.y < 0 else 1
			for y in range(initiator.position.y + direction, target.position.y, direction):
				entity = self.grid[target.position.x][y]
				if entity is not None and type(entity) not in ignoredEntities:
					logger.debug("Vertical hit: %s", entity)
					return False

			return True

		min_x = min(initiator.position.x, target.position.x)
		max_x = max(initiator.position.x, target.position.x)
		min_y = min(initiator.position.y, target.position.y)
		max_y = max(initiator.position.y, target.position.y)

		# Find all entitys that we could intercept with this is important because the lines we use in our equations are
		# infinatly long.  So we don't want to check if entitys behind the target intercept with our line of sight because
		# the next part would say they do.
		possible_intercepts = []
		for x in range(min_x, max_x + 1):
			for y in range(min_y, max_y + 1):
				current = Position(x, y)
				if self.grid[x][y] is not None and initiator.position != current and target.position != current \
						and type(self.grid[x][y]) not in ignoredEntities:
					possible_intercepts.append(self.grid[x][y])

		logger.debug("Possible intercepts: %s", possible_intercepts)

		slope = (target.position.y - initiator.position.y) / (target.position.x - initiator.position.x)
		b = (initiator.position.y + 0.5) - (slope * initiator.position.x)

		logger.debug("Line of sight equation: y = %dx + %d", slope, b)

		for intercept in possible_intercepts:
			line_y = (slope * intercept.position.x) + b
			logger.debug("Checking if %s intercepts with line of sight Los(%d) = %d", intercept.position, intercept.position.x, line_y)
			if abs(line_y - (intercept.position.y + 0.5)) < 0.4999:
				logger.debug(f"Hit %s", intercept.position)
				return False

		return True


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
		if not self.board.DoesLineOfSightExist(actor.position, targetPosition): raise Exception("No line of sight on targetPosition.")
		actor.PerformFire()

		targetObject = self.board.grid[targetPosition.x][targetPosition.y]
		isHit = targetObject.DoesShotHit(actor)
		if isHit: isDestroyed = targetObject.TakeDamage(FIRE_DAMAGE)
		# TODO: finish this

	def PerformShareActions(self, actor, target, amount):
		dist = Distance(actor.position, target.position)
		if dist > actor.range: raise Exception("target is out of range.")
		cost = DetermineShareCost(amount)
		if actor.AP < (amount + cost): raise Exception("Not enough AP to Share.")
		actor.AP -= (amount + cost)
		target.GainAP(amount)

	def PerformShareLife(self, actor, target):
		dist = Distance(actor.position, target.position)
		if dist > actor.range: raise Exception("target is out of range.")
		actor.lives -= 1
		if target.lives != 3: target.lives += 1

	def PerformTradeGold(self, actor, amount):
		if actor.gold < amount: raise Exception("Not enough gold.")
		ap_value = DetermineTradeValue(amount)
		actor.gold -= amount
		actor.GainAP(ap_value)

	def PerformUpgrade(self, actor):
		if actor.AP < UPGRADE_AP_COST: raise Exception("Not enough AP to Upgrade.")
		actor.PerformUpgrade()

	def DetermineTradeValue(amount):
		if amount % 3 != 0: raise Exception("Must trade gold in multiples of three")
		return amount // 3

	def DetermineShareCost(amount):
		return 0


def Distance(posA, posB):
	xDiff = abs(posA.x - posB.x)
	yDiff = abs(posA.y - posB.y)
	return max(xDiff, yDiff)


def PrintTanks(controller):
	for tank in controller.tanks:
		print(tank)


if __name__ == "__main__":
	controller = GameController(9, 9)

	mine = GoldMine()
	mine.AddSpace(Position(3, 3))
	mine.AddSpace(Position(4, 3))
	mine.AddSpace(Position(5, 3))
	mine.AddSpace(Position(3, 4))
	mine.AddSpace(Position(4, 4))
	mine.AddSpace(Position(5, 4))
	mine.AddSpace(Position(3, 5))
	mine.AddSpace(Position(4, 5))
	mine.AddSpace(Position(5, 5))
	controller.goldMines.append(mine)

	controller.AddWall(Position(3, 2))
	controller.AddWall(Position(4, 2))
	controller.AddWall(Position(5, 2))
	controller.AddWall(Position(6, 3))
	controller.AddWall(Position(6, 4))
	controller.AddWall(Position(6, 5))
	controller.AddWall(Position(5, 6))
	controller.AddWall(Position(4, 6))
	controller.AddWall(Position(3, 6))
	controller.AddWall(Position(2, 5))
	controller.AddWall(Position(2, 4))
	controller.AddWall(Position(2, 3))

	controller.AddTank(Position(1, 1), "Ryan")
	controller.AddTank(Position(3, 0), "Beyer")
	controller.AddTank(Position(5, 0), "Taylore")
	controller.AddTank(Position(7, 1), "John")
	controller.AddTank(Position(8, 3), "Marci")
	controller.AddTank(Position(8, 5), "Stomp")
	controller.AddTank(Position(7, 7), "David K.", tile="DK")
	controller.AddTank(Position(5, 8), "David Y.", tile="DY")
	controller.AddTank(Position(3, 8), "Dan")
	controller.AddTank(Position(1, 7), "Corey")
	controller.AddTank(Position(0, 5), "Mike")
	controller.AddTank(Position(0, 3), "Ty")

	print("INITIAL SETUP")
	PrintTanks(controller)
	controller.board.Render()

	controller.StartOfTurn()
	print("START OF DAY 1")
	PrintTanks(controller)
	controller.board.Render()
