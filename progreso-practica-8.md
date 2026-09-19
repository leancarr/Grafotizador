---
tags: [teoria-de-grafos, practica-8, seguimiento, arboles]
date: 2026-09-18
---
# 📍 Estado de Avance: Práctica 8 - Introducción a Árboles (IPS - UNR)

**Última actualización:** 18 de Septiembre de 2026

## 📌 ¿En qué ejercicio nos quedamos?
* **Último ejercicio completado:** **Ejercicio 6** (Contraejemplo de grafo no dirigido simple donde $|V| = |E| + 1$ pero no es árbol: triángulo $K_3$ + vértice aislado $K_1$).
* **Próximo ejercicio a resolver:** **Ejercicio 7** (Cálculo de vértices colgantes / hojas con Handshaking).

---

## 📋 Resumen de Ejercicios Resueltos:
* **Ejercicio 1:** Análisis topológico de árboles ($G_1, G_2, G_3, G_4$). Implementado y validado con `analizar_arboles.py` en Grafotizador.
  * $G_1$: Árbol (conexo y acíclico).
  * $G_2$: Árbol (estrella de 5 vértices, conexo y acíclico).
  * $G_3$: No es árbol (cíclico, contiene un ciclo $K_3$).
  * $G_4$: No es árbol (desconexo, bosque de 2 árboles).
* **Ejercicio 2:** Árbol con raíz en $k$. Niveles de cada vértice (0 a 4) y altura del árbol ($h = 4$, alcanzada en $h$).
* **Ejercicio 3:** (Pendiente dibujar con raíz en $d$, aunque se analizó la estructura).
* **Ejercicio 4:** Árbol con raíz en $a$. Relaciones genealógicas completas (padres, ancestros, hijos, descendientes, hermanos, terminales/hojas, internos y subárbol de $j$). Implementado en `analizar_arbol_con_raiz.py`.
* **Ejercicio 5:** Los 6 árboles no isomorfos con $n=6$ vértices clasificados por diámetro (5, 4, 3, 2). Demostración de por qué el Árbol 2 y el Árbol 3 no son isomorfos (distribución de grados de los vecinos del nodo de grado 3: $\{1, 1, 2\}$ vs $\{1, 2, 2\}$).
* **Ejercicio 6:** Contraejemplo de grafo simple con $|V| = |E| + 1$ que no es árbol ($K_3 \cup K_1$).

---

## 🎯 Próximos Ejercicios Pendientes:
* **Ejercicio 7:** Si un árbol tiene 4 vértices de grado 2, 1 de grado 3, 2 de grado 4, 1 de grado 5. ¿Cuántos vértices colgantes (hojas) tiene?
* **Ejercicio 8:** Generalización con $v_2, v_3, \dots, v_m$.
* **Ejercicio 9:** Probar que todos los árboles son planares.
* **Ejercicio 10:** Grafo conexo con 30 aristas, máximo $|V|$.
* **Ejercicio 11 a 15:** Bosques y árboles recubridores ($K_{2,3}$, $\kappa(G)$).
