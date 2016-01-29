class ArgParser():
	def __init__(self, keywords = None, flags = None):
		self.prep_arg_list(keywords, flags)

	def prep_arg_list(self, keywords, flags):
		self.keywords = keywords
		self.flags = flags

	def parse_args(self, args):
		out = dict()
		using_kwargs = False
		error = False
		print('\n')
		for i, arg in enumerate(args[1:]):
			if arg[0] != '-':
				if not using_kwargs:
					out[self.keywords[i]] = arg
				else:
					print('ERROR: Cannot use positional parameter "%s" after keyword parameter(s) "%s".' %(arg, '", "'.join(out.keys())))
					error = True
			else:
				using_kwargs = True
				if '=' in arg[1:]:
					key, value = arg[1:].split('=')
					if key in self.keywords:
						out[key] = value
					else:
						print('WARNING: Keyword "%s" not recognized. Value "%s" not used' %(key, value))
				elif arg[1:] in self.flags:
					out[arg[1:]] = True
				else:
					print('WARNING: Flag "%s" not recognized.' %arg[1:])
		if error:
			print out
			print 'Closing due to error in command line arguments.'
			print 'Please try again with proper arguments.'
			exit()
		return out

class ArgHandler():
	def handle(self, user = None, password = None, help = False):
		pass


if __name__ == '__main__':
    import sys
    args = sys.argv
    keywords = ['user', 'password']
    flags = ['help']
    argparser = ArgParser(keywords, flags)
    parsed = argparser.parse_args(args)
    print(parsed)
