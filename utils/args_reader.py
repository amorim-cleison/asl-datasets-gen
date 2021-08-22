class ArgsReader:
    """
        Arguments Reader
    """

    def __init__(self, args, section=None):
        self.args = args if args is dict else vars(args)

        if section in self.args:
            self.section_args = self.args[section]
        else:
            self.section_args = dict()

    def get_arg(self, name, default=None):
        return self.section_args.get(name, self.args.get(name, default))
