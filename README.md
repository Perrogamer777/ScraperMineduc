# 🏫 Scraper de Colegios MINEDUC Chile

Script automatizado para extraer información completa de **todos los colegios de Chile** desde el sitio web oficial del Ministerio de Educación (MINEDUC).

## 📊 Datos Extraídos

El scraper obtiene **11 campos** de cada colegio:

### Información Básica
- **Nombre** del establecimiento
- **Dirección** completa
- **Comuna**
- **Región**

### Datos de Contacto
- **Teléfono**
- **E-mail contacto**
- **Página web**

### Información Administrativa
- **Director(a)**
- **Sostenedor**

### Datos Académicos
- **Matrícula total de alumnos**

### Referencia
- **URL** (enlace a la ficha completa)

---

## 🚀 Instalación

### 1. Requisitos Previos

- **Python 3.8+**
- **Google Chrome** (versión actualizada)
- **ChromeDriver** (compatible con tu versión de Chrome)

### 2. Instalar ChromeDriver

**macOS (con Homebrew):**
```bash
brew install chromedriver
```

**Si aparece error de seguridad en macOS:**
```bash
xattr -d com.apple.quarantine $(which chromedriver)
```

**Otras plataformas:**
- Descarga desde: https://chromedriver.chromium.org/
- Coloca el ejecutable en tu PATH

### 3. Instalar Dependencias de Python

```bash
pip install -r requirements.txt
```

Esto instalará:
- `selenium` - Automatización de navegador
- `pandas` - Manipulación de datos
- `openpyxl` - Generación de archivos Excel

---

## 💻 Uso

### Prueba Piloto (Recomendado primero)

Antes de ejecutar el scraping completo, prueba con **1 región y 1 comuna**:

```bash
python scraper_piloto.py
```

Esto generará `colegios_piloto.xlsx` con datos de una sola comuna para verificar que todo funciona.

### Scraping Completo

Para obtener **todos los colegios de Chile**:

```bash
python scraper_mineduc.py
```

#### Opciones de Configuración

Edita el archivo `scraper_mineduc.py` (líneas finales):

```python
HEADLESS = True   # True = sin ventana, False = con ventana visible
RESUME_FROM = None  # O ruta a JSON para resumir
```

**Modo Headless (recomendado):**
- Más rápido
- No abre ventana del navegador
- Ideal para ejecuciones largas

**Modo con Ventana:**
- Puedes ver el proceso en tiempo real
- Útil para debugging

---

## ⏱️ Tiempo de Ejecución

El scraping completo de **todos los colegios de Chile**:
- **16 regiones**
- **Cientos de comunas**
- **Miles de colegios**

**Tiempo estimado:** 4-8 horas (dependiendo de conexión y velocidad del sitio)

### Recomendaciones:
- ✅ Ejecutar durante la noche
- ✅ Usar modo `HEADLESS = True`
- ✅ Dejar la computadora conectada a corriente
- ✅ Mantener conexión a Internet estable

---

## 📊 Monitoreo en Tiempo Real

**En otra terminal**, mientras el script corre:

```bash
tail -f scraper_mineduc.log
```

Verás:
- Región/comuna actual
- Número de colegios procesados
- Datos extraídos de cada colegio
- Errores o advertencias

---

## 🔄 Funcionalidades Avanzadas

### Auto-guardado

El script **automáticamente**:
- ✅ Guarda progreso cada **10 colegios**
- ✅ Genera backup intermedio en `colegios_chile_intermediate.xlsx`
- ✅ Registra posición actual en `scraper_progress.json`

### Interrumpir y Reanudar

**Para detener:**
```bash
# Presiona Ctrl + C
```

El script guardará todo el progreso automáticamente.

**Para reanudar:**
```bash
python scraper_mineduc.py
```

Continuará exactamente donde se quedó (misma región, comuna y colegio).

---

## 📁 Archivos Generados

| Archivo | Descripción |
|---------|-------------|
| `colegios_chile.xlsx` | 🎯 **Archivo final** con todos los colegios |
| `colegios_chile_intermediate.xlsx` | Backup automático (cada 10 colegios) |
| `colegios_piloto.xlsx` | Resultados de la prueba piloto |
| `scraper_progress.json` | Estado actual del scraping |
| `scraper_mineduc.log` | Log completo de ejecución |
| `scraper_piloto.log` | Log de prueba piloto |

---

## 📋 Estructura del Excel

El archivo Excel contiene las siguientes columnas (en orden):

1. **nombre** - Nombre del establecimiento
2. **direccion** - Dirección completa
3. **telefono** - Número de teléfono
4. **email** - E-mail de contacto
5. **pagina_web** - Sitio web del colegio
6. **director** - Nombre del director(a)
7. **sostenedor** - Nombre del sostenedor
8. **matricula_total** - Total de alumnos matriculados
9. **region** - Región de Chile
10. **comuna** - Comuna
11. **url** - Enlace a la ficha completa en MINEDUC

---

## 🛠️ Solución de Problemas

### Error: "selenium not found"
```bash
pip install selenium pandas openpyxl
```

### Error: "chromedriver not found"
```bash
brew install chromedriver
```

### Error: "chromedriver cannot be opened" (macOS)
```bash
xattr -d com.apple.quarantine $(which chromedriver)
```

### Error: "Session not created"
Tu ChromeDriver no coincide con tu versión de Chrome:
```bash
brew upgrade chromedriver
```

### El script se detiene inesperadamente
- Verifica tu conexión a Internet
- El sitio MINEDUC puede estar lento
- Revisa `scraper_mineduc.log` para ver el error
- Vuelve a ejecutar - se reanudará automáticamente

### No se extraen algunos datos
Algunos colegios pueden no tener todos los campos (ej: sin página web, sin email). Esto es normal y el script continuará, guardando campos vacíos donde corresponda.

---

## 🏗️ Arquitectura del Proyecto

```
olaaaa/
├── scraper_mineduc.py          # Script principal (todas las regiones)
├── scraper_piloto.py           # Script de prueba (1 región, 1 comuna)
├── requirements.txt            # Dependencias de Python
├── README.md                   # Este archivo
├── README_SCRAPER.md           # Documentación técnica adicional
├── INSTRUCCIONES.md            # Guía paso a paso
├── scraper_mineduc.log         # Log del scraping completo
├── scraper_piloto.log          # Log de la prueba piloto
├── scraper_progress.json       # Progreso guardado (auto-generado)
├── colegios_chile.xlsx         # Excel final (auto-generado)
└── colegios_chile_intermediate.xlsx  # Backup intermedio (auto-generado)
```

---

## 🔧 Características Técnicas

- **Selenium WebDriver** para automatización del navegador
- **Manejo robusto de errores** con try-catch en cada extracción
- **XPath selectores** para máxima precisión en la extracción
- **Logging completo** para debugging y monitoreo
- **Sistema de reanudación** mediante JSON de progreso
- **Auto-guardado periódico** para prevenir pérdida de datos
- **Soporte para modo headless** para ejecuciones desatendidas

---

## 📝 Ejemplos de Uso

### Ejemplo 1: Primera Ejecución

```bash
# 1. Probar que todo funciona
python scraper_piloto.py

# 2. Verificar el Excel generado
open colegios_piloto.xlsx

# 3. Si todo está OK, ejecutar completo
python scraper_mineduc.py
```

### Ejemplo 2: Monitoreo Activo

```bash
# Terminal 1: Ejecutar scraper
python scraper_mineduc.py

# Terminal 2: Ver logs en tiempo real
tail -f scraper_mineduc.log

# Terminal 3: Ver progreso del archivo
watch -n 60 'wc -l colegios_chile_intermediate.xlsx'
```

### Ejemplo 3: Reanudar Después de Interrupción

```bash
# El script se interrumpió
# Verificar progreso guardado
cat scraper_progress.json

# Reanudar
python scraper_mineduc.py
# Continuará desde la última región/comuna guardada
```

---

## ⚖️ Consideraciones Legales y Éticas

- ✅ Los datos provienen del sitio **público** del MINEDUC
- ✅ Script con **esperas entre peticiones** para no sobrecargar el servidor
- ✅ Uso recomendado: **investigación, análisis educativo, estadísticas**
- ⚠️ Respetar políticas de uso del sitio MINEDUC
- ⚠️ No hacer ejecuciones excesivas en horarios peak

---

## 🤝 Soporte

Si encuentras problemas:

1. **Revisa los logs:**
   ```bash
   cat scraper_mineduc.log
   ```

2. **Verifica tu versión de Chrome y ChromeDriver:**
   ```bash
   google-chrome --version
   chromedriver --version
   ```

3. **Asegúrate de tener las dependencias actualizadas:**
   ```bash
   pip install --upgrade selenium pandas openpyxl
   ```

---

## 📊 Estadísticas Esperadas

Al finalizar el scraping completo, deberías tener:

- **~12,000+** establecimientos educacionales
- **16** regiones de Chile
- **~346** comunas
- **11** campos de datos por cada colegio

---

## 🎯 Roadmap

Posibles mejoras futuras:
- [ ] Scraping paralelo por regiones
- [ ] Exportación a otros formatos (CSV, JSON, SQL)
- [ ] Dashboard de visualización de datos
- [ ] API REST para consultar datos extraídos
- [ ] Actualizaciones incrementales (solo nuevos colegios)

---

## 📄 Licencia

Este proyecto es para uso educativo e informativo. Los datos pertenecen al Ministerio de Educación de Chile.

---

## ✨ Versión

**Versión 1.0** - Enero 2026

- ✅ Extracción de 11 campos completos
- ✅ Soporte para todas las regiones de Chile
- ✅ Sistema de auto-guardado y reanudación
- ✅ Modo headless para ejecuciones desatendidas
- ✅ Logging completo y detallado

---

**¿Listo para empezar?** 🚀

```bash
python scraper_piloto.py
```
