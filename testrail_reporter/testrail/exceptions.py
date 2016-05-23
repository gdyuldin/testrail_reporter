class NotFound(Exception):
    def __init__(self, item_class, **conditions):
        self.item_class = item_class
        self.conditions = conditions

    def __str__(self):
        conditions = ', '.join(['{}="{}"'.format(x, y)
                               for (x, y) in self.conditions.items()])
        return u'{type} with {conditions}'.format(
            type=self.item_class._api_name().title(),
            conditions=conditions)
