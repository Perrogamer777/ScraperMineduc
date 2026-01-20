#!/usr/bin/env python3
"""
Script de PRUEBA PILOTO para el scraper MINEDUC
Solo procesa 1 región y 1 comuna para verificar que todo funcione correctamente
"""

import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper_piloto.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MinEducScraperPiloto:
    """Scraper de prueba - solo procesa 1 región y 1 comuna"""
    
    def __init__(self, headless: bool = False):
        self.base_url = "https://mi.mineduc.cl/mime-web/mvc/mime/busqueda_avanzada"
        self.headless = headless
        self.driver = None
        self.wait = None
        self.data = []
        
    def setup_driver(self):
        """Configura el driver de Chrome"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        logger.info("✓ Driver de Chrome configurado")
        
    def get_regions(self) -> List[Dict[str, str]]:
        """Obtiene la lista de regiones"""
        logger.info("Obteniendo regiones...")
        
        region_dropdown = self.wait.until(
            EC.element_to_be_clickable((By.ID, "region"))
        )
        
        options = self.driver.find_elements(By.CSS_SELECTOR, "#region option")
        regions = []
        
        for option in options:
            value = option.get_attribute("value")
            text = option.text.strip()
            if value and value.lower() != "todas" and text.lower() != "todas":
                regions.append({'value': value, 'text': text})
                
        logger.info(f"✓ Se encontraron {len(regions)} regiones")
        return regions
        
    def select_region(self, region_value: str, region_text: str) -> bool:
        """Selecciona una región"""
        try:
            logger.info(f"Seleccionando región: {region_text}")
            
            region_dropdown = self.wait.until(
                EC.element_to_be_clickable((By.ID, "region"))
            )
            
            # Seleccionar la región y disparar el evento change
            region_dropdown.click()
            time.sleep(0.5)
            
            option = self.driver.find_element(
                By.CSS_SELECTOR, 
                f"#region option[value='{region_value}']"
            )
            option.click()
            time.sleep(2)  # Esperar a que se carguen las comunas
            logger.info(f"✓ Región seleccionada: {region_text}")
            return True
        except Exception as e:
            logger.error(f"✗ Error seleccionando región: {e}")
            return False
            
    def get_comunas(self) -> List[Dict[str, str]]:
        """Obtiene la lista de comunas"""
        try:
            logger.info("Obteniendo comunas...")
            
            comuna_dropdown = self.wait.until(
                EC.presence_of_element_located((By.ID, "comuna"))
            )
            time.sleep(1)
            
            options = self.driver.find_elements(By.CSS_SELECTOR, "#comuna option")
            comunas = []
            
            for option in options:
                value = option.get_attribute("value")
                text = option.text.strip()
                # Filtrar "Todas" (value="0" o texto que contenga "todas")
                if value and value != "0" and "todas" not in text.lower():
                    comunas.append({
                        'value': value,
                        'text': text
                    })
                    
            logger.info(f"✓ Se encontraron {len(comunas)} comunas")
            return comunas
        except Exception as e:
            logger.error(f"✗ Error obteniendo comunas: {e}")
            return []
            
    def select_comuna(self, comuna_value: str, comuna_text: str) -> bool:
        """Selecciona una comuna y busca"""
        try:
            logger.info(f"Seleccionando comuna: {comuna_text}")
            
            comuna_dropdown = self.wait.until(
                EC.element_to_be_clickable((By.ID, "comuna"))
            )
            
            option = self.driver.find_element(
                By.CSS_SELECTOR, 
                f"#comuna option[value='{comuna_value}']"
            )
            option.click()
            time.sleep(1)
            
            # Hacer clic en el botón/enlace de búsqueda
            search_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.boton_caja[onclick*='EnviaBusqueda']")
            ))
            search_button.click()
            time.sleep(3)
            logger.info(f"✓ Comuna seleccionada y búsqueda ejecutada: {comuna_text}")
            return True
        except Exception as e:
            logger.error(f"✗ Error seleccionando comuna: {e}")
            return False
            
    def get_schools_in_page(self) -> List[str]:
        """Obtiene los links de colegios en la tabla"""
        try:
            logger.info("Buscando colegios en la tabla...")
            
            # Esperar a que la tabla de resultados esté presente
            self.wait.until(
                EC.presence_of_element_located((By.ID, "busqueda_avanzada"))
            )
            time.sleep(2)  # Esperar a que se completen todos los resultados
            
            # Los links están en la tabla con ID="busqueda_avanzada"
            # Usan onclick para enviar formulario, no href con 'ficha'
            school_links = self.driver.find_elements(
                By.CSS_SELECTOR, 
                "table#busqueda_avanzada tbody tr a"
            )
            
            # Extraer el RBD del onclick para construir la URL
            urls = []
            for link in school_links:
                onclick = link.get_attribute("onclick")
                if onclick and "document.fichaescuela" in onclick:
                    # Extraer RBD del onclick: document.fichaescuela.rbd.value='12736'
                    import re
                    match = re.search(r"value='(\d+)'", onclick)
                    if match:
                        rbd = match.group(1)
                        # Construir URL de la ficha
                        url = f"https://mi.mineduc.cl/mime-web/mvc/mime/ficha?rbd={rbd}"
                        urls.append(url)
                    
            logger.info(f"✓ Se encontraron {len(urls)} colegios")
            return urls
        except Exception as e:
            logger.error(f"✗ Error obteniendo colegios: {e}")
            return []
            
    def extract_school_data(self, school_url: str, region: str, comuna: str) -> Optional[Dict[str, str]]:
        """Extrae los datos de un colegio"""
        try:
            logger.info(f"Extrayendo datos de: {school_url}")
            self.driver.get(school_url)
            time.sleep(2)
            
            school_data = {
                'nombre': '',
                'direccion': '',
                'telefono': '',
                'email': '',
                'pagina_web': '',
                'director': '',
                'sostenedor': '',
                'matricula_total': '',
                'region': region,
                'comuna': comuna,
                'url': school_url
            }
            
            # Extraer nombre - está en div.titulo_color dentro de un td
            try:
                nombre_element = self.driver.find_element(
                    By.XPATH, 
                    "//div[@class='titulo_color']//td[1]"
                )
                school_data['nombre'] = nombre_element.text.strip()
                logger.info(f"  ✓ Nombre: {school_data['nombre']}")
            except:
                logger.warning(f"  ⚠ No se pudo extraer el nombre")
            
            # Extraer dirección
            try:
                direccion_element = self.driver.find_element(
                    By.XPATH,
                    "//td[contains(text(), 'Dirección:')]/following-sibling::td"
                )
                school_data['direccion'] = direccion_element.text.strip()
                logger.info(f"  ✓ Dirección: {school_data['direccion']}")
            except:
                logger.warning(f"  ⚠ No se pudo extraer la dirección")
            
            # Extraer teléfono
            try:
                telefono_element = self.driver.find_element(
                    By.XPATH, 
                    "//td[contains(text(), 'Teléfono')]/following-sibling::td | //strong[contains(text(), 'Teléfono')]/parent::*/following-sibling::*"
                )
                school_data['telefono'] = telefono_element.text.strip()
                logger.info(f"  ✓ Teléfono: {school_data['telefono']}")
            except:
                logger.warning(f"  ⚠ No se pudo extraer el teléfono")
            
            # Extraer email
            try:
                email_element = self.driver.find_element(
                    By.XPATH,
                    "//td[contains(text(), 'E-mail contacto:')]/following-sibling::td"
                )
                school_data['email'] = email_element.text.strip()
                logger.info(f"  ✓ Email: {school_data['email']}")
            except:
                logger.warning(f"  ⚠ No se pudo extraer el email")
            
            # Extraer página web
            try:
                web_element = self.driver.find_element(
                    By.XPATH,
                    "//td[contains(text(), 'Página web:')]/following-sibling::td"
                )
                school_data['pagina_web'] = web_element.text.strip()
                logger.info(f"  ✓ Página web: {school_data['pagina_web']}")
            except:
                logger.warning(f"  ⚠ No se pudo extraer la página web")
            
            # Extraer director(a)
            try:
                director_element = self.driver.find_element(
                    By.XPATH,
                    "//td[contains(text(), 'Director(a):')]/following-sibling::td"
                )
                school_data['director'] = director_element.text.strip()
                logger.info(f"  ✓ Director(a): {school_data['director']}")
            except:
                logger.warning(f"  ⚠ No se pudo extraer el director")
            
            # Extraer sostenedor
            try:
                sostenedor_element = self.driver.find_element(
                    By.XPATH,
                    "//td[contains(text(), 'Sostenedor:')]/following-sibling::td"
                )
                school_data['sostenedor'] = sostenedor_element.text.strip()
                logger.info(f"  ✓ Sostenedor: {school_data['sostenedor']}")
            except:
                logger.warning(f"  ⚠ No se pudo extraer el sostenedor")
            
            # Expandir "Información institucional" haciendo click en el enlace
            try:
                info_link = self.driver.find_element(
                    By.XPATH,
                    "//a[contains(text(), 'Información institucional')]"
                )
                info_link.click()
                time.sleep(1)
                logger.info("  ✓ Sección 'Información institucional' expandida")
            except:
                pass  # Puede que ya esté expandida
            
            # Extraer matrícula total - está en un div.form_detalle después del div que contiene el texto
            try:
                matricula_element = self.driver.find_element(
                    By.XPATH,
                    "//div[contains(text(), 'Matrícula total de alumnos:')]/following-sibling::div[@class='form_detalle']"
                )
                school_data['matricula_total'] = matricula_element.text.strip()
                logger.info(f"  ✓ Matrícula Total: {school_data['matricula_total']}")
            except:
                # Intentar con td (por si la estructura es diferente)
                try:
                    matricula_element = self.driver.find_element(
                        By.XPATH,
                        "//td[contains(text(), 'Matrícula total de alumnos:')]/following-sibling::td"
                    )
                    school_data['matricula_total'] = matricula_element.text.strip()
                    logger.info(f"  ✓ Matrícula Total: {school_data['matricula_total']}")
                except:
                    logger.warning(f"  ⚠ No se pudo extraer la matrícula total")
            
            return school_data
            
        except Exception as e:
            logger.error(f"✗ Error extrayendo datos: {e}")
            return None
            
    def run_pilot_test(self):
        """Ejecuta la prueba piloto - solo 1 región y 1 comuna"""
        logger.info("=" * 70)
        logger.info("INICIANDO PRUEBA PILOTO - 1 REGIÓN, 1 COMUNA")
        logger.info("=" * 70)
        
        try:
            self.setup_driver()
            self.driver.get(self.base_url)
            time.sleep(3)
            
            # Obtener regiones
            regions = self.get_regions()
            if not regions:
                logger.error("No se pudieron obtener las regiones")
                return
            
            # SOLO PRIMERA REGIÓN
            region = regions[0]
            logger.info(f"\n📍 REGIÓN DE PRUEBA: {region['text']}")
            
            # Navegar de nuevo y seleccionar región
            self.driver.get(self.base_url)
            time.sleep(2)
            
            if not self.select_region(region['value'], region['text']):
                return
            
            # Obtener comunas
            comunas = self.get_comunas()
            if not comunas:
                logger.error("No se pudieron obtener las comunas")
                return
            
            # SOLO PRIMERA COMUNA
            comuna = comunas[0]
            logger.info(f"\n📍 COMUNA DE PRUEBA: {comuna['text']}")
            
            # Seleccionar comuna y buscar
            if not self.select_comuna(comuna['value'], comuna['text']):
                return
            
            # Obtener colegios
            school_urls = self.get_schools_in_page()
            if not school_urls:
                logger.warning("No se encontraron colegios en esta comuna")
                return
            
            logger.info(f"\n🏫 Se procesarán {len(school_urls)} colegios\n")
            
            # Procesar cada colegio
            for i, school_url in enumerate(school_urls, 1):
                logger.info(f"\n{'─' * 70}")
                logger.info(f"COLEGIO {i}/{len(school_urls)}")
                logger.info(f"{'─' * 70}")
                
                school_data = self.extract_school_data(school_url, region['text'], comuna['text'])
                if school_data:
                    self.data.append(school_data)
            
            # Guardar resultados
            self.save_results()
            
            logger.info("\n" + "=" * 70)
            logger.info(f"✓ PRUEBA PILOTO COMPLETADA")
            logger.info(f"✓ Total de colegios procesados: {len(self.data)}")
            logger.info(f"✓ Archivo generado: colegios_piloto.xlsx")
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error(f"✗ Error durante la prueba piloto: {e}")
            if self.data:
                self.save_results()
        finally:
            if self.driver:
                self.driver.quit()
                
    def save_results(self):
        """Guarda los resultados en Excel"""
        if not self.data:
            logger.warning("No hay datos para guardar")
            return
            
        df = pd.DataFrame(self.data)
        columns_order = ['nombre', 'direccion', 'telefono', 'email', 'pagina_web', 'director', 'sostenedor', 'matricula_total', 'region', 'comuna', 'url']
        df = df[columns_order]
        
        filename = "colegios_piloto.xlsx"
        df.to_excel(filename, index=False, engine='openpyxl')
        
        logger.info(f"\n📊 Datos guardados en {filename}")
        logger.info(f"   Registros: {len(self.data)}")


if __name__ == "__main__":
    # Configuración
    HEADLESS = False  # Cambiar a True para ejecutar sin ventana visible
    
    print("\n" + "=" * 70)
    print("🧪 SCRAPER MINEDUC - PRUEBA PILOTO")
    print("=" * 70)
    print("\nEste script probará:")
    print("  ✓ Conexión al sitio MINEDUC")
    print("  ✓ Extracción de regiones")
    print("  ✓ Extracción de comunas")
    print("  ✓ Extracción de datos de colegios")
    print(f"\nModo: {'Headless (sin ventana)' if HEADLESS else 'Con ventana visible'}")
    print("=" * 70 + "\n")
    
    scraper = MinEducScraperPiloto(headless=HEADLESS)
    scraper.run_pilot_test()
