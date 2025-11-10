import math
from Objeto3D import Objeto3D
from Ponto import Ponto

class MorphManager:
    def __init__(self, total_frames=120):
        self.objeto1 = None
        self.objeto2 = None
        self.objetoMorph = None
        
        self.total_frames = total_frames
        self.frame_atual = 0
        self.executando = False
        
        # Mapeamentos de vértices e faces
        self.mapa_vertices_1_para_2 = []  # Para cada vértice do obj1, lista de (índice_obj2, distância)
        self.mapa_vertices_2_para_1 = []  # Para cada vértice do obj2, lista de (índice_obj1, distância)
        self.mapa_faces = []  # Mapeamento de faces: (face_obj1, face_obj2)
    
    def setObjetos(self, obj1, obj2):
        """Define os objetos a serem interpolados"""
        self.objeto1 = self.normalizarObjeto(obj1)
        self.objeto2 = self.normalizarObjeto(obj2)
        
        # Criar mapeamentos
        self.criarMapeamentoVertices()
        self.criarMapeamentoFaces()
        
        # Criar objeto de morphing (começa como cópia do objeto1)
        self.objetoMorph = self.copiarObjeto(self.objeto1)
        
        print(f"Mapeamento criado: {len(self.mapa_faces)} associações de faces")
    
    def normalizarObjeto(self, obj):
        """Normaliza e centraliza o objeto no bounding box"""
        if not obj.vertices:
            return obj
        
        # Calcular bounding box
        min_x = min(v.x for v in obj.vertices)
        max_x = max(v.x for v in obj.vertices)
        min_y = min(v.y for v in obj.vertices)
        max_y = max(v.y for v in obj.vertices)
        min_z = min(v.z for v in obj.vertices)
        max_z = max(v.z for v in obj.vertices)
        
        # Calcular centro e tamanho
        center_x = (min_x + max_x) / 2.0
        center_y = (min_y + max_y) / 2.0
        center_z = (min_z + max_z) / 2.0
        
        size_x = max_x - min_x
        size_y = max_y - min_y
        size_z = max_z - min_z
        max_size = max(size_x, size_y, size_z)
        
        if max_size == 0:
            return obj
        
        # Criar objeto normalizado
        obj_normalizado = Objeto3D()
        obj_normalizado.faces = [f[:] for f in obj.faces]  # Copiar faces
        obj_normalizado.position = Ponto(obj.position.x, obj.position.y, obj.position.z)
        obj_normalizado.rotation = obj.rotation
        
        # Normalizar vértices
        scale = 2.0 / max_size  # Escala para caber em [-1, 1]
        
        for v in obj.vertices:
            v_normalizado = Ponto(
                (v.x - center_x) * scale,
                (v.y - center_y) * scale,
                (v.z - center_z) * scale
            )
            obj_normalizado.vertices.append(v_normalizado)
        
        return obj_normalizado
    
    def copiarObjeto(self, obj):
        """Cria uma cópia profunda do objeto"""
        novo = Objeto3D()
        
        # Copiar vértices
        for v in obj.vertices:
            novo.vertices.append(Ponto(v.x, v.y, v.z))
        
        # Copiar faces (lista de listas de índices)
        for face in obj.faces:
            novo.faces.append(face[:])  # Cópia da lista
        
        novo.position = Ponto(obj.position.x, obj.position.y, obj.position.z)
        novo.rotation = obj.rotation
        
        return novo
    
    def distancia(self, p1, p2):
        """Calcula distância euclidiana entre dois pontos"""
        dx = p1.x - p2.x
        dy = p1.y - p2.y
        dz = p1.z - p2.z
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def criarMapeamentoVertices(self):
        """Cria mapeamento de vértices próximos entre os dois objetos"""
        # Para cada vértice do objeto1, encontrar os K vértices mais próximos do objeto2
        K = 5  # número de vizinhos a considerar
        
        self.mapa_vertices_1_para_2 = []
        for v1 in self.objeto1.vertices:
            distancias = []
            for idx2, v2 in enumerate(self.objeto2.vertices):
                dist = self.distancia(v1, v2)
                distancias.append((idx2, dist))
            
            # Ordenar por distância e pegar os K mais próximos
            distancias.sort(key=lambda x: x[1])
            self.mapa_vertices_1_para_2.append(distancias[:K])
        
        # Fazer o mesmo para objeto2 -> objeto1
        self.mapa_vertices_2_para_1 = []
        for v2 in self.objeto2.vertices:
            distancias = []
            for idx1, v1 in enumerate(self.objeto1.vertices):
                dist = self.distancia(v1, v2)
                distancias.append((idx1, dist))
            
            distancias.sort(key=lambda x: x[1])
            self.mapa_vertices_2_para_1.append(distancias[:K])
    
    def calcularCentroide(self, vertices, face):
        """Calcula o centroide de uma face"""
        cx = cy = cz = 0.0
        n_vertices = len(face)
        
        for idx in face:
            v = vertices[idx]
            cx += v.x
            cy += v.y
            cz += v.z
        
        return Ponto(cx / n_vertices, cy / n_vertices, cz / n_vertices)
    
    def criarMapeamentoFaces(self):
        """Associa faces entre os dois objetos baseado em proximidade de centroides"""
        # Calcular centroides de todas as faces
        centroides1 = [self.calcularCentroide(self.objeto1.vertices, f) for f in self.objeto1.faces]
        centroides2 = [self.calcularCentroide(self.objeto2.vertices, f) for f in self.objeto2.faces]
        
        self.mapa_faces = []
        faces2_usadas = set()
        
        # Para cada face do objeto1, encontrar a face mais próxima do objeto2
        for idx1, c1 in enumerate(centroides1):
            melhor_idx2 = -1
            menor_dist = float('inf')
            
            for idx2, c2 in enumerate(centroides2):
                dist = self.distancia(c1, c2)
                if dist < menor_dist:
                    menor_dist = dist
                    melhor_idx2 = idx2
            
            self.mapa_faces.append((idx1, melhor_idx2))
            faces2_usadas.add(melhor_idx2)
        
        # Tratar faces não mapeadas do objeto2 (associação N:1)
        for idx2 in range(len(self.objeto2.faces)):
            if idx2 not in faces2_usadas:
                # Encontrar a face do objeto1 mais próxima
                c2 = centroides2[idx2]
                melhor_idx1 = -1
                menor_dist = float('inf')
                
                for idx1, c1 in enumerate(centroides1):
                    dist = self.distancia(c1, c2)
                    if dist < menor_dist:
                        menor_dist = dist
                        melhor_idx1 = idx1
                
                # Adicionar associação extra (N:1)
                self.mapa_faces.append((melhor_idx1, idx2))
        
        print(f"Faces obj1: {len(self.objeto1.faces)}, Faces obj2: {len(self.objeto2.faces)}")
        print(f"Total de associações: {len(self.mapa_faces)} (incluindo N:1)")
    
    def interpolaPonto(self, p1, p2, t):
        """Interpola linearmente entre dois pontos"""
        x = p1.x * (1 - t) + p2.x * t
        y = p1.y * (1 - t) + p2.y * t
        z = p1.z * (1 - t) + p2.z * t
        return Ponto(x, y, z)
    
    def triangularizarFace(self, face):
        """Converte uma face (potencialmente quad) em triângulos"""
        triangulos = []
        
        if len(face) == 3:
            # Já é triângulo
            triangulos.append(face)
        elif len(face) == 4:
            # Quad -> dois triângulos
            triangulos.append([face[0], face[1], face[2]])
            triangulos.append([face[0], face[2], face[3]])
        elif len(face) > 4:
            # Polígono -> leque de triângulos a partir do primeiro vértice
            for i in range(1, len(face) - 1):
                triangulos.append([face[0], face[i], face[i+1]])
        
        return triangulos
    
    def atualizarMorph(self):
        """Atualiza o objeto de morphing baseado no frame atual"""
        if not self.objeto1 or not self.objeto2:
            return
        
        # Calcular t (0.0 a 1.0)
        t = self.frame_atual / float(self.total_frames)
        
        # Limpar vértices e faces do objeto morph
        self.objetoMorph.vertices.clear()
        self.objetoMorph.faces.clear()
        
        # Criar novo conjunto de vértices interpolados
        vertices_usados = {}  # Mapeia (idx_obj1, idx_obj2) -> novo_índice
        
        for idx_face_par, (idx_face1, idx_face2) in enumerate(self.mapa_faces):
            face1 = self.objeto1.faces[idx_face1]
            face2 = self.objeto2.faces[idx_face2]
            
            # Triangularizar ambas as faces
            triangulos1 = self.triangularizarFace(face1)
            triangulos2 = self.triangularizarFace(face2)
            
            # Usar o primeiro triângulo de cada (simplificação)
            tri1 = triangulos1[0]
            tri2 = triangulos2[0]
            
            # Interpolar os 3 vértices deste triângulo
            nova_face = []
            
            for i in range(3):
                idx_v1 = tri1[i]
                # Para faces com número diferente de vértices, usar módulo
                idx_v2 = tri2[i % len(tri2)]
                
                # Verificar se já interpolamos este par de vértices
                chave = (idx_v1, idx_v2)
                if chave in vertices_usados:
                    nova_face.append(vertices_usados[chave])
                else:
                    # Interpolar vértices
                    v1 = self.objeto1.vertices[idx_v1]
                    v2 = self.objeto2.vertices[idx_v2]
                    v_novo = self.interpolaPonto(v1, v2, t)
                    
                    # Adicionar ao objeto morph
                    novo_idx = len(self.objetoMorph.vertices)
                    self.objetoMorph.vertices.append(v_novo)
                    vertices_usados[chave] = novo_idx
                    nova_face.append(novo_idx)
            
            # Criar nova face com os índices interpolados
            self.objetoMorph.faces.append(nova_face)
    
    def iniciarMorphing(self):
        """Inicia a animação de morphing"""
        self.executando = True
        self.frame_atual = 0
        print(f"Morphing iniciado: {self.total_frames} frames")
    
    def pararMorphing(self):
        """Para a animação de morphing"""
        self.executando = False
        print("Morphing pausado")
    
    def proximoFrame(self):
        """Avança para o próximo frame. Retorna False quando terminar."""
        if not self.executando:
            return True
        
        self.frame_atual += 1
        
        if self.frame_atual > self.total_frames:
            self.executando = False
            self.frame_atual = self.total_frames
            print("Morphing concluído!")
            return False
        
        # Atualizar o objeto de morphing
        self.atualizarMorph()
        
        # Debug a cada 10 frames
        if self.frame_atual % 10 == 0:
            t = self.frame_atual / float(self.total_frames)
            print(f"Frame {self.frame_atual}/{self.total_frames} (t={t:.2f})")
        
        return True
    
    def reiniciar(self):
        """Reinicia o morphing do início"""
        self.frame_atual = 0
        self.executando = False
        self.atualizarMorph()
