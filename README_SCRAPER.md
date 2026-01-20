# Scraper de Colegios MINEDUC Chile

Script automatizado para extraer información de **todos los colegios de Chile** desde el sitio web del MINEDUC.

## 📊 Datos Extraídos

- **Nombre del colegio**
- **Teléfono**
- **Matrícula total de alumnos**
- Región
- Comuna
- URL del colegio

## 🚀 Instalación

### 1. Instalar Python
Asegúrate de tener Python 3.8 o superior instalado.

### 2. Instalar ChromeDriver

**En macOS (con Homebrew):**
```bash
brew install chromedriver
```

**O descarga manualmente:**
- Ve a https://chromedriver.chromium.org/
- Descarga la versión que coincida con tu versión de Chrome
- Coloca el ejecutable en tu PATH

### 3. Instalar dependencias de Python

```bash
pip install -r requirements.txt
```

## 💻 Uso

### Ejecución básica

```bash
python scraper_mineduc.py
```

El script:
1. Iterará por **todas las regiones de Chile**
2. Para cada región, iterará por **todas las comunas**
3. Para cada comuna, extraerá **todos los colegios**
4. Para cada colegio, obtendrá nombre, teléfono y matrícula
5. Guardará todo en un archivo Excel: `colegios_chile.xlsx`

### Opciones de configuración

Edita las variables al final del archivo `scraper_mineduc.py`:

```python
# Ejecutar sin ventana visible (más rápido)
HEADLESS = True

# Archivo para resumir ejecución interrumpida
RESUME_FROM = "scraper_progress.json"
```

## ⏸️ Reanudar Ejecución Interrumpida

El script guarda el progreso automáticamente. Si se interrumpe:

1. El progreso se guarda en `scraper_progress.json`
2. Los datos parciales se guardan en `colegios_chile_intermediate.xlsx`
3. Para resumir, ejecuta nuevamente:

```bash
python scraper_mineduc.py
```

El script detectará automáticamente el archivo de progreso y continuará desde donde se quedó.

## 📝 Archivos Generados

| Archivo | Descripción |
|---------|-------------|
| `colegios_chile.xlsx` | Archivo Excel final con todos los datos |
| `colegios_chile_intermediate.xlsx` | Respaldo intermedio (cada 10 colegios) |
| `scraper_progress.json` | Progreso actual del scraping |
| `scraper_mineduc.log` | Log detallado de la ejecución |

## ⚙️ Características

### ✅ Robustez
- **Manejo de errores**: Si un colegio falla, continúa con el siguiente
- **Auto-guardado**: Guarda progreso cada 10 colegios
- **Reanudar**: Puede continuar desde donde se interrumpió
- **Logging completo**: Registra todo en `scraper_mineduc.log`

### 🔄 Eficiencia
- Navegación optimizada entre regiones/comunas
- Esperas inteligentes para carga de páginas
- Modo headless para mayor velocidad

### 📊 Formato de Salida

El Excel contiene las siguientes columnas:

| nombre | telefono | matricula_total | region | comuna | url |
|--------|----------|-----------------|--------|--------|-----|
| Academia Pozo Almonte | 2751063 | 268 | DE TARAPACÁ | Pozo Almonte | https://... |

## 🕐 Tiempo Estimado

Con miles de colegios en Chile, el proceso completo puede tomar **varias horas** (dependiendo de tu conexión y velocidad del sitio).

**Recomendaciones:**
- Ejecutar en modo headless (`HEADLESS = True`) para mayor velocidad
- Dejar corriendo durante la noche
- No interrumpir manualmente (Ctrl+C guarda progreso)

## 🐛 Solución de Problemas

### Error: "chromedriver not found"
```bash
# macOS
brew install chromedriver

# O descarga manualmente y agrega al PATH
```

### Error: "Session not created"
Actualiza ChromeDriver para que coincida con tu versión de Chrome:
```bash
brew upgrade chromedriver
```

### El script se detiene aleatoriamente
- Verifica tu conexión a Internet
- El sitio puede tener límite de tasa (rate limiting)
- El script guardó el progreso, simplemente vuelve a ejecutarlo

### Selectores CSS no encuentran elementos
El sitio MINEDUC puede cambiar su estructura. Edita los selectores en:
- `get_regions()`
- `get_comunas()`
- `extract_school_data()`

## 📌 Notas Importantes

- ⚖️ **Uso responsable**: Este script hace muchas peticiones. Usa con moderación
- 🕐 **Paciencia**: El proceso completo toma tiempo
- 💾 **Espacio**: Asegúrate de tener espacio suficiente para el archivo Excel final
- 🔄 **Actualización**: Los datos del sitio pueden cambiar, verifica periódicamente

## 🤝 Soporte

Si encuentras problemas:
1. Revisa el archivo `scraper_mineduc.log`
2. Verifica que ChromeDriver coincida con tu versión de Chrome
3. Asegúrate de que el sitio MINEDUC esté accesible

## 📄 Licencia

Este script es para uso educativo e informativo.
