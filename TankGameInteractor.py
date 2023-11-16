from TankGameController import GameController
from Entities import Position
from collections import namedtuple

MOVE_ACTION = "move"
FIRE_ACTION = "fire"
UPGRADE_ACTION = "upgrade"
TRADE_ACTION = "trade"
SHARE_AP_ACTION = "share_ap"
SHARE_LIFE_ACTION = "share_life"

class Interactor:

    def __init__(self, gameController):
        self._controller = gameController
        self._date = None

    def TakeActions(self, action_source):
        while(action_source.HasAnotherAction()):
            action = action_source.NextAction()
            self._CheckDate(action)

            action_type = action.action_type
            if action_type == MOVE_ACTION:
                self._DoMoveAction(action)
            elif action_type == FIRE_ACTION:
                self._DoFireAction(action)
            elif action_type == UPGRADE_ACTION:
                self._DoUpgradeAction(action)
            elif action_type == TRADE_ACTION:
                self._DoTradeAction(action)
            elif action_type == SHARE_AP_ACTION:
                self._DoShareAPAction(action)
            elif action_type == SHARE_LIFE_ACTION:
                self._DoShareLifeAction(action)
            else:
                raise Exception("Unhandled action type: " + action_type)

    def _CheckDate(self, action):
        if self._date is None or self._date != action.date:
            self._controller.StartOfTurn()
            self._date = action.date

    def _DoMoveAction(self, action):
        self._controller.PerformMove(action.actor, AlgebraicNotationToPosition(action.target))

    def _DoFireAction(self, action):
        self._controller.PerformFire(action.actor, AlgebraicNotationToPosition(action.target), doesHit = bool(action.metadata))

    def _DoUpgradeAction(self, action):
        self._controller.PerformUpgrade(action.actor)

    def _DoTradeAction(self, action):
        self._controller.PerformTradeGold(action.actor, int(action.metadata))

    def _DoShareAPAction(self, action):
        self._controller.PerformShareActions(action.actor, action.target, int(metadata))

    def _DoShareLifeAction(self, action):
        self._controller.PerformShareLife(action.actor, action.target)
		
def AlgebraicNotationToPosition(alg_notation):
	alg_notation = alg_notation.lower()
	x = ord(alg_notation[0]) - ord('a')
	y = int(alg_notation[1:]) - 1
	return Position(x, y)

Action = namedtuple("Action", ["date", "actor", "action_type", "target", "metadata"])

class I_ActionSource:

    def HasAnotherAction(self):
        pass

    def NextAction(self):
        pass