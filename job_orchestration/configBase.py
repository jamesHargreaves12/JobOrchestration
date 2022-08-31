class Dict2Class(object):

    def __init__(self, input_dict):
        self.input_dict = input_dict
        for key in input_dict:
            setattr(self, key, input_dict[key])

    def validate(self):
        for param in self.__class__.__annotations__:
            assert param in vars(self), "{} missing from {}".format(param, self.__class__.__name__)
