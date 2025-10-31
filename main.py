import re

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
		tree = self.parse_expression(exploded)
		print(tree)
		
		
		
		
		
	# helpers
	def __groupWords(self):
		words = ['sin', 'cos', 'tan', 'log', 'ln', 'sqrt', 'pi', 'e', 'theta']
		for f in words:
			self.eq = re.sub(f, f' {f} ', self.eq)
	
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
		
	
		
eq = "x^2 + y^2 - log(x) - cos[sin(y)] + 8x + 6y"
parser = SymParser(eq)
parser.printEq()
parser.parse()