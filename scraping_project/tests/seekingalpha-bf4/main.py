import requests
from bs4 import BeautifulSoup
import json
import logging
import time

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("scraping_seekingalpha.log"),
        logging.StreamHandler()
    ]
)

# URL de la page listant les articles
url = 'https://seekingalpha.com/market-news'

# En-têtes HTTP pour simuler un navigateur web
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

def fetch_main_page(session):
    """
    Récupère le contenu de la page principale.
    """
    try:
        response = session.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            logging.info("Page principale récupérée avec succès.")
            return response.content
        else:
            logging.error(f"Erreur lors de la requête de la page principale: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Exception lors de la requête de la page principale: {e}")
        return None

def fetch_article_content(session, article_url):
    """
    Récupère le contenu d'un article donné.
    """
    try:
        response = session.get(article_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # La classe 'paywall-full-content' peut avoir changé, vérifiez sur le site
            content_div = soup.find('div', class_='paywall-full-content')
            if content_div:
                content = content_div.get_text(separator='\n', strip=True)
                return content
            else:
                logging.warning(f"Contenu non trouvé pour l'article: {article_url}")
                return None
        else:
            logging.error(f"Erreur lors de la requête de l'article {article_url}: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Exception lors de la requête de l'article {article_url}: {e}")
        return None

def scrape_seekingalpha():
    """
    Fonction principale pour scraper les articles de Seeking Alpha.
    """
    session = requests.Session()
    main_page_content = fetch_main_page(session)
    
    if not main_page_content:
        logging.error("Impossible de récupérer la page principale. Arrêt du scraping.")
        return
    
    soup = BeautifulSoup(main_page_content, 'html.parser')
    
    # Trouver toutes les balises 'a' avec l'attribut 'data-test-id' spécifique pour les titres d'articles
    links = soup.find_all('a', attrs={'data-test-id': 'post-list-item-title'})
    
    if not links:
        logging.warning("Aucun lien d'article trouvé sur la page principale.")
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
        content = fetch_article_content(session, full_url)
        
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
            with open('articles_with_content.json', 'w', encoding='utf-8') as json_file:
                json.dump(articles, json_file, ensure_ascii=False, indent=4)
            logging.info("Les articles ont été enregistrés dans 'articles_with_content.json' avec succès.")
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde des données dans le fichier JSON: {e}")
    else:
        logging.warning("Aucun article n'a été récupéré. Aucun fichier JSON créé.")

if __name__ == "__main__":
    scrape_seekingalpha()
