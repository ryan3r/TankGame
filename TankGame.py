from TankGameInteractor import Interactor
from CsvActionSource import CsvActionSource
from Entities import Position, GoldMine
from TankGameController import GameController

CSV_PATH = "game2.csv"

def PrintTanks(controller):
	for tank in controller.tanks:
		print(tank)
		
def AddWalls(controller, x_start, x_end, y_start, y_end):
	for x in range(x_start, x_end+1):
		for y in range(y_start, y_end+1):
			controller.AddWall(Position(x, y))
			
def BuildGeodeMap():
	geodeController = GameController(9, 9)

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
	geodeController.goldMines.append(mine)

	geodeController.AddWall(Position(3, 2))
	geodeController.AddWall(Position(4, 2))
	geodeController.AddWall(Position(5, 2))
	geodeController.AddWall(Position(6, 3))
	geodeController.AddWall(Position(6, 4))
	geodeController.AddWall(Position(6, 5))
	geodeController.AddWall(Position(5, 6))
	geodeController.AddWall(Position(4, 6))
	geodeController.AddWall(Position(3, 6))
	geodeController.AddWall(Position(2, 5))
	geodeController.AddWall(Position(2, 4))
	geodeController.AddWall(Position(2, 3))
	
	return geodeController
			
def BuildFourCornersMap():
	fourCornersController = GameController(11, 11)
	
	mine1 = GoldMine()
	mine1.AddSpace(Position(1, 5))
	mine2 = GoldMine()
	mine2.AddSpace(Position(5, 1))
	mine3 = GoldMine()
	mine3.AddSpace(Position(9, 5))
	mine4 = GoldMine()
	mine4.AddSpace(Position(5, 9))
	fourCornersController.goldMines.append(mine1)
	fourCornersController.goldMines.append(mine2)
	fourCornersController.goldMines.append(mine3)
	fourCornersController.goldMines.append(mine4)
	
	AddWalls(fourCornersController, 3, 7, 0, 0)
	AddWalls(fourCornersController, 3, 4, 1, 1)
	AddWalls(fourCornersController, 6, 7, 1, 1)
	AddWalls(fourCornersController, 3, 7, 2, 2)
	AddWalls(fourCornersController, 0, 10, 3, 4)
	fourCornersController.AddWall(Position(0, 5))
	AddWalls(fourCornersController, 2, 8, 5, 5)
	fourCornersController.AddWall(Position(10, 5))
	AddWalls(fourCornersController, 0, 10, 6, 7)
	AddWalls(fourCornersController, 3, 7, 8, 8)
	AddWalls(fourCornersController, 3, 4, 9, 9)
	AddWalls(fourCornersController, 6, 7, 9, 9)
	AddWalls(fourCornersController, 3, 7, 10, 10)
	
	return fourCornersController
	
def SetupSeason2():
	s2Controller = BuildGeodeMap()
	
	s2Controller.AddTank(Position(1, 1), "Ryan")
	s2Controller.AddTank(Position(3, 0), "Beyer")
	s2Controller.AddTank(Position(5, 0), "Taylore")
	s2Controller.AddTank(Position(7, 1), "John")
	s2Controller.AddTank(Position(8, 3), "Marci")
	s2Controller.AddTank(Position(8, 5), "Stomp")
	s2Controller.AddTank(Position(7, 7), "David K.", tile="DK")
	s2Controller.AddTank(Position(5, 8), "David Y.", tile="DY")
	s2Controller.AddTank(Position(3, 8), "Dan")
	s2Controller.AddTank(Position(1, 7), "Corey")
	s2Controller.AddTank(Position(0, 5), "Mike")
	s2Controller.AddTank(Position(0, 3), "Ty")
	
	return s2Controller
	
def SetupSeason3():
	s3Controller = BuildFourCornersMap()
	
	s3Controller.AddTank(Position(0, 0), 	"Schmude")
	s3Controller.AddTank(Position(2, 0), 	"Dan")
	s3Controller.AddTank(Position(0, 2), 	"Bryan")
	s3Controller.AddTank(Position(2, 2), 	"Trevor")
	s3Controller.AddTank(Position(8, 0), 	"Stomp")
	s3Controller.AddTank(Position(10, 0), 	"Ty")
	s3Controller.AddTank(Position(8, 2), 	"David")
	s3Controller.AddTank(Position(10, 2), 	"Lena")
	s3Controller.AddTank(Position(0, 8), 	"Beyer")
	s3Controller.AddTank(Position(2, 8), 	"Steve")
	s3Controller.AddTank(Position(0, 10), 	"Ryan")
	s3Controller.AddTank(Position(2, 10), 	"John")
	s3Controller.AddTank(Position(8, 8), 	"Joel")
	s3Controller.AddTank(Position(10, 8), 	"Xavion")
	s3Controller.AddTank(Position(8, 10), 	"Isaac")
	s3Controller.AddTank(Position(10, 10), 	"Corey")
	
	return s3Controller

if __name__ == "__main__":
	
	controller = SetupSeason2()	
	
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