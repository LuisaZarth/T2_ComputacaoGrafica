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
rotacao_automatica_janela3 = False

def init():
    """Inicializa as configurações comuns do OpenGL"""
    glClearColor(0.5, 0.5, 0.9, 1.0)
    glClearDepth(1.0)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    DefineLuz()

def carregaObjetos():
    """Carrega os dois objetos 3D"""
    global objeto1, objeto2, morph_manager
    
    try:
        objeto1 = Objeto3D()
        if not objeto1.LoadFile('hard3.obj'):
            print("ERRO: Não foi possível carregar o objeto hard1.obj")
            return False
        
        objeto2 = Objeto3D()
        if not objeto2.LoadFile('hard1.obj'):
            print("ERRO: Não foi possível carregar o objeto hard3.obj")
            return False
        
        # Configurar morph manager
        morph_manager.setObjetos(objeto1, objeto2)
        
        print("\n=== VERIFICAÇÃO DE INICIALIZAÇÃO ===")
        print(f"Objeto1: {len(objeto1.vertices)} vértices, {len(objeto1.faces)} faces")
        print(f"Objeto2: {len(objeto2.vertices)} vértices, {len(objeto2.faces)} faces")
        print(f"ObjetoMorph: {len(morph_manager.objetoMorph.vertices)} vértices, {len(morph_manager.objetoMorph.faces)} faces")
        print(f"Sistema pronto para morphing!")
        print("===================================\n")
        
        return True
        
    except Exception as e:
        print(f"Erro ao carregar objetos: {e}")
        import traceback
        traceback.print_exc()
        return False

def DefineLuz():
    """Configura a iluminação"""
    luz_ambiente = [0.4, 0.4, 0.4, 1.0]
    luz_difusa = [0.7, 0.7, 0.7, 1.0]
    luz_especular = [0.9, 0.9, 0.9, 1.0]
    posicao_luz = [2.0, 3.0, 0.0, 1.0]
    especularidade = [1.0, 1.0, 1.0, 1.0]
    
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, luz_ambiente)
    glLightfv(GL_LIGHT0, GL_AMBIENT, luz_ambiente)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, luz_difusa)
    glLightfv(GL_LIGHT0, GL_SPECULAR, luz_especular)
    glLightfv(GL_LIGHT0, GL_POSITION, posicao_luz)
    
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, especularidade)
    glMateriali(GL_FRONT_AND_BACK, GL_SHININESS, 51)

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
    glDisable(GL_LIGHTING)
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
    glEnable(GL_LIGHTING)

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
    if key == b'm' or key == b'M':
        if not morph_visible:
            criarJanelaMorphing()
            morph_visible = True
    glutSetWindow(janela1)
    glutPostRedisplay()

def redimensionaJanela1(largura, altura):
    """Manter aspect ratio"""
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
    if key == b'm' or key == b'M':
        if not morph_visible:
            criarJanelaMorphing()
            morph_visible = True
    glutSetWindow(janela2)
    glutPostRedisplay()

def redimensionaJanela2(largura, altura):
    """Manter aspect ratio"""
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
    
    if morph_manager.objetoMorph:
        morph_manager.objetoMorph.Desenha()
        morph_manager.objetoMorph.DesenhaWireframe()
    
    glutSwapBuffers()

def tecladoJanela3(key, x, y):
    """Função de teclado para a janela de morphing"""
    global morph_visible, rotacao_automatica_janela3
    
    if key == b' ':  # Espaço inicia/pausa morphing
        if morph_manager.executando:
            morph_manager.pararMorphing()
            pygame.mixer.music.pause()
            print("Morphing pausado")
        else:
            morph_manager.iniciarMorphing()
            rotacao_automatica_janela3 = False
            pygame.mixer.music.unpause()
            print("Morphing iniciado")
        glutPostRedisplay()

def timerJanela3(valor):
    """Timer para animação do morphing E rotação pós-conclusão"""
    global rotacao_automatica_janela3
    
    # Checa se o morphing está rodando
    if morph_manager.executando:
        if not morph_manager.proximoFrame():
            # O morphing acabou de terminar
            print("Morphing concluído. Iniciando rotação automática.")
            rotacao_automatica_janela3 = True
        glutPostRedisplay()
    
    # Se o morphing não está rodando, checa se a rotação deve estar ativa
    elif rotacao_automatica_janela3:
        if morph_manager.objetoMorph:
            morph_manager.objetoMorph.rotation = (
                0, 1, 0, 
                morph_manager.objetoMorph.rotation[3] + 2
            )
        glutPostRedisplay()
    
    # Chama o timer de novo para o próximo loop
    glutTimerFunc(16, timerJanela3, 0)

def redimensionaJanela3(largura, altura):
    """Manter aspect ratio"""
    glViewport(0, 0, largura, altura)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect = largura / float(altura) if altura > 0 else 1.0
    gluPerspective(60, aspect, 0.01, 50)
    glMatrixMode(GL_MODELVIEW)

def criarJanelaMorphing():
    """Cria a janela de morphing"""
    global janela3, morph_visible, rotacao_automatica_janela3
    
    if janela3 is not None:
        glutSetWindow(janela3)
        glutPopWindow()
        return
    
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
    
    rotacao_automatica_janela3 = False
    
    # Iniciar timer para animação
    glutTimerFunc(16, timerJanela3, 0)
    
    print("=" * 50)
    print("JANELA DE MORPHING CRIADA!")
    print("Comandos:")
    print(" ESPAÇO - Iniciar/Pausar morphing")
    print("=" * 50)
    
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
    janela1 = glutCreateWindow(b'Janela 1 - Objeto 1')
    glutDisplayFunc(desenhaJanela1)
    glutKeyboardFunc(tecladoJanela1)
    glutReshapeFunc(redimensionaJanela1)
    init()
    PosicUser()
    
    # CRIA JANELA 2
    glutInitWindowSize(400, 400)
    glutInitWindowPosition(550, 100)
    janela2 = glutCreateWindow(b'Janela 2 - Objeto 2')
    glutDisplayFunc(desenhaJanela2)
    glutKeyboardFunc(tecladoJanela2)
    glutReshapeFunc(redimensionaJanela2)
    init()
    PosicUser()
    
    print("=" * 50)
    print("SISTEMA DE MORPHING 3D INICIADO")
    print("Janelas 1 e 2 criadas")
    print("Comando:")
    print(" M - Abrir janela de morphing")
    print("=" * 50)
    
    # Inicializar música
    try:
        pygame.mixer.init()
        pygame.mixer.music.load('beatles.mp3')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        pygame.mixer.music.pause()
        print("Música carregada com sucesso!")
    except Exception as e:
        print(f"Não foi possível carregar a música: {e}")
        print("Continuando sem som.")
    
    try:
        glutMainLoop()
    except SystemExit:
        pass
    except Exception as e:
        print(f"Erro no loop principal: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
