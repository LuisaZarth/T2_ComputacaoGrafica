# MorphManager.py 
import math
from Ponto import Ponto
from Objeto3D import Objeto3D

class MorphManager:
    def __init__(self):
        self.objeto1 = None
        self.objeto2 = None
        self.objetoMorph = None
        self.mapa_vertices_1_para_2 = {}  # obj1 -> obj2
        self.mapa_vertices_2_para_1 = {}  # obj2 -> obj1
        self.frame_atual = 0
        self.total_frames = 300  # Mais frames para transição mais suave
        self.executando = False
        self.velocidade = 1.0
        self.modo_transicao = 1  # 0=obj1, 1=morph, 2=obj2

    def setObjetos(self, obj1: Objeto3D, obj2: Objeto3D):
        self.objeto1 = obj1
        self.objeto2 = obj2
        print("\n=== INICIANDO CONFIGURAÇÃO DE MORPHING ===")
        print("Normalizando objetos...")
        self.normalizarObjetos()
        print("Criando mapeamento bidirecional...")
        self.criarMapeamentoBidirecional()
        print("Inicializando objeto de morphing...")
        self.inicializarObjetoMorph()
        print("=== CONFIGURAÇÃO COMPLETA ===\n")
        
    def normalizarObjetos(self):
        """Normaliza a escala e centraliza os objetos"""
        if self.objeto1:
            self.normalizarObjeto(self.objeto1)
            print(f"  Obj1 normalizado: {len(self.objeto1.vertices)} vértices")
        if self.objeto2:
            self.normalizarObjeto(self.objeto2)
            print(f"  Obj2 normalizado: {len(self.objeto2.vertices)} vértices")
        
    def normalizarObjeto(self, obj: Objeto3D):
        """Normaliza um objeto individual para o cubo [-1, 1]"""
        if not obj.vertices:
            return
            
        # Encontrar bounding box
        min_x = min(v.x for v in obj.vertices)
        max_x = max(v.x for v in obj.vertices)
        min_y = min(v.y for v in obj.vertices)
        max_y = max(v.y for v in obj.vertices)
        min_z = min(v.z for v in obj.vertices)
        max_z = max(v.z for v in obj.vertices)
        
        # Calcular centro
        centro = Ponto(
            (min_x + max_x) / 2,
            (min_y + max_y) / 2, 
            (min_z + max_z) / 2
        )
        
        # Calcular escala máxima
        escala_x = max_x - min_x
        escala_y = max_y - min_y
        escala_z = max_z - min_z
        escala_max = max(escala_x, escala_y, escala_z)
        
        if escala_max == 0:
            escala_max = 1.0
            
        # Fator de escala para normalizar para [-1, 1]
        fator_escala = 2.0 / escala_max
        
        # Normalizar e centralizar
        for vertice in obj.vertices:
            vertice.x = (vertice.x - centro.x) * fator_escala
            vertice.y = (vertice.y - centro.y) * fator_escala
            vertice.z = (vertice.z - centro.z) * fator_escala
            
    def distanciaEntrePontos(self, p1: Ponto, p2: Ponto):
        """Calcula distância euclidiana entre dois pontos"""
        dx = p1.x - p2.x
        dy = p1.y - p2.y
        dz = p1.z - p2.z
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def encontrarKVizinhosProximos(self, vertice: Ponto, lista_vertices, k=3):
        """Encontra os K vértices mais próximos e retorna seus índices e distâncias"""
        distancias = []
        for i, v in enumerate(lista_vertices):
            dist = self.distanciaEntrePontos(vertice, v)
            distancias.append((i, dist))
        
        # Ordenar por distância e pegar os K menores
        distancias.sort(key=lambda x: x[1])
        return distancias[:k]
        
    def criarMapeamentoBidirecional(self):
        """
        Cria mapeamento bidirecional mais sofisticado:
        - Cada vértice mapeia para múltiplos vizinhos próximos
        - Usa interpolação ponderada por distância
        """
        if not self.objeto1 or not self.objeto2:
            return
        
        print(f"  Criando mapa obj1 -> obj2...")
        # Mapear obj1 -> obj2 (cada vértice do obj1 para 3 mais próximos do obj2)
        for i, v1 in enumerate(self.objeto1.vertices):
            vizinhos = self.encontrarKVizinhosProximos(v1, self.objeto2.vertices, k=5)
            self.mapa_vertices_1_para_2[i] = vizinhos
        
        print(f"  Criando mapa obj2 -> obj1...")
        # Mapear obj2 -> obj1 (cada vértice do obj2 para 3 mais próximos do obj1)
        for i, v2 in enumerate(self.objeto2.vertices):
            vizinhos = self.encontrarKVizinhosProximos(v2, self.objeto1.vertices, k=5)
            self.mapa_vertices_2_para_1[i] = vizinhos
        
        print(f"  Mapeamento bidirecional criado")
                    
    def inicializarObjetoMorph(self):
        """
        Inicializa o objeto de morphing
        Começa com estrutura híbrida que pode representar ambos os objetos
        """
        if not self.objeto1 or not self.objeto2:
            return
        
        self.objetoMorph = Objeto3D()
        
        # Começar com vértices do objeto1
        self.objetoMorph.vertices = []
        for v in self.objeto1.vertices:
            self.objetoMorph.vertices.append(Ponto(v.x, v.y, v.z))
        
        # Usar faces do objeto1
        self.objetoMorph.faces = []
        for face in self.objeto1.faces:
            self.objetoMorph.faces.append(list(face))
        
        self.objetoMorph.position = Ponto(0, 0, 0)
        self.objetoMorph.rotation = (0, 1, 0, 0)
        
        print(f"  Objeto morph: {len(self.objetoMorph.vertices)} vértices, {len(self.objetoMorph.faces)} faces")
        
    def interpolarComPesos(self, vizinhos, lista_vertices):
        """
        Interpola posição usando média ponderada dos K vizinhos mais próximos
        vizinhos: lista de tuplas (indice, distancia)
        """
        if not vizinhos:
            return Ponto(0, 0, 0)
        
        # Calcular pesos inversamente proporcionais à distância
        soma_pesos = 0
        posicao = Ponto(0, 0, 0)
        
        for idx, dist in vizinhos:
            if dist < 0.0001:  # Evitar divisão por zero
                peso = 1000000
            else:
                peso = 1.0 / (dist * dist)  # Peso quadrático inverso
            
            if idx < len(lista_vertices):
                v = lista_vertices[idx]
                posicao.x += v.x * peso
                posicao.y += v.y * peso
                posicao.z += v.z * peso
                soma_pesos += peso
        
        # Normalizar pelos pesos
        if soma_pesos > 0:
            posicao.x /= soma_pesos
            posicao.y /= soma_pesos
            posicao.z /= soma_pesos
        
        return posicao
        
    def atualizarMorph(self, progresso: float):
        """
        Atualiza o morphing com transição suave entre topologias
        Funciona em AMBAS as direções (expansão e contração)
        """
        if not self.objetoMorph or not self.objeto1 or not self.objeto2:
            return
        
        # Função de easing suave
        t = progresso
        # Ease in-out cúbico
        t_suave = t * t * (3.0 - 2.0 * t)
        
        num_v1 = len(self.objeto1.vertices)
        num_v2 = len(self.objeto2.vertices)
        
        # CASO 1: Obj1 tem MAIS vértices que Obj2 (CONTRAÇÃO)
        if num_v1 > num_v2:
            # Fase 1 (0 -> 0.5): Colapsar vértices extras
            # Fase 2 (0.5 -> 1.0): Ajustar para posições finais
            
            if progresso <= 0.5:
                fase = progresso * 2  # 0 a 1
                fase_suave = fase * fase * (3.0 - 2.0 * fase)
                
                # Interpolar todos os vértices
                for i in range(len(self.objetoMorph.vertices)):
                    if i >= num_v1:
                        continue
                    
                    v1 = self.objeto1.vertices[i]
                    
                    # Vértices que têm correspondente no obj2
                    if i < num_v2:
                        # Interpolar para a posição correspondente do obj2
                        if i in self.mapa_vertices_1_para_2:
                            vizinhos = self.mapa_vertices_1_para_2[i]
                            v2_interpolado = self.interpolarComPesos(vizinhos, self.objeto2.vertices)
                        else:
                            v2_interpolado = self.objeto2.vertices[i]
                        
                        v_morph = self.objetoMorph.vertices[i]
                        v_morph.x = v1.x + (v2_interpolado.x - v1.x) * fase_suave
                        v_morph.y = v1.y + (v2_interpolado.y - v1.y) * fase_suave
                        v_morph.z = v1.z + (v2_interpolado.z - v1.z) * fase_suave
                    
                    # Vértices extras (que não existem no obj2)
                    else:
                        # Colapsar para o vértice mais próximo do obj2
                        if i in self.mapa_vertices_1_para_2:
                            vizinhos = self.mapa_vertices_1_para_2[i]
                            v_destino = self.interpolarComPesos(vizinhos, self.objeto2.vertices)
                        else:
                            # Fallback: centro do obj2
                            v_destino = self.calcularCentroide(self.objeto2)
                        
                        v_morph = self.objetoMorph.vertices[i]
                        v_morph.x = v1.x + (v_destino.x - v1.x) * fase_suave
                        v_morph.y = v1.y + (v_destino.y - v1.y) * fase_suave
                        v_morph.z = v1.z + (v_destino.z - v1.z) * fase_suave
                
                # Gradualmente remover faces extras
                if fase_suave > 0.3:
                    proporcao_remover = (fase_suave - 0.3) / 0.7
                    num_faces_manter = int(len(self.objeto1.faces) * (1 - proporcao_remover * 0.5))
                    self.objetoMorph.faces = [list(f) for f in self.objeto1.faces[:num_faces_manter]]
            
            else:  # Fase 2: 0.5 -> 1.0
                fase = (progresso - 0.5) * 2  # 0 a 1
                fase_suave = fase * fase * (3.0 - 2.0 * fase)
                
                # Ajustar apenas os vértices que permanecerão
                for i in range(min(num_v2, len(self.objetoMorph.vertices))):
                    # Posição no final da fase 1
                    if i in self.mapa_vertices_1_para_2:
                        vizinhos = self.mapa_vertices_1_para_2[i]
                        v_meio = self.interpolarComPesos(vizinhos, self.objeto2.vertices)
                    else:
                        v_meio = self.objeto2.vertices[i] if i < num_v2 else self.objetoMorph.vertices[i]
                    
                    # Posição final
                    v2 = self.objeto2.vertices[i]
                    
                    v_morph = self.objetoMorph.vertices[i]
                    v_morph.x = v_meio.x + (v2.x - v_meio.x) * fase_suave
                    v_morph.y = v_meio.y + (v2.y - v_meio.y) * fase_suave
                    v_morph.z = v_meio.z + (v2.z - v_meio.z) * fase_suave
                
                # Transição completa para faces do obj2
                if fase_suave > 0.5:
                    proporcao_obj2 = (fase_suave - 0.5) / 0.5
                    num_faces_obj1 = int(len(self.objeto2.faces) * (1 - proporcao_obj2))
                    num_faces_obj2 = len(self.objeto2.faces) - num_faces_obj1
                    
                    self.objetoMorph.faces = []
                    # Adicionar faces do obj2
                    for face in self.objeto2.faces[:num_faces_obj2]:
                        face_ajustada = [idx for idx in face if idx < len(self.objetoMorph.vertices)]
                        if len(face_ajustada) >= 3:
                            self.objetoMorph.faces.append(face_ajustada)
        
        # CASO 2: Obj1 tem MENOS ou IGUAL vértices que Obj2 (EXPANSÃO)
        else:
            # Fase 1 (0.0 -> 0.5): Deformar obj1
            if progresso <= 0.5:
                fase = progresso * 2  # 0 a 1
                fase_suave = fase * fase * (3.0 - 2.0 * fase)
                
                for i in range(len(self.objetoMorph.vertices)):
                    if i >= num_v1:
                        continue
                    
                    v1 = self.objeto1.vertices[i]
                    
                    # Interpolar com múltiplos vizinhos do obj2
                    if i in self.mapa_vertices_1_para_2:
                        vizinhos = self.mapa_vertices_1_para_2[i]
                        v2_interpolado = self.interpolarComPesos(vizinhos, self.objeto2.vertices)
                        
                        v_morph = self.objetoMorph.vertices[i]
                        v_morph.x = v1.x + (v2_interpolado.x - v1.x) * fase_suave
                        v_morph.y = v1.y + (v2_interpolado.y - v1.y) * fase_suave
                        v_morph.z = v1.z + (v2_interpolado.z - v1.z) * fase_suave
            
            # Fase 2 (0.5 -> 1.0): Expandir para obj2
            else:
                fase = (progresso - 0.5) * 2  # 0 a 1
                fase_suave = fase * fase * (3.0 - 2.0 * fase)
                
                # Adicionar vértices extras se necessário
                while len(self.objetoMorph.vertices) < num_v2:
                    idx = len(self.objetoMorph.vertices)
                    if idx in self.mapa_vertices_2_para_1:
                        vizinhos = self.mapa_vertices_2_para_1[idx]
                        v_inter = self.interpolarComPesos(vizinhos, self.objeto1.vertices)
                        self.objetoMorph.vertices.append(Ponto(v_inter.x, v_inter.y, v_inter.z))
                    elif idx < num_v2:
                        v2 = self.objeto2.vertices[idx]
                        self.objetoMorph.vertices.append(Ponto(v2.x, v2.y, v2.z))
                
                # Interpolar todos os vértices
                for i in range(min(len(self.objetoMorph.vertices), num_v2)):
                    v_morph = self.objetoMorph.vertices[i]
                    v2 = self.objeto2.vertices[i]
                    
                    # Posição inicial (final da fase 1)
                    if i < num_v1:
                        v1 = self.objeto1.vertices[i]
                        if i in self.mapa_vertices_1_para_2:
                            vizinhos = self.mapa_vertices_1_para_2[i]
                            v_inicial = self.interpolarComPesos(vizinhos, self.objeto2.vertices)
                        else:
                            v_inicial = v1
                    else:
                        v_inicial = v_morph
                    
                    # Interpolar para posição final
                    v_morph.x = v_inicial.x + (v2.x - v_inicial.x) * fase_suave
                    v_morph.y = v_inicial.y + (v2.y - v_inicial.y) * fase_suave
                    v_morph.z = v_inicial.z + (v2.z - v_inicial.z) * fase_suave
                
                # Transição de faces
                if fase_suave > 0.7:
                    proporcao_obj2 = (fase_suave - 0.7) / 0.3
                    num_faces_obj2 = int(len(self.objeto2.faces) * proporcao_obj2)
                    
                    self.objetoMorph.faces = []
                    # Manter faces do obj1
                    for face in self.objeto1.faces[:len(self.objeto1.faces) - num_faces_obj2]:
                        self.objetoMorph.faces.append(list(face))
                    # Adicionar faces do obj2
                    for face in self.objeto2.faces[:num_faces_obj2]:
                        face_ajustada = [idx for idx in face if idx < len(self.objetoMorph.vertices)]
                        if len(face_ajustada) >= 3:
                            self.objetoMorph.faces.append(face_ajustada)
    
    def calcularCentroide(self, obj: Objeto3D):
        """Calcula o centroide do objeto"""
        if not obj.vertices:
            return Ponto(0, 0, 0)
        
        soma_x = sum(v.x for v in obj.vertices)
        soma_y = sum(v.y for v in obj.vertices)
        soma_z = sum(v.z for v in obj.vertices)
        n = len(obj.vertices)
        
        return Ponto(soma_x / n, soma_y / n, soma_z / n)
                
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
        
        # Debug a cada 5%
       # percentual_atual = int(progresso * 100)
       # percentual_anterior = int((self.frame_atual - self.velocidade) / self.total_frames * 100)
       # if percentual_atual // 5 != percentual_anterior // 5:
        #    print(f">>> Morphing: {percentual_atual}%")
        
        return True
        
    def iniciarMorphing(self):
        """Inicia a animação de morphing DO INÍCIO"""
        self.executando = True
        self.frame_atual = 0
        self.inicializarObjetoMorph()
        print("\n>>> Morphing INICIADO (0%)")
        
    def pararMorphing(self):
        """Para a animação de morphing"""
        self.executando = False
        progresso_atual = (self.frame_atual / self.total_frames) * 100
        #print(f"\n>>> Morphing PAUSADO em {progresso_atual:.1f}%")
