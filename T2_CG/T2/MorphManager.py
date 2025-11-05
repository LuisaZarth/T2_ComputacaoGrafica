# MorphManager.py
import math
from Ponto import Ponto
from Objeto3D import Objeto3D

class MorphManager:
    def __init__(self):
        self.objeto1 = None
        self.objeto2 = None
        self.objetoMorph = None
        self.associacoes = []
        self.frame_atual = 0
        self.total_frames = 200  # Mais frames para animação mais suave
        self.executando = False
        self.velocidade = 1.0

    def setObjetos(self, obj1: Objeto3D, obj2: Objeto3D):
        self.objeto1 = obj1
        self.objeto2 = obj2
        print("Normalizando objetos...")
        self.normalizarObjetos()
        print("Criando associações...")
        self.criarAssociacoes()
        print("Inicializando objeto de morphing...")
        self.inicializarObjetoMorph()
        print("MorphManager configurado com sucesso!")
        
    def normalizarObjetos(self):
        """Normaliza a escala e centraliza os objetos"""
        if self.objeto1:
            self.normalizarObjeto(self.objeto1)
        if self.objeto2:
            self.normalizarObjeto(self.objeto2)
        
    def normalizarObjeto(self, obj: Objeto3D):
        """Normaliza um objeto individual"""
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
            
    def calcularCentroideFace(self, obj: Objeto3D, face):
        """Calcula o centroide de uma face"""
        soma = Ponto(0, 0, 0)
        for indice_vertice in face:
            if indice_vertice < len(obj.vertices):
                vertice = obj.vertices[indice_vertice]
                soma.x += vertice.x
                soma.y += vertice.y
                soma.z += vertice.z
            
        num_vertices = len(face)
        if num_vertices > 0:
            return Ponto(
                soma.x / num_vertices,
                soma.y / num_vertices,
                soma.z / num_vertices
            )
        return Ponto(0, 0, 0)
        
    def distanciaEntrePontos(self, p1: Ponto, p2: Ponto):
        """Calcula distância euclidiana entre dois pontos"""
        dx = p1.x - p2.x
        dy = p1.y - p2.y
        dz = p1.z - p2.z
        return math.sqrt(dx*dx + dy*dy + dz*dz)
        
    def criarAssociacoes(self):
        """Cria associações entre faces dos dois objetos"""
        self.associacoes = []
        
        if not self.objeto1 or not self.objeto2:
            return
            
        # Calcular centroides para todas as faces
        centroides1 = []
        for i, face in enumerate(self.objeto1.faces):
            centroides1.append((i, self.calcularCentroideFace(self.objeto1, face)))
            
        centroides2 = []
        for i, face in enumerate(self.objeto2.faces):
            centroides2.append((i, self.calcularCentroideFace(self.objeto2, face)))
            
        print(f"Centroides calculados: Obj1={len(centroides1)}, Obj2={len(centroides2)}")
            
        # Estratégia: associar cada face do objeto menor com múltiplas faces do objeto maior
        if len(centroides1) <= len(centroides2):
            menor = centroides1
            maior = centroides2
            invertido = False
        else:
            menor = centroides2
            maior = centroides1
            invertido = True
            
        faces_usadas_maior = set()
        
        # Primeira passada: associação 1-1 mais próxima
        for idx_menor, centroide_menor in menor:
            menor_distancia = float('inf')
            melhor_idx_maior = -1
            
            for idx_maior, centroide_maior in maior:
                if idx_maior in faces_usadas_maior:
                    continue
                    
                distancia = self.distanciaEntrePontos(centroide_menor, centroide_maior)
                if distancia < menor_distancia:
                    menor_distancia = distancia
                    melhor_idx_maior = idx_maior
                    
            if melhor_idx_maior != -1:
                faces_usadas_maior.add(melhor_idx_maior)
                if not invertido:
                    self.associacoes.append((idx_menor, melhor_idx_maior))
                else:
                    self.associacoes.append((melhor_idx_maior, idx_menor))
                
        # Segunda passada: associar faces restantes com as mais próximas
        faces_nao_associadas_maior = set(range(len(maior))) - faces_usadas_maior
        
        for idx_maior in faces_nao_associadas_maior:
            centroide_maior = maior[idx_maior][1]
            menor_distancia = float('inf')
            melhor_idx_menor = -1
            
            for idx_menor, centroide_menor in menor:
                distancia = self.distanciaEntrePontos(centroide_menor, centroide_maior)
                if distancia < menor_distancia:
                    menor_distancia = distancia
                    melhor_idx_menor = idx_menor
                    
            if melhor_idx_menor != -1:
                if not invertido:
                    self.associacoes.append((melhor_idx_menor, idx_maior))
                else:
                    self.associacoes.append((idx_maior, melhor_idx_menor))
                    
    def inicializarObjetoMorph(self):
        """Inicializa o objeto de morphing como cópia do objeto 1"""
        if not self.objeto1:
            return
            
        self.objetoMorph = Objeto3D()
        self.objetoMorph.vertices = [Ponto(v.x, v.y, v.z) for v in self.objeto1.vertices]
        self.objetoMorph.faces = self.objeto1.faces.copy()
        
    def atualizarMorph(self, progresso: float):
        """Atualiza o morphing baseado no progresso (0 a 1)"""
        if not self.objetoMorph or not self.objeto1 or not self.objeto2:
            return
            
        # Resetar para o objeto 1
        for i, vertice in enumerate(self.objetoMorph.vertices):
            if i < len(self.objeto1.vertices):
                vertice_orig = self.objeto1.vertices[i]
                vertice.x = vertice_orig.x
                vertice.y = vertice_orig.y
                vertice.z = vertice_orig.z
            
        # Aplicar morphing baseado nas associações
        for idx1, idx2 in self.associacoes:
            if idx1 < len(self.objeto1.faces) and idx2 < len(self.objeto2.faces):
                face1 = self.objeto1.faces[idx1]
                face2 = self.objeto2.faces[idx2]
                
                # Interpolar vértices correspondentes
                num_vertices = min(len(face1), len(face2))
                for i in range(num_vertices):
                    vertice_idx1 = face1[i]
                    vertice_idx2 = face2[i]
                    
                    if (vertice_idx1 < len(self.objeto1.vertices) and 
                        vertice_idx2 < len(self.objeto2.vertices)):
                        
                        v1 = self.objeto1.vertices[vertice_idx1]
                        v2 = self.objeto2.vertices[vertice_idx2]
                        
                        # Interpolação linear
                        vertice_morph = self.objetoMorph.vertices[vertice_idx1]
                        vertice_morph.x = v1.x + (v2.x - v1.x) * progresso
                        vertice_morph.y = v1.y + (v2.y - v1.y) * progresso  
                        vertice_morph.z = v1.z + (v2.z - v1.z) * progresso
                
    def proximoFrame(self):
        """Avança para o próximo frame do morphing - PARA NO FINAL"""
        if not self.executando:
            return False
            
        self.frame_atual += self.velocidade
        
        # Se chegou ao final, PARA permanentemente
        if self.frame_atual >= self.total_frames:
            self.frame_atual = self.total_frames  # Mantém no último frame
            self.executando = False
            self.atualizarMorph(1.0)  # Garante 100% de transformação
            print("Morphing COMPLETO - Objeto final transformado")
            return False
            
        progresso = self.frame_atual / self.total_frames
        self.atualizarMorph(progresso)
        return True
        
    def iniciarMorphing(self):
        """Inicia a animação de morphing"""
        self.executando = True
        self.frame_atual = 0
        print("Morphing iniciado!")
        
    def pararMorphing(self):
        """Para a animação de morphing"""
        self.executando = False
        print("Morphing parado!")

    def setVelocidade(self, velocidade: float):
        """Define a velocidade do morphing"""
        self.velocidade = max(0.1, min(5.0, velocidade))  # Limite entre 0.1 e 5.0
        print(f"Velocidade do morphing: {self.velocidade}x")

    def reiniciarMorphing(self):
        """Reinicia o morphing do início"""
        self.executando = True
        self.frame_atual = 0
        print("Morphing reiniciado!")