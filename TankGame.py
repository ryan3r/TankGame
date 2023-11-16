from TankGameInteractor import Interactor
from CsvActionSource import CsvActionSource
from Entities import Position, GoldMine
from TankGameController import GameController

CSV_PATH = "game2.csv"

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
	
	print("Initial Setup")
	PrintTanks(controller)
	controller.board.Render()
	print()
	
	actionSource = CsvActionSource(CSV_PATH)
	
	tg_interactor = Interactor(controller)
	tg_interactor.TakeActions(actionSource)
	
	print("Post Actions")
	PrintTanks(controller)
	controller.board.Render()
	print()