from Ponto import Ponto
from Objeto3D import Objeto3D
import math

objeto1: Objeto3D = None
objeto2: Objeto3D = None
objeto_morphing: Objeto3D = None
associacoes_faces = []
velocidade = 0.02

# ------------------------------------------------------------
# Funções auxiliares
# ------------------------------------------------------------
def calcularBoundingBox(objeto):
    if len(objeto.vertices) == 0:
        return Ponto(0,0,0), Ponto(0,0,0)
    
    xs = [v.x for v in objeto.vertices]
    ys = [v.y for v in objeto.vertices]
    zs = [v.z for v in objeto.vertices]
    return Ponto(min(xs), min(ys), min(zs)), Ponto(max(xs), max(ys), max(zs))

def calcularCentro(objeto):
    min_p, max_p = calcularBoundingBox(objeto)
    return Ponto(
        (min_p.x + max_p.x) / 2,
        (min_p.y + max_p.y) / 2,
        (min_p.z + max_p.z) / 2
    )

def normalizarObjeto(objeto):
    """Normaliza o objeto para [-1,1] e centraliza na origem"""
    min_p, max_p = calcularBoundingBox(objeto)
    centro = calcularCentro(objeto)
    
    dx = max_p.x - min_p.x
    dy = max_p.y - min_p.y
    dz = max_p.z - min_p.z
    escala = max(dx, dy, dz)
    
    if escala == 0:
        return
    
    for v in objeto.vertices:
        v.x = (v.x - centro.x) / escala * 2
        v.y = (v.y - centro.y) / escala * 2
        v.z = (v.z - centro.z) / escala * 2

def distancia3D(p1, p2):
    dx = p1.x - p2.x
    dy = p1.y - p2.y
    dz = p1.z - p2.z
    return math.sqrt(dx*dx + dy*dy + dz*dz)

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

# ------------------------------------------------------------
# Associação de faces (igual ao código da sua amiga)
# ------------------------------------------------------------
def associarFaces():
    """Associa cada face do obj1 com a face mais próxima do obj2"""
    global associacoes_faces
    associacoes_faces = []
    
    num_faces1 = len(objeto1.faces)
    num_faces2 = len(objeto2.faces)
    
    # Calcula centroides
    centroides1 = [calcularCentroideFace(objeto1, face) for face in objeto1.faces]
    centroides2 = [calcularCentroideFace(objeto2, face) for face in objeto2.faces]
    
    # Para cada face do obj1, encontra a mais próxima no obj2
    for i in range(num_faces1):
        c1 = centroides1[i]
        
        melhor_dist = float('inf')
        melhor_j = 0
        
        for j in range(num_faces2):
            dist = distancia3D(c1, centroides2[j])
            if dist < melhor_dist:
                melhor_dist = dist
                melhor_j = j
        
        associacoes_faces.append((i, melhor_j))

def interpolarVertice(v1, v2, t):
    """Interpolação linear entre dois vértices"""
    return Ponto(
        v1.x * (1-t) + v2.x * t,
        v1.y * (1-t) + v2.y * t,
        v1.z * (1-t) + v2.z * t
    )

# ------------------------------------------------------------
# Morphing (técnica da sua amiga = MELHOR)
# ------------------------------------------------------------
def criarObjetoMorphing():
    """Cria objeto de morphing baseado no obj1"""
    global objeto_morphing
    objeto_morphing = Objeto3D()
    
    # Copia estrutura do objeto1 (faces e vértices)
    objeto_morphing.faces = [face.copy() for face in objeto1.faces]
    objeto_morphing.vertices = [Ponto(v.x, v.y, v.z) for v in objeto1.vertices]

def atualizarMorphing(t):
    """
    Atualiza o morphing (técnica da sua amiga)
    Mantém topologia do Obj1, mas move vértices para posições do Obj2
    """
    # Reseta para posições do obj1
    for i, v in enumerate(objeto_morphing.vertices):
        v1 = objeto1.vertices[i]
        v.x = v1.x
        v.y = v1.y
        v.z = v1.z
    
    # Aplica interpolação baseada nas associações de faces
    for idx1, idx2 in associacoes_faces:
        face1 = objeto1.faces[idx1]
        face2 = objeto2.faces[idx2]
        
        # Interpola vértices correspondentes
        num_vertices = min(len(face1), len(face2))
        for i in range(num_vertices):
            vertice_idx1 = face1[i]
            vertice_idx2 = face2[i]
            
            if vertice_idx1 < len(objeto1.vertices) and vertice_idx2 < len(objeto2.vertices):
                v1 = objeto1.vertices[vertice_idx1]
                v2 = objeto2.vertices[vertice_idx2]
                
                # Interpolação LINEAR suave
                v_morph = objeto_morphing.vertices[vertice_idx1]
                v_morph.x = v1.x + (v2.x - v1.x) * t
                v_morph.y = v1.y + (v2.y - v1.y) * t
                v_morph.z = v1.z + (v2.z - v1.z) * t

# ------------------------------------------------------------
# Carregamento
# ------------------------------------------------------------
def carregar_objetos():
    """Carrega e prepara os objetos para morphing"""
    global objeto1, objeto2
    
    objeto1 = Objeto3D()
    objeto1.LoadFile('easy1.obj')
    
    objeto2 = Objeto3D()
    objeto2.LoadFile('boat.obj')
    
    normalizarObjeto(objeto1)
    normalizarObjeto(objeto2)
    
    associarFaces()
    criarObjetoMorphing()