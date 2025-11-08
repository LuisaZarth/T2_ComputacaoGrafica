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
    # No método LoadFile da classe Objeto3D, substitua por:

    def LoadFile(self, file:str):
        try:
            f = open(file, "r")
            self.vertices = []
            self.faces = []

            for line in f:
                values = line.split()
                if not values:
                    continue

                if values[0] == 'v': 
                    if len(values) >= 4:
                        self.vertices.append(Ponto(float(values[1]),
                                                    float(values[2]),
                                                    float(values[3])))

                if values[0] == 'f':
                    face_vertices = []
                    for fVertex in values[1:]:
                        if fVertex:
                            fInfo = fVertex.split('/')
                        # Pega apenas o índice do vértice (primeiro valor)
                            vert_index = int(fInfo[0]) - 1  # OBJ é 1-indexed
                            face_vertices.append(vert_index)
                
                    if len(face_vertices) >= 3:  # Só adiciona se tiver pelo menos 3 vértices
                        self.faces.append(face_vertices)
                
            f.close()
            print(f"Arquivo {file} carregado: {len(self.vertices)} vértices, {len(self.faces)} faces")
            return True
        
        except Exception as e:
            print(f"Erro ao carregar arquivo {file}: {e}")
            return False
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
    # Adicione estes métodos à classe Objeto3D:
    
    def getNumFaces(self):
        return len(self.faces)
        
    def getNumVertices(self):
        return len(self.vertices)
        
    def getBoundingBox(self):
        if not self.vertices:
            return (Ponto(0,0,0), Ponto(0,0,0))
            
        min_x = min(v.x for v in self.vertices)
        max_x = max(v.x for v in self.vertices)
        min_y = min(v.y for v in self.vertices)
        max_y = max(v.y for v in self.vertices)
        min_z = min(v.z for v in self.vertices)
        max_z = max(v.z for v in self.vertices)
        
        return (Ponto(min_x, min_y, min_z), Ponto(max_x, max_y, max_z))

