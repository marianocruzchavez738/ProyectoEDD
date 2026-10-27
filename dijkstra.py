import heapq

CRITERIOS = ["distancia", "tiempo", "precio", "seguridad"]

UNIDADES = {
    "distancia": "km",
    "tiempo": "min",
    "precio": "soles",
    "seguridad": "de riesgo acumulado",
}


def dijkstra(grafo, origen, criterio):
    # Paso 1: tablas de costos y de nodos previos
    costo = {}
    previo = {}
    for lugar in grafo.adyacencia:
        costo[lugar] = float("inf")
        previo[lugar] = None

    costo[origen] = 0

    # Paso 2: cola de prioridad con (costo, lugar)
    cola = [(0, origen)]

    # Paso 3: se extrae siempre el lugar de menor costo pendiente
    while len(cola) > 0:
        c, u = heapq.heappop(cola)

        # Entrada vieja: ya se encontro un costo mejor para u
        if c > costo[u]:
            continue

        # Paso 4: se relajan las conexiones de u (lista de adyacencia)
        for conexion in grafo.obtener_vecinos(u):
            v = conexion.destino
            nuevo = costo[u] + conexion.obtener_peso(criterio)

            if nuevo < costo[v]:
                costo[v] = nuevo
                previo[v] = u
                heapq.heappush(cola, (nuevo, v))

    return costo, previo


def reconstruir_camino(previo, origen, destino):
    # Se apila desde el destino hacia el origen siguiendo los nodos previos
    pila = []
    actual = destino
    while actual is not None:
        pila.append(actual)
        actual = previo[actual]

    # Si no se llego al origen, no hay camino
    if pila[-1] != origen:
        return None

    # Se desapila para obtener el recorrido en orden origen -> destino
    camino = []
    while len(pila) > 0:
        camino.append(pila.pop())

    return camino


def ruta_simple(grafo, origen, destino, criterio):
    # Funcionalidad 1: validaciones (RN07, RN08)
    if criterio not in CRITERIOS:
        return {"ok": False, "mensaje": "Criterio no valido."}

    if not grafo.existe_lugar(origen):
        return {"ok": False, "mensaje": "El origen no existe en el mapa."}

    if not grafo.existe_lugar(destino):
        return {"ok": False, "mensaje": "El destino no existe en el mapa."}

    if origen == destino:
        return {"ok": False, "mensaje": "El destino no puede ser igual al origen."}

    costo, previo = dijkstra(grafo, origen, criterio)

    # RN14: si no hay camino se informa y no se genera la ruta
    if costo[destino] == float("inf"):
        return {"ok": False, "mensaje": "No existe camino entre " + origen + " y " + destino + "."}

    camino = reconstruir_camino(previo, origen, destino)

    return {
        "ok": True,
        "camino": camino,
        "costo": costo[destino],
        "criterio": criterio,
        "mensaje": "",
    }


def mostrar_ruta(resultado):
    if not resultado["ok"]:
        print(resultado["mensaje"])
        return

    print("Ruta:", " -> ".join(resultado["camino"]))
    print("Costo total:", resultado["costo"], UNIDADES[resultado["criterio"]])
