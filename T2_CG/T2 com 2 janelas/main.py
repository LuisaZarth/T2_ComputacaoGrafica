from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from Objeto3D import *

# Variáveis globais para os dois objetos
objeto1: Objeto3D
objeto2: Objeto3D

# IDs das janelas
janela1 = None
janela2 = None

def init():
    """Inicializa as configurações comuns do OpenGL"""
    glClearColor(0.5, 0.5, 0.9, 1.0)
    glClearDepth(1.0)

    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    DefineLuz()

def carregaObjetos():
    """Carrega os dois objetos 3D"""
    global objeto1, objeto2
    
    objeto1 = Objeto3D()
    objeto1.LoadFile('Human_Head.obj')  # Primeiro objeto
    
    objeto2 = Objeto3D()
    objeto2.LoadFile('boat.obj')  # Segundo objeto

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
    gluPerspective(60, 16/9, 0.01, 50)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(-2, 6, -8, 0, 0, 0, 0, 1.0, 0)

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

# FUNÇÕES PARA JANELA 1 

def desenhaJanela1():
    """Função de desenho para a primeira janela"""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)

    DesenhaPiso()
    objeto1.Desenha()
    objeto1.DesenhaWireframe()
    objeto1.DesenhaVertices()

    glutSwapBuffers()

def tecladoJanela1(key, x, y):
    """Função de teclado para a primeira janela"""
    objeto1.rotation = (1, 0, 0, objeto1.rotation[3] + 2)
    
    # Redesenha apenas a janela 1
    glutSetWindow(janela1)
    glutPostRedisplay()

def inicializaJanela1():
    """Inicializa configurações específicas da janela 1"""
    init()
    PosicUser()

# FUNÇÕES PARA JANELA 2
def desenhaJanela2():
    """Função de desenho para a segunda janela"""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)

    DesenhaPiso()
    objeto2.Desenha()
    objeto2.DesenhaWireframe()
    objeto2.DesenhaVertices()

    glutSwapBuffers()

def tecladoJanela2(key, x, y):
    """Função de teclado para a segunda janela"""
    objeto2.rotation = (0, 1, 0, objeto2.rotation[3] + 2)  # Rotaciona em eixo diferente (Y)
    
    # Redesenha apenas a janela 2
    glutSetWindow(janela2)
    glutPostRedisplay()

def inicializaJanela2():
    """Inicializa configurações específicas da janela 2"""
    init()
    PosicUser()

# FUNÇÃO PRINCIPAL

def main():
    global janela1, janela2

    glutInit(sys.argv)
    glutInitDisplayMode(int(GLUT_RGBA) | int(GLUT_DEPTH))

    # Carrega os objetos antes de criar as janelas
    carregaObjetos()

    # CRIA JANELA 1 
    glutInitWindowSize(640, 480)
    glutInitWindowPosition(100, 100)
    janela1 = glutCreateWindow(b'Janela 1 - Cabeca')
    
    # Configura callbacks da janela 1
    inicializaJanela1()
    glutDisplayFunc(desenhaJanela1)
    glutKeyboardFunc(tecladoJanela1)

    # CRIA JANELA 2
    glutInitWindowSize(640, 480)
    glutInitWindowPosition(750, 100)  # Posição diferente para não sobrepor
    janela2 = glutCreateWindow(b'Janela 2 - Barco')
    
    # Configura callbacks da janela 2
    inicializaJanela2()
    glutDisplayFunc(desenhaJanela2)
    glutKeyboardFunc(tecladoJanela2)

    try:
        glutMainLoop()
    except SystemExit:
        pass

if __name__ == '__main__':
    main()