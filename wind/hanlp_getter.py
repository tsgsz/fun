import thulac

class ThuNameGetter:
    def __init__(self):
        self.thu = thulac.thulac()

    def process(self, param):
        cut_res = self.thu.cut(param, text=False)
        names = {x[0] for x in cut_res if x[1] == 'np'}
        return names

class ThuLocationGetter:
    def __init__(self):
        self.thu = thulac.thulac()

    def process(self, param):
        cut_res = self.thu.cut(param, text=False)
        locations = {x[0] for x in cut_res if x[1] == 'ns' or x[1] == 'ni'}
        return locations

class ThuItemGetter:
    def __init__(self):
        self.thu = thulac.thulac()

    def process(self, param):
        cut_res = self.thu.cut(param, text=False)
        items = {x[0] for x in cut_res if x[1] == 'nz'}
        return items