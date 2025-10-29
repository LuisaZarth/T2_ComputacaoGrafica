# ************************************************
#   Linha.py
#   Define a classe Linha
#   Autor: Márcio Sarroglia Pinho
#       pinho@pucrs.br
# ************************************************

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from Ponto import Ponto

from random import randint as rand

""" Classe Linha """
class Linha:
    def __init__(self, *args):
        if len(args) == 2 and isinstance(args[0], Ponto) and isinstance(args[1], Ponto):
            self.a, self.b = args[0], args[1]
        elif len(args) == 6:
            self.a = Ponto(args[0], args[1], args[2])
            self.b = Ponto(args[3], args[4], args[5])
        else:
            self.a = Ponto(0, 0, 0)
            self.b = Ponto(0, 0, 0)
            
    """ Desenha a linha na tela atual """
    def desenhaLinha(self):
        glBegin(GL_LINES) #linhas, pares de vértices
        
        glVertex3f(self.a.x, self.a.y, self.a.z) #coordenada inicial
        glVertex3f(self.b.x, self.b.y, self.b.z) #coordenada final
        #3f significa que são três coordenadas (x,y,z)
        glEnd()
