import unittest
from TankGame import Board, Position, Wall, Tank

WIDTH = 9
HEIGHT = 7


class TestBoard(unittest.TestCase):
    def _make_board(self):
        board = Board(WIDTH, HEIGHT)
        for entity in self.entities:
            board.AddEntity(entity)
        return board

    def _check_line_of_sight(self, entity1_idx, entity2_idx, expected, **kwargs):
        """Make a board containing entities, then check if the entities specified have line of sight."""
        board = self._make_board()

        position1 = self.entities[entity1_idx].position
        position2 = self.entities[entity2_idx].position

        entity1 = board.grid[position1.x][position1.y]
        entity2 = board.grid[position2.x][position2.y]

        self.assertEqual(board.DoesLineOfSightExist(entity1, entity2), expected)
        self.assertEqual(board.DoesLineOfSightExist(entity2, entity1), expected)

    def test_has_line_of_sight_basic(self):
        """
        Test basic cases that have line of sight.

        T1|  |T4|  |  |  |  |
        --+--+--+--+--+--+--+--
         |  |  |  |  |  |  |
        --+--+--+--+--+--+--+--
        T3|  |T2|  |  |  |  |
        --+--+--+--+--+--+--+--
        |  |  |W5|  |  |  |
        --+--+--+--+--+--+--+--
        |  |  |  |  |  |  |
        """
        self.entities = [
            Tank(Position(0, 0), "T1"),
            Tank(Position(2, 2), "T2"),
            Tank(Position(0, 2), "T3"),
            Tank(Position(2, 0), "T4"),
            Wall(Position(3, 3))
        ]

        # X axis
        self._check_line_of_sight(0, 3, True) # T1 can see T4
        self._check_line_of_sight(1, 2, True) # T2 can see T3

        # Y axis
        self._check_line_of_sight(0, 2, True) # T1 can see T3
        self._check_line_of_sight(1, 3, True) # T2 can see T4

        # Diagonal
        self._check_line_of_sight(0, 1, True) # T1 can see T2
        self._check_line_of_sight(2, 3, True) # T3 can see T4

    def test_line_of_sight_blocked_basic(self):
        """
        Test basic cases that don't have line of sight.
        """
        self.entities = [
            Tank(Position(0, 0), "T1"),
            Tank(Position(2, 2), "T2"),
            Tank(Position(0, 2), "T3"),
            Tank(Position(2, 0), "T4"),
            Wall(Position(1, 1)),
            Wall(Position(0, 1)),
            Wall(Position(1, 0)),
            Wall(Position(2, 1)),
            Wall(Position(1, 2)),
        ]

        # X axis
        self._check_line_of_sight(0, 3, False) # T1 can't see T4
        self._check_line_of_sight(1, 2, False) # T2 can't see T3

        # Y axis
        self._check_line_of_sight(0, 2, False) # T1 can't see T3
        self._check_line_of_sight(1, 3, False) # T2 can't see T4

        # Diagonal
        self._check_line_of_sight(0, 1, False) # T1 can't see T2
        self._check_line_of_sight(2, 3, False) # T3 can't see T4

    def test_factional_slope_line_of_sight(self):
        """
        Test line of sight cases with slopes other than 0 and 1.
        """
        self.entities = [
            Tank(Position(3, 3), "T1"),
            Tank(Position(5, 6), "T2"),
            Tank(Position(6, 5), "T3"),
            Tank(Position(1, 0), "T4"),
            Tank(Position(0, 1), "T5"),
        ]

        self._check_line_of_sight(0, 1, True) # T1 can see T2
        self._check_line_of_sight(0, 2, True) # T1 can see T3
        self._check_line_of_sight(0, 3, True) # T1 can see T4
        self._check_line_of_sight(0, 4, True) # T1 can see T5

        self._check_line_of_sight(2, 4, False) # T3 can't see T5 (blocked by T1)
        self._check_line_of_sight(1, 3, False) # T2 can't see T4 (blocked by T1)

        self._check_line_of_sight(1, 4, False) # T2 can't see T5
        self._check_line_of_sight(2, 3, False) # T3 can't see T4

    def test_line_of_sight_through_corner(self):
        """
        Test line of sight through the corner of two walls.
        """
        self.entities = [
            Tank(Position(0, 0), "T1"),
            Tank(Position(1, 1), "T2"),
            Tank(Position(2, 0), "T3"),
            Wall(Position(1, 0)),
            Wall(Position(0, 1)),
            Wall(Position(2, 1)),
        ]

        self._check_line_of_sight(0, 1, True) # T1 can't see T2
        self._check_line_of_sight(1, 2, True) # T2 can't see T3

    def test_line_of_sight_through_objects(self):
        """
        Test line of sight through an ignored entity.
        """
        self.entities = [
            Tank(Position(0, 0), "T1"),
            Wall(Position(1, 0)),
            Tank(Position(2, 0), "T2"),
        ]

        self._check_line_of_sight(0, 2, False) # T1 can't see T2
        self._check_line_of_sight(0, 2, True, ignoredEntities=[Wall]) # T1 can see T2
