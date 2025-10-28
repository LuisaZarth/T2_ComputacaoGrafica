# ************************************************
#   Ponto.py
#   Define a classe Ponto
#   Autor: Márcio Sarroglia Pinho
#       pinho@pucrs.br
# ************************************************

import math

""" Classe Ponto """
class Ponto:   
    def __init__(self, x=0,y=0,z=0):
        self.x = x
        self.y = y
        self.z = z
#coordenadas do ponto no espaço 3D, 0 como valores padrão    
    """ Imprime os valores de cada eixo do ponto """
    # Faz a impressao usando sobrecarga de funcao
    # https://www.educative.io/edpresso/what-is-method-overloading-in-python
    #exibe as coordenadas dos Pontos no console
    def imprime(self, msg=None):
        if msg is not None:
            print (msg, self.x, self.y, self.z)
        else:
            print (self.x, self.y, self.z)

    """ Define os valores dos eixos do ponto 
    Modifica as coordenadas do ponto"""
    def set(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z
    
# Definicao de operadores
# https://www.programiz.com/python-programming/operator-overloading
#permite usar + entre pontos, ignora z 
    def __add__(self, other):
            x = self.x + other.x
            y = self.y + other.y
            return Ponto(x, y)
#permite usar - entre pontos, para calcular vetores, diferenças entre pontos, ignora z
    def __sub__(self, other):
            x = self.x - other.x
            y = self.y - other.y
            return Ponto(x, y)
#multiplica por um escalar, amplia ou reduz
    def __mul__(self, other: int):
            x = self.x * other
            y = self.y * other
            return Ponto(x, y)
#rotaciona o ponto em torno do eixo z
#converte o ângulo de graus para radianos
    def rotacionaZ(self, angulo):
        anguloRad = angulo * 3.14159265359/180.0
        xr = self.x*math.cos(anguloRad) - self.y*math.sin(anguloRad) #matriz de rotação 2D no plano XY
        yr = self.x*math.sin(anguloRad) + self.y*math.cos(anguloRad)
        self.x = xr #atualiza as coordenadas, z inalterada.
        self.y = yr
#rotação do ponto em torno do eixo Y
    def rotacionaY(self, angulo):
        anguloRad = angulo* 3.14159265359/180.0
        xr =  self.x*math.cos(anguloRad) + self.z*math.sin(anguloRad)
        zr = -self.x*math.sin(anguloRad) + self.z*math.cos(anguloRad)
        self.x = xr #idem, y inalterado
        self.z = zr
#rotaciona o ponto em torno do eixo X
    def rotacionaX(self, angulo):
        anguloRad = angulo* 3.14159265359/180.0
        yr =  self.y*math.cos(anguloRad) - self.z*math.sin(anguloRad)
        zr =  self.y*math.sin(anguloRad) + self.z*math.cos(anguloRad)
        self.y = yr
        self.z = zr

# ********************************************************************** */
#                                                                        */
#  Calcula a interseccao entre 2 retas (no plano "XY" Z = 0)             */
#                                                                        */
# k : ponto inicial da reta 1                                            */
# l : ponto final da reta 1                                              */
# m : ponto inicial da reta 2                                            */
# n : ponto final da reta 2                                              */
# 
# Retorna:
# 0, se não houver interseccao ou 1, caso haja                                                                       */
# int, valor do parâmetro no ponto de interseção (sobre a reta KL)       */
# int, valor do parâmetro no ponto de interseção (sobre a reta MN)       */
#                                                                        */
# ********************************************************************** */
#calcula a interseção entre duas retas no plano XY, ignora Z
#Reta 1 k até l, reta 2 m até n.
'''Ela calcula o determinante, para verificar se as retas são paralelas, 
se det =! 0, calcula os parâmetros s e t e eles indicam onde nas retas 
ocorre a interseção'''
def intersec2d(k: Ponto, l: Ponto, m: Ponto, n: Ponto) -> (int, float, float):
    det = (n.x - m.x) * (l.y - k.y)  -  (n.y - m.y) * (l.x - k.x)

    if (det == 0.0):
        return 0, None, None # não há intersecção, retas paralelas.
    #parâmetro na reta KL - 0 e 1 significa dentro do segmento
    s = ((n.x - m.x) * (m.y - k.y) - (n.y - m.y) * (m.x - k.x))/ det
    #parâmetro na MN
    t = ((l.x - k.x) * (m.y - k.y) - (l.y - k.y) * (m.x - k.x))/ det

    return 1, s, t # há intersecção

# **********************************************************************
# HaInterseccao(k: Ponto, l: Ponto, m: Ponto, n: Ponto)
# Detecta interseccao entre os pontos
#
# **********************************************************************
'''Verifica se dois segmentos da reta se interceptam
Se s e t entre 0 e 1, há interseção dentro dos segmentos '''
def HaInterseccao(k: Ponto, l: Ponto, m: Ponto, n: Ponto) -> bool:
    ret, s, t = intersec2d( k,  l,  m,  n)

    if not ret: return False #True se os segmentos se cruzam e False se não

    return s>=0.0 and s <=1.0 and t>=0.0 and t<=1.0

