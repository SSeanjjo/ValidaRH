from . import tablas as tb

class Limpiador:
    """
    Normaliza el espacio tipográfico del texto:
      - Colapsa espacios/tabs internos de cada línea a un solo espacio.
      - Elimina líneas en blanco consecutivas (deja máximo una).
    """

    @staticmethod
    def limpiar(texto: str) -> str:
        lineas = texto.splitlines()
        resultado = []
        prev_vacia = False
        for linea in lineas:
            linea_s = ' '.join(linea.split())
            vacia = linea_s == ''
            if vacia and prev_vacia:
                continue
            resultado.append(linea_s)
            prev_vacia = vacia
        return '\n'.join(resultado)
