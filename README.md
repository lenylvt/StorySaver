# 📱 StorySaver - Visualiseur de Stories

Une application Streamlit pour visualiser et explorer les stories récupérées depuis Cloudflare R2.

## Fonctionnalités

- Affichage des images et vidéos directement dans l'interface
- Filtrage par utilisateur et par date
- Statistiques sur le nombre de stories par utilisateur
- Téléchargement des fichiers
- Interface responsive et intuitive

## Installation

1. Clonez ce dépôt :
```bash
git clone <URL_DU_REPO>
cd StorySaver
```

2. Créez un environnement virtuel et installez les dépendances :
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Les informations de connexion à Cloudflare R2 sont définies dans le fichier `app.py` :

```python
ACCOUNT_ID = '5b4ba7caa456bf4c1d7f4fbd5d20c880'
ACCESS_KEY = 'f99c3f1f0cbfccdb77df487e67f382c6'
SECRET_KEY = 'd962d4b783f65b59adadb47b7181feaa05c0d1c6744508686b8c34b23bee5ed2'
BUCKET_NAME = 'story'
ENDPOINT_URL = f'https://{ACCOUNT_ID}.r2.cloudflarestorage.com'
```

## Lancement de l'application

Pour lancer l'application :

```bash
streamlit run app.py
```

L'application sera accessible dans votre navigateur à l'adresse `http://localhost:8501`.

## Utilisation

1. Sélectionnez un utilisateur dans la liste déroulante
2. Choisissez une date
3. Filtrez par type de fichier (Images/Vidéos)
4. Visualisez et téléchargez les stories

## Structure des données

L'application s'attend à une structure de fichiers spécifique dans le bucket R2 :

```
BUCKET/story/(nom_utilisateur)/(date)/(date_heure)_(id)_(nom_utilisateur).(jpg|mp4)
```

Exemple :
```
story/zinedineblc2/2025-04-24/2025-04-24_16-15-56 P28znZ8LS1aoSWK38h6OBgAAgZm9odGt3ZWJmAZZolZciAZZolZbVAAAAAA zinedineblc2.mp4
``` 