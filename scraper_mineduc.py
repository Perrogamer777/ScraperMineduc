#!/usr/bin/env python3
"""
Script para extraer datos de colegios desde el sitio MINEDUC de Chile
Extrae: nombre, teléfono y matrícula total de alumnos
De todas las regiones y comunas de Chile
"""

import time
import json
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper_mineduc.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MinEducScraper:
    """Scraper para extraer datos de colegios del sitio MINEDUC"""
    
    def __init__(self, headless: bool = False, resume_from: Optional[str] = None):
        """
        Inicializa el scraper
        
        Args:
            headless: Si True, ejecuta Chrome en modo headless (sin ventana visible)
            resume_from: JSON file para resumir desde un punto específico
        """
        self.base_url = "https://mi.mineduc.cl/mime-web/mvc/mime/busqueda_avanzada"
        self.headless = headless
        self.driver = None
        self.wait = None
        self.data = []
        self.progress_file = "scraper_progress.json"
        self.resume_from = resume_from
        self.current_region = None
        self.current_comuna = None
        
    def setup_driver(self):
        """Configura y retorna el driver de Chrome"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        logger.info("Driver de Chrome configurado correctamente")
        
    def save_progress(self):
        """Guarda el progreso actual para poder resumir después"""
        progress = {
            'current_region': self.current_region,
            'current_comuna': self.current_comuna,
            'records_collected': len(self.data),
            'timestamp': datetime.now().isoformat()
        }
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
            
    def load_progress(self) -> Optional[Dict]:
        """Carga el progreso guardado"""
        try:
            with open(self.resume_from or self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
            
    def get_regions(self) -> List[Dict[str, str]]:
        """Obtiene la lista de todas las regiones"""
        logger.info("Obteniendo lista de regiones...")
        
        # Esperar y obtener el dropdown de regiones
        region_dropdown = self.wait.until(
            EC.element_to_be_clickable((By.ID, "region"))
        )
        
        # Obtener todas las opciones
        options = self.driver.find_elements(By.CSS_SELECTOR, "#region option")
        regions = []
        
        for option in options:
            value = option.get_attribute("value")
            text = option.text.strip()
            # Filtrar la opción "Todas"
            if value and value.lower() != "todas" and text.lower() != "todas":
                regions.append({
                    'value': value,
                    'text': text
                })
                
        logger.info(f"Se encontraron {len(regions)} regiones")
        return regions
        
    def select_region(self, region_value: str) -> bool:
        """Selecciona una región específica"""
        try:
            region_dropdown = self.wait.until(
                EC.element_to_be_clickable((By.ID, "region"))
            )
            
            # Seleccionar la región
            region_dropdown.click()
            time.sleep(0.5)
            
            # Buscar la opción por value
            option = self.driver.find_element(
                By.CSS_SELECTOR, 
                f"#region option[value='{region_value}']"
            )
            option.click()
            time.sleep(2)  # Esperar a que se carguen las comunas dinámicamente
            return True
        except Exception as e:
            logger.error(f"Error seleccionando región {region_value}: {e}")
            return False
            
    def get_comunas(self) -> List[Dict[str, str]]:
        """Obtiene la lista de comunas para la región seleccionada"""
        try:
            # Esperar a que se cargue el dropdown de comunas
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
                    
            logger.info(f"Se encontraron {len(comunas)} comunas")
            return comunas
        except Exception as e:
            logger.error(f"Error obteniendo comunas: {e}")
            return []
            
    def select_comuna(self, comuna_value: str) -> bool:
        """Selecciona una comuna específica y busca"""
        try:
            comuna_dropdown = self.wait.until(
                EC.element_to_be_clickable((By.ID, "comuna"))
            )
            
            option = self.driver.find_element(
                By.CSS_SELECTOR, 
                f"#comuna option[value='{comuna_value}']"
            )
            option.click()
            time.sleep(1)
            
            # Hacer click en el botón/enlace de búsqueda
            search_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.boton_caja[onclick*='EnviaBusqueda']")
            ))
            search_button.click()
            time.sleep(3)  # Esperar resultados
            return True
        except Exception as e:
            logger.error(f"Error seleccionando comuna {comuna_value}: {e}")
            return False
            
    def get_schools_in_page(self) -> List[str]:
        """Obtiene los links de todos los colegios en la tabla de resultados"""
        try:
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
                    
            logger.info(f"Se encontraron {len(urls)} colegios en esta página")
            return urls
        except Exception as e:
            logger.error(f"Error obteniendo colegios: {e}")
            return []
            
    def extract_school_data(self, school_url: str) -> Optional[Dict[str, str]]:
        """
        Extrae los datos de un colegio específico
        
        Returns:
            Dict con nombre, telefono y matricula_total
        """
        try:
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
                'region': self.current_region,
                'comuna': self.current_comuna,
                'url': school_url
            }
            
            # Extraer nombre - está en div.titulo_color dentro de un td
            try:
                nombre_element = self.driver.find_element(
                    By.XPATH, 
                    "//div[@class='titulo_color']//td[1]"
                )
                school_data['nombre'] = nombre_element.text.strip()
            except:
                logger.warning(f"No se pudo extraer el nombre del colegio de {school_url}")
            
            # Extraer dirección
            try:
                direccion_element = self.driver.find_element(
                    By.XPATH,
                    "//td[contains(text(), 'Dirección:')]/following-sibling::td"
                )
                school_data['direccion'] = direccion_element.text.strip()
            except:
                logger.warning(f"No se pudo extraer la dirección de {school_url}")
            
            # Extraer teléfono - buscar el td que contiene "Teléfono:" y obtener el siguiente
            try:
                telefono_element = self.driver.find_element(
                    By.XPATH,
                    "//td[contains(text(), 'Teléfono:')]/following-sibling::td"
                )
                school_data['telefono'] = telefono_element.text.strip()
            except:
                logger.warning(f"No se pudo extraer el teléfono de {school_url}")
            
            # Extraer email
            try:
                email_element = self.driver.find_element(
                    By.XPATH,
                    "//td[contains(text(), 'E-mail contacto:')]/following-sibling::td"
                )
                school_data['email'] = email_element.text.strip()
            except:
                logger.warning(f"No se pudo extraer el email de {school_url}")
            
            # Extraer página web
            try:
                web_element = self.driver.find_element(
                    By.XPATH,
                    "//td[contains(text(), 'Página web:')]/following-sibling::td"
                )
                school_data['pagina_web'] = web_element.text.strip()
            except:
                logger.warning(f"No se pudo extraer la página web de {school_url}")
            
            # Extraer director(a)
            try:
                director_element = self.driver.find_element(
                    By.XPATH,
                    "//td[contains(text(), 'Director(a):')]/following-sibling::td"
                )
                school_data['director'] = director_element.text.strip()
            except:
                logger.warning(f"No se pudo extraer el director de {school_url}")
            
            # Extraer sostenedor
            try:
                sostenedor_element = self.driver.find_element(
                    By.XPATH,
                    "//td[contains(text(), 'Sostenedor:')]/following-sibling::td"
                )
                school_data['sostenedor'] = sostenedor_element.text.strip()
            except:
                logger.warning(f"No se pudo extraer el sostenedor de {school_url}")
            
            # Expandir "Información institucional" haciendo click en el enlace
            try:
                info_link = self.driver.find_element(
                    By.XPATH,
                    "//a[contains(text(), 'Información institucional')]"
                )
                info_link.click()
                time.sleep(1)
            except:
                pass  # Puede que ya esté expandida
            
            # Extraer matrícula total - está en un div.form_detalle después del div que contiene el texto
            try:
                matricula_element = self.driver.find_element(
                    By.XPATH,
                    "//div[contains(text(), 'Matrícula total de alumnos:')]/following-sibling::div[@class='form_detalle']"
                )
                school_data['matricula_total'] = matricula_element.text.strip()
            except:
                # Intentar con td (por si la estructura es diferente)
                try:
                    matricula_element = self.driver.find_element(
                        By.XPATH,
                        "//td[contains(text(), 'Matrícula total de alumnos:')]/following-sibling::td"
                    )
                    school_data['matricula_total'] = matricula_element.text.strip()
                except:
                    logger.warning(f"No se pudo extraer la matrícula total de {school_url}")
            
            logger.info(f"Datos extraídos: {school_data['nombre']} | Dir: {school_data['direccion'][:30] if school_data['direccion'] else 'N/A'}... | Tel: {school_data['telefono']} | Email: {school_data['email'][:30] if school_data['email'] else 'N/A'}... | Web: {school_data['pagina_web'][:30] if school_data['pagina_web'] else 'N/A'}... | Director: {school_data['director'][:30] if school_data['director'] else 'N/A'}... | Sostenedor: {school_data['sostenedor'][:30] if school_data['sostenedor'] else 'N/A'}... | Matrícula: {school_data['matricula_total']}")
            return school_data
            
        except Exception as e:
            logger.error(f"Error extrayendo datos del colegio {school_url}: {e}")
            return None
            
    def scrape_all(self):
        """Ejecuta el scraping completo de todas las regiones y comunas"""
        logger.info("Iniciando scraping completo...")
        
        # Cargar progreso si existe
        progress = self.load_progress() if self.resume_from else None
        skip_until_region = progress['current_region'] if progress else None
        skip_until_comuna = progress['current_comuna'] if progress else None
        should_skip = skip_until_region is not None
        
        try:
            self.setup_driver()
            self.driver.get(self.base_url)
            time.sleep(3)
            
            # Obtener todas las regiones
            regions = self.get_regions()
            
            for region in regions:
                self.current_region = region['text']
                
                # Saltar hasta llegar a la región donde se dejó
                if should_skip:
                    if region['text'] != skip_until_region:
                        logger.info(f"Saltando región {region['text']}")
                        continue
                    else:
                        logger.info(f"Resumiendo desde región {region['text']}")
                
                logger.info(f"\n{'='*60}")
                logger.info(f"Procesando región: {region['text']}")
                logger.info(f"{'='*60}")
                
                # Navegar de nuevo a la página principal
                self.driver.get(self.base_url)
                time.sleep(2)
                
                # Seleccionar región
                if not self.select_region(region['value']):
                    continue
                
                # Obtener comunas de esta región
                comunas = self.get_comunas()
                
                for comuna in comunas:
                    self.current_comuna = comuna['text']
                    
                    # Saltar hasta llegar a la comuna donde se dejó
                    if should_skip and skip_until_comuna:
                        if comuna['text'] != skip_until_comuna:
                            logger.info(f"Saltando comuna {comuna['text']}")
                            continue
                        else:
                            logger.info(f"Resumiendo desde comuna {comuna['text']}")
                            should_skip = False  # Ya llegamos al punto de reanudación
                    
                    logger.info(f"\nProcesando comuna: {comuna['text']}")
                    
                    # Recargar página y seleccionar región nuevamente
                    self.driver.get(self.base_url)
                    time.sleep(2)
                    self.select_region(region['value'])
                    time.sleep(2)
                    
                    # Seleccionar comuna y buscar
                    if not self.select_comuna(comuna['value']):
                        continue
                    
                    # Obtener todos los colegios de esta comuna
                    school_urls = self.get_schools_in_page()
                    
                    # Procesar cada colegio
                    for i, school_url in enumerate(school_urls, 1):
                        logger.info(f"Procesando colegio {i}/{len(school_urls)}")
                        
                        school_data = self.extract_school_data(school_url)
                        if school_data:
                            self.data.append(school_data)
                            
                        # Guardar progreso cada 10 colegios
                        if len(self.data) % 10 == 0:
                            self.save_progress()
                            self.save_to_excel(intermediate=True)
                    
                    logger.info(f"Comuna {comuna['text']} completada. Total registros: {len(self.data)}")
                
                logger.info(f"Región {region['text']} completada")
            
            logger.info(f"\n{'='*60}")
            logger.info(f"Scraping completado. Total de colegios: {len(self.data)}")
            logger.info(f"{'='*60}")
            
        except Exception as e:
            logger.error(f"Error durante el scraping: {e}")
            self.save_progress()
            self.save_to_excel(intermediate=True)
            raise
        finally:
            if self.driver:
                self.driver.quit()
                
    def save_to_excel(self, intermediate: bool = False):
        """Guarda los datos recolectados en un archivo Excel"""
        if not self.data:
            logger.warning("No hay datos para guardar")
            return
            
        df = pd.DataFrame(self.data)
        
        # Reordenar columnas
        columns_order = ['nombre', 'direccion', 'telefono', 'email', 'pagina_web', 'director', 'sostenedor', 'matricula_total', 'region', 'comuna', 'url']
        df = df[columns_order]
        
        filename = f"colegios_chile{'_intermediate' if intermediate else ''}.xlsx"
        df.to_excel(filename, index=False, engine='openpyxl')
        
        logger.info(f"Datos guardados en {filename} ({len(self.data)} registros)")
        
    def run(self):
        """Ejecuta el scraper completo"""
        try:
            self.scrape_all()
            self.save_to_excel()
        except KeyboardInterrupt:
            logger.info("\nScraping interrumpido por el usuario")
            self.save_progress()
            self.save_to_excel(intermediate=True)
        except Exception as e:
            logger.error(f"Error fatal: {e}")
            self.save_to_excel(intermediate=True)


if __name__ == "__main__":
    # Configuración
    HEADLESS = True  # Cambiar a True para ejecutar sin ventana visible
    RESUME_FROM = None  # O especificar archivo JSON para resumir
    
    scraper = MinEducScraper(headless=HEADLESS, resume_from=RESUME_FROM)
    scraper.run()
