# 🚀 Instrucciones de Instalación y Prueba

## Paso 1: Instalar Dependencias

```bash
pip install -r requirements.txt
```

Esto instalará:
- `selenium` - Para automatizar el navegador
- `pandas` - Para manipular datos
- `openpyxl` - Para crear archivos Excel

## Paso 2: Verificar ChromeDriver

```bash
chromedriver --version
```

Si no está instalado, instálalo con:

```bash
brew install chromedriver
```

**Nota:** Si te aparece un error de seguridad en macOS que dice que ChromeDriver no puede abrirse porque no se puede verificar el desarrollador:

```bash
xattr -d com.apple.quarantine $(which chromedriver)
```

## Paso 3: Ejecutar Prueba Piloto

**Primero ejecuta la prueba piloto** para verificar que todo funciona:

```bash
python scraper_piloto.py
```

Esto procesará **solo 1 región y 1 comuna** para probar que:
- ✅ ChromeDriver funciona correctamente
- ✅ El sitio MINEDUC es accesible
- ✅ Los selectores CSS encuentran los elementos
- ✅ Se pueden extraer los datos correctamente
- ✅ Se genera el archivo Excel

### Qué esperar:

1. Se abrirá una ventana de Chrome (o correrá sin ventana si configuras `HEADLESS = True`)
2. Navegará al sitio MINEDUC
3. Seleccionará la primera región
4. Seleccionará la primera comuna
5. Extraerá datos de todos los colegios de esa comuna
6. Generará `colegios_piloto.xlsx`
7. Mostrará el progreso en la terminal

### Archivos generados:
- `colegios_piloto.xlsx` - Excel con los datos de prueba
- `scraper_piloto.log` - Log detallado de la ejecución

### Verificar resultados:

```bash
# Ver el archivo Excel generado
open colegios_piloto.xlsx

# Ver el log
cat scraper_piloto.log
```

---

## Paso 4: Ejecutar Scraping Completo

⚠️ **SOLO después de verificar que la prueba piloto funciona correctamente**

El scraping completo puede tardar **varias horas** (4-8 horas o más).

### Opción A: Con ventana visible (recomendado para la primera vez)

```bash
python scraper_mineduc.py
```

### Opción B: Sin ventana (headless - más rápido)

1. Editar `scraper_mineduc.py`
2. Cambiar la línea:
   ```python
   HEADLESS = True
   ```
3. Ejecutar:
   ```bash
   python scraper_mineduc.py
   ```

### Monitorear progreso en tiempo real:

```bash
# En otra terminal
tail -f scraper_mineduc.log
```

### Interrumpir y Reanudar

Si necesitas detener el script:
- Presiona `Ctrl + C`
- El script guardará el progreso en `scraper_progress.json`
- Se guardará un backup en `colegios_chile_intermediate.xlsx`

Para reanudar:
```bash
python scraper_mineduc.py
```

El script detectará automáticamente el archivo de progreso y continuará desde donde se quedó.

---

## 📊 Archivos Finales

Al terminar tendrás:

| Archivo | Descripción |
|---------|-------------|
| `colegios_chile.xlsx` | 🎯 **Archivo principal** con TODOS los colegios |
| `colegios_chile_intermediate.xlsx` | Backup intermedio |
| `scraper_progress.json` | Progreso guardado |
| `scraper_mineduc.log` | Log completo |

---

## 🔧 Solución de Problemas

### Error: "selenium not found"
```bash
pip install selenium pandas openpyxl
```

### Error: "chromedriver not found"
```bash
brew install chromedriver
```

### Error: "chromedriver cannot be opened"
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
- El sitio puede estar lento o bloqueando peticiones
- Revisa `scraper_mineduc.log` para ver el error
- Vuelve a ejecutar y se reanudará automáticamente

### No se encuentran elementos en la página
El sitio MINEDUC puede haber cambiado su estructura HTML.
Revisa el log y contacta para actualizar los selectores CSS.

---

## ✅ Checklist de Verificación

Antes de ejecutar el scraping completo:

- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] ChromeDriver instalado y funcionando
- [ ] Prueba piloto ejecutada exitosamente
- [ ] `colegios_piloto.xlsx` generado y verificado
- [ ] Los datos en el Excel se ven correctos
- [ ] Entiendes cómo interrumpir y reanudar el script

---

## 📝 Notas Importantes

1. **Tiempo**: El proceso completo puede tardar varias horas
2. **Internet**: Necesitas conexión estable durante todo el proceso
3. **Energía**: Si es laptop, conéctala a corriente
4. **Auto-guardado**: El script guarda progreso cada 10 colegios
5. **Reanudación**: Puedes detener y reanudar cuando quieras

---

## 🎯 Resumen Rápido

```bash
# 1. Instalar
pip install -r requirements.txt

# 2. Verificar ChromeDriver
chromedriver --version

# 3. Probar (MUY IMPORTANTE)
python scraper_piloto.py

# 4. Verificar resultados de prueba
open colegios_piloto.xlsx

# 5. Si todo está OK, ejecutar completo
python scraper_mineduc.py

# 6. Monitorear (en otra terminal)
tail -f scraper_mineduc.log
```

---

**¡Listo!** Si la prueba piloto funciona correctamente, puedes ejecutar el scraping completo con confianza. 🚀
