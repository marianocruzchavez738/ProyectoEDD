from itertools import permutations

from dijkstra import dijkstra, reconstruir_camino, CRITERIOS, UNIDADES

# Con n destinos hay n! ordenes posibles (8! = 40 320), por eso se limita la cantidad
MAX_DESTINOS = 8

INF = float("inf")


def validar_entrada(grafo, origen, destinos, criterio):
    # Validaciones comunes a las funcionalidades 2 y 3 (devuelve mensaje o None)
    if criterio not in CRITERIOS:
        return "Criterio no valido."

    if not grafo.existe_lugar(origen):
        return "El origen no existe en el mapa."

    if len(destinos) == 0:
        return "Debe indicar al menos un destino."

    if len(destinos) > MAX_DESTINOS:
        return "Se permiten como maximo " + str(MAX_DESTINOS) + " destinos."

    for destino in destinos:
        if not grafo.existe_lugar(destino):
            return "El destino " + destino + " no existe en el mapa."

    return None


def unir_tramos(tramos):
    # Une los tramos en un solo recorrido sin repetir el lugar de union:
    # el ultimo lugar de un tramo es el primero del siguiente
    recorrido = list(tramos[0])
    for tramo in tramos[1:]:
        recorrido.extend(tramo[1:])
    return recorrido


def ruta_varios_destinos(grafo, origen, destinos, criterio):
    # Funcionalidad 2: la aplicacion calcula el mejor orden de visita.
    # El recorrido termina en el ultimo destino, sin regresar al origen.
    error = validar_entrada(grafo, origen, destinos, criterio)
    if error is None:
        if len(destinos) < 2:
            error = "Debe indicar al menos dos destinos."
        elif len(set(destinos)) != len(destinos):
            error = "Los destinos no pueden repetirse."
        elif origen in destinos:
            error = "El origen no puede estar entre los destinos."
    if error is not None:
        return {"ok": False, "mensaje": error}

    # Paso 1: Dijkstra desde el origen y desde cada destino (tabla de costos entre puntos)
    tablas = {}
    for punto in [origen] + destinos:
        tablas[punto] = dijkstra(grafo, punto, criterio)

    # Paso 2: se evalua el costo total de cada orden posible
    mejor_orden = None
    mejor_costo = INF
    for orden in permutations(destinos):
        costo_total = 0
        actual = origen
        for siguiente in orden:
            costo_total += tablas[actual][0][siguiente]
            if costo_total == INF:
                break  # un tramo sin camino: se descarta este orden
            actual = siguiente

        if costo_total < mejor_costo:
            mejor_costo = costo_total
            mejor_orden = orden

    # Si todos los ordenes tienen algun tramo sin camino, no hay recorrido
    if mejor_orden is None:
        return {"ok": False, "mensaje": "No existe un recorrido que conecte todos los destinos."}

    # Paso 3: se reconstruye cada tramo del orden elegido y se unen
    tramos = []
    actual = origen
    for siguiente in mejor_orden:
        previo = tablas[actual][1]
        tramos.append(reconstruir_camino(previo, actual, siguiente))
        actual = siguiente

    return {
        "ok": True,
        "orden": list(mejor_orden),
        "tramos": tramos,
        "camino": unir_tramos(tramos),
        "costo": mejor_costo,
        "criterio": criterio,
        "mensaje": "",
    }


def ruta_personalizada(grafo, origen, destinos, criterio):
    # Funcionalidad 3: el turista define el orden; se calcula un tramo por cada
    # par de lugares consecutivos y luego se unen
    error = validar_entrada(grafo, origen, destinos, criterio)
    if error is None:
        puntos = [origen] + destinos
        for i in range(len(puntos) - 1):
            if puntos[i] == puntos[i + 1]:
                error = "Dos lugares consecutivos no pueden ser iguales: " + puntos[i] + "."
                break
    if error is not None:
        return {"ok": False, "mensaje": error}

    puntos = [origen] + destinos
    tramos = []
    costos = []
    tablas = {}  # evita repetir Dijkstra si un lugar aparece mas de una vez como inicio de tramo

    for i in range(len(puntos) - 1):
        inicio = puntos[i]
        fin = puntos[i + 1]

        if inicio not in tablas:
            tablas[inicio] = dijkstra(grafo, inicio, criterio)
        costo, previo = tablas[inicio]

        # Tramo sin camino: se informa el par afectado y no se genera la ruta
        if costo[fin] == INF:
            return {"ok": False, "mensaje": "No existe camino entre " + inicio + " y " + fin + "."}

        tramos.append(reconstruir_camino(previo, inicio, fin))
        costos.append(costo[fin])

    return {
        "ok": True,
        "orden": list(destinos),
        "tramos": tramos,
        "costos_tramos": costos,
        "camino": unir_tramos(tramos),
        "costo": sum(costos),
        "criterio": criterio,
        "mensaje": "",
    }


def mostrar_recorrido(resultado):
    if not resultado["ok"]:
        print(resultado["mensaje"])
        return

    print("Orden de visita:", " -> ".join(resultado["orden"]))
    print("Ruta completa:", " -> ".join(resultado["camino"]))
    print("Costo total:", resultado["costo"], UNIDADES[resultado["criterio"]])
