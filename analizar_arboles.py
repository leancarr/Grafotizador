import cv2
import numpy as np
import networkx as nx

def analizar_grafo_imagen(image_path, name="Grafo"):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"No se pudo cargar la imagen: {image_path}")
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
    
    # 1. Componentes conexas en el dibujo
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh)
    valid_components = [i for i in range(1, num_labels) if stats[i, cv2.CC_STAT_AREA] > 15]
    componentes = len(valid_components)
    es_conexo = (componentes == 1)
    
    # 2. Detección de ciclos (caras internas / agujeros topológicos)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    ciclos = 0
    if hierarchy is not None:
        for i, h in enumerate(hierarchy[0]):
            if h[3] != -1:  # hueco encerrado por líneas
                if cv2.contourArea(contours[i]) > 15:
                    ciclos += 1
    es_aciclico = (ciclos == 0)
    
    # 3. Veredicto
    es_arbol = es_conexo and es_aciclico
    
    diagnostico = {
        "nombre": name,
        "componentes": componentes,
        "es_conexo": es_conexo,
        "ciclos_detectados": ciclos,
        "es_aciclico": es_aciclico,
        "es_arbol": es_arbol
    }
    return diagnostico

if __name__ == "__main__":
    grafos = ["G1", "G2", "G3", "G4"]
    print("=" * 60)
    print("ANÁLISIS DE ÁRBOLES CON GRAFOTIZADOR (EJERCICIO 1)")
    print("=" * 60)
    for g in grafos:
        res = analizar_grafo_imagen(f"{g}.png", g)
        print(f"\nGrafo {res['nombre']}:")
        print(f"  • Componentes conexas (k): {res['componentes']} -> {'Conexo' if res['es_conexo'] else 'NO conexo'}")
        print(f"  • Ciclos detectados: {res['ciclos_detectados']} -> {'Acíclico' if res['es_aciclico'] else 'CÍCLICO (tiene ciclos)'}")
        print(f"  • ¿Es un árbol?: {'✅ SÍ ES UN ÁRBOL' if res['es_arbol'] else '❌ NO ES UN ÁRBOL'}")
