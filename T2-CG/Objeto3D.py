from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from Ponto import *

class Objeto3D:
    def __init__(self):
        self.vertices = []
        self.faces = []
        self.position = Ponto(0, 0, 0)
        self.rotation = (0, 0, 0, 0)

    def LoadFile(self, file: str):
        """Carrega um arquivo obj e extrai vértices e faces"""
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
                            vert_index = int(fInfo[0]) - 1  # OBJ é 1-indexed
                            face_vertices.append(vert_index)
                    
                    if len(face_vertices) >= 3:
                        self.faces.append(face_vertices)
            
            f.close()
            print(f"Arquivo {file} carregado: {len(self.vertices)} vértices, {len(self.faces)} faces")
            return True
            
        except Exception as e:
            print(f"Erro ao carregar arquivo {file}: {e}")
            return False

    def calcularNormal(self, v0, v1, v2):
        """Calcula a normal de uma face dados 3 vértices"""
        # Vetores da face
        ux = v1.x - v0.x
        uy = v1.y - v0.y
        uz = v1.z - v0.z
        
        vx = v2.x - v0.x
        vy = v2.y - v0.y
        vz = v2.z - v0.z
        
        # Produto vetorial para normal
        nx = uy * vz - uz * vy
        ny = uz * vx - ux * vz
        nz = ux * vy - uy * vx
        
        # Normalizar
        length = (nx*nx + ny*ny + nz*nz) ** 0.5
        if length > 0:
            return (nx/length, ny/length, nz/length)
        return (0, 0, 1)

    def DesenhaVertices(self):
        """Desenha somente as vértices do objeto"""
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glRotatef(self.rotation[3], self.rotation[0], self.rotation[1], self.rotation[2])
        
        glDisable(GL_LIGHTING)
        glColor3f(.1, .1, .8)
        glPointSize(8)
        glBegin(GL_POINTS)
        for v in self.vertices:
            glVertex(v.x, v.y, v.z)
        glEnd()
        glEnable(GL_LIGHTING)
        
        glPopMatrix()

    def DesenhaWireframe(self):
        """Desenha o contorno (aramado) das faces"""
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glRotatef(self.rotation[3], self.rotation[0], self.rotation[1], self.rotation[2])
        
        glDisable(GL_LIGHTING)
        glColor3f(0, 0, 0)
        glLineWidth(1)
        
        for f in self.faces:
            glBegin(GL_LINE_LOOP)
            for iv in f:
                if iv < len(self.vertices):  # Verificação de segurança
                    v = self.vertices[iv]
                    glVertex(v.x, v.y, v.z)
            glEnd()
        
        glEnable(GL_LIGHTING)
        glPopMatrix()

    def Desenha(self):
        """Desenha o objeto sólido com iluminação"""
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glRotatef(self.rotation[3], self.rotation[0], self.rotation[1], self.rotation[2])
        
        # Habilitar iluminação
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Cor base do objeto (cinza claro)
        cor_base = [0.7, 0.7, 0.7]
        glColor3fv(cor_base)
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [0.2, 0.2, 0.2])
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, cor_base)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.5, 0.5, 0.5])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 32.0)
        
        # Desenhar cada face
        for f in self.faces:
            if len(f) < 3:
                continue
            
            # Calcular e aplicar normal da face
            if all(iv < len(self.vertices) for iv in f[:3]):
                v0 = self.vertices[f[0]]
                v1 = self.vertices[f[1]]
                v2 = self.vertices[f[2]]
                nx, ny, nz = self.calcularNormal(v0, v1, v2)
                glNormal3f(nx, ny, nz)
            
            # Desenhar a face
            glBegin(GL_POLYGON)
            for iv in f:
                if iv < len(self.vertices):  # Verificação de segurança
                    v = self.vertices[iv]
                    glVertex3f(v.x, v.y, v.z)
            glEnd()
        
        glPopMatrix()

    def getNumFaces(self):
        return len(self.faces)

    def getNumVertices(self):
        return len(self.vertices)

    def getBoundingBox(self):
        if not self.vertices:
            return (Ponto(0, 0, 0), Ponto(0, 0, 0))
        
        min_x = min(v.x for v in self.vertices)
        max_x = max(v.x for v in self.vertices)
        min_y = min(v.y for v in self.vertices)
        max_y = max(v.y for v in self.vertices)
        min_z = min(v.z for v in self.vertices)
        max_z = max(v.z for v in self.vertices)
        
        return (Ponto(min_x, min_y, min_z), Ponto(max_x, max_y, max_z))
