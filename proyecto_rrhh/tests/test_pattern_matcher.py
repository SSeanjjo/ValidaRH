import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from logic.pattern_matcher import PatternMatcher

def cargar_casos(tipo: str) -> list:
    ruta = os.path.join(os.path.dirname(__file__), '..', 'data', 'casos_prueba.csv')
    casos = []
    with open(ruta, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['tipo'] == tipo:
                casos.append({
                    'entrada': row['entrada'],
                    'esperado': row['esperado'] == 'True',
                    'descripcion': row['descripcion'],
                })
    return casos


def ejecutar_suite(nombre: str, funcion, casos: list) -> dict:
    pasados = 0
    fallidos = []

    for caso in casos:
        resultado = funcion(caso['entrada'])
        if resultado == caso['esperado']:
            pasados += 1
        else:
            fallidos.append({
                'entrada': caso['entrada'],
                'esperado': caso['esperado'],
                'obtenido': resultado,
                'descripcion': caso['descripcion'],
            })

    total = len(casos)
    print(f"\n{'='*50}")
    print(f"Suite: {nombre} — {pasados}/{total} pasados")
    if fallidos:
        for f in fallidos:
            print(f"  FALLO: '{f['entrada']}'")
            print(f"         esperado={f['esperado']}, obtenido={f['obtenido']}")
            print(f"         ({f['descripcion']})")
    else:
        print("  Todos los casos pasaron.")

    return {'total': total, 'pasados': pasados, 'fallidos': fallidos}


def main():
    matcher = PatternMatcher()
    suites = [
        ('Correo electrónico', matcher.es_correo,    'correo'),
        ('Teléfono colombiano', matcher.es_telefono_co, 'telefono'),
        ('Cédula',             matcher.es_cedula,    'cedula'),
        ('Fecha',              matcher.es_fecha,      'fecha'),
        ('URL',                matcher.es_url,        'url'),
        ('Placa',              matcher.es_placa_co,   'placa'),
    ]

    resumen = []
    for nombre, funcion, tipo in suites:
        casos = cargar_casos(tipo)
        resultado = ejecutar_suite(nombre, funcion, casos)
        resumen.append((nombre, resultado))

    print(f"\n{'='*50}")
    print("RESUMEN FINAL")
    total_global = sum(r['total'] for _, r in resumen)
    pasados_global = sum(r['pasados'] for _, r in resumen)
    for nombre, r in resumen:
        estado = "OK" if r['pasados'] == r['total'] else "FALLO"
        print(f"  [{estado}] {nombre}: {r['pasados']}/{r['total']}")
    print(f"\n  Total: {pasados_global}/{total_global} casos pasados")


if __name__ == '__main__':
    main()