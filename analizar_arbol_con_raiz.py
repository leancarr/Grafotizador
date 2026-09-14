import networkx as nx

def build_tree_t():
    # Árbol del Ejercicio 4
    edges = [
        # Nivel 0 -> 1
        ('a', 'b'), ('a', 'c'), ('a', 'd'), ('a', 'e'),
        # Nivel 1 -> 2
        ('b', 'f'),
        ('c', 'g'), ('c', 'h'), ('c', 'i'),
        ('d', 'j'),
        ('e', 'k'), ('e', 'l'),
        # Nivel 2 -> 3
        ('g', 'm'), ('g', 'n'),
        ('j', 'o'), ('j', 'p'),
        ('l', 'q'),
        # Nivel 3 -> 4
        ('q', 'r')
    ]
    
    # Grafo dirigido desde la raíz 'a'
    T = nx.DiGraph()
    T.add_edges_from(edges)
    return T

def analizar_arbol_t():
    T = build_tree_t()
    raiz = 'a'
    
    print("=" * 60)
    print("ANÁLISIS DEL ÁRBOL T CON GRAFOTIZADOR (EJERCICIO 4)")
    print("=" * 60)
    
    # a) Padre de c y h
    padre_c = list(T.predecessors('c'))[0]
    padre_h = list(T.predecessors('h'))[0]
    print(f"a) Padre de c: {padre_c}")
    print(f"   Padre de h: {padre_h}")
    
    # b) Ancestros de c y j (camino hacia la raíz, excluyendo el nodo)
    # nx.ancestors devuelve todos los ancestros
    ancestros_c = nx.ancestors(T, 'c')
    ancestros_j = nx.ancestors(T, 'j')
    print(f"b) Ancestros de c: {sorted(ancestros_c)}")
    print(f"   Ancestros de j: {sorted(ancestros_j)}")
    
    # c) Hijos de d y e
    hijos_d = list(T.successors('d'))
    hijos_e = list(T.successors('e'))
    print(f"c) Hijos de d: {sorted(hijos_d)}")
    print(f"   Hijos de e: {sorted(hijos_e)}")
    
    # d) Descendientes de c y e
    desc_c = nx.descendants(T, 'c')
    desc_e = nx.descendants(T, 'e')
    print(f"d) Descendientes de c: {sorted(desc_c)}")
    print(f"   Descendientes de e: {sorted(desc_e)}")
    
    # e) Hermanos de f y h
    def get_hermanos(nodo):
        padre = list(T.predecessors(nodo))[0] if list(T.predecessors(nodo)) else None
        if not padre: return []
        return [h for h in T.successors(padre) if h != nodo]
        
    print(f"e) Hermanos de f: {get_hermanos('f') if get_hermanos('f') else 'No tiene (hijo único)'}")
    print(f"   Hermanos de h: {sorted(get_hermanos('h'))}")
    
    # f) Vértices terminales (hojas: grado de salida 0)
    hojas = [n for n in T.nodes() if T.out_degree(n) == 0]
    print(f"f) Vértices terminales (hojas): {sorted(hojas)}")
    
    # g) Vértices internos (tienen al menos un hijo)
    internos = [n for n in T.nodes() if T.out_degree(n) > 0]
    print(f"g) Vértices internos: {sorted(internos)}")
    
    # h) Subárbol con raíz en j
    desc_j = nx.descendants(T, 'j')
    subarbol_j_nodos = ['j'] + list(desc_j)
    subarbol_j_aristas = list(T.subgraph(subarbol_j_nodos).edges())
    print(f"h) Subárbol con raíz en j:")
    print(f"   Vértices: {sorted(subarbol_j_nodos)}")
    print(f"   Aristas: {subarbol_j_aristas}")

if __name__ == "__main__":
    analizar_arbol_t()
