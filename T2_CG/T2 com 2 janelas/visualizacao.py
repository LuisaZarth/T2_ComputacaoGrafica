from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
import morphing

# Controle da animação
t_interpolacao = 0.0
animando = False
janela1 = janela2 = janela_morph = None


# ------------------------------------------------------------
# Iluminação e visual
# ------------------------------------------------------------
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


def init():
    """Configuração inicial"""
    glClearColor(0.5, 0.5, 0.9, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    DefineLuz()


def PosicUser():
    """Posiciona a câmera"""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, 1.0, 0.01, 50)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(-2, 6, -8, 0, 0, 0, 0, 1, 0)


# ------------------------------------------------------------
# Piso ladrilhado (igual ao original)
# ------------------------------------------------------------
def DesenhaLadrilho():
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


# ------------------------------------------------------------
# Desenho das janelas
# ------------------------------------------------------------
def desenhaJanela1():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    DesenhaPiso()
    morphing.objeto1.Desenha()
    morphing.objeto1.DesenhaWireframe()
    glutSwapBuffers()


def desenhaJanela2():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    DesenhaPiso()
    morphing.objeto2.Desenha()
    morphing.objeto2.DesenhaWireframe()
    glutSwapBuffers()


def desenhaJanelaMorph():
    global t_interpolacao
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    DesenhaPiso()

    if morphing.objeto_morphing:
        morphing.objeto_morphing.Desenha()
        morphing.objeto_morphing.DesenhaWireframe()

    # HUD simples mostrando o t atual
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

    info = "SPACE=Play/Pause | R=Reset | Q=Quit"
    glRasterPos2f(10, 360)
    for c in info:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_LIGHTING)

    glutSwapBuffers()


# ------------------------------------------------------------
# Controles e animação
# ------------------------------------------------------------
def teclado(key, x, y):
    global animando, t_interpolacao

    if key == b' ':
        animando = not animando
    elif key in (b'r', b'R'):
        t_interpolacao = 0.0
        morphing.atualizarMorphing(t_interpolacao)
    elif key in (b'q', b'Q'):
        sys.exit()

    glutPostRedisplay()


def idle():
    global t_interpolacao, animando
    if animando:
        t_interpolacao += morphing.velocidade
        if t_interpolacao > 1.0:
            t_interpolacao = 1.0
            animando = False

        morphing.atualizarMorphing(t_interpolacao)
        glutPostRedisplay()


# ------------------------------------------------------------
# Criação das janelas (mantém as 3 originais)
# ------------------------------------------------------------
def inicializar_janelas():
    global janela1, janela2, janela_morph

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DEPTH | GLUT_DOUBLE)

    # Janela 1
    glutInitWindowSize(400, 400)
    glutInitWindowPosition(50, 50)
    janela1 = glutCreateWindow(b'Objeto 1')
    init()
    PosicUser()
    glutDisplayFunc(desenhaJanela1)
    glutKeyboardFunc(teclado)

    # Janela 2
    glutInitWindowSize(400, 400)
    glutInitWindowPosition(500, 50)
    janela2 = glutCreateWindow(b'Objeto 2')
    init()
    PosicUser()
    glutDisplayFunc(desenhaJanela2)
    glutKeyboardFunc(teclado)

    # Janela Morph
    glutInitWindowSize(400, 400)
    glutInitWindowPosition(950, 50)
    janela_morph = glutCreateWindow(b'Morphing')
    init()
    PosicUser()
    glutDisplayFunc(desenhaJanelaMorph)
    glutKeyboardFunc(teclado)
    glutIdleFunc(idle)

    glutMainLoop()
