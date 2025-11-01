import tkinter as tk
from tkinter import scrolledtext
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt



from solver import *


class SymREPL(tk.Tk):
	def __init__(self, solver):
		super().__init__()
		self.solver = solver
		self.title("Symbolic Math REPL")
		self.geometry("800x600")
		
		self.output = scrolledtext.ScrolledText(self, wrap=tk.WORD, state="disabled", bg="#fdf9eb", fg="#000", font=("Monaco", 12))
		self.output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
		
		self.input = tk.Entry(self, bg="#fff", fg="#000", font=("Monaco", 12))
		self.input.pack(fill=tk.X, padx=5, pady=(0,5))
		self.input.bind("<Return>", self.handle_input)
		
		self.__write("Symbolic Mathematics Project\nREPL Interface\n------\nType into the input box and press Return.\n", color="#0d7680")
		
	def __write(self, s, color="#355778"):
		self.output.configure(state="normal")
		tag_name = f"color_{color}"
		if not tag_name in self.output.tag_names():
			self.output.tag_configure(tag_name, foreground=color)
		self.output.insert(tk.END, s + "\n", tag_name)
		self.output.configure(state="disabled")
		self.output.see(tk.END)
	
	def handle_input(self, event):
		cmd = self.input.get().strip()
		self.input.delete(0, tk.END)

		if not cmd:
			return
		self.__write(f">>> {cmd}", color="#e6175c")
		try:
			self.process_command(cmd)
		except Exception as e:
			self.__write(f"error: {e}", color="#f00")
			
			
	def process_command(self, cmd):
		if "=" in cmd:
			var, expr = map(str.strip, cmd.split("=", 1))
			if expr.replace('.', '', 1).isdigit():
				self.solver.set_var_value(var, float(expr))
				self.__write(f"set {var} = {expr}")
			else:
				self.solver.add_equation(var, expr)
				self.__write(f"added equation: {var} = {expr}")
		elif cmd.startswith("eval "):
			var = cmd.split(" ", 1)[1]
			val = self.solver.evaluate(var)
			self.__write(f"{var} = {val}")
		elif cmd.startswith("plot"):
			parts = cmd.split()
			if len(parts) != 6:
				self.__write("usage: plot <evaluated_var> <varying_var> <start> <end> <step>", color="#f00")
				return
	
			evar = parts[1]
			vvar = parts[2]
			start = float(parts[3])
			end = float(parts[4])
			step = float(parts[5])
	
			try:
				data = self.solver.provide_graph_values(evar, vvar, (start, end), step)
			except Exception as e:
				self.__write(f"plot error: {e}", color="#f00")
				return
	
			xs, ys = zip(*data)
			plt.figure()
			plt.plot(xs, ys)
			plt.title(f"{evar} vs {vvar}")
			plt.xlabel(vvar)
			plt.ylabel(evar)
			plt.grid(True)
			self.__write(f"plotted {evar} over {vvar} in range [{start}, {end}], opening plot...", color="#0a0")
			plt.show()
			self.__write(f"done.", color="#0a0")
		
		
		elif cmd == "vars":
			self.__write(str(self.solver.values))
		elif cmd == "help":
			self.__write("commands:\n"
						"  var = expr   define equation\n"
						"  var = num    set value\n"
						"  eval var     evaluate a variable\n"
						"  plot         plot a graph\n"
						"  vars         show all known values\n"
						"  help         show this help\n"
						"  clear        reset everything")
		elif cmd == "clear":
			self.solver = SymSolver()
			self.__write("cleared all equations + values")
		else:
			self.__write(f"unknown command: {cmd}")

if __name__ == "__main__":
	solver = SymSolver()
	app = SymREPL(solver)
	app.mainloop()