# ************************************************
# MorphManager.py
# Classe MorphManager - Faz a interpolação entre dois objetos 3D
#
# Esta versão é compatível com o main_glut.py:
# 1. Usa a interface (setObjetos, proximoFrame, etc.)
# 2. Implementa a lógica do T2 (centroides de faces, interpolação por vértice)
# ************************************************

from Ponto import Ponto
from Objeto3D import Objeto3D
import numpy as np

class MorphManager:
    def __init__(self):
        # Objetos originais
        self.objeto1 = None
        self.objeto2 = None
        
        # Objeto que será desenhado
        self.objetoMorph = Objeto3D() 
        
        # Estado da animação (controlado pelo main)
        self.frame_atual = 0
        self.total_frames = 300 # Ajustado para 300
        self.executando = False
        
        # ----- Caches para Mapeamento -----
        self.mapa_faces_1_para_2 = {}
        self.centroides_obj1 = []
        self.centroides_obj2 = []
        self.adj_v_faces_obj1 = {}
        self.posicoes_alvo_obj2 = {}

    def setObjetos(self, obj1: Objeto3D, obj2: Objeto3D):
        """Este método é chamado pelo main.py para configurar o morphing."""
        print("\n=== CONFIGURANDO MORPH MANAGER (T2 - CENTROIDES) ===")
        self.objeto1 = obj1
        self.objeto2 = obj2
        
        # Garante que o objetoMorph começa como uma cópia exata do obj1
        self.copiarObjeto(self.objeto1, self.objetoMorph)
        
        # 1. Normalizar objetos (conforme Morphing 1)
        #    Isso é crucial para a comparação de centroides funcionar bem
        print("Normalizando objetos...")
        self.normalizarObjeto(self.objeto1)
        self.normalizarObjeto(self.objeto2)

        # 2. Mapeamento de faces (centroides)
        print("Calculando centroides de faces...")
        self.centroides_obj1 = self.calcularCentroidesDeFaces(self.objeto1)
        self.centroides_obj2 = self.calcularCentroidesDeFaces(self.objeto2)
        
        print("Criando mapeamento de faces 1 -> 2...")
        self.criarMapeamentoFacesPorCentroides()

        # 3. Mapeamento de adjacência (vértice -> faces que ele toca)
        print("Construindo adjacência Vértice -> Faces...")
        self.adj_v_faces_obj1 = self.construirAdjacenciaFacesPorVertice(self.objeto1)

        # 4. Cache de posições alvo (para onde cada vértice do obj1 deve ir)
        print("Pré-calculando posições alvo...")
        self.precalcularPosicoesAlvo()
        
        print("=== CONFIGURAÇÃO COMPLETA ===\n")

    def copiarObjeto(self, origem: Objeto3D, destino: Objeto3D):
        """Copia vértices e faces de um objeto para outro."""
        destino.vertices = [Ponto(v.x, v.y, v.z) for v in origem.vertices]
        destino.faces = [list(face) for face in origem.faces]

    # --------------------------------------------
    # Funções de Normalização (do Morphing 1)
    # --------------------------------------------
    
    def normalizarObjeto(self, obj: Objeto3D):
        """Normaliza o objeto para caber em uma caixa de -1 a 1."""
        if not obj.vertices:
            return
        
        coords = np.array([[v.x, v.y, v.z] for v in obj.vertices])
        
        min_coords = coords.min(axis=0)
        max_coords = coords.max(axis=0)
        centro = (min_coords + max_coords) / 2
        
        escala = (max_coords - min_coords).max()
        if escala == 0:
            escala = 1.0
        
        fator_escala = 2.0 / escala
        coords_norm = (coords - centro) * fator_escala
        
        for i, vertice in enumerate(obj.vertices):
            vertice.x, vertice.y, vertice.z = coords_norm[i]

    # --------------------------------------------
    # Funções de Mapeamento (Baseadas em Centroides)
    # --------------------------------------------

    def calcularCentroidesDeFaces(self, obj: Objeto3D):
        """Retorna array numpy de centroides das faces do objeto."""
        centroides = []
        if not obj.vertices: # Evita erro se o objeto estiver vazio
            return np.array([])
            
        coords_obj = np.array([[v.x, v.y, v.z] for v in obj.vertices])
        
        for face in obj.faces:
            if not face:
                centroides.append([0,0,0])
                continue
            
            # Pega os índices válidos
            indices_validos = [idx for idx in face if idx < len(coords_obj)]
            if not indices_validos:
                centroides.append([0,0,0])
                continue
                
            coords_face = coords_obj[indices_validos]
            c = coords_face.mean(axis=0)
            centroides.append(c)
            
        return np.array(centroides)

    def criarMapeamentoFacesPorCentroides(self):
        """Mapeia cada face de objeto1 para a face mais próxima em objeto2."""
        self.mapa_faces_1_para_2 = {}
        if self.centroides_obj1.size == 0 or self.centroides_obj2.size == 0:
            return

        arr1 = self.centroides_obj1
        arr2 = self.centroides_obj2

        # Para cada centroide em obj1, acha o mais próximo em obj2
        for i, c1_vec in enumerate(arr1):
            dists = np.linalg.norm(arr2 - c1_vec, axis=1)
            idx_mais_proximo = int(np.argmin(dists))
            self.mapa_faces_1_para_2[i] = idx_mais_proximo

    def construirAdjacenciaFacesPorVertice(self, obj: Objeto3D):
        """Retorna dict: vertex_idx -> set(face_idx que tocam esse vértice)"""
        adj = {i:set() for i in range(len(obj.vertices))}
        for face_index, face in enumerate(obj.faces):
            for vertex_index in face:
                if 0 <= vertex_index < len(obj.vertices):
                    adj[vertex_index].add(face_index)
        return adj

    def calcularPosicaoMediaVerticesDasFaces(self, obj: Objeto3D, faces_indices):
        """
        Dado um conjunto de índices de face, calcula a média das posições 
        de todos os vértices únicos que formam essas faces.
        """
        if not faces_indices or not obj.vertices:
            return np.array([0,0,0])
            
        coords_obj = np.array([[v.x, v.y, v.z] for v in obj.vertices])
        
        vertices_unicos = set()
        for face_index in faces_indices:
            if face_index is None or face_index < 0 or face_index >= len(obj.faces):
                continue
            for vertex_index in obj.faces[face_index]:
                 if 0 <= vertex_index < len(coords_obj):
                    vertices_unicos.add(vertex_index)
        
        if not vertices_unicos:
            return np.array([0,0,0])

        coords_face = coords_obj[list(vertices_unicos)]
        m = coords_face.mean(axis=0)
        return m

    def precalcularPosicoesAlvo(self):
        """
        Para cada vértice do obj1, calcula sua posição alvo final no obj2.
        Isso evita recálculos a cada frame.
        """
        self.posicoes_alvo_obj2 = {}
        centroide_geral_obj2 = self.centroides_obj2.mean(axis=0) if self.centroides_obj2.size > 0 else np.array([0,0,0])

        for v_idx in range(len(self.objeto1.vertices)):
            faces_adj_obj1 = self.adj_v_faces_obj1.get(v_idx, set())
            
            faces_mapeadas_obj2 = set()
            for f_idx in faces_adj_obj1:
                mapped_f_idx = self.mapa_faces_1_para_2.get(f_idx)
                if mapped_f_idx is not None:
                    faces_mapeadas_obj2.add(mapped_f_idx)
            
            if faces_mapeadas_obj2:
                pos_e = self.calcularPosicaoMediaVerticesDasFaces(self.objeto2, faces_mapeadas_obj2)
            else:
                pos_e = centroide_geral_obj2 # Fallback

            self.posicoes_alvo_obj2[v_idx] = pos_e

    # --------------------------------------------
    # Funções de Controle (Chamadas pelo Main)
    # --------------------------------------------
    
    def iniciarMorphing(self):
        """Chamado pelo main.py para iniciar a animação."""
        print("Iniciando morphing...")
        self.executando = True
        self.frame_atual = 0
        
        # Reseta o objeto morph para o estado inicial (obj1)
        self.copiarObjeto(self.objeto1, self.objetoMorph)
        
        # Garante que o número de vértices seja o MÁXIMO entre os dois
        num_v1 = len(self.objeto1.vertices)
        num_v2 = len(self.objeto2.vertices)
        if num_v2 > num_v1:
            # Adiciona vértices "fantasma" que serão preenchidos
            for _ in range(num_v1, num_v2):
                self.objetoMorph.vertices.append(Ponto(0,0,0))
        
        self.atualizar(0.0) # Renderiza o frame 0

    def pararMorphing(self):
        """Chamado pelo main.py para pausar a animação."""
        print("Pausando morphing.")
        self.executando = False

    def proximoFrame(self):
        """
        Chamado pelo timer do main.py.
        Avança a animação em um passo.
        Retorna False quando a animação termina.
        """
        if not self.executando:
            return True # Continua no timer, mas não faz nada
        
        self.frame_atual += 1 # Assumindo velocidade 1.0
        
        progresso = self.frame_atual / self.total_frames
        
        if self.frame_atual >= self.total_frames:
            self.atualizar(1.0) # Garante o estado final
            self.executando = False
            return False # Sinaliza que terminou
        
        self.atualizar(progresso)
        return True # Sinaliza que ainda está rodando

    # --------------------------------------------
    # Funções de Atualização (Lógica Interna)
    # --------------------------------------------

    def atualizar(self, progresso: float):
        """Função interna que calcula o estado do morph para um progresso (0.0 a 1.0)"""
        # 1. Atualiza as posições dos vértices
        self.atualizarVertices(progresso)
        
        # 2. Atualiza a lista de faces (topologia)
        self.atualizarFaces(progresso)

    def atualizarVertices(self, progresso: float):
        """Atualiza CADA vértice do objetoMorph UMA VEZ."""
        
        # Interpolação "ease-in-out" para suavizar (do Morphing 1)
        t = progresso * progresso * (3.0 - 2.0 * progresso)
        
        num_v_morph = len(self.objetoMorph.vertices)
        num_v_obj1 = len(self.objeto1.vertices)
        num_v_obj2 = len(self.objeto2.vertices)
        
        # Posições do obj1 (para vértices extras)
        coords_obj1 = np.array([[v.x, v.y, v.z] for v in self.objeto1.vertices])
        centroide_obj1 = coords_obj1.mean(axis=0) if coords_obj1.size > 0 else np.array([0,0,0])
        
        # Posições do obj2 (para vértices extras)
        coords_obj2 = np.array([[v.x, v.y, v.z] for v in self.objeto2.vertices])
        centroide_obj2 = coords_obj2.mean(axis=0) if coords_obj2.size > 0 else np.array([0,0,0])

        for i in range(num_v_morph):
            
            # --- Posição Inicial (pos_s) ---
            if i < num_v_obj1:
                v_s = self.objeto1.vertices[i]
                pos_s = np.array([v_s.x, v_s.y, v_s.z])
            else:
                pos_s = centroide_obj1 # Vértice extra começa do centro

            # --- Posição Final (pos_e) ---
            pos_alvo = self.posicoes_alvo_obj2.get(i)
            if pos_alvo is not None:
                pos_e = pos_alvo
            else:
                # Vértice extra (não tem alvo pré-calculado)
                if i < num_v_obj2:
                    v_e = self.objeto2.vertices[i]
                    pos_e = np.array([v_e.x, v_e.y, v_e.z])
                else:
                    pos_e = centroide_obj2 # Fallback
            
            # --- Interpolação (LERP) ---
            pos_atual = pos_s + (pos_e - pos_s) * t
            
            self.objetoMorph.vertices[i].x = float(pos_atual[0])
            self.objetoMorph.vertices[i].y = float(pos_atual[1])
            self.objetoMorph.vertices[i].z = float(pos_atual[2])

    def atualizarFaces(self, progresso: float):
        """
        Atualiza a lista de faces do objetoMorph.
        Troca da topologia do obj1 para a do obj2.
        """
        
        # Troca de faces acontece na metade da animação
        if progresso < 0.5:
            if len(self.objetoMorph.faces) != len(self.objeto1.faces):
                self.objetoMorph.faces = [list(face) for face in self.objeto1.faces]
        else:
            if len(self.objetoMorph.faces) != len(self.objeto2.faces):
                novas_faces = []
                max_v_idx = len(self.objetoMorph.vertices) - 1
                
                for face in self.objeto2.faces:
                    # Garante que os índices da face são válidos para o morph
                    face_ajustada = [min(idx, max_v_idx) for idx in face if idx <= max_v_idx]
                    
                    if len(set(face_ajustada)) >= 3: # Garante que é um polígono válido
                        novas_faces.append(face_ajustada)
                        
                self.objetoMorph.faces = novas_faces
