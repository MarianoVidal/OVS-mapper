import pandas as pd
from rdflib import BNode, Graph, URIRef
from csv2pronto.src.converter import create_graph
import unittest

# CONSTANTES
RUTA_INPUT_AVE = './input/input_Ave.csv'
RUTA_OUTPUT_AVE_1 = './output/out_ave_1.ttl'
RUTA_ONTOLOGIA_PRONTO = '../ontology/pronto.owl'

class TestConverterScraper(unittest.TestCase):
    # Función que crea un grafo a partir de un archivo que esté en /input
    def crear_grafo_desde_archivo(ruta_archivo: str, ontology: str) -> Graph:
        # Abrir archivo
        with open(ruta_archivo, "r", encoding="utf-8") as archivo_csv:
            graph: Graph = Graph()
            graph.parse(args.ontology)
            # Máximo de filas leidas por trozo
            chunksize = 3000

            for idx, row in enumerate(pd.read_csv(csv_file, chunksize=chunksize, iterator=True, dialect='excel', delimiter=",", keep_default_na=False, dtype=str)):
                crear_grafo_de_trozo(row, graph, idx, args.destination)

    # Función que es una copia de la que está en converter.py, salvo que
    # no serializa el grafo
    def crear_grafo_de_trozo(df: pd.DataFrame, graph, idx) -> Graph:
        for i in range(len(df)):
            graph += create_graph(df.iloc[i].to_dict())

    # Si recibe un input concreto, debería retornar el mismo output
    # que recibió en otra ocasión
    def test_create_graph_from_chunk_con_input_correcto(self):

        # Crear y cargar grafo esperado
        expected_graph: Graph = Graph()
        expected_graph.parse(RUTA_OUTPUT_AVE_1)

        # Crear y cargar grafo actual
        actual_graph = crear_grafo_de_archivo(RUTA_INPUT_AVE, RUTA_ONTOLOGIA_PRONTO)

        # Comparar ambos grafos de manera isomórfica
        # osea, ignorando el orden y los nodos en blanco
        print(f"Comparando {RUTA_INPUT_AVE} y {RUTA_OUTPUT_AVE_1}")
        self.assertTrue(isomorphic(actual_graph, expected_graph))