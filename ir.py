nodetypes = '''
	assign lval rval
	not value
	binary op lval rval
	if condition true false
	when condition body
	unless condition body
	while head condition body
	constant type value
	argument num
	local num
	return value
	callStatic target args
	call obj target args
	field obj name
'''

class BaseNode(object):
	def __init__(self, *args, **kwargs):
		args = list(args)
		assert len(args) + len(kwargs) == len(self._params)
		assert sorted(kwargs.keys()) == sorted(self._params[len(args):])
		for param in self._params:
			if len(args):
				setattr(self, param, args.pop(0))
			else:
				setattr(self, param, kwargs[param])

	def toList(self):
		def sub(x):
			if isinstance(x, tuple):
				return tuple(map(sub, x))
			elif isinstance(x, list):
				return map(sub, x)
			elif isinstance(x, BaseNode):
				return x.toList()
			else:
				return x
		return [self.__class__.__name__] + [sub(getattr(self, x)) for x in self._params]

	def __repr__(self):
		return '%s(%s)' % (self.__class__.__name__, ', '.join('%s=%r' % (param, getattr(self, param)) for param in self._params))

__all__ = ['BaseNode']

for line in nodetypes.strip().split('\n'):
	line = line.strip().split(' ')
	name, params = line[0], line[1:]
	clsname = name[0].upper() + name[1:]
	cls = type(clsname, (BaseNode, ), dict(_params=params))
	globals()[clsname] = cls
	__all__.append(clsname)
