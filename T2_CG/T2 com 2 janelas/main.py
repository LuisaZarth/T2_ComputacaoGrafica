from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from Objeto3D import *
from Ponto import Ponto
import math

# Variáveis globais
objeto1: Objeto3D
objeto2: Objeto3D
objeto_morphing: Objeto3D

# IDs das janelas
janela1 = None
janela2 = None
janela_morph = None

# Controle de animação
t_interpolacao = 0.0  # 0.0 = objeto1, 1.0 = objeto2
animando = False
velocidade = 0.02
frames_totais = 50

# Associação de faces
associacoes = []  # Lista de tuplas (indice_face_obj1, indice_face_obj2)

def init():
    """Inicializa as configurações comuns do OpenGL"""
    glClearColor(0.5, 0.5, 0.9, 1.0)
    glClearDepth(1.0)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    DefineLuz()

def DefineLuz():
    """Configura a iluminação"""
    luz_ambiente = [0.4, 0.4, 0.4]
    luz_difusa = [0.7, 0.7, 0.7]
    luz_especular = [0.9, 0.9, 0.9]
    posicao_luz = [2.0, 3.0, 0.0]
    especularidade = [1.0, 1.0, 1.0]

    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_LIGHTING)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, luz_ambiente)
    glLightfv(GL_LIGHT0, GL_AMBIENT, luz_ambiente)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, luz_difusa)
    glLightfv(GL_LIGHT0, GL_SPECULAR, luz_especular)
    glLightfv(GL_LIGHT0, GL_POSITION, posicao_luz)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glMaterialfv(GL_FRONT, GL_SPECULAR, especularidade)
    glMateriali(GL_FRONT, GL_SHININESS, 51)

def PosicUser():
    """Configura a câmera"""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, 1.0, 0.01, 50)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(-2, 6, -8, 0, 0, 0, 0, 1.0, 0)

def calcularBoundingBox(objeto):
    """Calcula o bounding box de um objeto"""
    if len(objeto.vertices) == 0:
        return Ponto(0,0,0), Ponto(0,0,0)
    
    min_x = min_y = min_z = float('inf')
    max_x = max_y = max_z = float('-inf')
    
    for v in objeto.vertices:
        min_x = min(min_x, v.x)
        min_y = min(min_y, v.y)
        min_z = min(min_z, v.z)
        max_x = max(max_x, v.x)
        max_y = max(max_y, v.y)
        max_z = max(max_z, v.z)
    
    return Ponto(min_x, min_y, min_z), Ponto(max_x, max_y, max_z)

def calcularCentro(objeto):
    """Calcula o centro de um objeto"""
    min_p, max_p = calcularBoundingBox(objeto)
    return Ponto(
        (min_p.x + max_p.x) / 2,
        (min_p.y + max_p.y) / 2,
        (min_p.z + max_p.z) / 2
    )

def normalizarObjeto(objeto):
    """Normaliza um objeto para caber em [-1, 1] e centraliza na origem"""
    min_p, max_p = calcularBoundingBox(objeto)
    centro = calcularCentro(objeto)
    
    # Calcula a maior dimensão
    dx = max_p.x - min_p.x
    dy = max_p.y - min_p.y
    dz = max_p.z - min_p.z
    escala = max(dx, dy, dz)
    
    if escala == 0:
        return
    
    # Normaliza e centraliza
    for v in objeto.vertices:
        v.x = (v.x - centro.x) / escala * 2
        v.y = (v.y - centro.y) / escala * 2
        v.z = (v.z - centro.z) / escala * 2

def calcularCentroideFace(objeto, face_indices):
    """Calcula o centroide de uma face"""
    cx = cy = cz = 0
    n = len(face_indices)
    
    for idx in face_indices:
        v = objeto.vertices[idx]
        cx += v.x
        cy += v.y
        cz += v.z
    
    return Ponto(cx/n, cy/n, cz/n)

def distancia3D(p1, p2):
    """Calcula distância euclidiana entre dois pontos"""
    dx = p1.x - p2.x
    dy = p1.y - p2.y
    dz = p1.z - p2.z
    return math.sqrt(dx*dx + dy*dy + dz*dz)

def associarFaces():
    """Associa faces do objeto1 com faces do objeto2 por proximidade de centroides"""
    global associacoes
    associacoes = []
    
    # Calcula centroides de todas as faces do objeto2
    centroides_obj2 = []
    for face in objeto2.faces:
        centroides_obj2.append(calcularCentroideFace(objeto2, face))
    
    # Para cada face do objeto1, encontra a face mais próxima no objeto2
    for i, face1 in enumerate(objeto1.faces):
        centroide1 = calcularCentroideFace(objeto1, face1)
        
        # Encontra a face mais próxima
        min_dist = float('inf')
        melhor_j = 0
        
        for j, centroide2 in enumerate(centroides_obj2):
            dist = distancia3D(centroide1, centroide2)
            if dist < min_dist:
                min_dist = dist
                melhor_j = j
        
        associacoes.append((i, melhor_j))
    
    print(f"Associadas {len(associacoes)} faces")
    print(f"Objeto1: {len(objeto1.faces)} faces, Objeto2: {len(objeto2.faces)} faces")

def triangularizarFace(face):
    """Converte uma face (quad ou polígono) em triângulos"""
    if len(face) == 3:
        return [face]
    elif len(face) == 4:
        # Divide quad em 2 triângulos
        return [[face[0], face[1], face[2]], 
                [face[0], face[2], face[3]]]
    else:
        # Triangularização simples por leque
        triangulos = []
        for i in range(1, len(face)-1):
            triangulos.append([face[0], face[i], face[i+1]])
        return triangulos

def interpolarVertice(v1, v2, t):
    """Interpola linearmente entre dois vértices"""
    return Ponto(
        v1.x * (1-t) + v2.x * t,
        v1.y * (1-t) + v2.y * t,
        v1.z * (1-t) + v2.z * t
    )

def criarObjetoMorphing(t):
    """Cria objeto interpolado entre objeto1 e objeto2"""
    global objeto_morphing
    objeto_morphing = Objeto3D()
    objeto_morphing.vertices = []
    objeto_morphing.faces = []
    
    # Para cada associação de faces
    for i, (idx1, idx2) in enumerate(associacoes):
        face1 = objeto1.faces[idx1]
        face2 = objeto2.faces[idx2]
        
        # Triangulariza as faces
        tris1 = triangularizarFace(face1)
        tris2 = triangularizarFace(face2)
        
        # Garante mesmo número de triângulos
        num_tris = max(len(tris1), len(tris2))
        
        # Preenche com triângulos degenerados se necessário
        while len(tris1) < num_tris:
            tris1.append(tris1[-1])
        while len(tris2) < num_tris:
            tris2.append(tris2[-1])
        
        # Interpola cada triângulo
        for tri1, tri2 in zip(tris1, tris2):
            novo_tri = []
            
            # Garante que ambos triângulos tenham 3 vértices
            for j in range(3):
                v1 = objeto1.vertices[tri1[j]]
                v2 = objeto2.vertices[tri2[j % len(tri2)]]
                
                # Interpola e adiciona novo vértice
                v_interp = interpolarVertice(v1, v2, t)
                objeto_morphing.vertices.append(v_interp)
                novo_tri.append(len(objeto_morphing.vertices) - 1)
            
            objeto_morphing.faces.append(novo_tri)

def carregaObjetos():
    """Carrega e prepara os objetos para morphing"""
    global objeto1, objeto2
    
    objeto1 = Objeto3D()
    objeto1.LoadFile('easy1.obj')
    
    objeto2 = Objeto3D()
    objeto2.LoadFile('easy3.obj')
    
    # Normaliza os objetos
    normalizarObjeto(objeto1)
    normalizarObjeto(objeto2)
    
    # Associa as faces
    associarFaces()
    
    # Cria objeto inicial de morphing
    criarObjetoMorphing(0.0)

def DesenhaLadrilho():
    """Desenha um ladrilho do piso"""
    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    glVertex3f(-0.5, 0.0, -0.5)
    glVertex3f(-0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, -0.5)
    glEnd()

    glColor3f(1, 1, 1)
    glBegin(GL_LINE_STRIP)
    glNormal3f(0, 1, 0)
    glVertex3f(-0.5, 0.0, -0.5)
    glVertex3f(-0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, -0.5)
    glEnd()

def DesenhaPiso():
    """Desenha o piso completo"""
    glPushMatrix()
    glTranslated(-20, -1, -10)
    for x in range(-20, 20):
        glPushMatrix()
        for z in range(-20, 20):
            DesenhaLadrilho()
            glTranslated(0, 0, 1)
        glPopMatrix()
        glTranslated(1, 0, 0)
    glPopMatrix()

# FUNÇÕES JANELA 1
def desenhaJanela1():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    DesenhaPiso()
    objeto1.Desenha()
    objeto1.DesenhaWireframe()
    glutSwapBuffers()

def tecladoJanela1(key, x, y):
    if key == b'q' or key == b'Q':
        sys.exit()
    glutSetWindow(janela1)
    glutPostRedisplay()

def redimensionaJanela1(w, h):
    if h == 0: h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, w/h, 0.01, 50)
    glMatrixMode(GL_MODELVIEW)

# FUNÇÕES JANELA 2
def desenhaJanela2():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    DesenhaPiso()
    objeto2.Desenha()
    objeto2.DesenhaWireframe()
    glutSwapBuffers()

def tecladoJanela2(key, x, y):
    if key == b'q' or key == b'Q':
        sys.exit()
    glutSetWindow(janela2)
    glutPostRedisplay()

def redimensionaJanela2(w, h):
    if h == 0: h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, w/h, 0.01, 50)
    glMatrixMode(GL_MODELVIEW)

# FUNÇÕES JANELA MORPHING
def desenhaJanelaMorph():
    global t_interpolacao
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    DesenhaPiso()
    
    if objeto_morphing:
        objeto_morphing.Desenha()
        objeto_morphing.DesenhaWireframe()
    
    # Desenha informações na tela
    glDisable(GL_LIGHTING)
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 400, 0, 400)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    texto = f"t = {t_interpolacao:.2f}"
    glRasterPos2f(10, 380)
    for c in texto:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))
    
    info = "SPACE=Play/Pause R=Reset"
    glRasterPos2f(10, 360)
    for c in info:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_LIGHTING)
    
    glutSwapBuffers()

def tecladoJanelaMorph(key, x, y):
    global animando, t_interpolacao
    
    if key == b' ':  # SPACE
        animando = not animando
    elif key == b'r' or key == b'R':  # Reset
        t_interpolacao = 0.0
        criarObjetoMorphing(t_interpolacao)
    elif key == b'q' or key == b'Q':
        sys.exit()
    
    glutSetWindow(janela_morph)
    glutPostRedisplay()

def redimensionaJanelaMorph(w, h):
    if h == 0: h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, w/h, 0.01, 50)
    glMatrixMode(GL_MODELVIEW)

def idle():
    """Função de animação"""
    global t_interpolacao, animando
    
    if animando:
        t_interpolacao += velocidade
        
        if t_interpolacao >= 1.0:
            t_interpolacao = 1.0
            animando = False
        
        criarObjetoMorphing(t_interpolacao)
        
        glutSetWindow(janela_morph)
        glutPostRedisplay()

def main():
    global janela1, janela2, janela_morph

    glutInit(sys.argv)
    glutInitDisplayMode(int(GLUT_RGBA) | int(GLUT_DEPTH) | int(GLUT_DOUBLE))

    # Carrega objetos
    print("Carregando objetos...")
    carregaObjetos()
    print("Objetos carregados e normalizados!")

    # JANELA 1 - Objeto 1
    glutInitWindowSize(400, 400)
    glutInitWindowPosition(50, 50)
    janela1 = glutCreateWindow(b'Objeto 1')
    init()
    PosicUser()
    glutDisplayFunc(desenhaJanela1)
    glutKeyboardFunc(tecladoJanela1)
    glutReshapeFunc(redimensionaJanela1)

    # JANELA 2 - Objeto 2
    glutInitWindowSize(400, 400)
    glutInitWindowPosition(500, 50)
    janela2 = glutCreateWindow(b'Objeto 2')
    init()
    PosicUser()
    glutDisplayFunc(desenhaJanela2)
    glutKeyboardFunc(tecladoJanela2)
    glutReshapeFunc(redimensionaJanela2)

    # JANELA MORPHING
    glutInitWindowSize(400, 400)
    glutInitWindowPosition(950, 50)
    janela_morph = glutCreateWindow(b'Morphing')
    init()
    PosicUser()
    glutDisplayFunc(desenhaJanelaMorph)
    glutKeyboardFunc(tecladoJanelaMorph)
    glutReshapeFunc(redimensionaJanelaMorph)
    
    glutIdleFunc(idle)

    print("\nControles da janela de Morphing:")
    print("SPACE - Play/Pause animação")
    print("R - Reset (volta para t=0)")
    print("Q - Sair")

    try:
        glutMainLoop()
    except SystemExit:
        pass

if __name__ == '__main__':
    main()