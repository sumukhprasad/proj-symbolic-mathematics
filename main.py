import re
import math


class SymParser:
	def __init__(self, eq):
		eq = "".join(eq.split(" "))
		eq = "(".join(eq.split("["))
		eq = ")".join(eq.split("]"))
		self.eq = eq
		self.__fixXY()
		self.__fixImplicitMultiplication()
		self.__groupOperators()
		self.__groupWords()
		self.__fixParentheses()
	
	
	# tree generation from separated expression
	# precedence: ^ over *, / over + and -
	# expression -> term -> power -> factor
	def parse_expression(self, tokens):
		node = self.parse_term(tokens)
		while tokens and tokens[0] in ['+', '-']:
			op = tokens.pop(0)
			right = self.parse_term(tokens)
			node = Node(op, node, right)
		return node
	
	def parse_term(self, tokens):
		node = self.parse_power(tokens)
		while tokens and tokens[0] in ['*', '/']:
			op = tokens.pop(0)
			right = self.parse_power(tokens)
			node = Node(op, node, right)
		return node
	
	def parse_power(self, tokens):
		node = self.parse_factor(tokens)
		while tokens and tokens[0] == '^':
			op = tokens.pop(0)
			right = self.parse_factor(tokens)
			node = Node(op, node, right)
		return node
	
	def parse_factor(self, tokens):
		print("parse_factor start:", tokens)
		token = tokens.pop(0)
		print("popped:", token)
		if token == '(':
			node = self.parse_expression(tokens)
			tokens.pop(0)  # pop ')'
			return node
		elif token.isalpha():
			# could be variable or function
			if tokens and tokens[0] == '(':
				func = token
				tokens.pop(0)  # remove '('
				arg = self.parse_expression(tokens)
				tokens.pop(0)  # remove ')'
				return Node(func, arg)
			else:
				return Node(token)
		elif re.match(r'^\d+(\.\d+)?$', token):
			return Node(float(token))
		elif token == '-':  # handle negation
			return Node('*', Node('-1'), self.parse_factor(tokens))
		else:
			raise ValueError(f"unexpected token {token}")
	
	
	def parse(self):
		exploded = [t for t in self.eq.split() if t]
		print(exploded)

		if len(exploded)==0:
			raise ValueError(f"no terms resolvable to tree")
		elif len(exploded)==1:
			print(f"length of resolved tree is 1, are you sure this is not redundant?")
		
		tree = self.parse_expression(exploded)
		return tree
	
	
	
	
	
	# helpers
	def __groupWords(self):
	    words = ['arcsin', 'arccos', 'arctan', 'cosec', 'sin', 'cos', 'tan', 'sec', 'cot', 'log', 'ln', 'sqrt', 'pi', 'e', 'theta']
	    words.sort(key=len, reverse=True)
	    for f in words:
	        self.eq = re.sub(rf'\b{f}\b', f' {f} ', self.eq)
	
	def __groupOperators(self):
		ops = ['(', ')', '^', '/', '*', '+', '-']
		for f in ops:
			self.eq = re.sub(re.escape(f), f' {f} ', self.eq)
		
	def __fixXY(self):
		self.eq = re.sub(r'x[y]', 'x*y', self.eq)
		self.eq = re.sub(r'y[x]', 'y*x', self.eq)
		self.eq = re.sub(r'([0-9a-zA-Z])x', r'\1*x', self.eq)
		self.eq = re.sub(r'([0-9a-zA-Z])y', r'\1*y', self.eq)
	
	def __fixImplicitMultiplication(self):
		self.eq = re.sub(r'(?<!sin)(?<!cos)(?<!tan)(?<!log)(?<!ln)(?<!sqrt)(?<=\w|\))\(', r'*\(', self.eq)
		self.eq = re.sub(r'\)(?=\w|\()', r')*', self.eq)
	
	def __fixParentheses(self):
		sttParCount = self.eq.count('(')
		endParCount = self.eq.count(')')
		if sttParCount != endParCount:
			print(f"WARNING: parentheses mismatch ({sttParCount} '(' vs {endParCount} ')')")

		
		
	def printEq(self):
		print(self.eq)
		

class Node:
	def __init__(self, value, left=None, right=None):
		self.value = value
		self.left = left
		self.right = right

	def __repr__(self):
		# unary node (function probably)
		if self.left and not self.right:
			return f"{self.value}({self.left})"
		# binary node
		elif self.left and self.right:
			return f"({self.left} {self.value} {self.right})"
		# value
		else:
			return str(self.value)






class SymSolver:
	def __init__(self):
		self.eqns = {}
		self.values = {}
		self.words = {
			# trig
			'sin': math.sin,
			'cos': math.cos,
			'tan': math.tan,
			'arcsin': math.asin,
			'arccos': math.acos,
			'arctan': math.atan,
			'sec': lambda x: 1 / math.cos(x),
			'cosec': lambda x: 1 / math.sin(x),
			'cot': lambda x: 1 / math.tan(x),
			
			# logs
			'log': math.log10,
			'ln': math.log,
			'sqrt': math.sqrt,
			
			# constants
			'pi': math.pi,
			'e': math.e
		}
		
		self._evaluating = set()
		
	def add_equation(self,var,expr):
		parser = SymParser(expr)
		tree = parser.parse()
		self.eqns[var] = tree	
		
	def set_var_value(self, var, val):
		self.values[var] = val
		
	def evaluate(self, var):
		print("Attempting to solve for", var, "...")
		
		# very good luck
		if var in self._evaluating:
			raise ValueError(f"cannot proceed, circular dependency: {var} defined as result of function with argument {var}")

		if var in self.values:
			return self.values[var]
		elif var in self.eqns:
			self._evaluating.add(var)
			res=self.__evaluateNode(self.eqns[var])
			self._evaluating.remove(var)
			self.values[var]=res
			return res
		else:
			print(f"ERROR: no expression available for {var}")
			
	
	def __evaluateNode(self, node):
		# operands
		if node.value in ['+', '-', '*', '/', '^']:
			left = self.__evaluateNode(node.left)
			right = self.__evaluateNode(node.right)
			return self.__applyOp(node.value, left, right)
		
		# predefined constant
		elif node.value in self.words and isinstance(self.words[node.value], (int, float)):
			return self.words[node.value]
		
		# unary function
		elif node.value in self.words and callable(self.words[node.value]):
			arg = self.__evaluateNode(node.left)
			return self.words[node.value](arg)
		
		# straight numbers
		elif isinstance(node.value, (int, float)):
			return node.value
		
		# previously known or computed variables
		elif node.value in self.values:
			return self.values[node.value]
		
		# evaluate other equations
		elif node.value in self.eqns:
			return self.evaluate(node.value)

		# good luck
		else:
			raise ValueError(f"unknown variable {node.value}")
	
	
	
	def provide_graph_values(self, evar, vvar, vary, step):
		inp = vary[0]
		gvalues = []
		while inp<vary[1]:
			self.values[vvar]=inp
			res=solver.evaluate(evar)
			gvalues.append((inp,res))
			inp+=step
		
		return gvalues
			
			
	
	
	def __applyOp(self, op, left, right):
		if op == '+': return left + right
		if op == '-': return left - right
		if op == '*': return left * right
		if op == '/': return left / right
		if op == '^': return left ** right





#eq = "x^2 + y^2 - log(x) - cos[sin(y)] + (8x/6y)"
#parser = SymParser(eq)
#parser.printEq()
#t = parser.parse()
#print(t)

solver = SymSolver()

#solver.add_equation('x', "x^2 + y^2 - log(x) - cos[sin(y)] + (8x/6y)")
#print(solver.evaluate('x'))


'''
solver.add_equation('x', "y^2+2*y*z+4*a*b*z")
solver.add_equation('z', "(sin(y))^2")
solver.add_equation('y', "sin(1-sqrt(2))")

solver.add_equation('a', "12")
solver.add_equation('b', "27")

print("Resolved value for x:", solver.evaluate('x'))
'''

solver.add_equation('x', "y^2+2*y*z+4*a*b*z")
solver.add_equation('z', "(arccos(y))^2")

solver.add_equation('a', "12")
solver.add_equation('b', "27")

print("Resolved values for x over [-1,1] with step 0.1:", solver.provide_graph_values('x', 'y', [-1,1], 0.1))