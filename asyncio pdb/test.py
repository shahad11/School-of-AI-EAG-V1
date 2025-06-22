#code is for interactive python shell
import code
#pdb is for debugger
from pdb import set_trace


def adder(a, b):

    return a + b

a = 4
b = 6
set_trace()
d=3
#code.interact(local=locals())
print("breaking into the code")
holder =  adder(a, b)
print(f"Result of adder: {holder}")


