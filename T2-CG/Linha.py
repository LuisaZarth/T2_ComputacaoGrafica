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
    def __init__(self, a: Ponto, b: Ponto):
        self.a = a
        self.b = b
    #cria dois objetos a partir das coordenadas fornecidas e armazena em self.a e self.b
    def __init__(self, x1: float = 0, y1: float = 0, z1 : float = 0, x2: float = 0, y2: float = 0, z2: float = 0):
        self.a = Ponto(x1, y1, z1) #coordenadas do primeiro ponto
        self.b = Ponto(x2, y2, z2) #coordenadas do segundo ponto

    """ Desenha a linha na tela atual """
    def desenhaLinha(self):
        glBegin(GL_LINES) #linhas, pares de vértices
        
        glVertex3f(self.a.x, self.a.y, self.a.z) #coordenada inicial
        glVertex3f(self.b.x, self.b.y, self.b.z) #coordenada final
        #3f significa que são três coordenadas (x,y,z)
        glEnd()