from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from Ponto import *
'''Carrega modelos 3D do formato obj e os renderiza usando OpenGl de 3 formas:
vértices, wireframe e sólido'''
class Objeto3D:
        
    def __init__(self):
        self.vertices = [] #lista de objetos Ponto que representa cada vértice do modelo
        self.faces    = [] #lista contendo índices dos vértices que formam cada face
        self.position = Ponto(0,0,0) #posição do objeto no espaço 3D, translação
        self.rotation = (0,0,0,0) #tupla para rotação, (x,y,z,ângulo)
        pass
    #carrega um arquivo obj e extrai vértices e faces.
    def LoadFile(self, file:str):
        f = open(file, "r")

        # leitor de .obj baseado na descrição em https://en.wikipedia.org/wiki/Wavefront_.obj_file    
        for line in f:
            values = line.split(' ')
            # dividimos a linha por ' ' e usamos o primeiro elemento para saber que tipo de item temos

            if values[0] == 'v': 
                # se a linha começa com v, é um vértice
                #converte os valores para float , coordenadas
                self.vertices.append(Ponto(float(values[1]),
                                           float(values[2]),
                                           float(values[3])))

            if values[0] == 'f':
                # se a linha começa com f, é uma face. 
                self.faces.append([]) 
                for fVertex in values[1:]:
                    fInfo = fVertex.split('/')
                    # dividimos cada elemento por '/'
                    self.faces[-1].append(int(fInfo[0]) - 1) # primeiro elemento é índice do vértice da face
                    # ignoramos textura e normal
                
            # ignoramos outros tipos de items, no exercício não é necessário e vai só complicar mais
        pass
    #desenha somente as vértices do objeto    
    def DesenhaVertices(self):
        glPushMatrix() #salva o estado atual da matriz de transformação
        glTranslatef(self.position.x, self.position.y, self.position.z) #move objeto para sua posição
        glRotatef(self.rotation[3], self.rotation[0], self.rotation[1], self.rotation[2]) #aplica rotação
        glColor3f(.1, .1, .8)
        glPointSize(8) #tamanho dos pontos

        glBegin(GL_POINTS) #desenho dos pontos
        for v in self.vertices: #para cada vértice, desenha 1 ponto em sua posição
            glVertex(v.x, v.y, v.z)
        glEnd()
        
        glPopMatrix() #desfaz a matriz de transformação
        pass
    #desenha o contorno (aramado) das faces
    def DesenhaWireframe(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glRotatef(self.rotation[3], self.rotation[0], self.rotation[1], self.rotation[2])
        glColor3f(0, 0, 0)
        glLineWidth(2)        
        
        for f in self.faces:  #para cada face
            glBegin(GL_LINE_LOOP) 
            for iv in f: #para cada índice de vértice na face
                v = self.vertices[iv] #busca o vértice correspondente
                glVertex(v.x, v.y, v.z) #desenha na vértice
            glEnd()
        
        glPopMatrix()
        pass
    #desenha o objeto sólido, preenchido em cinza
    def Desenha(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glRotatef(self.rotation[3], self.rotation[0], self.rotation[1], self.rotation[2])
        glColor3f(0.34, .34, .34)
        glLineWidth(2)        
        
        for f in self.faces:            
            glBegin(GL_TRIANGLE_FAN) #preenche a face como triângulos
            for iv in f:
                v = self.vertices[iv]
                glVertex(v.x, v.y, v.z)
            glEnd()
        
        glPopMatrix()
        pass


