from jarvis import Jarvis



class Engine:
    def __init__(self):

        self.jarvis = Jarvis()

    def runtime(self):
        self.jarvis.print_version()
        self.jarvis.run()




if __name__ == '__main__':
    engine = Engine()
    engine.runtime()