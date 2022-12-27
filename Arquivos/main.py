from matplotlib import scale
#from eightpuzzle import get_steps, show_board, solve, START, FINISH
#from grafo import Grafo
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import PySimpleGUI as sg
from PySimpleGUI.PySimpleGUI import WIN_CLOSED
from grafo import MULTIPARTITE

from pertcpm import build_pertcpm_graph, critical_duration

"""
    Embedding the Matplotlib toolbar into your application
"""

def main():
    # ------------------------------- This is to include a matplotlib figure in a Tkinter canvas
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

    def draw_figure(canvas, fig):
        if canvas.children:
            for child in canvas.winfo_children():
                child.destroy()
        figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack(side='right', fill='both', expand=1)


    # class Toolbar(NavigationToolbar2Tk):
    #     def __init__(self, *args, **kwargs):
    #         super(Toolbar, self).__init__(*args, **kwargs)


    # ------------------------------- PySimpleGUI CODE
    sg.theme('LightGrey')

    esquerda=[
        [sg.T('Trabalho realizado pelos acadêmicos: André, Bruno e Eduardo')],
        [sg.T('Nome:')],
        [sg.I(key = 'nome')],
        [sg.T('Duração:')],
        [sg.I(key = 'duracao')],
        [sg.T('Precedente(s):'), sg.T('\t(separar com espaços)')],
        [sg.I(key = 'precedente')],
        [sg.B('Adicionar Tarefa', key='adicionar'), sg.B('Sair')],
    ]

    table_data = [ 
        # ['A', 15, ''], 
        # ['B', 10, 'A'], 
        # ['C', 20, 'A'] 
    ]

    input_keys = ['nome', 'duracao', 'precedente']

    direita=[
        [sg.Table(values=table_data, headings=['Nome', 'Duracao', 'Precedente'], auto_size_columns=False, col_widths=[20, 7, 20],background_color='#DAE0E6',justification = 'center',key='table')],
        [sg.B('Montar Grafo', key='montar'), sg.B('Apagar tabela', key='apagar')],
    ]

    grafico = [
        [sg.Canvas(key='fig_cv',
                    # it's important that you set this size
                    size=(400, 400)
                    )]
    ]

    layout=[
        [
            sg.Column(esquerda),
            sg.VSeparator(),
            sg.Column(direita),
            sg.Column(layout=grafico, background_color='#DAE0E6', pad=(0, 0))
        ]
    ]

    sg.theme('LightGrey')

    window = sg.Window('Caminho Crítico', layout)

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Sair'):  # always,  always give a way out!
            break
        elif event == 'adicionar':
            if((values['nome'] == '') or values['duracao'] == ''):
                #n faz nada
                pass
            else:
                try:
                    nome = str(values['nome']).upper()
                    duracao = int(values['duracao'])
                    precedente = str(values['precedente']).upper().split()

                    values['nome']
                    values['duracao']
                    values['precedente']

                    table_data.append( [nome, duracao, precedente] )

                    window.Element('table').Update(values=table_data)
                except ValueError:
                    print(f'Exceção: Valor inserido inválido.')

                for key in input_keys:
                    window[key]('') # limpa campos de entrada
        elif event == 'apagar':
            del table_data
            table_data = []
            window.Element('table').Update(values=table_data)
        elif event == 'montar':
            task_dict = {
                'name': None, 
                'duration': None, 
                'precedent': None
            }

            task_table = []

            for task in table_data:
                task_table.append(task_dict.copy())

                task_table[-1]['name'] = task[0]
                task_table[-1]['duration'] = task[1]
                task_table[-1]['precedent'] = task[2] if len(task[2]) else [None]

            if task_table:
                plt.close()

                grafo, attrs = build_pertcpm_graph(task_table)

                G = grafo.gerarNetworkx(MULTIPARTITE)
                pos = nx.multipartite_layout(G, subset_key='layer')
                nx.draw(G, pos, with_labels = True, node_size = 500, node_color = grafo.getColorMap(), cmap=plt.cm.Set2)

                high_y = 0

                for key, item in pos.items():
                    x, y = item
                    print(x, y)

                    if key == 'finish':
                        i = grafo.grau - 1
                    elif key == 'start':
                        i = grafo.grau - 2
                    else:
                        for aux, attr in enumerate(attrs):
                            if aux < len(attrs) - 1:
                                if attr['name'] == key:
                                    i = aux

                    if i != grafo.grau - 2:
                        x, y = item

                        if abs(y) > high_y:
                            high_y = abs(y)

                        x_off = 0.1

                        if i < grafo.grau - 2:
                            early_start = attrs[i]['early_start']
                            early_finish = attrs[i]['early_finish']
                            late_start = attrs[i]['late_start']
                            late_finish = attrs[i]['late_finish']

                            slack = attrs[i]['slack']

                            # plt.text(x - x_off, -y, s=f'Início cedo: {early_start}\nFim cedo: {early_finish}\n\n', horizontalalignment='right', verticalalignment='center', size=7)
                            # plt.text(x + x_off, -y, s=f'Início tarde: {late_start}\nFim tarde: {late_finish}\nFolga: {slack}\n', horizontalalignment='left', verticalalignment='center', size=7)
                            plt.text(x + x_off, y, s=f'Início cedo: {early_start}\nFim cedo: {early_finish}\nInício tarde: {late_start}\nFim tarde: {late_finish}\nFolga: {slack}\n', horizontalalignment='left', verticalalignment='center', size=7)
                        else:
                            y_off = high_y/2 if high_y > 0 else 0.001
                            plt.text(x, y - y_off, s=f'Tempo máximo: {attrs[-1]}', horizontalalignment='right', verticalalignment='center', size=7)

                fig = plt.gcf()
                draw_figure(window['fig_cv'].TKCanvas, fig)
            #break
            

    window.close()


if __name__ == '__main__':
    main()