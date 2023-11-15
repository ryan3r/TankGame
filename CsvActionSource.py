from TankGameInteractor import I_ActionSource

class CsvActionSource(I_ActionSource):

    def __init__(self, path):
        self.path = path

    def HasAnotherAction(self):
        pass

    def NextAction(self):
        pass