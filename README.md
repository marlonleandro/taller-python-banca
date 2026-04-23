# Taller 01: Python para Analítica Bancaria

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

# Taller 02: Análisis financiero con IA

Este taller está orientado a demostrar el uso de la IA para el análisis de datos:

- Python calcula KPIs
- IA redacta insights ejecutivos

## Archivos
- `dataset_clientes.csv`
- `dataset_creditos.csv`
- `dataset_transacciones.csv`

## Flujo del caso
1. Cargar archivos
2. Limpiar datos
3. Calcular KPIs con Pandas
4. Preparar prompt con tablas resumidas
5. Enviar prompt a OpenAI
6. Guardar reporte ejecutivo generado por IA

## Requisito para la parte de IA

Instalar librerías:
pip install openai pandas openpyxl

Definir API key:
OPENAI_API_KEY="TU_API_KEY"
