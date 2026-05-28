# Respuestas — Deep Learning y Generación Multimodal

## Pregunta: Suponga que tiene un clasificador para distinguir si una imagen publicitaria generará alto/bajo engagement (1/0). ¿Cómo validaría que el modelo está dando respuestas lógicas basadas en el análisis de píxeles?

No he implementado un clasificador de engagement en producción. Mi experiencia con visión por computadora se limita a experimentos académicos con redes neuronales convolucionales (CNNs) y transfer learning con ResNet50 para clasificación de imágenes médicas.

Desde lo que conozco, para validar que un modelo de clasificación de imágenes está tomando decisiones lógicas basándose en los píxeles correctos, aplicaría el mismo principio que en cualquier modelo supervisado: separar los datos en entrenamiento, validación y test, asegurándome de que el conjunto de test contenga imágenes donde ya sé qué elementos visuales deberían ser relevantes para la predicción. Si el modelo acierta en esos casos controlados, hay mayor confianza en que aprendió patrones reales.

Adicionalmente, he revisado que existen técnicas como Grad-CAM que generan mapas de calor sobre la imagen para mostrar qué regiones activaron la predicción, pero no las he implementado personalmente.
