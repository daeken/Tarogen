class AstNode(object):
	pass

def ListNode(*args):
	return list(args)

class SymbolNode(AstNode):
	def __init__(self, name):
		self.name = name

	def __str__(self):
		return self.name
	__repr__ = __str__

class StringNode(AstNode):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return `self.value`
	__repr__ = __str__

class UnsignedNode(AstNode):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return '0x%xU' % self.value
	__repr__ = __str__

class SignedNode(AstNode):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return '0x%x' % self.value
	__repr__ = __str__
