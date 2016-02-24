import re
from . import CommandParser

class Macro:
	'''This class represents a Latex macro, a 
	newcommands. It saves the definition of the macro
	and it's able to recreate the tex replacement of the macro
	given the params parsed.'''

	@staticmethod
	def parse_macro(tex):
		'''
		The function need the options part of the 
		\newcommand command, withoud newcommand. It returns the
		parsed Macro object.
		'''
		grammar = [('name','{','}'),
				   ('n_param','[',']'),
				   ('default','[',']'),
				   ('definition','{','}')]
		#now we can parse the options
		things = CommandParser.parse_options(tex, grammar)[0]
		np = things['n_param']
		if np != None:
			things['n_param'] = int(np)
		else: 
			things['n_param'] = 0

		#now we split the definition around args
		#inserction 
		toks = re.split(r'#(\d+)', things['definition'])
		content = []
		#we insert into content a list of text tokens and 
		#indexs that are the index of option to be inserted
		for i in range(len(toks)):
			if i % 2 == 0:
				content.append(toks[i])
			else:
				content.append(int(toks[i]))
		return Macro(things['name'], things['n_param'],
					things['default'],content)


	def __init__(self, name, n_param, default, content):
		self.name = name
		self.n_param = n_param
		self.default = default
		self.content = content


	def get_tex(self, params, param_default=None):
		'''
		This function return the tex replacement for the 
		macro given a list of ordered parameters and, 
		if present, the default param (inside [...]).
		'''
		#dictionary for params
		pars = {}
		if self.default != None: 
			#if a default param is present
			if param_default != None:
				#if a default param is found
				pars[1] = param_default
				#we had all the params in order
				if len(params) > 0: 
					for i in range(len(params)):
						pars[i+2] = params[i]
			else:
				#we have to check if the
				#lenght of param is less then the
				#required n_param
				if len(params) < self.n_param:
					#the default param is the one in
					#the definition
					pars[1] = self.default
					#we had all the params in order
					if len(params) > 0: 
						for i in range(len(params)):
							pars[i+2] = params[i]
				else:
					#we had all the params in order
					if len(params) > 0: 
						for i in range(len(params)):
							pars[i+1] = params[i]
		else:
			#we had all the params in order
			if len(params) > 0: 
				for i in range(len(params)):
					pars[i+1] = params[i]
		#now we can work with self.content
		tex = []
		for j in range(len(self.content)):
			if j % 2 == 0: 
				tex.append(self.content[j])
			else:
				tex.append(pars[self.content[j]])
		return ''.join(tex)





