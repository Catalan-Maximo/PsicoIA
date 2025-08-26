def recommend(state: str) -> list[str]:
    base = ["Línea local de ayuda", "Ejercicio de respiración guiado", "Artículo breve sobre ansiedad"]
    if state == "aguda":
        return ["Técnica 5-4-3-2-1", *base]
    return base
