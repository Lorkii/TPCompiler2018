import AST
import copy
from AST import addToClass
import re
from functools import reduce

# operateurs mathematiques
operations = {
    '+': lambda x, y : x + y,
    '-': lambda x, y : x - y,
    '*': lambda x, y : x * y,
    '/': lambda x, y : x / y,
}

# operateurs de comparaison
compOperations = {
    '<': lambda x, y : x < y,
    '>': lambda x, y : x > y,
    '<=': lambda x, y : x <= y,
    '>=': lambda x, y : x >= y,
    '==': lambda x, y : x == y,
    '!=': lambda x,y : x != y,
}

vars = [{}]
globalVars = {}
funs = {}


@addToClass(AST.ProgramNode)
def execute(self):
    for c in self.children:
        c.execute()

@addToClass(AST.TokenNode)
def execute(self):
    if isinstance(self.tok, str):
        try:
            # we check if it exists in the local variables, if not we also check the globals and otherwise it's undefined
            try:
                return vars[0][self.tok]
            except:
                return globalVars[self.tok]
        except KeyError:
            print("*** Error : variable %s undefined!" % self.tok)
            return None
    return self.tok

@addToClass(AST.OpNode)
def execute(self):
    args = [c.execute() for c in self.children]
    if len(args) == 1:
        args.insert(0, 0)
    try:
        return reduce(operations[self.op], args)
    except:
        print(f"*** Error : invalid operation between operands {args[0]} and {args[1]}")

@addToClass(AST.CompOpNode)
def execute(self):
    args = [c.execute() for c in self.children]
    if len(args) == 2:
        try:
            return compOperations[self.op](float(args[0]), float(args[1]))
        except:
            print(f"*** Error : Invalid comparison between operands {args[0]} and {args[1]}")
    else:
        return False

#We save the function's body in the functions dict, under the function's name
@addToClass(AST.FunDecNode)
def execute(self):
    funs[self.name] = self
    
#When we call the function, we extract it's body to add at the start the parameters as assignation nodes.
#The parameters are actually just variables (AssignNode) that we add at the start of the body
#We also manage the local and global memory in the function. When we start a function, we add a "memory" in the vars. When the return
#is attained, we unpop it. With this method, we can make recursive functions call, and the local memories are still intact when leaving the recursion
@addToClass(AST.FunCallNode)
def execute(self):
    try:
        #If the numbers of parameters at call and in the prototype aren't the same, we throw an error
        if len(funs[self.name].params) is not len(self.params):
            print(f"*** Error : Number of parameters doesn't correspond to function's prototype ({len(self.params)} given, {len(funs[self.name].params)} expected) ")
            return
        
        localVars = {}
        #Add parameters at the start of the body
        for identifier, value in zip(funs[self.name].params, self.params):
            localVars[identifier] = value.execute()
        
        #we add the memory to the top of the stack
        global vars
        vars.insert(0, localVars)
        
        #execution of the body code
        try:
            funs[self.name].body.execute()
        except:
            pass
        
        return funs[self.name].result.execute()
        
    except KeyError:
        print(f"*** Error : Call to undefined function ")

#This node is used to return a value and know when to unstack the function's local memory
@addToClass(AST.ReturnNode)
def execute(self):
    result = self.result.execute()
    #return to the last variable scope
    global vars
    vars = vars[1:]
    return result

@addToClass(AST.StringNode)
def execute(self):
    return str(self)

@addToClass(AST.BooleanNode)
def execute(self):
    return self.val

@addToClass(AST.AssignNode)
def execute(self):
    if(self.isGlobal):
        globalVars[self.children[0].tok] = self.children[1].execute()
    else:
        vars[0][self.children[0].tok] = self.children[1].execute()

@addToClass(AST.PrintNode)
def execute(self):
    print(self.children[0].execute())

@addToClass(AST.WhileNode)
def execute(self):
    while self.children[0].execute():
        self.children[1].execute()

@addToClass(AST.IfNode)
def execute(self):
    if self.children[0].execute():
        self.children[1].execute()

if __name__ == '__main__':
    from parser5 import parse
    import sys
    
    try:
        with open(sys.argv[1]) as f:
            prog = f.read()
    except:
        print("passer un fichier en argument")
    
    ast = parse(prog)

    ast.execute()
