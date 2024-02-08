import logging
from collections import namedtuple

logger = logging.getLogger(__name__)

STARTING_LIVES = 3
STARTING_RANGE = 2

FIRE_DAMAGE = 1

#AP COSTS
MOVE_AP_COST = 1
UPGRADE_AP_COST = 5

Position = namedtuple("Position", ["x", "y"])
AttackDrops = namedtuple("AttackDrops", ["AP", "gold", "kills", "lives"])


class Tank:

	def __init__(self, position, owner, tile=None):
		self.position = position
		self.owner = owner
		self.lives = STARTING_LIVES
		self.AP = 0
		self._gold = 0
		self.range = STARTING_RANGE
		self.kills = 0

		#Accolade stats
		self._totalMoves = 0
		self._totalGold = 0

		self.tile = tile if tile is not None else self.owner[:2]

	def PerformMove(self, targetPos):
		self.AP -= MOVE_AP_COST
		self.position = targetPos
		self._totalMoves += 1

	def PerformUpgrade(self):
		self.AP -= UPGRADE_AP_COST
		self.range += 1

	def HasGold(self, amount):
		return self._gold >= amount

	def GainGold(self, amount_to_gain):
		self._gold += amount_to_gain
		self._totalGold += amount_to_gain

	def SpendGold(self, amount_to_spend):
		self._gold -= amount_to_spend

	def TakeDamage(self, actor, amount):
		remove_from_board = False
		gained_AP = 0
		gained_gold = 0
		gained_kills = 0
		gained_lives = 0
		
		self.lives = max(0, self.lives - amount)
		if self.lives == 0:
			gained_gold = 3 if self._gold == 0 else self._gold
			gained_kills = 1
			self._Die()
			remove_from_board = True
			
		return remove_from_board, AttackDrops(AP = gained_AP, gold = gained_gold, kills = gained_kills, lives = gained_lives)

	def _Die(self):
		self.AP = 0

	def __str__(self):
		return f"{self.owner:15} - {self.position.x:2},{self.position.y:2} Lives: {self.lives} Range: {self.range} AP: {self.AP} Gold: {self._gold:2} Total Gold: {self._totalGold:3}"

class Wall:

	def __init__(self, position, durability):
		self.position = position
		self.durability = durability

	def TakeDamage(self, actor, amount):
		remove_from_board = False
		gained_AP = 0
		gained_gold = 0
		gained_kills = 0
		gained_lives = 0
		
		self.durability = max(0, self.durability - amount)
		if self.durability == 0:
			remove_from_board = True
			
		return remove_from_board, AttackDrops(AP = gained_AP, gold = gained_gold, kills = gained_kills, lives = gained_lives)

	@property
	def tile(self):
		return f"W{self.durability}"		

class Council:

	def __init__(self):
		pass
	
	def GetCouncilors(self):
		pass
		
	def GetSenators(self):
		pass

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
			tank.GainGold(awardPerTank)


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
		assert gridSpace is entity, \
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