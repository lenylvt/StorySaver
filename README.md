# 📱 StorySaver - Visualiseur de Stories

Une application Streamlit pour visualiser et explorer les stories récupérées depuis Cloudflare R2.
Pour le R2 surveiller les GO (10go gratuit) et les Operations (Class A : max 30k/J, Class B : max 300k/J pour ne rien payer)

## Fonctionnalités

- Affichage des images et vidéos directement dans l'interface
- Filtrage par utilisateur et par date
- Statistiques sur le nombre de stories par utilisateur
- Téléchargement des fichiers
- Interface responsive et intuitive

## Configuration de l'environnement

L'application utilise Cloudflare R2 pour le stockage des fichiers. Vous devez configurer les variables d'environnement suivantes dans un fichier `.env` à la racine du projet :

```
R2_ENDPOINT_ID=votre_endpoint_id
R2_ACCESS_KEY_ID=votre_access_key
R2_SECRET_ACCESS_KEY=votre_secret_key
R2_BUCKET_NAME=nom_du_bucket
```

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

3. Créez un fichier `.env` avec vos informations d'authentification

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

## Utilisation de Repository Secrets

Si vous déployez cette application, utilisez les Repository Secrets pour stocker les informations sensibles :

- R2_ENDPOINT_ID
- R2_ACCESS_KEY_ID
- R2_SECRET_ACCESS_KEY
- R2_BUCKET_NAME 
