from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

from Objeto3D import *

o:Objeto3D #variável global que armazena o objeto 3D principal
#inicializa as configurações do OpenGL
def init():
    global o
    glClearColor(0.5, 0.5, 0.9, 1.0) #cor de fundo
    glClearDepth(1.0) #define valor inicial do buffer de profundidade.

    glDepthFunc(GL_LESS) #desenha pixel se estiver mais próximo e garante que objetos na frente tapem os de trás
    glEnable(GL_DEPTH_TEST) #ativa o teste de profundidade
    glEnable(GL_CULL_FACE) #não desenha faces traseiras
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL) #define modo de renderização, polígonos preenchidos
    #e desenha somente faces visíveis
    #cria instância do objeto e carrega ele
    o = Objeto3D()
    o.LoadFile('Human_Head.obj')

    DefineLuz() #configura iluminação
    PosicUser() #configura câmera

#configura iluminação
def DefineLuz():
    # Define cores para um objeto dourado
    luz_ambiente = [0.4, 0.4, 0.4] #iluminação geral uniforme, cinza, sem direção, ilumina tudo igual, simula luz refletida do ambiente
    luz_difusa = [0.7, 0.7, 0.7] #luz direcional, cinza claro, depende do ângulo da superfície, cria efeito de volume nos objetos
    luz_especular = [0.9, 0.9, 0.9] #brilhos, refelexos, cria pontos brilhantes
    posicao_luz = [2.0, 3.0, 0.0]  # PosiÃ§Ã£o da Luz
    especularidade = [1.0, 1.0, 1.0]

    # ****************  Fonte de Luz 0

    glEnable(GL_COLOR_MATERIAL) #cores afetam o material

    #Habilita o uso de iluminaÃ§Ã£o
    glEnable(GL_LIGHTING)

    #Ativa o uso da luz ambiente
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, luz_ambiente)
    # Define os parametros da luz nÃºmero Zero
    glLightfv(GL_LIGHT0, GL_AMBIENT, luz_ambiente)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, luz_difusa)
    glLightfv(GL_LIGHT0, GL_SPECULAR, luz_especular)
    glLightfv(GL_LIGHT0, GL_POSITION, posicao_luz)
    glEnable(GL_LIGHT0)

    # Ativa o "Color Tracking"
    glEnable(GL_COLOR_MATERIAL)

    # Define a reflectancia do material
    glMaterialfv(GL_FRONT, GL_SPECULAR, especularidade)

    # Define a concentraÃ§Ã£oo do brilho.
    # Quanto maior o valor do Segundo parametro, mais
    # concentrado serÃ¡ o brilho. (Valores vÃ¡lidos: de 0 a 128)
    glMateriali(GL_FRONT, GL_SHININESS, 51)
#configura a câmera 
def PosicUser():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    # Configura a matriz da projeção perspectiva (FOV, proporção da tela, distância do mínimo antes do clipping, distância máxima antes do clipping
    # https://registry.khronos.org/OpenGL-Refpages/gl2.1/xhtml/gluPerspective.xml
    gluPerspective(60, 16/9, 0.01, 50)  # Projecao perspectiva

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    '''
    gluPerspective(FOV, aspect, near, far):
    - FOV = 60°: Campo de visão vertical
    - Ângulo de abertura da câmera
    - aspect = 16/9: Proporção largura/altura da tela
    - Evita distorção da imagem
    - near = 0.01: Plano de recorte próximo
    - Objetos mais perto que 0.01 não são desenhados
    - far = 50: Plano de recorte distante
    - Objetos mais longe que 50 não são desenhados

    **Visualização:**

            /\
           /  \     ← FOV 60°
          /    \
         /      \
        /________\
    Câmera    Far plane'''
    #Especifica a matriz de transformação da visualização
    # As três primeiras variáveis especificam a posição do observador nos eixos x, y e z
    # As três próximas especificam o ponto de foco nos eixos x, y e z
    # As três últimas especificam o vetor up
    # https://registry.khronos.org/OpenGL-Refpages/gl2.1/xhtml/gluLookAt.xml
    gluLookAt(-2, 6, -8, 0, 0, 0, 0, 1.0, 0)
    '''gluLookAt(eyeX, eyeY, eyeZ, centerX, centerY, centerZ, upX, upY, upZ):
    - Posição da câmera (eye): (-2, 6, -8)
    - x=-2: levemente à esquerda
    - y=6: bem acima
    - z=-8: atrás da cena
  
    - Ponto focal (center): (0, 0, 0)
    - Câmera olha para a origem

    - Vetor "para cima" (up): (0, 1, 0)
    - Define orientação da câmera
    - Eixo Y positivo = topo da câmera

    **Visualização da câmera:**

        y (up)
        ↑
        |    Câmera (-2, 6, -8)
        |      ╱
        |     ╱
        |    ╱ olhando para
        |   ╱
        |  ╱
        | ╱
        |╱________→ x
       Origem (0,0,0)
      ╱
     ╱ z
'''
#desenha ladrilho quadrado no piso
def DesenhaLadrilho():
    glColor3f(0.5, 0.5, 0.5)  # desenha QUAD preenchido
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0) #para cima
    glVertex3f(-0.5, 0.0, -0.5)
    glVertex3f(-0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, -0.5)
    glEnd()

    glColor3f(1, 1, 1)  # desenha a borda da QUAD
    glBegin(GL_LINE_STRIP)
    glNormal3f(0, 1, 0)
    glVertex3f(-0.5, 0.0, -0.5)
    glVertex3f(-0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, -0.5)
    glEnd()
'''
    **Vértices do quadrado:**
(-0.5, 0, 0.5) ●————● (0.5, 0, 0.5)
               |    |
               |    |  (tamanho 1x1)
(-0.5, 0,-0.5) ●————● (0.5, 0,-0.5)'''
#desenha a grade 40x40 ladrilhos
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

def DesenhaCubo():
    glPushMatrix()
    glColor3f(1, 0, 0)
    glTranslated(0, 0.5, 0)
    glutSolidCube(1)

    glColor3f(0.5, 0.5, 0)
    glTranslated(0, 0.5, 0)
    glRotatef(90, -1, 0, 0)
    glRotatef(45, 0, 0, 1)
    glutSolidCone(1, 1, 4, 4)
    glPopMatrix()

def desenha():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)

    DesenhaPiso() #desenha o piso
    #DesenhaCubo()    
    o.Desenha() #desenha objeto sólido cinza
    o.DesenhaWireframe() #sobrepõe wireframe 
    o.DesenhaVertices() #sobrepõe vértices

    glutSwapBuffers()
    pass
#eventos do teclado, qualquer tecla pressionada
def teclado(key, x, y):
    o.rotation = (1, 0, 0, o.rotation[3] + 2)    

    glutPostRedisplay()
    pass

def main():

    glutInit(sys.argv)

    # Define o modelo de operacao da GLUT
    glutInitDisplayMode(GLUT_RGBA | GLUT_DEPTH)

    # Especifica o tamnho inicial em pixels da janela GLUT
    glutInitWindowSize(640, 480)

    # Especifica a posição de início da janela
    glutInitWindowPosition(100, 100)

    # Cria a janela passando o título da mesma como argumento
    glutCreateWindow(b'Computacao Grafica - 3D')

    # Função responsável por fazer as inicializações
    init()

    # Registra a funcao callback de redesenho da janela de visualizacao
    glutDisplayFunc(desenha)

    # Registra a funcao callback para tratamento das teclas ASCII
    glutKeyboardFunc(teclado)

    try:
        # Inicia o processamento e aguarda interacoes do usuario
        glutMainLoop()
    except SystemExit:
        pass

if __name__ == '__main__':
    main()