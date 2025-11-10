# MorphManager.py - VERSÃO OTIMIZADA
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
        
        # Converter para numpy arrays uma vez
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
        
        # Converter para array numpy
        coords = np.array([[v.x, v.y, v.z] for v in obj.vertices])
        
        # Calcular min, max e centro em uma operação
        min_coords = coords.min(axis=0)
        max_coords = coords.max(axis=0)
        centro = (min_coords + max_coords) / 2
        
        # Calcular escala
        escala = (max_coords - min_coords).max()
        if escala == 0:
            escala = 1.0
        
        fator_escala = 2.0 / escala
        
        # Normalizar todos os vértices de uma vez
        coords_norm = (coords - centro) * fator_escala
        
        # Atualizar vértices
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
        # np.argpartition é mais rápido que sort completo para encontrar k menores
        indices_k_menores = np.argpartition(distancias, min(k, len(distancias)-1))[:k]
        # Ordenar apenas os k selecionados
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
        """Inicializa o objeto de morphing"""
        if not self.objeto1 or not self.objeto2:
            return
        
        self.objetoMorph = Objeto3D()
        
        # Copiar vértices do objeto1
        self.objetoMorph.vertices = [Ponto(v.x, v.y, v.z) for v in self.objeto1.vertices]
        
        # Copiar faces do objeto1
        self.objetoMorph.faces = [list(face) for face in self.objeto1.faces]
        
        self.objetoMorph.position = Ponto(0, 0, 0)
        self.objetoMorph.rotation = (0, 1, 0, 0)
        
        print(f"  Objeto morph: {len(self.objetoMorph.vertices)} vértices, {len(self.objetoMorph.faces)} faces")
    
    def interpolarComPesos(self, vizinhos, array_vertices):
        """Versão otimizada com cache de pesos"""
        if not vizinhos:
            return Ponto(0, 0, 0)
        
        # Criar chave para cache
        cache_key = tuple((idx, dist) for idx, dist in vizinhos)
        
        if cache_key in self._cache_pesos:
            pesos = self._cache_pesos[cache_key]
        else:
            # Calcular pesos
            pesos = []
            for idx, dist in vizinhos:
                peso = 1000000 if dist < 0.0001 else 1.0 / (dist * dist)
                pesos.append((idx, peso))
            
            soma_pesos = sum(p[1] for p in pesos)
            pesos = [(idx, p/soma_pesos) for idx, p in pesos]
            self._cache_pesos[cache_key] = pesos
        
        # Calcular posição interpolada usando numpy
        posicao = np.zeros(3)
        for idx, peso in pesos:
            if idx < len(array_vertices):
                posicao += array_vertices[idx] * peso
        
        return Ponto(posicao[0], posicao[1], posicao[2])
        
    def atualizarMorph(self, progresso: float):
        """Versão otimizada da atualização de morphing"""
        if not self.objetoMorph or not self.objeto1 or not self.objeto2:
            return
        
        # Ease in-out cúbico
        t = progresso * progresso * (3.0 - 2.0 * progresso)
        
        num_v1 = len(self.objeto1.vertices)
        num_v2 = len(self.objeto2.vertices)
        
        # CASO 1: CONTRAÇÃO (obj1 > obj2)
        if num_v1 > num_v2:
            if progresso <= 0.5:
                fase = progresso * 2
                fase_suave = fase * fase * (3.0 - 2.0 * fase)
                
                # Processar vértices em lote
                for i in range(min(num_v1, len(self.objetoMorph.vertices))):
                    v1 = self.objeto1.vertices[i]
                    
                    if i < num_v2:
                        if i in self.mapa_vertices_1_para_2:
                            v2_interpolado = self.interpolarComPesos(
                                self.mapa_vertices_1_para_2[i], 
                                self._vertices_array_obj2
                            )
                        else:
                            v2_interpolado = self.objeto2.vertices[i]
                    else:
                        if i in self.mapa_vertices_1_para_2:
                            v2_interpolado = self.interpolarComPesos(
                                self.mapa_vertices_1_para_2[i],
                                self._vertices_array_obj2
                            )
                        else:
                            v2_interpolado = self.calcularCentroide(self.objeto2)
                    
                    v_morph = self.objetoMorph.vertices[i]
                    v_morph.x = v1.x + (v2_interpolado.x - v1.x) * fase_suave
                    v_morph.y = v1.y + (v2_interpolado.y - v1.y) * fase_suave
                    v_morph.z = v1.z + (v2_interpolado.z - v1.z) * fase_suave
                
                if fase_suave > 0.3:
                    proporcao_remover = (fase_suave - 0.3) / 0.7
                    num_faces_manter = int(len(self.objeto1.faces) * (1 - proporcao_remover * 0.5))
                    self.objetoMorph.faces = [list(f) for f in self.objeto1.faces[:num_faces_manter]]
            
            else:  # Fase 2
                fase = (progresso - 0.5) * 2
                fase_suave = fase * fase * (3.0 - 2.0 * fase)
                
                for i in range(min(num_v2, len(self.objetoMorph.vertices))):
                    if i in self.mapa_vertices_1_para_2:
                        v_meio = self.interpolarComPesos(
                            self.mapa_vertices_1_para_2[i],
                            self._vertices_array_obj2
                        )
                    else:
                        v_meio = self.objeto2.vertices[i] if i < num_v2 else self.objetoMorph.vertices[i]
                    
                    v2 = self.objeto2.vertices[i]
                    v_morph = self.objetoMorph.vertices[i]
                    v_morph.x = v_meio.x + (v2.x - v_meio.x) * fase_suave
                    v_morph.y = v_meio.y + (v2.y - v_meio.y) * fase_suave
                    v_morph.z = v_meio.z + (v2.z - v_meio.z) * fase_suave
                
                if fase_suave > 0.5:
                    proporcao_obj2 = (fase_suave - 0.5) / 0.5
                    num_faces_obj2 = int(len(self.objeto2.faces) * proporcao_obj2)
                    
                    self.objetoMorph.faces = []
                    for face in self.objeto2.faces[:num_faces_obj2]:
                        face_ajustada = [idx for idx in face if idx < len(self.objetoMorph.vertices)]
                        if len(face_ajustada) >= 3:
                            self.objetoMorph.faces.append(face_ajustada)
        
        # CASO 2: EXPANSÃO (obj1 <= obj2)
        else:
            if progresso <= 0.5:
                fase = progresso * 2
                fase_suave = fase * fase * (3.0 - 2.0 * fase)
                
                for i in range(len(self.objetoMorph.vertices)):
                    if i >= num_v1:
                        continue
                    
                    v1 = self.objeto1.vertices[i]
                    
                    if i in self.mapa_vertices_1_para_2:
                        v2_interpolado = self.interpolarComPesos(
                            self.mapa_vertices_1_para_2[i],
                            self._vertices_array_obj2
                        )
                        
                        v_morph = self.objetoMorph.vertices[i]
                        v_morph.x = v1.x + (v2_interpolado.x - v1.x) * fase_suave
                        v_morph.y = v1.y + (v2_interpolado.y - v1.y) * fase_suave
                        v_morph.z = v1.z + (v2_interpolado.z - v1.z) * fase_suave
            
            else:  # Fase 2
                fase = (progresso - 0.5) * 2
                fase_suave = fase * fase * (3.0 - 2.0 * fase)
                
                # Adicionar vértices extras
                while len(self.objetoMorph.vertices) < num_v2:
                    idx = len(self.objetoMorph.vertices)
                    if idx in self.mapa_vertices_2_para_1:
                        v_inter = self.interpolarComPesos(
                            self.mapa_vertices_2_para_1[idx],
                            self._vertices_array_obj1
                        )
                        self.objetoMorph.vertices.append(Ponto(v_inter.x, v_inter.y, v_inter.z))
                    elif idx < num_v2:
                        v2 = self.objeto2.vertices[idx]
                        self.objetoMorph.vertices.append(Ponto(v2.x, v2.y, v2.z))
                
                # Interpolar todos os vértices
                for i in range(min(len(self.objetoMorph.vertices), num_v2)):
                    v_morph = self.objetoMorph.vertices[i]
                    v2 = self.objeto2.vertices[i]
                    
                    if i < num_v1:
                        v1 = self.objeto1.vertices[i]
                        if i in self.mapa_vertices_1_para_2:
                            v_inicial = self.interpolarComPesos(
                                self.mapa_vertices_1_para_2[i],
                                self._vertices_array_obj2
                            )
                        else:
                            v_inicial = v1
                    else:
                        v_inicial = v_morph
                    
                    v_morph.x = v_inicial.x + (v2.x - v_inicial.x) * fase_suave
                    v_morph.y = v_inicial.y + (v2.y - v_inicial.y) * fase_suave
                    v_morph.z = v_inicial.z + (v2.z - v_inicial.z) * fase_suave
                
                # Transição de faces
                if fase_suave > 0.7:
                    proporcao_obj2 = (fase_suave - 0.7) / 0.3
                    num_faces_obj2 = int(len(self.objeto2.faces) * proporcao_obj2)
                    
                    self.objetoMorph.faces = []
                    for face in self.objeto1.faces[:len(self.objeto1.faces) - num_faces_obj2]:
                        self.objetoMorph.faces.append(list(face))
                    for face in self.objeto2.faces[:num_faces_obj2]:
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
        self._cache_pesos.clear()  # Limpar cache
        self.inicializarObjetoMorph()
        print("\n>>> Morphing INICIADO (0%)")
        
    def pararMorphing(self):
        """Para a animação de morphing"""
        self.executando = False
