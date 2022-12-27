#import numpy as np
import networkx as nx

DEFAULT = 0
MULTIPARTITE = 50

class Vertice:
    def __init__(self, nome = "default", chave = -1, cor = 0):
        self.nome = nome
        self.chave = chave
        self.cor = cor


    def getNome(self):
        return self.nome

    def setNome(self, value):
        self.nome = value


    def getChave(self):
        return self.chave

    def setChave(self, value):
        self.chave = value


    def getCor(self):
        return self.cor

    def setCor(self, value):
        self.cor = value

class Grafo:
    def __init__(self, vetVertices = list(), grau = 0, matAdjacencia = list(), direcionado = False):
        self.vetVertices = vetVertices[:]
        self.grau = grau
        self.matAdjacencia = matAdjacencia[:]
        self.direcionado = direcionado

    def reset(self, direcionado):
        self.vetVertices = []
        self.grau = 0
        self.matAdjacencia = []
        self.direcionado = direcionado


    def nomeParaChave(self, nome):
        for it in self.vetVertices:
            if it.getNome() == nome:
                return it.getChave()

        return -1

    
    def chaveParaNome(self, chave):
        for it in self.vetVertices:
            if it.getChave() == chave:
                return it.getNome()

        return ""


    def codificaArco(self, origem, destino):
        res = [self.nomeParaChave(origem), self.nomeParaChave(destino)]

        if res[0] == -1 or res[1] == -1:
            return []
        
        return res


    def existeVertice(self, nome):
        return self.nomeParaChave(nome) != -1


    def adicionarVertice(self, nome):
        if self.existeVertice(nome):
            return False
        
        novoGrau = self.grau + 1
        novaMatAdjacencia = [[False]*novoGrau for i in range(novoGrau)]
        # novaMatAdjacencia = np.zeros((novoGrau, novoGrau), dtype = bool)

        for i in range(self.grau):
            for j in range(self.grau):
                novaMatAdjacencia[i][j] = self.matAdjacencia[i][j]

        vertice = Vertice(nome, novoGrau - 1)

        novoVetVertices = self.vetVertices
        novoVetVertices.append(vertice)

        self.grau = novoGrau
        self.vetVertices = novoVetVertices
        self.matAdjacencia = novaMatAdjacencia

        return True

    
    def adicionarArco(self, entrada):
        aux = entrada.split(",")

        origem = self.nomeParaChave( aux[0] )
        destino = self.nomeParaChave( aux[1] )

        if origem == -1 or destino == -1:
            return False

        self.matAdjacencia[origem][destino] = True
        if not self.direcionado:
            self.matAdjacencia[destino][origem] = True

        return True
    

    def removerVertice(self, nome):
        chave = self.nomeParaChave(nome)

        if chave == -1:
            return False

        novoGrau = self.grau - 1
        novaMatAdjacencia = self.matAdjacencia
        novoVetVertices = self.vetVertices

        novaMatAdjacencia.pop(chave)
        for it in novaMatAdjacencia:
            it.pop(chave)

        novoVetVertices.pop(chave)
        for i in range(chave, novoGrau):
            novoVetVertices[i].setChave(i)

        self.grau = novoGrau
        self.vetVertices = novoVetVertices
        self.matAdjacencia = novaMatAdjacencia

        return True


    def removerArco(self, entrada):
        aux = entrada.split(",")

        origem = aux[0]
        destino = aux[1]

        arco = self.codificaArco(origem, destino)

        if arco:
            self.matAdjacencia[ arco[0] ][ arco[1] ] = False
            if not self.direcionado:
                self.matAdjacencia[ arco[1] ][ arco[0] ] = False

            return True
        
        return False

    def fechoTransitivoDireto(self, vertice = ""):
        percorre = True
        visitados = [-1] * self.grau
        profundidade = 0
        nos = list()

        if not self.grau:
            return []

        atual = self.nomeParaChave(vertice)

        if atual == -1:
            atual = 0

        visitados[atual] = profundidade

        nos.append(atual)

        while percorre:
            atual = nos[0]

            profundidade = visitados[atual] + 1

            for i in range(self.grau):
                if self.matAdjacencia[atual][i] and visitados[i] < 0:
                    nos.append(i)

                    visitados[i] = profundidade
            
            nos.pop(0)

            if not nos:
                percorre = False
                
        return visitados

    def fechoTransitivoInverso(self, vertice = ""):
        percorre = True
        visitados = [-1] * self.grau
        profundidade = 0
        nos = list()

        if not self.grau:
            return []

        atual = self.nomeParaChave(vertice)

        if atual == -1:
            atual = 0

        visitados[atual] = profundidade

        nos.append(atual)

        while percorre:
            atual = nos[0]

            profundidade = visitados[atual] + 1

            for i in range(self.grau):
                if self.matAdjacencia[i][atual] and visitados[i] < 0:
                    nos.append(i)

                    visitados[i] = profundidade
            
            nos.pop(0)

            if not nos:
                percorre = False
                
        return visitados

    def isConexo(self):
        conexo = True
        percorre = True
        atual = 0
        grafo = list()
        subgrafos = list()

        bDireto = self.fechoTransitivoDireto()
        bInverso = self.fechoTransitivoInverso()

        for i in range(self.grau):
            conexo = conexo and bDireto[i] >= 0 and bInverso[i] >= 0

        if not conexo:
            interseccao = [False]*self.grau
            visitados = [False]*self.grau

            visitados[0] = True

            while percorre:
                if grafo:
                    grafo = list()

                bDireto = self.fechoTransitivoDireto(self.chaveParaNome(atual))
                bInverso = self.fechoTransitivoInverso(self.chaveParaNome(atual))

                for i in range(self.grau):
                    interseccao[i] = bDireto[i] >= 0 and bInverso[i] >= 0

                for i in range(self.grau):
                    if interseccao[i]:
                        grafo.append(self.chaveParaNome(i))

                        visitados[i] = True
                
                subgrafos.append(grafo)

                percorre = False

                for i in range(self.grau):
                    if not visitados[i]:
                        atual = i
                        percorre = True
                        i = self.grau

        return (conexo, subgrafos)



    def colorirGrafo(self, subgrafos = False):
        coresNum = [0]*self.grau
        # coresNum = np.zeros(self.grau, dtype = int)

        if not self.grau:
            return 0

        if subgrafos:
            conexo, subgrafos = self.isConexo()

            if conexo:
                for i in self.vetVertices:
                    i.setCor(1)
                for i in coresNum:
                    i.setCor(1)
            else:
                for i in range(len(subgrafos)):
                    for j in range(len(subgrafos[i])):
                        chave = self.nomeParaChave(subgrafos[i][j])

                        self.vetVertices[chave].setCor(i)
                        coresNum[chave] = i
        else:
            grauVertice = [0]*self.grau
            # grauVertice = list(np.zeros(self.grau, dtype = int))

            for i in range(self.grau):
                for j in range(self.grau):
                    grauVertice[i] += self.matAdjacencia[i][j]

            atual = grauVertice.index(max(grauVertice))
            coresNum[atual] = 1

            while not (min(coresNum)):
                grauSaturacao = [0]*self.grau
                # grauSaturacao = list(np.zeros(self.grau, dtype = int))
                difCoresLista = list()

                for i in range(self.grau):
                    difCoresLista.append( [] )

                    if not coresNum[i]:
                        for j in range(self.grau):
                            if self.matAdjacencia[i][j] and coresNum[j] and not coresNum[j] in difCoresLista[i]:
                                difCoresLista[i].append(coresNum[j])
                                grauSaturacao[i] += 1
                    else:
                        grauSaturacao[i] = -1

                atual = grauSaturacao.index(max(grauSaturacao))

                aux = range(1, self.grau)
                if not (set(aux) - set(difCoresLista[atual])):
                    coresNum[atual] = max(difCoresLista[atual]) + 1
                else:
                    coresNum[atual] = min(set(aux) - set(difCoresLista[atual]))

            for i in range(self.grau):
                self.vetVertices[i].setCor(coresNum[i])

        return max(coresNum)

    def getColorMap(self):
        colorMap = list()

        for it in self.vetVertices:
            colorMap.append(it.getCor())

        return colorMap

    def _DFSNumCiclos(self, visitados, profundidadeRestante, atual, alvo, ciclos):
        visitados[atual] = True

        if profundidadeRestante == 1:
            visitados[atual] = False

            ciclos += self.matAdjacencia[atual][alvo]
            return ciclos
        else:
            for i in range(self.grau):
                if self.matAdjacencia[atual][i] and not visitados[i]:
                    ciclos = self._DFSNumCiclos(visitados, profundidadeRestante - 1, i, alvo, ciclos)

        visitados[atual] = False

        return ciclos

    def numCiclos(self, tam): # conta ciclos de comprimento tam para grafo nao direcionado
        visitados = [False] * self.grau
        ciclos = 0

        for i in range(self.grau - (tam - 1)):
            ciclos = self._DFSNumCiclos(visitados, tam, i, i, ciclos)

            visitados[i] = True

        # divide por 2 pois todo ciclo pode ser percorrido por dois sentidos, logo contagem da o dobro do numero real de ciclos
        return ciclos/2

    def isPlanar(self):
        G = self.gerarNetworkx()

        planar, _ = nx.check_planarity(G)
        regioes = -1

        if planar:
            vertices = self.grau
            arestas = 0

            for i in range(vertices):
                for j in range(i, vertices):
                    arestas += self.matAdjacencia[i][j]

            regioes = arestas - vertices + 2
        
        return (planar, regioes)

    def _get_layer(self, key):
        check = False
        nos_anterior = []

        for i in range(self.grau):
            arco = self.matAdjacencia[i][key]
            check = check or arco
            if arco:
                nos_anterior.append(i)

        if not check:
            return 0
        else:
            layers_anterior = []

            for i in nos_anterior:
                layers_anterior.append(self._get_layer(i))

            return max(layers_anterior) + 1


    def gerarNetworkx(self, layout = DEFAULT):
        if self.direcionado:
            G = nx.DiGraph()
        else:
            G = nx.Graph()

        if layout == DEFAULT:
            for i in range(self.grau):
                G.add_node(self.chaveParaNome(i))

            for i in range(self.grau):
                for j in range(self.grau):
                    if self.matAdjacencia[i][j]:
                        G.add_edge(self.chaveParaNome(i), self.chaveParaNome(j))
        elif layout == MULTIPARTITE:
            for i in range(self.grau):
                G.add_node(self.chaveParaNome(i), layer = self._get_layer(i))

            for i in range(self.grau):
                for j in range(self.grau):
                    if self.matAdjacencia[i][j]:
                        G.add_edge(self.chaveParaNome(i), self.chaveParaNome(j))

        return G
