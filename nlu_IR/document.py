from collections import OrderedDict
from typing import *

def concat_list(list_: Iterable, sep='-', exclude_none=True):
	"""
	>>> concat_list(["ABC", "123", None], sep='|', exclude_none=False)
	'ABC|123|None'
	>>> concat_list(["C", None, "D1", "S2", "T", 7], sep='-')
	'C-D1-S2-T-7
	>>> concat_list(None)
	Traceback (most recent call last):
	...
	TypeError: The first argument of the function concat_list must be an iterable object.
	"""
	try:
		if exclude_none:
			return sep.join([str(item) for item in list_ if item is not None])
		else:
			return sep.join([str(item) for item in list_])
	except TypeError:
		raise TypeError('The first argument of the function concat_list must be an iterable object.')


def ids_to_full_id(ids: OrderedDict) -> str:
    """
    >>> ids_to_full_id(OrderedDict({'D':1, 'S':2, 'E': None}))
    'D1-S2'
    """
    return concat_list([str(key) + str(value) for key, value in ids.items() if value is not None])


class Hierarchy:
    """
    A ``Hierarchy`` is an abstract class handling hierarchical ids and full_id for the sub-classes.
    """
    def __init__(self, id, symbol, parent_ids=None):
        default_ids = OrderedDict({'C': None, 'D': None})
        self._id: int = id
        # self.ids: OrderedDict[str, int] = parent_ids or self.__class__.default_ids
        if parent_ids:
            self.ids: OrderedDict[str, int] = copy.deepcopy(parent_ids)
        else:
            self.ids = default_ids

        self.ids[symbol] = id
        self.refs: Dict = {}

    @property
    def full_id(self):
        return ids_to_full_id(self.ids)


class Document:
    def __init__(self):
        self._title:str
        self._context:str
            
    @property
    def title(self):
        return self._title
    
    @title.setter
    def title(self, title):
        self._title = title
    
    @property
    def context(self):
        return self._context
    
    @context.setter
    def context(self, context):
        self._context = context
    
    
        