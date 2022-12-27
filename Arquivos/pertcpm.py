import networkx as nx
import grafo as Grafo

START = 50
LOOSE_PATH = 100
CRITICAL_PATH = 0
FINISH = 20

critical_duration = 0

def set_early_attrs_recursive(task_attrs, index, graph):
    node = []
    for i in range(graph.grau):
        node.append(graph.matAdjacencia[i][index])

    if node[-2]: # se tarefa vier do inicio
        task_attrs[index]['early_start'] = 0
    else:
        precedent_early_finish = []

        for i, task in enumerate(task_attrs):
            if node[i]:
                if task['early_finish'] == None:
                    set_early_attrs_recursive(task_attrs, i, graph)

                precedent_early_finish.append(task['early_finish'])

        task_attrs[index]['early_start'] = max(precedent_early_finish)

    task_attrs[index]['early_finish'] = task_attrs[index]['early_start'] + task_attrs[index]['duration']

def set_early_attrs(task_attrs, graph):
    for i, task in enumerate(task_attrs):
        if task['early_start'] == None:
            set_early_attrs_recursive(task_attrs, i, graph)

def set_late_attrs_recursive(task_attrs, index, graph):
    node = graph.matAdjacencia[index]

    if node[-1]: # se tarefa levar ao fim
        task_attrs[index]['late_finish'] = critical_duration
    else:
        successor_late_start = []

        for i, task in enumerate(task_attrs):
            if node[i]:
                if task['late_start'] == None:
                    set_late_attrs_recursive(task_attrs, i, graph)

                successor_late_start.append(task['late_start'])

        task_attrs[index]['late_finish'] = min(successor_late_start)

    task_attrs[index]['late_start'] = task_attrs[index]['late_finish'] - task_attrs[index]['duration']

def set_late_attrs(task_attrs, graph):
    for i, task in enumerate(task_attrs):
        if task['late_finish'] == None:
            set_late_attrs_recursive(task_attrs, i, graph)

def build_pertcpm_graph(task_table):
    global critical_duration

    critical_duration = 0

    graph = Grafo.Grafo(direcionado=True)

    attr_dict = {
        'name': None, 
        'duration': None, 
        'precedent': None, 
        'early_start': None, 
        'early_finish': None, 
        'late_start': None, 
        'late_finish': None, 
        'slack': None
    }

    task_attrs = []

    for task in task_table:
        if graph.adicionarVertice(task['name']):
            task_attrs.append(attr_dict.copy())

            task_attrs[-1]['name'] = task['name']
            task_attrs[-1]['duration'] = task['duration']
            task_attrs[-1]['precedent'] = task['precedent']

    graph.adicionarVertice('start')
    graph.adicionarVertice('finish')

    for attrs in task_attrs:
        for precendent in attrs['precedent']:
            if precendent != None:
                graph.adicionarArco(str(precendent) + ',' + str(attrs['name']))
            else:
                graph.adicionarArco('start' + ',' + str(attrs['name']))

    set_early_attrs(task_attrs, graph)
    
    for i in range(graph.grau):
        check = False

        for j in range(graph.grau):
            check = check or graph.matAdjacencia[i][j]

        if not check and graph.chaveParaNome(i) != 'finish':
            if task_attrs[i]['early_finish'] > critical_duration:
                critical_duration = task_attrs[i]['early_finish']

            graph.adicionarArco(graph.chaveParaNome(i) + ',' + 'finish')

    set_late_attrs(task_attrs, graph)

    for attrs in task_attrs:
        attrs['slack'] = attrs['late_finish'] - attrs['early_finish']

    for i in range(len(task_attrs)):
        graph.vetVertices[i].setCor(CRITICAL_PATH if not task_attrs[i]['slack'] else LOOSE_PATH)

    graph.vetVertices[-1].setCor(FINISH)
    graph.vetVertices[-2].setCor(START)

    task_attrs.append(critical_duration)

    return graph, task_attrs

    

# def test():
#     task_dict = {
#         'name': None, 
#         'duration': None, 
#         'precedent': None
#     }

#     task_table = []

#     for i in range(3):
#         task_table.append(task_dict.copy())

#         task_table[-1]['name'] = str(i)
#         task_table[-1]['duration'] = 3*(i + 1) - i
#         task_table[-1]['precedent'] = [ str(i - 1) if i > 0 else None ]

#     task_table.append(task_dict.copy())

#     task_table[-1]['name'] = 'batata'
#     task_table[-1]['duration'] = 10
#     task_table[-1]['precedent'] = [ None ]

#     task_table.append(task_dict.copy())

#     task_table[-1]['name'] = 'frita'
#     task_table[-1]['duration'] = 25
#     task_table[-1]['precedent'] = [ '0', 'batata' ]

#     build_pertcpm_graph(task_table)