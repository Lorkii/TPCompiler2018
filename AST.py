# coding: latin-1

''' Petit module utilitaire pour la construction, la manipulation et la 
repr�sentation d'arbres syntaxiques abstraits.

S�rement plein de bugs et autres surprises. � prendre comme un 
"work in progress"...
Notamment, l'utilisation de pydot pour repr�senter un arbre syntaxique cousu
est une utilisation un peu "limite" de graphviz. �a marche, mais le layout n'est
pas toujours optimal...
'''

import pydot_ng as pydot

class Node:
    count = 0
    type = 'Node (unspecified)'
    shape = 'ellipse'
    def __init__(self,children=None):
        self.ID = str(Node.count)
        Node.count+=1
        if not children: self.children = []
        elif hasattr(children,'__len__'):
            self.children = children
        else:
            self.children = [children]
        self.next = []

    def addNext(self,next):
        self.next.append(next)

    def asciitree(self, prefix=''):
        result = "%s%s\n" % (prefix, repr(self))
        prefix += '|  '
        for c in self.children:
            if not isinstance(c,Node):
                result += "%s*** Error: Child of type %r: %r\n" % (prefix,type(c),c)
                continue
            result += c.asciitree(prefix)
        return result
    
    def __str__(self):
        return self.asciitree()
    
    def __repr__(self):
        return self.type
    
    def makegraphicaltree(self, dot=None, edgeLabels=True):
            if not dot: dot = pydot.Dot()
            dot.add_node(pydot.Node(self.ID,label=repr(self), shape=self.shape))
            label = edgeLabels and len(self.children)-1
            for i, c in enumerate(self.children):
                c.makegraphicaltree(dot, edgeLabels)
                edge = pydot.Edge(self.ID,c.ID)
                if label:
                    edge.set_label(str(i))
                dot.add_edge(edge)
                #Workaround for a bug in pydot 1.0.2 on Windows:
                #dot.set_graphviz_executables({'dot': r'C:\Program Files\Graphviz2.38\bin\dot.exe'})
            return dot
        
    def threadTree(self, graph, seen = None, col=0):
            colors = ('red', 'green', 'blue', 'yellow', 'magenta', 'cyan')
            if not seen: seen = []
            if self in seen: return
            seen.append(self)
            new = not graph.get_node(self.ID)
            if new:
                graphnode = pydot.Node(self.ID,label=repr(self), shape=self.shape)
                graphnode.set_style('dotted')
                graph.add_node(graphnode)
            label = len(self.next)-1
            for i,c in enumerate(self.next):
                if not c: return
                col = (col + 1) % len(colors)
                col=0 # FRT pour tout afficher en rouge
                color = colors[col]                
                c.threadTree(graph, seen, col)
                edge = pydot.Edge(self.ID,c.ID)
                edge.set_color(color)
                edge.set_arrowsize('.5')
                # Les arr�tes correspondant aux coutures ne sont pas prises en compte
                # pour le layout du graphe. Ceci permet de garder l'arbre dans sa repr�sentation
                # "standard", mais peut provoquer des surprises pour le trajet parfois un peu
                # tarabiscot� des coutures...
                # En commantant cette ligne, le layout sera bien meilleur, mais l'arbre nettement
                # moins reconnaissable.
                edge.set_constraint('false') 
                if label:
                    edge.set_taillabel(str(i))
                    edge.set_labelfontcolor(color)
                graph.add_edge(edge)
            return graph    
        
class ProgramNode(Node):
    type = 'Program'

#This represent the declaration of a function. Under the function's name, we save the function's body and parameters for later uses
class FunDecNode(Node):
    type = 'Func'
    def __init__(self, name, body, params, result):
        Node.__init__(self)
        self.body = body
        self.name = name
        self.params = params
        self.result = result

class FunCallNode(Node):
    type = "callNode"
    def __init__(self, name, params):
        Node.__init__(self)
        self.name = name
        self.params = params

class ReturnNode(Node):
    type = "returnNode"
    def __init__(self, result):
        Node.__init__(self)
        self.result = result
    
class TokenNode(Node):
    type = 'token'
    def __init__(self, tok):
        Node.__init__(self)
        self.tok = tok
        
    def __repr__(self):
        return repr(self.tok)

class StringNode(Node):
    type = 'string'
    def __init__(self, val):
        Node.__init__(self)
        self.val = val
        
    def __str__(self):
        return str(self.val)

class BooleanNode(Node):
    type = 'boolean'
    def __init__(self, val):
        Node.__init__(self)
        if val == "True":
            self.val = True
        else:
            self.val = False

class OpNode(Node):
    def __init__(self, op, children):
        Node.__init__(self,children)
        self.op = op
        try:
            self.nbargs = len(children)
        except AttributeError:
            self.nbargs = 1
        
    def __repr__(self):
        return "%s (%s)" % (self.op, self.nbargs)

class CompOpNode(Node):
    def __init__(self, op, children):
        Node.__init__(self,children)
        self.op = op

class AssignNode(Node):
    type = '='
    def __init__(self, children, isGlobal=False):
        Node.__init__(self, children)
        self.isGlobal = isGlobal
    
class PrintNode(Node):
    type = 'print'
    
class IfNode(Node):
    type = 'if'

class WhileNode(Node):
    type = 'while'
    
class EntryNode(Node):
    type = 'ENTRY'
    def __init__(self):
        Node.__init__(self, None)
    
def addToClass(cls):
    ''' Decorateur permettant d'ajouter la fonction decoree en tant que methode
    a une classe.
    
    Permet d'implementer une forme elementaire de programmation orientee
    aspects en regroupant les methodes de differentes classes implementant
    une meme fonctionnalite en un seul endroit.
    
    Attention, apres utilisation de ce decorateur, la fonction decoree reste dans
    le namespace courant. Si cela derange, on peut utiliser del pour la detruire.
    Je ne sais pas s'il existe un moyen d'eviter ce phenomene.
    '''
    def decorator(func):
        setattr(cls,func.__name__,func)
        return func
    return decorator
