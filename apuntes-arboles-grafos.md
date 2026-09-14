---
tags: [teoria-de-grafos, arboles, matematicas, apuntes, ips-unr]
date: 2026-09-14
---
# 🌲 Apuntes Maestros: Introducción a Árboles (Teoría de Grafos)
**Materia:** Teoría de Grafos y Algoritmos (IPS - UNR)  
**Tema:** Práctica 8 - Árboles, Árboles con Raíz, Grados, Bosques y Árboles Recubridores

---

## 1. ¿Qué es un Árbol? (Definiciones Equivalentes)
Un grafo no dirigido $T = (V, E)$ es un **árbol** si y solo si cumple cualquiera de las siguientes condiciones equivalentes:
1. $T$ es **conexo y acíclico** (sin ciclos simples).
2. Entre cualquier par de vértices existe un **único camino simple**.
3. $T$ es **conexo** y tiene exactamente **$|E| = |V| - 1$** aristas.
4. $T$ es **acíclico** y tiene exactamente **$|E| = |V| - 1$** aristas.
5. $T$ es acíclico, pero si agregás cualquier arista nueva, se forma exactamente un ciclo.
6. $T$ es conexo, pero si sacás cualquier arista (puente), deja de ser conexo.

> ⚠️ **Trampa clásica de examen:** Que se cumpla $|V| = |E| + 1$ **NO alcanza** para asegurar que sea un árbol si el grafo no es conexo. Ejemplo: Un triángulo ($K_3$) más un vértice aislado ($K_1$) tiene $|V|=4$ y $|E|=3$, pero no es un árbol porque tiene un ciclo y no es conexo.

---

## 2. Bosques (Colección de Árboles)
Un **bosque** $F = (V, E)$ es un grafo acíclico (cuyas componentes conexas son árboles).
* Si el bosque tiene $k$ árboles (componentes conexas):
  $$|V| = |E| + k \iff |E| = |V| - k \iff k = |V| - |E|$$
* Si $k = 1$, el bosque es un árbol conexo ($|V| = |E| + 1$).

---

## 3. Grados, Vértices Colgantes (Hojas) y Handshaking
* **Vértice colgante (hoja / terminal):** Aquel con $\text{grado}(v) = 1$.
* **Vértice interno:** Aquel con $\text{grado}(v) \ge 2$ (o en árboles con raíz, no hoja y no raíz si tiene hijos).
* **Fórmula de oro:** Combinar el Lema del Apretón de Manos con la fórmula del árbol:
  $$\sum_{v \in V} \text{gr}(v) = 2|E| = 2(|V| - 1)$$
* **Despeje de hojas ($x$):**
  Si te dan la cantidad de vértices de cada grado $\ge 2$:
  $$x \cdot 1 + \sum_{i \ge 2} i \cdot v_i = 2 \left( x + \sum_{i \ge 2} v_i - 1 \right)$$
  De acá siempre despejás directamente la cantidad de hojas $x$.

---

## 4. Árboles con Raíz (Jerarquías Familiares)
Al fijar un vértice como **raíz** ($r$):
* **Nivel de un vértice $v$:** Longitud del único camino simple desde la raíz $r$ hasta $v$. ($\text{nivel}(r) = 0$).
* **Altura del árbol ($h$):** El nivel máximo alcanzado por cualquier vértice del árbol.
* **Padre de $v$:** El vértice adyacente a $v$ que está en el nivel anterior ($\text{nivel}(v) - 1$).
* **Hijo de $u$:** Vértice adyacente a $u$ en el nivel posterior ($\text{nivel}(u) + 1$).
* **Ancestros de $v$:** Todos los vértices en el camino desde $v$ hasta la raíz (excluyendo o incluyendo a $v$ según convención; si es propio, excluye a $v$).
* **Descendientes de $u$:** Todos los vértices que tienen a $u$ como ancestro.
* **Hermanos:** Vértices distintos que comparten el mismo padre.
* **Subárbol con raíz en $v$:** El subgrafo inducido formado por $v$ y todos sus descendientes.

---

## 5. Árboles Recubridores (Spanning Trees)
* Un **árbol recubridor** de un grafo conexo $G = (V, E)$ es un subgrafo que contiene a **todos los vértices de $V$** y es un árbol.
* Para obtenerlo, se van eliminando aristas de los ciclos hasta que no queden ciclos, manteniendo la conexidad.
* Si el grafo tiene $k$ componentes, se busca un **bosque recubridor**.
* El número de aristas de cualquier árbol recubridor de $G$ es siempre $|V| - 1$.
* Las aristas que pertenecen al árbol se llaman **ramas**, y las que sobran se llaman **cuerdas**.

---

## 6. Planaridad de los Árboles
* **Todo árbol es un grafo planar.**
* Justificación rápida:
  1. No tiene ciclos, por lo que no puede contener ningún subgrafo homeomorfo a $K_5$ ni a $K_{3,3}$ (Teorema de Kuratowski).
  2. Fórmula de Euler: Como no encierra ciclos, tiene una única región (la cara exterior infinita, $F = 1$). Reemplazando:
     $$V - E + F = V - (V - 1) + 1 = 2 \quad \text{(se cumple idénticamente)}$$
