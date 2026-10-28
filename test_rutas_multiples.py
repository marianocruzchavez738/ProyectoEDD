# Pruebas de las funcionalidades 2 y 3.
# Como grafo.py no esta en el repositorio, se usa un grafo de prueba con la misma
# interfaz que usa dijkstra.py: adyacencia, obtener_vecinos(), existe_lugar() y
# conexion.destino / conexion.obtener_peso(criterio).
# Para probar con el grafo real: reemplazar GrafoPrueba por la clase de grafo.py.
import itertools
import random

from dijkstra import CRITERIOS
from rutas_multiples import (ruta_varios_destinos, ruta_personalizada, unir_tramos,
                             MAX_DESTINOS)

INF = float("inf")


class Conexion:
    def __init__(self, destino, pesos):
        self.destino = destino
        self.pesos = pesos

    def obtener_peso(self, criterio):
        return self.pesos[criterio]


class GrafoPrueba:
    def __init__(self):
        self.adyacencia = {}

    def agregar_lugar(self, nombre):
        self.adyacencia.setdefault(nombre, [])

    def agregar_conexion(self, a, b, pesos):
        self.adyacencia[a].append(Conexion(b, pesos))
        self.adyacencia[b].append(Conexion(a, pesos))  # bidireccional

    def obtener_vecinos(self, lugar):
        return self.adyacencia[lugar]

    def existe_lugar(self, lugar):
        return lugar in self.adyacencia


def grafo_aleatorio(n, p, semilla):
    rnd = random.Random(semilla)
    g = GrafoPrueba()
    nombres = ["L" + str(i) for i in range(n)]
    for nombre in nombres:
        g.agregar_lugar(nombre)
    for a, b in itertools.combinations(nombres, 2):
        if rnd.random() < p:
            g.agregar_conexion(a, b, {
                "distancia": rnd.randint(1, 20), "tiempo": rnd.randint(1, 60),
                "precio": rnd.randint(1, 15), "seguridad": rnd.randint(1, 5)})
    return g, nombres


def floyd(g, criterio):
    # Referencia independiente de Dijkstra: costos minimos entre todos los pares
    d = {a: {b: (0 if a == b else INF) for b in g.adyacencia} for a in g.adyacencia}
    for a in g.adyacencia:
        for c in g.obtener_vecinos(a):
            d[a][c.destino] = min(d[a][c.destino], c.obtener_peso(criterio))
    for k in d:
        for i in d:
            for j in d:
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
    return d


def costo_camino(g, camino, criterio):
    # Suma los pesos reales de las aristas del camino (verifica que existan)
    total = 0
    for a, b in zip(camino, camino[1:]):
        pesos = [c.obtener_peso(criterio) for c in g.obtener_vecinos(a) if c.destino == b]
        assert pesos, "arista inexistente " + a + "-" + b
        total += min(pesos)
    return total


def probar_aleatorios():
    rnd = random.Random(7)
    casos = 0
    sin_camino = 0
    for semilla in range(60):
        g, nombres = grafo_aleatorio(rnd.randint(6, 12), rnd.choice([0.25, 0.4, 0.7]), semilla)
        for criterio in CRITERIOS:
            ref = floyd(g, criterio)
            k = rnd.randint(2, 5)
            elegidos = rnd.sample(nombres, k + 1)
            origen, destinos = elegidos[0], elegidos[1:]

            # Funcionalidad 2 contra busqueda exhaustiva
            mejor = INF
            for orden in itertools.permutations(destinos):
                c, act = 0, origen
                for s in orden:
                    c += ref[act][s]
                    act = s
                mejor = min(mejor, c)
            r = ruta_varios_destinos(g, origen, destinos, criterio)
            if mejor == INF:
                assert not r["ok"]
                sin_camino += 1
            else:
                assert r["ok"] and r["costo"] == mejor, (semilla, criterio)
                assert costo_camino(g, r["camino"], criterio) == mejor
                assert r["camino"][0] == origen and r["camino"][-1] == r["orden"][-1]
                assert sorted(r["orden"]) == sorted(destinos)
            casos += 1

            # Funcionalidad 3 contra la suma de costos minimos del orden dado
            orden = destinos[:]
            rnd.shuffle(orden)
            puntos = [origen] + orden
            esperado = sum(ref[a][b] for a, b in zip(puntos, puntos[1:]))
            r = ruta_personalizada(g, origen, orden, criterio)
            if esperado == INF:
                assert not r["ok"] and r["mensaje"].startswith("No existe camino")
                sin_camino += 1
            else:
                assert r["ok"] and r["costo"] == esperado, (semilla, criterio)
                assert costo_camino(g, r["camino"], criterio) == esperado
                assert r["camino"][0] == origen and r["camino"][-1] == orden[-1]
                for lugar in orden:
                    assert lugar in r["camino"]
            casos += 1
    return casos, sin_camino


def probar_invalidos():
    g = GrafoPrueba()
    for x in "ABCDE":
        g.agregar_lugar(x)
    p = {"distancia": 1, "tiempo": 1, "precio": 1, "seguridad": 1}
    g.agregar_conexion("A", "B", p)
    g.agregar_conexion("B", "C", p)  # D y E quedan aislados (D-E conectados entre si)
    g.agregar_conexion("D", "E", p)

    casos = [
        (ruta_varios_destinos, ("A", ["B", "C"], "peso"), "Criterio no valido."),
        (ruta_varios_destinos, ("Z", ["B", "C"], "distancia"), "El origen no existe en el mapa."),
        (ruta_varios_destinos, ("A", ["B", "Z"], "distancia"), "El destino Z no existe en el mapa."),
        (ruta_varios_destinos, ("A", [], "distancia"), "Debe indicar al menos un destino."),
        (ruta_varios_destinos, ("A", ["B"], "distancia"), "Debe indicar al menos dos destinos."),
        (ruta_varios_destinos, ("A", ["B", "B"], "distancia"), "Los destinos no pueden repetirse."),
        (ruta_varios_destinos, ("A", ["A", "B"], "distancia"), "El origen no puede estar entre los destinos."),
        (ruta_varios_destinos, ("A", ["B", "D"], "distancia"), "No existe un recorrido que conecte todos los destinos."),
        (ruta_personalizada, ("A", [], "distancia"), "Debe indicar al menos un destino."),
        (ruta_personalizada, ("A", ["A", "B"], "distancia"), "Dos lugares consecutivos no pueden ser iguales: A."),
        (ruta_personalizada, ("A", ["B", "B"], "distancia"), "Dos lugares consecutivos no pueden ser iguales: B."),
        (ruta_personalizada, ("A", ["B", "D"], "distancia"), "No existe camino entre B y D."),
        (ruta_personalizada, ("A", ["Z"], "distancia"), "El destino Z no existe en el mapa."),
    ]
    for funcion, args, mensaje in casos:
        r = funcion(g, *args)
        assert not r["ok"] and r["mensaje"] == mensaje, (funcion.__name__, args, r)

    # Limite de destinos
    grande = GrafoPrueba()
    nombres = ["N" + str(i) for i in range(MAX_DESTINOS + 2)]
    for n in nombres:
        grande.agregar_lugar(n)
    r = ruta_varios_destinos(grande, nombres[0], nombres[1:], "distancia")
    assert not r["ok"] and "maximo" in r["mensaje"]

    # Un lugar puede repetirse si no es consecutivo (A-B-A es valido)
    r = ruta_personalizada(g, "A", ["B", "A"], "distancia")
    assert r["ok"] and r["camino"] == ["A", "B", "A"] and r["costo"] == 2

    # Union de tramos sin repetir el lugar de union
    assert unir_tramos([["A", "B"], ["B", "C", "D"], ["D", "E"]]) == ["A", "B", "C", "D", "E"]
    return len(casos) + 3


if __name__ == "__main__":
    n_inv = probar_invalidos()
    print("Casos invalidos y especiales correctos:", n_inv)
    n, sin = probar_aleatorios()
    print("Casos aleatorios contra busqueda exhaustiva correctos:", n, "(de ellos sin camino:", str(sin) + ")")
    print("TODO OK")
