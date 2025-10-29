from Ponto import Ponto
from Objeto3D import Objeto3D
import math

objeto1: Objeto3D = None
objeto2: Objeto3D = None
objeto_morphing: Objeto3D = None
associacoes = []
velocidade = 0.02

# ------------------------------------------------------------
# Funções auxiliares
# ------------------------------------------------------------
def calcularBoundingBox(objeto):
    xs = [v.x for v in objeto.vertices]
    ys = [v.y for v in objeto.vertices]
    zs = [v.z for v in objeto.vertices]
    return Ponto(min(xs), min(ys), min(zs)), Ponto(max(xs), max(ys), max(zs))

def calcularCentro(objeto):
    min_p, max_p = calcularBoundingBox(objeto)
    return Ponto((min_p.x+max_p.x)/2, (min_p.y+max_p.y)/2, (min_p.z+max_p.z)/2)

def normalizarObjeto(objeto):
    min_p, max_p = calcularBoundingBox(objeto)
    centro = calcularCentro(objeto)
    escala = max(max_p.x-min_p.x, max_p.y-min_p.y, max_p.z-min_p.z)
    if escala == 0: return
    for v in objeto.vertices:
        v.x, v.y, v.z = [(coord - c) / escala * 2 for coord, c in zip((v.x, v.y, v.z), (centro.x, centro.y, centro.z))]

def distancia3D(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)

def calcularCentroideFace(objeto, face_indices):
    cx = cy = cz = 0
    for idx in face_indices:
        v = objeto.vertices[idx]
        cx += v.x
        cy += v.y
        cz += v.z
    n = len(face_indices)
    return Ponto(cx/n, cy/n, cz/n)

# ------------------------------------------------------------
# Associação e morphing
# ------------------------------------------------------------
def associarFaces():
    global associacoes
    associacoes.clear()

    f1, f2 = len(objeto1.faces), len(objeto2.faces)
    centroides_obj1 = [calcularCentroideFace(objeto1, f) for f in objeto1.faces]
    centroides_obj2 = [calcularCentroideFace(objeto2, f) for f in objeto2.faces]

    # Associa cada face do obj1 com a mais próxima do obj2
    for i, face1 in enumerate(objeto1.faces):
        c1 = centroides_obj1[i]
        melhor_j = min(range(f2), key=lambda j: distancia3D(c1, centroides_obj2[j]))
        associacoes.append((i, melhor_j))

    # Trata diferença no número de faces
    if f2 > f1:
        # Obj2 tem mais faces: associa faces extras com a última do obj1
        for j in range(f1, f2):
            associacoes.append((f1 - 1, j))
    elif f1 > f2:
        # Obj1 tem mais faces: associa faces extras com a última do obj2
        for i in range(f2, f1):
            associacoes.append((i, f2 - 1))

def interpolarVertice(v1, v2, t):
    return Ponto(
        v1.x * (1-t) + v2.x * t,
        v1.y * (1-t) + v2.y * t,
        v1.z * (1-t) + v2.z * t
    )

def criarObjetoMorphing():
    global objeto_morphing
    objeto_morphing = Objeto3D()
    objeto_morphing.faces = objeto1.faces.copy()
    objeto_morphing.vertices = [Ponto(0,0,0) for _ in objeto1.vertices]

def atualizarMorphing(t):
    """Atualiza posições dos vértices sem recriar o objeto"""
    for i, (idx1, idx2) in enumerate(associacoes):
        face1 = objeto1.faces[idx1]
        face2 = objeto2.faces[idx2]
        n = min(len(face1), len(face2))

        for j in range(n):
            v1 = objeto1.vertices[face1[j]]
            v2 = objeto2.vertices[face2[j]]
            v_interp = interpolarVertice(v1, v2, t)
            objeto_morphing.vertices[face1[j]] = v_interp

def carregar_objetos():
    global objeto1, objeto2
    objeto1 = Objeto3D()
    objeto1.LoadFile('Human_Head.obj')
    objeto2 = Objeto3D()
    objeto2.LoadFile('boat.obj')

    normalizarObjeto(objeto1)
    normalizarObjeto(objeto2)
    associarFaces()
    criarObjetoMorphing()
