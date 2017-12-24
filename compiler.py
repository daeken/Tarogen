from pprint import pprint

import mod
from ast import *
import ir

def walk(node):
	if not isinstance(node, list) or len(node) == 0 or not isinstance(node[0], SymbolNode):
		return

	cmd = node[0].name
	if cmd == 'namespace':
		name = node[1].name
		map(walk, node[2:])
	elif cmd == 'class':
		name = node[1].name
		bases = map(walk, node[2])
		map(walk, node[3:])
	elif cmd == 'type':
		pass
	elif cmd == 'field':
		pass
	elif cmd == 'property':
		pass
	elif cmd == 'method':
		name = node[1].name
		sig = node[2]
		for elem in node[3:]:
			cmd = elem[0].name
			if cmd == 'body':
				decompile(name, sig, elem[1:])
				import sys
				sys.exit(0)
			elif cmd == 'attribute':
				pass
	else:
		print 'Unknown node:', cmd
		print node

class GraphNode(object):
	def __init__(self, pos, _from, to):
		self.processed = False
		self.pos, self._from, self.to = pos, _from, to

	def __str__(self):
		return '%s(%i, %r, %r)' % (self.__class__.__name__, self.pos, self._from, self.to)

class RawNode(GraphNode):
	def __init__(self, body, pos, _from, to):
		GraphNode.__init__(self, pos, _from, to)
		self.body = body

class IfNode(GraphNode):
	def __init__(self, begin, _if, _else, end):
		GraphNode.__init__(self, begin.pos, begin._from, end.to)
		_if.to = []
		_else.to = []
		end.to = []
		self.begin, self._if, self._else, self.end = begin, _if, _else, end

class WhenNode(GraphNode):
	def __init__(self, begin, _if, end):
		GraphNode.__init__(self, begin.pos, begin._from, end.to)
		_if.to = []
		end.to = []
		self.begin, self._if, self.end = begin, _if, end

class UnlessNode(GraphNode):
	def __init__(self, begin, _else, end):
		GraphNode.__init__(self, begin.pos, begin._from, end.to)
		_else.to = []
		end.to = []
		self.begin, self._else, self.end = begin, _else, end

class WhileNode(GraphNode):
	def __init__(self, begin, _while, end):
		GraphNode.__init__(self, begin.pos, begin._from, end.to)
		_while.to = []
		end.to = []
		self.begin, self._while, self.end = begin, _while, end

class UntilNode(GraphNode):
	def __init__(self, begin, _until, end):
		GraphNode.__init__(self, begin.pos, begin._from, end.to)
		_until.to = []
		end.to = []
		self.begin, self._until, self.end = begin, _until, end

def printGraph(blocks, edges):
	print 'digraph {'
	for pos, insns in blocks.items():
		print '_%i [shape="box" label="%s"];' % (pos, '\n'.join(map(repr, insns)).replace('&', '&amp;').replace('"', '&quot;'))
	for pos, insns in blocks.items():
		for i, end in enumerate(edges[pos]):
			if len(edges[pos]) == 1:
				color = 'black'
			elif i == 0:
				color = 'green'
			elif i == 1:
				color = 'red'
			print '_%i -> _%i [color="%s"];' % (pos, end, color)
	print '}'

def reduceGraph(graph):
	def display():
		for pos in sorted(graph.keys()):
			print graph[pos]

	def isIf(node):
		if len(node.to) == 2:
			a, b, c = node, graph[node.to[0]], graph[node.to[1]]
			if len(b.to) == 1 and len(b._from) == 1 and len(c.to) == 1 and len(c._from) == 1 and b.to[0] == c.to[0]:
				d = graph[c.to[0]]
				if len(d._from) == 2:
					return a, b, c, d
	def isWhen(node):
		if len(node.to) == 2:
			a, b, c = node, graph[node.to[0]], graph[node.to[1]]
			if len(b.to) == 1 and len(b._from) == 1 and len(c._from) == 2 and b.to[0] == c.pos:
				return a, b, c
	def isUnless(node):
		if len(node.to) == 2:
			a, b, c = node, graph[node.to[0]], graph[node.to[1]]
			if len(c.to) == 1 and len(c._from) == 1 and len(b._from) == 2 and c.to[0] == b.pos:
				return a, c, b
	def isWhile(node):
		if len(node.to) == 2:
			a, b, c = node, graph[node.to[0]], graph[node.to[1]]
			if len(b.to) == 1 and b.to[0] == a.pos:
				return a, b, c
	def isUntil(node):
		if len(node.to) == 2:
			a, b, c = node, graph[node.to[1]], graph[node.to[0]]
			if len(b.to) == 1 and b.to[0] == a.pos:
				return a, b, c
	def isSerial(node):
		if isinstance(node, RawNode) and len(node.to) == 1 and isinstance(graph[node.to[0]], RawNode) and len(graph[node.to[0]]._from) == 1:
			return node, graph[node.to[0]]
	while True:
		changed = False

		if not changed:
			for pos, node in graph.items():
				x = isSerial(node)
				if x is not None:
					print 'Found serial!'
					a, b = x
					new = RawNode(a.body[:-1] + b.body, a.pos, a._from, b.to)
					del graph[a.pos]
					del graph[b.pos]
					graph[new.pos] = new
					changed = True
		if not changed:
			for pos, node in graph.items():
				x = isIf(node)
				if x is not None:
					print 'Found if!'
					a, b, c, d = x
					new = IfNode(a, b, c, d)
					del graph[a.pos]
					del graph[b.pos]
					del graph[c.pos]
					del graph[d.pos]
					graph[new.pos] = new
					changed = True
					break
		if not changed:
			for pos, node in graph.items():
				x = isWhen(node)
				if x is not None:
					print 'Found when!'
					a, b, c = x
					new = WhenNode(a, b, c)
					del graph[a.pos]
					del graph[b.pos]
					del graph[c.pos]
					graph[new.pos] = new
					changed = True
					break
		if not changed:
			for pos, node in graph.items():
				x = isUnless(node)
				if x is not None:
					print 'Found unless!'
					a, b, c = x
					new = UnlessNode(a, b, c)
					del graph[a.pos]
					del graph[b.pos]
					del graph[c.pos]
					graph[new.pos] = new
					changed = True
					break
		if not changed:
			for pos, node in graph.items():
				x = isWhile(node)
				if x is not None:
					print 'Found while!'
					a, b, c = x
					new = WhileNode(a, b, c)
					del graph[a.pos]
					del graph[b.pos]
					del graph[c.pos]
					graph[new.pos] = new
					changed = True
					break
		if not changed:
			for pos, node in graph.items():
				x = isUntil(node)
				if x is not None:
					print 'Found until!'
					a, b, c = x
					new = UntilNode(a, b, c)
					del graph[a.pos]
					del graph[b.pos]
					del graph[c.pos]
					graph[new.pos] = new
					changed = True
					break

		if not changed:
			break

	def sub(node):
		if node.processed:
			return
		node.processed = True
		node._from = [graph[x] for x in node._from if x in graph]
		node.to = [graph[x] for x in node.to if x in graph]
		if isinstance(node, RawNode):
			map(sub, node.to)
		elif isinstance(node, IfNode):
			sub(node.begin)
			sub(node._if)
			sub(node._else)
			sub(node.end)
		elif isinstance(node, WhenNode):
			sub(node.begin)
			sub(node._if)
			sub(node.end)
		elif isinstance(node, UnlessNode):
			sub(node.begin)
			sub(node._else)
			sub(node.end)
		elif isinstance(node, WhileNode):
			sub(node.begin)
			sub(node._while)
			sub(node.end)
		elif isinstance(node, UntilNode):
			sub(node.begin)
			sub(node._until)
			sub(node.end)
	sub(graph[0])
	return graph

class Scoped(object):
	def __init__(self, transformer):
		self.stack = []
		self.stmts = []
		self.transformer = transformer

	def __enter__(self):
		prev = self.transformer.scope
		self.transformer.scopes.append(prev)
		self.transformer.scope = self
		self.stack = prev.stack[:]
		return self

	def __exit__(self, *args):
		self.transformer.scope = self.transformer.scopes.pop()

def transform(node):
	transformer = Transformer()
	transformer.transform(node)
	return transformer.stmts

class Transformer(object):
	def __init__(self):
		self.scope = Scoped(self)
		self.scopes = []

	@property
	def stmts(self):
		return self.scope.stmts

	def scoped(self):
		return Scoped(self)

	def pop(self, count=None):
		stack = self.scope.stack
		if count is None:
			return stack.pop()
		elif count == 0:
			return []
		else:
			ret = stack[-count:]
			self.scope.stack = stack[:-count]
			return ret

	def push(self, value):
		self.scope.stack.append(value)

	def stmt(self, stmt):
		print stmt
		self.scope.stmts.append(stmt)

	def local(self, num, value=None):
		if value is None:
			return ir.Local(num)
		self.stmt(ir.Assign(ir.Local(num), value))

	def transform(self, node):
		if node is None:
			return

		#print 'Transforming', node
		if isinstance(node, RawNode):
			self.run(node.body)
			self.transform(node.to[0] if len(node.to) == 1 else None)
		elif isinstance(node, IfNode):
			self.transform(node.begin)
			cond = self.pop()
			with self.scoped() as a:
				self.transform(node._if)
			with self.scoped() as b:
				self.transform(node._else)
			self.stmt(ir.If(cond, a.stmts, b.stmts))
			self.transform(node.end)
		elif isinstance(node, WhileNode):
			with self.scoped() as head:
				self.transform(node.begin)
				cond = self.pop()
			with self.scoped() as body:
				self.transform(node._while)
			self.stmt(ir.While(head.stmts, cond, body.stmts))
			self.transform(node.end)
		else:
			print 'Unknown node type to transform:', node

	def run(self, insns):
		for insn in insns:
			opc = insn[0].name
			named = opc.replace('.', '_')
			if hasattr(self, named):
				getattr(self, named)(*insn)
			else:
				print 'Unknown opcode:', insn

	def nop(self, *args):
		pass
	br_s = nop

	def ldc_i4_0(self, _):
		self.push(ir.Constant('i32', 0))
	def ldc_i4_1(self, _):
		self.push(ir.Constant('i32', 1))
	def ldc_i4_2(self, _):
		self.push(ir.Constant('i32', 2))
	def ldc_i4_3(self, _):
		self.push(ir.Constant('i32', 3))
	def ldc_i4_4(self, _):
		self.push(ir.Constant('i32', 4))
	def ldc_i4_5(self, _):
		self.push(ir.Constant('i32', 5))
	def ldc_i4_6(self, _):
		self.push(ir.Constant('i32', 6))
	def ldc_i4_7(self, _):
		self.push(ir.Constant('i32', 7))
	def ldc_i4_8(self, _):
		self.push(ir.Constant('i32', 8))

	def ldarg_0(self, _):
		self.push(ir.Argument(0))

	def stloc_0(self, _):
		self.local(0, self.pop())
	def stloc_1(self, _):
		self.local(1, self.pop())
	def stloc_2(self, _):
		self.local(2, self.pop())
	def stloc_3(self, _):
		self.local(3, self.pop())

	def ldloc_0(self, _):
		self.push(self.local(0))
	def ldloc_1(self, _):
		self.push(self.local(1))
	def ldloc_2(self, _):
		self.push(self.local(2))
	def ldloc_3(self, _):
		self.push(self.local(3))

	def ldc_i4_s(self, _, value):
		self.push(ir.Constant('i32', value.value))

	def clt(self, _):
		self.push(ir.Binary('<', *self.pop(2)))

	def add(self, _):
		self.push(ir.Binary('+', *self.pop(2)))

	def call(self, _, target):
		args = self.pop(len(target) - 4)
		call = ir.CallStatic(target[2][0].name, args)
		if target[3][1].name != 'Void':
			self.push(call)
		else:
			self.stmt(call)

	def newobj(self, _, ctor):
		self.push(ir.Constant('i32', 1234))

	def dup(self, _):
		v = self.pop()
		self.push(v)
		self.push(v)

	def stfld(self, _, field):
		v = self.pop()
		obj = self.pop()
		self.stmt(ir.Assign(ir.Field(obj, field[2].name), v))

	def ret(self, _):
		self.stmt(ir.Return(self.pop()))

	def brtrue_s(self, _, a, b):
		pass
	def brfalse_s(self, _, a, b):
		self.push(ir.Not(self.pop()))

def decompile(name, sig, insns):
	args = sig[1:]
	locs = {insn[0].value : i for i, insn in enumerate(insns)}
	targets = set()
	for i, insn in enumerate(insns):
		#print insn
		op = insn[1].name
		if op[0] == 'b' and op not in ('box', 'break'):
			targets.add(insn[2].value)
			if i != len(insns) - 1 and op not in ('br', 'br.s'):
				alt = insns[i + 1][0].value
				targets.add(alt)
				insn.append(SignedNode(alt))
	blocks = {0 : []}
	cur = blocks[0]
	for insn in insns:
		offset = insn[0].value
		if offset != 0 and offset in targets:
			cur = blocks[offset] = []
		cur.append(insn[1:])
	edges = {}
	for pos, insns in blocks.items():
		op = insns[-1][0].name
		if op[0] == 'b' and op not in ('box', 'break'):
			edges[pos] = [x.value for x in insns[-1][1:]]
		elif sorted(blocks.keys())[-1] != pos:
			edges[pos] = [[x for x in sorted(blocks.keys()) if x > pos][0]]
		else:
			edges[pos] = []

	revedges = {key : [] for key in blocks.keys()}
	for pos, ends in edges.items():
		for end in ends:
			revedges[end].append(pos)

	graph = {}
	for pos, insns in blocks.items():
		graph[pos] = RawNode(insns, pos, revedges[pos], edges[pos])

	graph = reduceGraph(graph)

	pprint([x.toList() for x in transform(graph[0])])

	#printGraph(blocks, edges)

walk(mod.root)
