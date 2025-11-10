# MorphManager.py - VERSÃO MELHORADA (SEM DESAPARECIMENTO)
import math
import numpy as np
from Ponto import Ponto
from Objeto3D import Objeto3D

class MorphManager:
    def __init__(self):
        self.objeto1 = None
        self.objeto2 = None
        self.objetoMorph = None
        self.mapa_vertices_1_para_2 = {}
        self.mapa_vertices_2_para_1 = {}
        self.frame_atual = 0
        self.total_frames = 300
        self.executando = False
        self.velocidade = 1.0
        self.modo_transicao = 1
        
        # Cache para otimização
        self._vertices_array_obj1 = None
        self._vertices_array_obj2 = None
        self._cache_pesos = {}

    def setObjetos(self, obj1: Objeto3D, obj2: Objeto3D):
        self.objeto1 = obj1
        self.objeto2 = obj2
        print("\n=== INICIANDO CONFIGURAÇÃO DE MORPHING ===")
        print("Normalizando objetos...")
        self.normalizarObjetos()
        
        self._vertices_array_obj1 = self._vertices_para_array(self.objeto1)
        self._vertices_array_obj2 = self._vertices_para_array(self.objeto2)
        
        print("Criando mapeamento bidirecional...")
        self.criarMapeamentoBidirecional()
        print("Inicializando objeto de morphing...")
        self.inicializarObjetoMorph()
        print("=== CONFIGURAÇÃO COMPLETA ===\n")
    
    def _vertices_para_array(self, obj):
        """Converte lista de Pontos para numpy array para cálculos mais rápidos"""
        return np.array([[v.x, v.y, v.z] for v in obj.vertices])
        
    def normalizarObjetos(self):
        """Normaliza a escala e centraliza os objetos"""
        if self.objeto1:
            self.normalizarObjeto(self.objeto1)
            print(f"  Obj1 normalizado: {len(self.objeto1.vertices)} vértices")
        if self.objeto2:
            self.normalizarObjeto(self.objeto2)
            print(f"  Obj2 normalizado: {len(self.objeto2.vertices)} vértices")
        
    def normalizarObjeto(self, obj: Objeto3D):
        """Normaliza usando numpy para melhor performance"""
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
    
    def distanciaEntrePontosVetorizada(self, ponto, array_vertices):
        """Calcula distâncias para todos os vértices de uma vez usando numpy"""
        p = np.array([ponto.x, ponto.y, ponto.z])
        diff = array_vertices - p
        return np.sqrt(np.sum(diff * diff, axis=1))
    
    def encontrarKVizinhosProximos(self, vertice: Ponto, array_vertices, k=3):
        """Versão vetorizada usando numpy - MUITO mais rápida"""
        distancias = self.distanciaEntrePontosVetorizada(vertice, array_vertices)
        indices_k_menores = np.argpartition(distancias, min(k, len(distancias)-1))[:k]
        indices_ordenados = indices_k_menores[np.argsort(distancias[indices_k_menores])]
        return [(int(idx), float(distancias[idx])) for idx in indices_ordenados]
        
    def criarMapeamentoBidirecional(self):
        """Cria mapeamento usando operações vetorizadas"""
        if not self.objeto1 or not self.objeto2:
            return
        
        print(f"  Criando mapa obj1 -> obj2...")
        for i, v1 in enumerate(self.objeto1.vertices):
            vizinhos = self.encontrarKVizinhosProximos(v1, self._vertices_array_obj2, k=5)
            self.mapa_vertices_1_para_2[i] = vizinhos
        
        print(f"  Criando mapa obj2 -> obj1...")
        for i, v2 in enumerate(self.objeto2.vertices):
            vizinhos = self.encontrarKVizinhosProximos(v2, self._vertices_array_obj1, k=5)
            self.mapa_vertices_2_para_1[i] = vizinhos
        
        print(f"  Mapeamento bidirecional criado")
                    
    def inicializarObjetoMorph(self):
        """Inicializa o objeto de morphing com o número máximo de vértices"""
        if not self.objeto1 or not self.objeto2:
            return
        
        self.objetoMorph = Objeto3D()
        
        num_v1 = len(self.objeto1.vertices)
        num_v2 = len(self.objeto2.vertices)
        max_vertices = max(num_v1, num_v2)
        
        # Criar vértices suficientes desde o início
        for i in range(max_vertices):
            if i < num_v1:
                v = self.objeto1.vertices[i]
                self.objetoMorph.vertices.append(Ponto(v.x, v.y, v.z))
            else:
                # Interpolar posição inicial para vértices extras
                if i in self.mapa_vertices_2_para_1:
                    v_inter = self.interpolarComPesos(
                        self.mapa_vertices_2_para_1[i],
                        self._vertices_array_obj1
                    )
                    self.objetoMorph.vertices.append(Ponto(v_inter.x, v_inter.y, v_inter.z))
                else:
                    centro = self.calcularCentroide(self.objeto1)
                    self.objetoMorph.vertices.append(Ponto(centro.x, centro.y, centro.z))
        
        # Começar com faces do objeto1
        self.objetoMorph.faces = [list(face) for face in self.objeto1.faces]
        
        self.objetoMorph.position = Ponto(0, 0, 0)
        self.objetoMorph.rotation = (0, 1, 0, 0)
        
        print(f"  Objeto morph: {len(self.objetoMorph.vertices)} vértices, {len(self.objetoMorph.faces)} faces")
    
    def interpolarComPesos(self, vizinhos, array_vertices):
        """Versão otimizada com cache de pesos"""
        if not vizinhos:
            return Ponto(0, 0, 0)
        
        cache_key = tuple((idx, dist) for idx, dist in vizinhos)
        
        if cache_key in self._cache_pesos:
            pesos = self._cache_pesos[cache_key]
        else:
            pesos = []
            for idx, dist in vizinhos:
                peso = 1000000 if dist < 0.0001 else 1.0 / (dist * dist)
                pesos.append((idx, peso))
            
            soma_pesos = sum(p[1] for p in pesos)
            pesos = [(idx, p/soma_pesos) for idx, p in pesos]
            self._cache_pesos[cache_key] = pesos
        
        posicao = np.zeros(3)
        for idx, peso in pesos:
            if idx < len(array_vertices):
                posicao += array_vertices[idx] * peso
        
        return Ponto(posicao[0], posicao[1], posicao[2])
        
    def atualizarMorph(self, progresso: float):
        """Versão melhorada - transição suave sem desaparecimento"""
        if not self.objetoMorph or not self.objeto1 or not self.objeto2:
            return
        
        # Ease in-out suave
        t = progresso * progresso * (3.0 - 2.0 * progresso)
        
        num_v1 = len(self.objeto1.vertices)
        num_v2 = len(self.objeto2.vertices)
        
        # Interpolar TODOS os vértices suavemente
        for i in range(len(self.objetoMorph.vertices)):
            v_morph = self.objetoMorph.vertices[i]
            
            # Determinar posição inicial (objeto1)
            if i < num_v1:
                v_start = self.objeto1.vertices[i]
                pos_start = np.array([v_start.x, v_start.y, v_start.z])
            else:
                # Vértice extra: usar interpolação do objeto1
                if i in self.mapa_vertices_2_para_1:
                    v_start = self.interpolarComPesos(
                        self.mapa_vertices_2_para_1[i],
                        self._vertices_array_obj1
                    )
                    pos_start = np.array([v_start.x, v_start.y, v_start.z])
                else:
                    centro = self.calcularCentroide(self.objeto1)
                    pos_start = np.array([centro.x, centro.y, centro.z])
            
            # Determinar posição final (objeto2)
            if i < num_v2:
                v_end = self.objeto2.vertices[i]
                pos_end = np.array([v_end.x, v_end.y, v_end.z])
            else:
                # Vértice extra: usar interpolação do objeto2
                if i in self.mapa_vertices_1_para_2:
                    v_end = self.interpolarComPesos(
                        self.mapa_vertices_1_para_2[i],
                        self._vertices_array_obj2
                    )
                    pos_end = np.array([v_end.x, v_end.y, v_end.z])
                else:
                    centro = self.calcularCentroide(self.objeto2)
                    pos_end = np.array([centro.x, centro.y, centro.z])
            
            # Interpolação linear suave
            pos_atual = pos_start + (pos_end - pos_start) * t
            v_morph.x, v_morph.y, v_morph.z = pos_atual[0], pos_atual[1], pos_atual[2]
        
        # Transição GRADUAL de faces
        self.atualizarFaces(progresso, num_v1, num_v2)
    
    def atualizarFaces(self, progresso, num_v1, num_v2):
        """Transição suave de faces mantendo o objeto visível"""
        # Ponto de transição mais tardio para evitar desaparecimento
        if progresso < 0.7:
            # Manter faces do objeto1 por mais tempo
            self.objetoMorph.faces = [list(face) for face in self.objeto1.faces]
        elif progresso < 0.9:
            # Transição gradual (70% - 90%)
            fase = (progresso - 0.7) / 0.2
            
            # Misturar faces dos dois objetos
            num_faces_obj1 = int(len(self.objeto1.faces) * (1 - fase))
            num_faces_obj2 = int(len(self.objeto2.faces) * fase)
            
            self.objetoMorph.faces = []
            
            # Adicionar faces do objeto1
            for face in self.objeto1.faces[:num_faces_obj1]:
                self.objetoMorph.faces.append(list(face))
            
            # Adicionar faces do objeto2
            for face in self.objeto2.faces[:num_faces_obj2]:
                face_ajustada = [idx for idx in face if idx < len(self.objetoMorph.vertices)]
                if len(face_ajustada) >= 3:
                    self.objetoMorph.faces.append(face_ajustada)
        else:
            # Final: usar apenas faces do objeto2
            self.objetoMorph.faces = []
            for face in self.objeto2.faces:
                face_ajustada = [idx for idx in face if idx < len(self.objetoMorph.vertices)]
                if len(face_ajustada) >= 3:
                    self.objetoMorph.faces.append(face_ajustada)
    
    def calcularCentroide(self, obj: Objeto3D):
        """Versão otimizada usando numpy"""
        if not obj.vertices:
            return Ponto(0, 0, 0)
        
        coords = np.array([[v.x, v.y, v.z] for v in obj.vertices])
        centro = coords.mean(axis=0)
        return Ponto(centro[0], centro[1], centro[2])
                
    def proximoFrame(self):
        """Avança para o próximo frame do morphing"""
        if not self.executando:
            return False
            
        self.frame_atual += self.velocidade
        
        if self.frame_atual >= self.total_frames:
            self.frame_atual = self.total_frames
            self.executando = False
            self.atualizarMorph(1.0)
            print(">>> Morphing COMPLETO (100%)")
            return False
            
        progresso = self.frame_atual / self.total_frames
        self.atualizarMorph(progresso)
        return True
        
    def iniciarMorphing(self):
        """Inicia a animação de morphing DO INÍCIO"""
        self.executando = True
        self.frame_atual = 0
        self._cache_pesos.clear()
        self.inicializarObjetoMorph()
        print("\n>>> Morphing INICIADO (0%)")
        
    def pararMorphing(self):
        """Para a animação de morphing"""
        self.executando = False
