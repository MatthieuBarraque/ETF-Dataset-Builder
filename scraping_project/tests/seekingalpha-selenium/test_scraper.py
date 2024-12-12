from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
import logging
import time

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("scraping_seekingalpha_selenium.log"),
        logging.StreamHandler()
    ]
)

# Liste des ETFs à surveiller
ETF_LIST = ['SPY', 'QQQ', 'EEM']  # Modifiez cette liste selon vos besoins

# Intervalle de récupération des données (en secondes)
FETCH_INTERVAL = 60  # Récupérer les données toutes les 60 secondes

# Fuseau horaire du marché (heure de New York)
from pytz import timezone
MARKET_TIMEZONE = timezone('America/New_York')

# Verrou pour synchroniser l'accès au fichier JSON
import threading
file_lock = threading.Lock()

# URL de la page listant les articles
url = 'https://seekingalpha.com/market-news'

def is_market_open():
    from datetime import datetime
    now = datetime.now(MARKET_TIMEZONE)
    # Marchés ouverts de 9h30 à 16h00, du lundi au vendredi
    if now.weekday() >= 5:
        return False  # 5 = samedi, 6 = dimanche
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    return market_open <= now <= market_close

def setup_driver():
    """
    Configure et retourne un WebDriver Selenium en mode sans tête.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def fetch_main_page_selenium(driver):
    """
    Récupère le contenu de la page principale en utilisant Selenium.
    """
    try:
        driver.get(url)
        time.sleep(5)  # Attendre que la page se charge complètement
        logging.info("Page principale récupérée avec succès via Selenium.")
        return driver.page_source
    except Exception as e:
        logging.error(f"Exception lors de la récupération de la page principale avec Selenium: {e}")
        return None

def fetch_article_content_selenium(driver, article_url):
    """
    Récupère le contenu d'un article donné en utilisant Selenium.
    """
    try:
        driver.get(article_url)
        time.sleep(5)  # Attendre que la page se charge complètement
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # Vérifiez la classe correcte pour le contenu de l'article
        content_div = soup.find('div', class_='paywall-full-content')
        if content_div:
            content = content_div.get_text(separator='\n', strip=True)
            return content
        else:
            logging.warning(f"Contenu non trouvé pour l'article: {article_url}")
            return None
    except Exception as e:
        logging.error(f"Exception lors de la récupération de l'article {article_url} avec Selenium: {e}")
        return None

def scrape_seekingalpha_selenium():
    """
    Fonction principale pour scraper les articles de Seeking Alpha en utilisant Selenium.
    """
    driver = setup_driver()
    main_page_content = fetch_main_page_selenium(driver)
    
    if not main_page_content:
        logging.error("Impossible de récupérer la page principale via Selenium. Arrêt du scraping.")
        driver.quit()
        return
    
    soup = BeautifulSoup(main_page_content, 'html.parser')
    
    # Trouver toutes les balises 'a' avec l'attribut 'data-test-id' spécifique pour les titres d'articles
    links = soup.find_all('a', attrs={'data-test-id': 'post-list-item-title'})
    
    if not links:
        logging.warning("Aucun lien d'article trouvé sur la page principale.")
        driver.quit()
        return
    
    # Liste pour stocker les articles (titre et contenu)
    articles = []
    
    for link in links:
        title = link.get_text(strip=True)  # Récupérer le titre
        relative_url = link.get('href')  # Récupérer l'URL relative
        if not relative_url.startswith('http'):
            full_url = 'https://seekingalpha.com' + relative_url  # Construire l'URL complète
        else:
            full_url = relative_url
        
        logging.info(f"Traitement de l'article: {title} - URL: {full_url}")
        
        # Récupérer le contenu de l'article
        content = fetch_article_content_selenium(driver, full_url)
        
        if content:
            articles.append({
                'titre': title,
                'url': full_url,
                'contenu': content
            })
        else:
            logging.warning(f"Contenu non disponible pour l'article: {title}")
        
        # Délai entre les requêtes pour éviter d'être bloqué
        time.sleep(1)  # Attendre 1 seconde entre les requêtes
    
    # Enregistrer les données dans un fichier JSON
    if articles:
        try:
            with file_lock:
                with open('articles_with_content.json', 'w', encoding='utf-8') as json_file:
                    json.dump(articles, json_file, ensure_ascii=False, indent=4)
            logging.info("Les articles ont été enregistrés dans 'articles_with_content.json' avec succès.")
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde des données dans le fichier JSON: {e}")
    else:
        logging.warning("Aucun article n'a été récupéré. Aucun fichier JSON créé.")
    
    driver.quit()

if __name__ == "__main__":
    if is_market_open():
        scrape_seekingalpha_selenium()
    else:
        logging.info("Le marché est fermé. Le scraping ne sera pas effectué.")
