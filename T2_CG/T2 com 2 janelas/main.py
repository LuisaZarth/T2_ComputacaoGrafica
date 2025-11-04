from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from Objeto3D import *
from MorphManager import MorphManager
import sys
import pygame

# Variáveis globais
objeto1 = None
objeto2 = None
morph_manager = MorphManager()

# IDs das janelas
janela1 = None
janela2 = None
janela3 = None
morph_visible = False

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
    global objeto1, objeto2, morph_manager
    
    try:
        objeto1 = Objeto3D()
        if not objeto1.LoadFile('easy2.obj'):
            print("ERRO: Não foi possível carregar easy2.obj")
            return False

        objeto2 = Objeto3D()  
        if not objeto2.LoadFile('easy1.obj'):
            print("ERRO: Não foi possível carregar easy1.obj") 
            return False
        
        print(f"Objeto 1: {objeto1.getNumVertices()} vértices, {objeto1.getNumFaces()} faces")
        print(f"Objeto 2: {objeto2.getNumVertices()} vértices, {objeto2.getNumFaces()} faces")
        
        # Configurar morph manager
        morph_manager.setObjetos(objeto1, objeto2)
        print(f"Associações criadas: {len(morph_manager.associacoes)} pares de faces")
        return True
        
    except Exception as e:
        print(f"Erro ao carregar objetos: {e}")
        return False

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
    
    DesenhaPiso()
    if objeto1:
        objeto1.Desenha()
        objeto1.DesenhaWireframe()

    glutSwapBuffers()

def tecladoJanela1(key, x, y):
    """Função de teclado para a primeira janela"""
    global morph_visible
    
    if key == b'r' or key == b'R':
        if objeto1:
            objeto1.rotation = (1, 0, 0, objeto1.rotation[3] + 2)
    elif key == b'm' or key == b'M':
        if not morph_visible:
            criarJanelaMorphing()
            morph_visible = True
    
    glutSetWindow(janela1)
    glutPostRedisplay()

def redimensionaJanela1(largura, altura):
    """Manter aspect ratio 1:1"""
    glViewport(0, 0, largura, altura)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect = largura / float(altura) if altura > 0 else 1.0
    gluPerspective(60, aspect, 0.01, 50)
    glMatrixMode(GL_MODELVIEW)

# FUNÇÕES PARA JANELA 2
def desenhaJanela2():
    """Função de desenho para a segunda janela"""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    DesenhaPiso()
    if objeto2:
        objeto2.Desenha()
        objeto2.DesenhaWireframe()

    glutSwapBuffers()

def tecladoJanela2(key, x, y):
    """Função de teclado para a segunda janela"""
    global morph_visible
    
    if key == b'r' or key == b'R':
        if objeto2:
            objeto2.rotation = (0, 1, 0, objeto2.rotation[3] + 2)
    elif key == b'm' or key == b'M':
        if not morph_visible:
            criarJanelaMorphing()
            morph_visible = True
    
    glutSetWindow(janela2)
    glutPostRedisplay()

def redimensionaJanela2(largura, altura):
    """Manter aspect ratio 1:1"""
    glViewport(0, 0, largura, altura)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect = largura / float(altura) if altura > 0 else 1.0
    gluPerspective(60, aspect, 0.01, 50)
    glMatrixMode(GL_MODELVIEW)

# FUNÇÕES PARA JANELA 3 (MORPHING)
def desenhaJanela3():
    """Função de desenho para a janela de morphing"""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    DesenhaPiso()
    
    # Desenhar objeto em morphing
    if morph_manager.objetoMorph:
        morph_manager.objetoMorph.Desenha()
        morph_manager.objetoMorph.DesenhaWireframe()

    glutSwapBuffers()

def tecladoJanela3(key, x, y):
    """Função de teclado para a janela de morphing"""
    if key == b' ':
        # Espaço inicia/pausa morphing
        if morph_manager.executando:
            morph_manager.pararMorphing()
            print("Morphing pausado")
        else:
            morph_manager.iniciarMorphing()
            print("Morphing iniciado")
    elif key == b'r' or key == b'R':
        # Rotacionar objeto em morphing
        if morph_manager.objetoMorph:
            morph_manager.objetoMorph.rotation = (0, 1, 0, morph_manager.objetoMorph.rotation[3] + 2)
    elif key == 27:  # ESC
        glutDestroyWindow(janela3)
        global morph_visible
        morph_visible = False
        return
    
    glutPostRedisplay()

def timerJanela3(valor):
    """Timer para animação do morphing"""
    if morph_manager.executando:
        if morph_manager.proximoFrame():
            glutPostRedisplay()
    glutTimerFunc(16, timerJanela3, 0)  # ~60 FPS

def redimensionaJanela3(largura, altura):
    """Manter aspect ratio 1:1"""
    glViewport(0, 0, largura, altura)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect = largura / float(altura) if altura > 0 else 1.0
    gluPerspective(60, aspect, 0.01, 50)
    glMatrixMode(GL_MODELVIEW)

def criarJanelaMorphing():
    """Cria a janela de morphing"""
    global janela3
    
    if janela3 is not None:
        glutSetWindow(janela3)
        glutPopWindow()
        return
        
    # Precisamos inicializar o contexto novamente para a nova janela
    glutInitWindowSize(400, 400)
    glutInitWindowPosition(1000, 100)
    janela3 = glutCreateWindow(b'Janela 3 - Morphing')
    
    # Configurar callbacks para a nova janela
    glutDisplayFunc(desenhaJanela3)
    glutKeyboardFunc(tecladoJanela3)
    glutReshapeFunc(redimensionaJanela3)
    
    # Inicializar OpenGL para esta janela
    init()
    PosicUser()
    
    # Iniciar timer para animação
    glutTimerFunc(16, timerJanela3, 0)
    
    print("=" * 50)
    print("JANELA DE MORPHING CRIADA!")
    print("Comandos:")
    print("  ESPAÇO - Iniciar/Pausar morphing")
    print("  R - Rotacionar objeto")
    print("  ESC - Fechar janela")
    print("=" * 50)
    
    # Forçar primeiro redesenho
    glutPostRedisplay()

# FUNÇÃO PRINCIPAL
def main():
    global janela1, janela2

    # Inicializar GLUT
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)

    # Carrega os objetos antes de criar as janelas
    if not carregaObjetos():
        print("Falha ao carregar objetos. Verifique se os arquivos .obj existem.")
        return

    # CRIA JANELA 1 
    glutInitWindowSize(400, 400)
    glutInitWindowPosition(100, 100)
    janela1 = glutCreateWindow(b'Janela 1 - Cabeca')
    
    glutDisplayFunc(desenhaJanela1)
    glutKeyboardFunc(tecladoJanela1)
    glutReshapeFunc(redimensionaJanela1)
    init()
    PosicUser()

    # CRIA JANELA 2
    glutInitWindowSize(400, 400)
    glutInitWindowPosition(550, 100)
    janela2 = glutCreateWindow(b'Janela 2 - Barco')
    
    glutDisplayFunc(desenhaJanela2)
    glutKeyboardFunc(tecladoJanela2)
    glutReshapeFunc(redimensionaJanela2)
    init()
    PosicUser()

    print("=" * 50)
    print("SISTEMA DE MORPHING 3D INICIADO")
    print("Janelas 1 e 2 criadas")
    print("Comandos:")
    print("  M - Abrir janela de morphing")
    print("  R - Rotacionar objeto")
    print("=" * 50)

    try:
        pygame.mixer.init()
        pygame.mixer.music.load('beatles.mp3') # Use .mp3 ou .ogg
        pygame.mixer.music.set_volume(0.5) # Volume de 0.0 a 1.0
        
        # O argumento '-1' significa "tocar em loop infinito"
        pygame.mixer.music.play(-1) 
        
        print("Musica carregada. Iniciando animacao...")
        
    except Exception as e:
        print(f"Nao foi possivel carregar a musica: {e}")
        print("Continuando sem som.")
    
    try:
        glutMainLoop()
    except SystemExit:
        pass
    except Exception as e:
        print(f"Erro no loop principal: {e}")

if __name__ == '__main__':
    main()