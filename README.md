# TP1 - Transacciones Sospechosas - Algoritmo Greedy

Proyecto desarrollado para la materia Teoría de Algoritmos - FIUBA.

## Índice
- [Descripción](#descripción)
- [Problema](#problema)
- [Estructura del código](#estructura-del-código)
- [Características principales](#características-principales)
- [Ejecución](#ejecución)
- [Documentación](#documentación)
- [Autores](#autores)

## Descripción
Implementación de un algoritmo greedy para determinar si un conjunto de transacciones coincide con intervalos de tiempo aproximados de actividades fraudulentas.

## Problema
Verificar si las transacciones de un sospechoso (timestamps exactos) pueden asignarse unívocamente a transacciones sospechosas (intervalos de tiempo con error).

## Estructura del código
- `check_suspicius_transactions`: Función principal que implementa el algoritmo greedy.
- `tie_break_candidates`: Selecciona el intervalo con menor tiempo de finalización.
- `suspicious_transaction_is_in_range`: Verifica si un timestamp está dentro de un intervalo.
- `read_and_process_file`: Lee y procesa datos desde un archivo de entrada.
- `format_result`: Formatea el resultado para su visualización.

## Características principales
- Algoritmo greedy con estrategia "elegir primero el que termina antes".
- Complejidad temporal: O(n²).
- Demostración formal de correctitud incluida en el informe.
- Pruebas con casos proporcionados por la cátedra y pruebas propias.

## Ejecución
Para ejecutar el programa:
python3 tp1.py ruta/a/entrada.txt

## Documentación
Para una explicación detallada del algoritmo, su demostración de correctitud y análisis de complejidad, consultar el [informe completo](informe_tp1.pdf).

## Autores
- [Nathalia Lucía Encinoza Vilela](https://github.com/nathencinoza)
- [Iván Erlich](https://github.com/ivanovic99)
- [Chiara López Angelini](https://github.com/chiaraLopezAn)