class Dict2Class(object):

    def __init__(self, input_dict):
        self.raw_dict = input_dict
        for key in input_dict:
            setattr(self, key, input_dict[key])

    def validate(self):
        errs = []
        for param in self.__class__.__annotations__:
            if param not in vars(self):
                errs.append("{} missing from {}".format(param, self.__class__.__name__))
        return errs
