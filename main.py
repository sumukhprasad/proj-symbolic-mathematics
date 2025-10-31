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
		
	def parse(self):
		exploded = self.eq.split()
		print(exploded)
		
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
		self.eq = re.sub(r'([0-9a-zA-Z)])\(', r'\1*(', self.eq)
		self.eq = re.sub(r'\)([0-9a-zA-Z(])', r')*\1', self.eq)
	
	def __fixParentheses(self):
		sttParCount = self.eq.count('(')
		endParCount = self.eq.count(')')
		while sttParCount < endParCount:
			self.eq = '(' + self.eq
			sttParCount += 1
		while endParCount < sttParCount:
			self.eq += ')'
			endParCount += 1
		
	def printEq(self):
		print(self.eq)



	
		
eq = "x^2 + y^2 - log(x) - cos[sin(y)] + 8x + 6y"
parser = SymParser(eq)
parser.printEq()
parser.parse()