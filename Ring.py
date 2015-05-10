class Ring:
    def __init__(self, l):
        if not len(l):
            raise "ring must have at least one element"
        self._data = l

    def __repr__(self):
        return repr(self._data)

    def __len__(self):
        return len(self._data)

    def __getitem__(self, i):
        return self._data[i]
    
    def __setitem__(self, key, item):
        self._data[key] = item
    
    def append(self, item):
        self._data.append(item)

    def extend(self, newList):
        self._data.extend(newList)

    def turn(self, n=1):
        n = n % len(self._data)
        tmpList = self._data[n:]
        tmpList.extend(self._data[:n])
        self._data = tmpList

    def first(self):
        return self._data[0]

    def last(self):
        return self._data[-1]
