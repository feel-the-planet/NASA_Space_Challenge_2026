# Feel the Planet! 🌍
## Plan de trabajo, checklist y arquitectura de GitHub

**Lema:** *Touch the Earth. Hear the Science.*  
**Reto:** NASA Space Apps Challenge 2026 — The Earth Information Jukebox  
**Documento:** v1.0 · 14 de noviembre de 2026  
**Equipo:** 5 integrantes (incluida la coordinación e integración)  
**Estado:** Prototipo funcional parcial / preparación de entrega

> **Objetivo:** crear una plataforma abierta de divulgación científica que permita explorar un mapa terrestre con relieve impreso en 3D. Una cámara identifica el dedo índice y su posición sobre el mapa; el software recupera datos georreferenciados de la NASA, los convierte en sonido y presenta el resultado en una interfaz visual. Botones físicos permiten elegir una o varias variables.

## 1. Convenciones de seguimiento

- `[x]` Completado y confirmado por el equipo.
- `[ ]` Pendiente o no verificado. Marcar solamente después de comprobar el resultado.
- **P0** Imprescindible para una demostración científica y la entrega del hackatón.
- **P1** Importante para publicar un prototipo abierto y reproducible.
- **P2** Mejora posterior a la entrega.
- En cada tarea se recomienda abrir un **GitHub Issue**, agregar responsable, fecha, prioridad, evidencia y enlace a su *pull request*.
- Para el hackatón, **distinguir y atribuir los avances anteriores al evento** del trabajo generado durante la competencia; verificar condiciones oficiales vigentes.

### Estado inicial confirmado

- [x] Se dispone de un modelo 3D terrestre con relieve (no implica que ya esté optimizado, impreso o publicado).
- [x] Existe un prototipo capaz de localizar el dedo índice mediante cámara.
- [x] El prototipo reproduce tonos según el modo o variable seleccionada.
- [ ] Está validada la correspondencia entre tonos y valores científicos reales de la NASA.
- [ ] Está terminada la estación física (mapa, cámara y botonera).
- [ ] Existe documentación pública suficiente para reproducir el sistema.

## 2. Responsables y entregables

| Responsable | Módulo | Entregable verificable |
|---|---|---|
| Integrante 1 | Diseño 3D, fabricación y botonera | Archivos fuente y STL, lista de materiales, fotografías y montaje probado |
| Integrante 2 | Aplicación y UI | Interfaz ejecutable, localización/calibración del dedo, selección de variables |
| Integrante 3 | Datos NASA y sonificación | Dataset documentado, asociación lat/lon → dato y síntesis verificable |
| Integrante 4 | GitHub, documentación y sitio | Repositorios organizados, README, manuales y página de presentación |
| Integrante 5 (coordinación) | Integración, pruebas y entrega | Demostración de punta a punta, pitch, presentación, video y envío |

**Colaboración cruzada:** el pitch, la presentación, los ensayos y la revisión científica requieren aportaciones de todo el equipo. Los nombres definitivos se agregan al asignar los Issues.

## 3. Checklist de ejecución por módulo

### A. Hardware, modelos 3D y mapas — Integrante 1

- [x] **P0** Contar con un modelo inicial de relieve terrestre.
- [ ] **P0** Definir dimensiones de impresión, orientación y proyección cartográfica (preferible equirectangular para la primera versión).
- [ ] **P0** Comprobar que el mapa puede registrarse con la cámara y no produce oclusiones excesivas.
- [ ] **P0** Imprimir/ensamblar y fijar el mapa; validar estabilidad del soporte cenital.
- [ ] **P0** Diseñar y montar botonera mínima (selección de variables y controles necesarios).
- [ ] **P0** Probar comunicación física de botones → aplicación.
- [ ] **P1** Publicar STL, archivos editables, orientación de impresión y parámetros recomendados.
- [ ] **P1** Publicar BOM, diagramas de conexión, guía de armado y fotografías.
- [ ] **P2** Crear mapas intercambiables con texturas/relieves de otras variables ambientales.
- [ ] **P2** Versionar las texturas y registrar su fuente, escala y significado científico.

### B. Aplicación, visión e interfaz — Integrante 2

- [x] **P0** Prototipo de detección del índice con cámara.
- [x] **P0** Prototipo de generación de tonos por modo.
- [ ] **P0** Calibrar perspectiva de cámara (esquinas o marcadores ArUco).
- [ ] **P0** Transformar píxeles → coordenadas normalizadas → latitud/longitud, según proyección del mapa.
- [ ] **P0** Conectar la posición del índice a la consulta del dato científico.
- [ ] **P0** Mostrar en UI variable, valor, unidad, ubicación, fecha y fuente de datos.
- [ ] **P0** Integrar el selector de variables con botonera y/o controles digitales.
- [ ] **P0** Manejar regiones sin datos, ausencia de mano, desconexión de cámara y errores.
- [ ] **P1** Añadir selección estable mediante permanencia, filtrado temporal y recuperación de calibración.
- [ ] **P1** Crear configuraciones reproducibles de cámara, puertos y resolución.
- [ ] **P2** Explorar dos manos, comparación simultánea de regiones y accesibilidad adicional.

### C. Datos de la NASA y sonificación — Integrante 3

- [ ] **P0** Seleccionar al menos una variable y un dataset oficial de NASA pertinente al reto.
- [ ] **P0** Documentar URL, autor/productor, licencia, unidad, cobertura, resolución y periodo temporal.
- [ ] **P0** Confirmar cómo se utilizarán visualizaciones del Earth Information Center.
- [ ] **P0** Preparar una muestra local pequeña o script para obtener datos de manera reproducible.
- [ ] **P0** Implementar consulta o interpolación por ubicación, especificando límites y valores faltantes.
- [ ] **P0** Definir una relación cuantitativa explícita entre dato y parámetro acústico (frecuencia, amplitud, ritmo o timbre).
- [ ] **P0** Verificar con valores de prueba que cambios reales en los datos produzcan cambios sonoros coherentes.
- [ ] **P0** Indicar en pantalla la explicación de cada asignación sonora; no presentar tonos arbitrarios como mediciones.
- [ ] **P1** Añadir segunda variable con sonificación diferenciable y mezcla controlada.
- [ ] **P1** Documentar normalización, umbrales, valores extremos, incertidumbre y limitaciones.
- [ ] **P2** Incorporar escala temporal, comparación histórica y nuevos conjuntos georreferenciados.

### D. Repositorio, documentación y sitio — Integrante 4

- [ ] **P0** Crear repositorio público del proyecto y enlazar el repositorio de seguimiento.
- [ ] **P0** Publicar README en inglés: problema, propuesta, estado, instalación y demostración.
- [ ] **P0** Organizar código, hardware, documentación, datos de ejemplo y demo.
- [ ] **P0** Añadir instrucciones de ejecución mínimas y dependencias versionadas.
- [ ] **P0** Registrar enlaces y atribuciones NASA y de otros recursos utilizados.
- [ ] **P0** Agregar registro de contribuciones y trabajo previo al hackatón.
- [ ] **P1** Publicar README.es.md, instrucciones de montaje e impresión y fotografías.
- [ ] **P1** Añadir LICENSE para software y términos de uso apropiados para modelos y recursos externos.
- [ ] **P1** Crear plantillas de Issues y pull requests, CONTRIBUTING.md y CHANGELOG.md.
- [ ] **P1** Publicar landing page mediante GitHub Pages con concepto, imágenes, demo y enlaces.
- [ ] **P2** Añadir guías educativas, actividades de aula, FAQ, versiones y catálogo de mapas.

### E. Integración, validación y entrega — Integrante 5 (coordinación)

- [ ] **P0** Confirmar roles y delimitar alcance mínimo viable (MVP).
- [ ] **P0** Probar el flujo completo: dedo → ubicación → dato NASA → sonido → UI.
- [ ] **P0** Integrar botonera, cámara, impresión 3D y aplicación.
- [ ] **P0** Documentar qué funciona realmente y qué sigue planeado.
- [ ] **P0** Completar campos de entrega: problema, solución, uso de datos NASA y resultado esperado.
- [ ] **P0** Preparar pitch breve en inglés, presentación y video de demostración.
- [ ] **P0** Verificar requisitos, formato, horario y enlaces del portal oficial antes del envío.
- [ ] **P0** Registrar y enviar la propuesta dentro del plazo aplicable.
- [ ] **P1** Realizar pruebas con usuarios y documentar claridad del audio y usabilidad.
- [ ] **P1** Incorporar guía de solución de problemas, validación cruzada y versión etiquetada.
- [ ] **P2** Preparar taller educativo, publicaciones y hoja de ruta comunitaria.

## 4. Pruebas mínimas de aceptación (MVP)

- [ ] Dedo detectado y seguimiento estable en distintas regiones del mapa.
- [ ] Calibración reproducible con error geográfico estimado y registrado.
- [ ] Dos puntos diferentes devuelven valores correctos o justifican por qué coinciden.
- [ ] La variable seleccionada modifica el sonido en función de un **valor científico real**.
- [ ] UI identifica el valor, unidad, fuente y fecha del dato.
- [ ] Botones seleccionan efectivamente el modo sin cerrar la aplicación.
- [ ] Demo funciona de forma local sin depender de una descarga inesperada.
- [ ] Documentación permite instalar y ejecutar el sistema en otra computadora.
- [ ] Se explican límites de accesibilidad, cobertura y resolución espacial.
- [ ] Enlaces de la entrega son públicos y funcionan en modo incógnito.

## 5. Dos repositorios GitHub: seguimiento y producto

Se recomienda separar el **tablero de trabajo** del **código y materiales**:

1. **`feel-the-planet-tracker`**: este documento como `README.md`, tareas, responsables, incidencias, hitos y evidencias de avance.
2. **`feel-the-planet`**: código fuente, firmware, modelos 3D, datos de muestra, manuales, pruebas, landing page y versiones publicadas.

### Estructura del repositorio de seguimiento

```text
feel-the-planet-tracker/
├── README.md                 # Este plan y checklist
├── PROGRESS.md               # Registro cronológico de avances
├── ROADMAP.md                # Hitos y prioridades
├── CONTRIBUTORS.md           # Responsabilidades y contactos de trabajo
├── docs/
│   ├── decisions.md          # Decisiones técnicas importantes
│   ├── meeting-notes.md      # Acuerdos de reuniones
│   └── demo-checklist.md     # Verificación antes de presentar
└── .github/
    └── ISSUE_TEMPLATE/
        ├── task.md           # Nueva tarea
        └── bug.md            # Reporte de error
```

### Estructura del repositorio principal

```text
feel-the-planet/
├── README.md                 # Presentación e instalación (inglés)
├── README.es.md              # Presentación en español
├── LICENSE                   # Licencia del software
├── CITATION.cff              # Forma de citar el proyecto
├── CONTRIBUTING.md           # Guía para colaboradores
├── CHANGELOG.md              # Registro de versiones
├── requirements.txt          # Dependencias Python
├── app/
│   ├── main.py               # Punto de entrada
│   ├── vision/               # Detección de dedos y calibración
│   ├── geo/                  # Proyección y conversión geográfica
│   ├── nasa_data/            # Lectura y consulta de datasets
│   ├── sonification/         # Funciones dato → sonido
│   └── interface/            # UI
├── firmware/
│   └── button_controller/    # ESP32/Arduino
├── hardware/
│   ├── 3d-models/            # Fuentes CAD/editables
│   ├── stl/                  # Archivos para imprimir
│   ├── alternative-maps/     # Relieves por variable (futuro)
│   ├── button-panel/         # Diseño de botonera
│   ├── electronics/          # Diagramas y componentes
│   └── assembly-guide/       # Montaje, ajustes y fotografías
├── datasets/
│   ├── README.md             # Procedencia y términos de datos
│   ├── metadata/             # Fichas de datasets
│   ├── samples/              # Muestras pequeñas permitidas
│   └── scripts/              # Descarga y preprocesamiento
├── docs/
│   ├── installation/         # Pasos de instalación
│   ├── user-guide/           # Uso y calibración
│   ├── scientific-method/    # Sonificación y validez científica
│   ├── educational-activities/
│   └── images/
├── tests/                     # Pruebas automáticas y manuales
├── demo/                      # Guion, video y capturas
├── website/                   # Sitio para GitHub Pages
└── .github/
    └── workflows/            # Integración continua (futuro)
```

**Nota:** no subir datasets completos si son voluminosos ni materiales de terceros sin revisar las condiciones de reutilización. En su lugar, conservar metadatos, enlaces y scripts de descarga. Un STL es una salida imprimible; compartir también el CAD permite modificar el relieve y la botonera.

## 6. Flujo sugerido de gestión en GitHub

**GitHub Issues:** una tarea por incidencia; usar etiquetas `P0`, `P1`, `P2`, `hardware`, `vision`, `data`, `audio`, `documentation`, `presentation`, `bug`.

**Tablero GitHub Projects:** `Backlog` → `Ready` → `In progress` → `Review / Test` → `Done`.

**Criterio de terminado (Definition of Done):** la tarea tiene evidencia verificable (archivo, prueba, foto o video), documentación mínima, responsable y enlace a cambio integrado. Un avance parcial no cuenta como completado.

**Plantilla de progreso para `PROGRESS.md`:**

```md
## AAAA-MM-DD — Avance
- Responsable:
- Tarea / Issue:
- Resultado conseguido:
- Evidencia (commit, PR, foto o video):
- Bloqueos:
- Próximo paso:
```

**Plantilla de Issue:**

```md
## Objetivo
¿Qué debe funcionar o quedar entregado?

## Criterios de aceptación
- [ ] Resultado verificable 1
- [ ] Resultado verificable 2

## Responsable
Por asignar

## Prioridad
P0 / P1 / P2

## Evidencia
Enlace a PR, archivo, prueba, foto o video
```

## 7. Hitos y prioridades

| Etapa | Objetivo | Condición de cierre |
|---|---|---|
| A. MVP científico | Integrar al menos un dataset NASA, coordenadas y audio | Demostración de punta a punta validada |
| B. Integración física | Mapa, cámara y botonera | Estación estable y controles operativos |
| C. Entrega Space Apps | Pitch, presentación, demo, ficha y atribuciones | Envío completado y enlaces verificados |
| D. Publicación reproducible | Software, modelos, montaje y dependencias | Persona externa puede reproducir el prototipo |
| E. Divulgación ampliada | Web, mapas alternativos y material educativo | Versión pública documentada y mantenible |

**Prioridad temporal:** completar A, B y C para el cierre de Space Apps; continuar D y E después del evento. Verificar fechas y restricciones directamente en la plataforma oficial.

## 8. Descripción breve de proyecto para la entrega (borrador)

**Problem.** Earth observation data is scientifically valuable but often difficult for non-specialists to explore, especially through conventional visualizations alone.

**Proposed solution.** Feel the Planet! combines a 3D-printed relief map, camera-based finger tracking, physical controls and real-time data sonification. Users point to a region and explore NASA Earth observation information through coordinated sound and visual feedback.

**NASA data and technology.** The project will use documented NASA Earth observation datasets and relevant Earth Information Center visualizations. The exact datasets and sonification mappings must be specified and validated before final submission.

**Expected outcome.** An engaging, accessible, reproducible educational demonstrator, accompanied by open-source software, printable 3D designs, assembly instructions and learning resources.

## 9. Riesgos y decisiones por cerrar

- **R1 — Datos NASA:** falta confirmar dataset(s), cobertura y acceso sin conexión.
- **R2 — Ciencia del sonido:** definir relación cuantitativa y comprensible entre datos y audio.
- **R3 — Geometría:** calibración de mapa/cámara y error por altura del relieve.
- **R4 — Interfaz física:** selección fiable de botones y del dedo sin falsas activaciones.
- **R5 — Tiempo:** evitar expandir alcance antes de lograr un MVP estable.
- **R6 — Licencias:** distinguir recursos originales, aportes preexistentes y materiales de terceros.
- **R7 — Accesibilidad:** sonificación como complemento, no sustituto obligatorio del audio/visual/tacto.

## 10. Enlaces de referencia

- [Reto oficial: The Earth Information Jukebox](https://www.spaceappschallenge.org/2026/challenges/the-earth-information-jukebox/)
- [NASA Space Apps Challenge](https://www.spaceappschallenge.org/)
- [NASA Earth Information Center](https://earth.gov/)
- [GitHub Docs: Issues y Projects](https://docs.github.com/)

---

**Mantenimiento:** actualizar el checklist después de cada sesión; usar Issues/Projects como fuente de verdad de asignaciones y fechas. Este archivo es una línea base del 14-11-2026, no una afirmación de que todas las actividades pendientes hayan sido iniciadas.
