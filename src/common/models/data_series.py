from sortedcontainers import SortedDict

class DataSeries(SortedDict):
    
    def get_first_point(self):
        return self.peekitem(0)
    
    def get_last_point(self):
        return self.peekitem(-1)
    
    def get_latest_point(self, key):
        next_id = self.bisect_right(key)
        if next_id == 0:
            raise IndexError(f"{key} is before the first available point {self.peekitem(0)[0]}")
        return self.peekitem(next_id-1)
    
    def get_latest_value(self, key):
        return self.get_latest_point(key)[1]
