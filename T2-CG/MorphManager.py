# MorphManager.py - VERSÃO BEM SIMPLES
from Ponto import Ponto
from Objeto3D import Objeto3D

class MorphManager:
    def __init__(self):
        self.objeto1 = None
        self.objeto2 = None
        self.objetoMorph = None
        self.frame_atual = 0
        self.total_frames = 150
        self.executando = False
        self.velocidade = 1.0

    def setObjetos(self, obj1: Objeto3D, obj2: Objeto3D):
        self.objeto1 = obj1
        self.objeto2 = obj2
        self.normalizarObjetos()
        self.inicializarObjetoMorph()
        
    def normalizarObjetos(self):
        # normaliza os dois objetos
        self.normalizarObjeto(self.objeto1)
        self.normalizarObjeto(self.objeto2)
        
    def normalizarObjeto(self, obj: Objeto3D):
        # deixa o objeto no tamanho certo
        if len(obj.vertices) == 0:
            return
            
        # achar os limites
        min_x = obj.vertices[0].x
        max_x = obj.vertices[0].x
        min_y = obj.vertices[0].y
        max_y = obj.vertices[0].y
        min_z = obj.vertices[0].z
        max_z = obj.vertices[0].z
        
        for v in obj.vertices:
            if v.x < min_x:
                min_x = v.x
            if v.x > max_x:
                max_x = v.x
            if v.y < min_y:
                min_y = v.y
            if v.y > max_y:
                max_y = v.y
            if v.z < min_z:
                min_z = v.z
            if v.z > max_z:
                max_z = v.z
        
        # centro do objeto
        centro_x = (min_x + max_x) / 2.0
        centro_y = (min_y + max_y) / 2.0
        centro_z = (min_z + max_z) / 2.0
        
        # tamanho do objeto
        tam_x = max_x - min_x
        tam_y = max_y - min_y
        tam_z = max_z - min_z
        
        # pegar o maior tamanho
        t_max = tam_x
        if tam_y > t_max:
            t_max = tam_y
        if tam_z > t_max:
            t_max = tam_z
        
        if t_max == 0:
            t_max = 1.0
            
        # calcular escala
        escala = 2.0 / t_max
        
        # aplicar nos vertices
        for v in obj.vertices:
            v.x = (v.x - centro_x) * escala
            v.y = (v.y - centro_y) * escala
            v.z = (v.z - centro_z) * escala
    
    def inicializarObjetoMorph(self):
        # criar o objeto do morphing
        self.objetoMorph = Objeto3D()
        
        # copiar vertices do objeto1
        self.objetoMorph.vertices = []
        for i in range(len(self.objeto1.vertices)):
            v = self.objeto1.vertices[i]
            self.objetoMorph.vertices.append(Ponto(v.x, v.y, v.z))
        
        # se objeto2 tem mais vertices, adicionar
        verices_obj1 = len(self.objeto1.vertices)
        vertices_obj2 = len(self.objeto2.vertices)
        if vertices_obj2 > verices_obj1:
            for i in range(verices_obj1, vertices_obj2):
                v = self.objeto2.vertices[i]
                self.objetoMorph.vertices.append(Ponto(v.x, v.y, v.z))
        
        # copiar faces do objeto1
        self.objetoMorph.faces = []
        for face in self.objeto1.faces:
            nova_face = []
            for idx in face:
                nova_face.append(idx)
            self.objetoMorph.faces.append(nova_face)
        
        self.objetoMorph.position = Ponto(0, 0, 0)
        self.objetoMorph.rotation = (0, 1, 0, 0)
    
    def atualizarMorph(self, tam):
        # tam vai de 0 ate 1
        # 0 = objeto1, 1 = objeto2
        
        verices_obj1 = len(self.objeto1.vertices)
        vertices_obj2 = len(self.objeto2.vertices)
        
        # atualizar cada vertice
        for i in range(len(self.objetoMorph.vertices)):
            
            # se existe nos dois objetos
            if i < verices_obj1 and i < vertices_obj2:
                v1 = self.objeto1.vertices[i]
                v2 = self.objeto2.vertices[i]
                v = self.objetoMorph.vertices[i]
                
                # interpolacao linear
                v.x = v1.x + (v2.x - v1.x) * tam
                v.y = v1.y + (v2.y - v1.y) * tam
                v.z = v1.z + (v2.z - v1.z) * tam
            
            # se so existe no objeto1
            elif i < verices_obj1:
                v1 = self.objeto1.vertices[i]
                v = self.objetoMorph.vertices[i]
                # vai sumindo
                v.x = v1.x * (1.0 - tam)
                v.y = v1.y * (1.0 - tam)
                v.z = v1.z * (1.0 - tam)
            
            # se so existe no objeto2
            else:
                v2 = self.objeto2.vertices[i]
                v = self.objetoMorph.vertices[i]
                # vai aparecendo
                v.x = v2.x * tam
                v.y = v2.y * tam
                v.z = v2.z * tam
        
        # trocar as faces no meio
        if tam < 0.5:
            # usar faces do objeto1
            if len(self.objetoMorph.faces) != len(self.objeto1.faces):
                self.objetoMorph.faces = []
                for face in self.objeto1.faces:
                    nova_face = []
                    for idx in face:
                        nova_face.append(idx)
                    self.objetoMorph.faces.append(nova_face)
        else:
            # usar faces do objeto2
            if len(self.objetoMorph.faces) != len(self.objeto2.faces):
                self.objetoMorph.faces = []
                for face in self.objeto2.faces:
                    # verificar se os indices sao validos
                    face_ok = True
                    for idx in face:
                        if idx >= len(self.objetoMorph.vertices):
                            face_ok = False
                            break
                    
                    if face_ok:
                        nova_face = []
                        for idx in face:
                            nova_face.append(idx)
                        self.objetoMorph.faces.append(nova_face)
    
    def proximoFrame(self):
        if not self.executando:
            return False
            
        self.frame_atual = self.frame_atual + self.velocidade
        
        if self.frame_atual >= self.total_frames:
            self.frame_atual = self.total_frames
            self.executando = False
            self.atualizarMorph(1.0)
            return False
        
        # calcular o tam
        tam = self.frame_atual / self.total_frames
        self.atualizarMorph(tam)
        
        return True
        
    def iniciarMorphing(self):
        self.executando = True
        self.frame_atual = 0
        self.atualizarMorph(0.0)

    def pararMorphing(self):
        self.executando = False