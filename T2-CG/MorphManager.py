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
        
        # Mapeamentos melhorados
        self.mapa_faces = []
        self.vertices_extra_obj1 = []  # Vértices extras do obj1 (desaparecem)
        self.vertices_extra_obj2 = []  # Vértices extras do obj2 (aparecem)

    def setObjetos(self, obj1, obj2):
        """Define os objetos a serem interpolados"""
        self.objeto1 = self.normalizarObjeto(obj1)
        self.objeto2 = self.normalizarObjeto(obj2)
        
        # Criar mapeamento melhorado
        self.criarMapeamentoFacesRobusto()
        
        # Criar objeto de morphing
        self.objetoMorph = self.criarObjetoMorphInicial()
        
        print(f"\n=== MAPEAMENTO DE MORPHING ===")
        print(f"Objeto 1: {len(self.objeto1.vertices)} vértices, {len(self.objeto1.faces)} faces")
        print(f"Objeto 2: {len(self.objeto2.vertices)} vértices, {len(self.objeto2.faces)} faces")
        print(f"Faces mapeadas: {len(self.mapa_faces)}")
        print(f"Faces desaparecendo: {len(self.vertices_extra_obj1)}")
        print(f"Faces aparecendo: {len(self.vertices_extra_obj2)}")
        print("==============================\n")
        
        # Debug detalhado
        self.debugMapeamento()

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
        obj_normalizado.faces = [f[:] for f in obj.faces]
        obj_normalizado.position = Ponto(obj.position.x, obj.position.y, obj.position.z)
        obj_normalizado.rotation = obj.rotation
        
        # Normalizar vértices
        scale = 2.0 / max_size
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
        
        # Copiar faces
        for face in obj.faces:
            novo.faces.append(face[:])
        
        novo.position = Ponto(obj.position.x, obj.position.y, obj.position.z)
        novo.rotation = obj.rotation
        
        return novo

    def distancia(self, p1, p2):
        """Calcula distância euclidiana entre dois pontos"""
        dx = p1.x - p2.x
        dy = p1.y - p2.y
        dz = p1.z - p2.z
        return math.sqrt(dx*dx + dy*dy + dz*dz)

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

    def criarMapeamentoFacesRobusto(self):
        """
        Estratégia robusta para mapeamento de faces com números diferentes
        """
        num_faces1 = len(self.objeto1.faces)
        num_faces2 = len(self.objeto2.faces)
        
        # Calcular centroides
        centroides1 = [self.calcularCentroide(self.objeto1.vertices, f) 
                      for f in self.objeto1.faces]
        centroides2 = [self.calcularCentroide(self.objeto2.vertices, f) 
                      for f in self.objeto2.faces]
        
        self.mapa_faces = []
        self.vertices_extra_obj1 = []
        self.vertices_extra_obj2 = []
        
        if num_faces1 == num_faces2:
            # Caso simples: mapeamento 1:1 por proximidade
            self.mapeamentoUmParaUm(centroides1, centroides2)
            
        elif num_faces1 < num_faces2:
            # Objeto1 tem menos faces - algumas faces do obj2 aparecem progressivamente
            self.mapeamentoObjeto1Menor(centroides1, centroides2)
            
        else:
            # Objeto1 tem mais faces - algumas faces do obj1 desaparecem progressivamente
            self.mapeamentoObjeto1Maior(centroides1, centroides2)

    def mapeamentoUmParaUm(self, centroides1, centroides2):
        """Mapeamento quando número de faces é igual"""
        faces2_usadas = set()
        
        for idx1, c1 in enumerate(centroides1):
            melhor_idx2 = -1
            menor_dist = float('inf')
            
            for idx2, c2 in enumerate(centroides2):
                if idx2 not in faces2_usadas:
                    dist = self.distancia(c1, c2)
                    if dist < menor_dist:
                        menor_dist = dist
                        melhor_idx2 = idx2
            
            if melhor_idx2 != -1:
                self.mapa_faces.append((idx1, melhor_idx2))
                faces2_usadas.add(melhor_idx2)

    def mapeamentoObjeto1Menor(self, centroides1, centroides2):
        """
        Objeto1 tem MENOS faces que Objeto2
        Estratégia: faces extras do obj2 aparecem de dentro das faces do obj1
        """
        num_faces1 = len(self.objeto1.faces)
        num_faces2 = len(self.objeto2.faces)
        
        # Primeiro: mapear cada face do obj1 para a mais próxima do obj2
        faces2_mapeadas = set()
        
        for idx1, c1 in enumerate(centroides1):
            melhor_idx2 = -1
            menor_dist = float('inf')
            
            for idx2, c2 in enumerate(centroides2):
                if idx2 not in faces2_mapeadas:
                    dist = self.distancia(c1, c2)
                    if dist < menor_dist:
                        menor_dist = dist
                        melhor_idx2 = idx2
            
            if melhor_idx2 != -1:
                self.mapa_faces.append((idx1, melhor_idx2))
                faces2_mapeadas.add(melhor_idx2)
        
        # Segundo: para faces restantes do obj2, criar vértices extras
        for idx2 in range(num_faces2):
            if idx2 not in faces2_mapeadas:
                # Encontrar a face mais próxima do obj1
                c2 = centroides2[idx2]
                melhor_idx1 = min(range(num_faces1), 
                                key=lambda i: self.distancia(centroides1[i], c2))
                
                # Criar vértices extras que surgirão do centroide
                face2 = self.objeto2.faces[idx2]
                centroide_face1 = centroides1[melhor_idx1]
                
                # Armazenar informações para criação progressiva
                self.vertices_extra_obj2.append({
                    'face_origem': melhor_idx1,
                    'face_destino': idx2,
                    'centroide_origem': centroide_face1,
                    'vertices_destino': [self.objeto2.vertices[i] for i in face2],
                    'indices_destino': face2
                })

    def mapeamentoObjeto1Maior(self, centroides1, centroides2):
        """
        Objeto1 tem MAIS faces que Objeto2
        Estratégia: faces extras do obj1 desaparecem em direção às faces do obj2
        """
        num_faces1 = len(self.objeto1.faces)
        num_faces2 = len(self.objeto2.faces)
        
        # Primeiro: mapear cada face do obj2 para a mais próxima do obj1
        faces1_mapeadas = set()
        
        for idx2, c2 in enumerate(centroides2):
            melhor_idx1 = -1
            menor_dist = float('inf')
            
            for idx1, c1 in enumerate(centroides1):
                if idx1 not in faces1_mapeadas:
                    dist = self.distancia(c1, c2)
                    if dist < menor_dist:
                        menor_dist = dist
                        melhor_idx1 = idx1
            
            if melhor_idx1 != -1:
                self.mapa_faces.append((melhor_idx1, idx2))
                faces1_mapeadas.add(melhor_idx1)
        
        # Segundo: para faces restantes do obj1, criar vértices extras
        for idx1 in range(num_faces1):
            if idx1 not in faces1_mapeadas:
                # Encontrar a face mais próxima do obj2
                c1 = centroides1[idx1]
                melhor_idx2 = min(range(num_faces2), 
                                key=lambda i: self.distancia(centroides2[i], c1))
                
                # Armazenar informações para desaparecimento progressivo
                face1 = self.objeto1.faces[idx1]
                centroide_face2 = centroides2[melhor_idx2]
                
                self.vertices_extra_obj1.append({
                    'face_origem': idx1,
                    'face_destino': melhor_idx2,
                    'centroide_destino': centroide_face2,
                    'vertices_origem': [self.objeto1.vertices[i] for i in face1],
                    'indices_origem': face1
                })

    def criarObjetoMorphInicial(self):
        """Cria o objeto morph inicial considerando todas as faces"""
        novo = Objeto3D()
        
        # Copiar TODOS os vértices do objeto1
        for v in self.objeto1.vertices:
            novo.vertices.append(Ponto(v.x, v.y, v.z))
        
        # Copiar TODAS as faces do objeto1
        for face in self.objeto1.faces:
            novo.faces.append(face[:])
        
        # Adicionar espaço para vértices extras (serão adicionados dinamicamente)
        # Eles começam nos centroides e se movem para suas posições finais
        
        novo.position = Ponto(self.objeto1.position.x, self.objeto1.position.y, self.objeto1.position.z)
        novo.rotation = self.objeto1.rotation
        
        return novo

    def interpolaPonto(self, p1, p2, t):
        """Interpola linearmente entre dois pontos"""
        x = p1.x * (1 - t) + p2.x * t
        y = p1.y * (1 - t) + p2.y * t
        z = p1.z * (1 - t) + p2.z * t
        return Ponto(x, y, z)

    def suavizarInterpolacao(self, t):
        """Suaviza a interpolação para movimento mais natural"""
        return t * t * (3 - 2 * t)  # Smoothstep function

    def atualizarMorph(self):
        """Atualiza o objeto de morphing com estratégia robusta"""
        if not self.objeto1 or not self.objeto2:
            return
        
        t = self.frame_atual / float(self.total_frames)
        t_suavizado = self.suavizarInterpolacao(t)
        
        # Limpar e reconstruir o objeto morph
        self.objetoMorph.vertices.clear()
        self.objetoMorph.faces.clear()
        
        next_vertex_idx = 0
        vertices_interpolados = {}

        # 1. Interpolar faces mapeadas (1:1)
        for idx_face1, idx_face2 in self.mapa_faces:
            face1 = self.objeto1.faces[idx_face1]
            face2 = self.objeto2.faces[idx_face2]
            
            # Usar o maior número de vértices entre as duas faces
            max_vertices = max(len(face1), len(face2))
            nova_face = []
            
            for i in range(max_vertices):
                idx_v1 = face1[i % len(face1)]
                idx_v2 = face2[i % len(face2)]
                
                chave = (idx_face1, idx_face2, i)
                if chave in vertices_interpolados:
                    nova_face.append(vertices_interpolados[chave])
                else:
                    v1 = self.objeto1.vertices[idx_v1]
                    v2 = self.objeto2.vertices[idx_v2]
                    v_interpolado = self.interpolaPonto(v1, v2, t_suavizado)
                    
                    self.objetoMorph.vertices.append(v_interpolado)
                    vertices_interpolados[chave] = next_vertex_idx
                    nova_face.append(next_vertex_idx)
                    next_vertex_idx += 1
            
            if len(nova_face) >= 3:  # Apenas faces válidas
                self.objetoMorph.faces.append(nova_face)
        
        # 2. Tratar vértices extras do objeto1 (desaparecimento)
        for extra in self.vertices_extra_obj1:
            # Faces extras do obj1 desaparecem nos primeiros 80% da animação
            if t < 0.8:
                fade_t = 1.0 - (t / 0.8)  # Vai de 1 a 0
                
                nova_face = []
                for i, v_orig in enumerate(extra['vertices_origem']):
                    v_interpolado = self.interpolaPonto(
                        v_orig, 
                        extra['centroide_destino'], 
                        fade_t
                    )
                    self.objetoMorph.vertices.append(v_interpolado)
                    nova_face.append(next_vertex_idx)
                    next_vertex_idx += 1
                
                if len(nova_face) >= 3:
                    self.objetoMorph.faces.append(nova_face)
        
        # 3. Tratar vértices extras do objeto2 (aparecimento)
        for extra in self.vertices_extra_obj2:
            # Faces extras do obj2 aparecem nos últimos 80% da animação
            if t > 0.2:
                appear_t = (t - 0.2) / 0.8  # Vai de 0 a 1
                
                nova_face = []
                for i, v_dest in enumerate(extra['vertices_destino']):
                    v_interpolado = self.interpolaPonto(
                        extra['centroide_origem'],
                        v_dest,
                        appear_t
                    )
                    self.objetoMorph.vertices.append(v_interpolado)
                    nova_face.append(next_vertex_idx)
                    next_vertex_idx += 1
                
                if len(nova_face) >= 3:
                    self.objetoMorph.faces.append(nova_face)

    def debugMapeamento(self):
        """Debug detalhado do mapeamento"""
        print("\n=== DEBUG MAPEAMENTO ===")
        print("Faces mapeadas 1:1:")
        for i, (idx1, idx2) in enumerate(self.mapa_faces):
            face1 = self.objeto1.faces[idx1]
            face2 = self.objeto2.faces[idx2]
            print(f"  {i}: Obj1[{idx1}]({len(face1)}v) -> Obj2[{idx2}]({len(face2)}v)")
        
        print("\nFaces desaparecendo:")
        for i, extra in enumerate(self.vertices_extra_obj1):
            print(f"  {i}: Face {extra['face_origem']} -> Centroide face {extra['face_destino']}")
        
        print("\nFaces aparecendo:")
        for i, extra in enumerate(self.vertices_extra_obj2):
            print(f"  {i}: Centroide face {extra['face_origem']} -> Face {extra['face_destino']}")
        print("=======================\n")

    def iniciarMorphing(self):
        """Inicia a animação de morphing"""
        self.executando = True
        self.frame_atual = 0
        print(f"Morphing iniciado: {self.total_frames} frames")
        print(f"Estratégia: {len(self.vertices_extra_obj1)} faces desaparecem, "
              f"{len(self.vertices_extra_obj2)} faces aparecem")

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
            print(f"Frame {self.frame_atual}/{self.total_frames} (t={t:.2f}) - "
                  f"{len(self.objetoMorph.vertices)} vértices, {len(self.objetoMorph.faces)} faces")
        
        return True

    def reiniciar(self):
        """Reinicia o morphing do início"""
        self.frame_atual = 0
        self.executando = False
        self.atualizarMorph()
