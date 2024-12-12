import logging
import subprocess
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

SCRIPTS_DIR = os.path.dirname(os.path.realpath(__file__))

def run_script(script_name):
    script_path = os.path.join(SCRIPTS_DIR, f"{script_name}.py")
    if os.path.exists(script_path):
        try:
            subprocess.run(['python', script_path], check=True)
            logging.info(f"Script {script_name}.py exécuté avec succès.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Erreur lors de l'exécution de {script_name}.py: {e}")
    else:
        logging.error(f"Script {script_name}.py non trouvé dans {SCRIPTS_DIR}.")

if __name__ == "__main__":
    scripts = ['moving_averages', 'rsi', 'bollinger_bands', 'macd', 'stochastic', 'adx']
    for script in scripts:
        run_script(script)
