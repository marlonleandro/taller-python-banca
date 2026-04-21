# Taller de Python para Analítica Bancaria

## Objetivo del taller
Integrar un flujo completo de análisis de datos en Python para banca:
- carga de datos
- filtros operativos
- cruces entre tablas
- cálculo de KPIs
- obtención de insights accionables de negocio

## Archivos incluidos
- `clientes.csv`
- `cartera_creditos.csv`
- `pagos.csv`
- `taller_banca_kpis.py`

## Resultados esperados
1. Visión clara del estado de la cartera por segmento.
2. Detección temprana de mora alta (>8%).
3. Script automatizable para reporte diario.

## Actividades propuestas para el alumno
1. Cargar los tres CSV con pandas.
2. Revisar dimensiones, tipos de datos y valores nulos.
3. Filtrar solo cartera activa.
4. Cruzar clientes, cartera y pagos.
5. Calcular KPIs generales.
6. Calcular KPIs por segmento.
7. Calcular KPIs por segmento y región.
8. Detectar alertas de mora >8%.
9. Exportar resultados para un reporte diario.

## Preguntas guía
- ¿Qué segmento concentra mayor saldo?
- ¿Qué segmento tiene peor tasa de mora?
- ¿Qué región debe ser intervenida primero?
- ¿Existe señal de alto esfuerzo de pago?
- ¿Qué acción de negocio tomarías mañana?