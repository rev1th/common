from sortedcontainers import SortedDict

class DataSeries(SortedDict):
    
    def get_first_point(self):
        return self.peekitem(0)
    
    def get_last_point(self):
        return self.peekitem(-1)
    
    def get_latest_value(self, key):
        return self.peekitem(self.bisect_left(key)-1)[1]
