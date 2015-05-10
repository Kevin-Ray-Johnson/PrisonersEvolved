class Vector:
    def __init__(self, data):
        self.data = data
    
    def __repr__(self):
        return repr(self.data)  
    
    def __add__(self, other):
        return Vector(map(lambda x, y: x+y, self, other))

    def __mul__(self, other):
        return Vector(map(lambda x: x*other, self))
    
    __rmul__ = __mul__

    def __getitem__(self, index):
        return self.data[index]

    def __len__(self):
        return len(self.data)
