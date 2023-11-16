from TankGameInteractor import I_ActionSource, Action
from csv import DictReader

class CsvActionSource(I_ActionSource):

	def __init__(self, path):
		self.dict_list = list(DictReader(open(path, 'r')))
		self.num_actions = len(self.dict_list)
		self.next_action = 0

	def HasAnotherAction(self):
		return self.next_action < self.num_actions

	def NextAction(self):
		action_dict = self.dict_list[self.next_action]
		self.next_action += 1
		a = Action(action_dict["date"], action_dict["actor"], action_dict["action_type"], action_dict["target"], action_dict["metadata"])
		return a