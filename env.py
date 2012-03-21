from htmlr.environment import Environment

e = Environment('.')

t = e.get_template('sample')
print(t.display())
