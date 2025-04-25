import streamlit as st
import json
import boto3
import re
import os
from botocore.exceptions import ClientError
import pandas as pd
from datetime import datetime

# Configuration
ACCOUNT_ID = '5b4ba7caa456bf4c1d7f4fbd5d20c880'
ACCESS_KEY = 'f99c3f1f0cbfccdb77df487e67f382c6'
SECRET_KEY = 'd962d4b783f65b59adadb47b7181feaa05c0d1c6744508686b8c34b23bee5ed2'
BUCKET_NAME = 'story'
ENDPOINT_URL = f'https://{ACCOUNT_ID}.r2.cloudflarestorage.com'

# Initialisation du client S3 (compatible avec R2)
@st.cache_resource
def get_s3_client():
    return boto3.client(
        service_name='s3',
        endpoint_url=ENDPOINT_URL,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name='auto'
    )

def extract_file_info(file_key):
    """Extrait les informations du chemin du fichier."""
    # Ignorer les fichiers .json
    if file_key.endswith('.json'):
        return None
    
    # Format attendu: story/username/date/date_heure ID username.extension
    parts = file_key.split('/')
    
    if len(parts) != 4 or parts[0] != 'story':
        return None
    
    username = parts[1]
    date = parts[2]
    file_name = parts[3]
    
    # Extraction des détails du fichier
    file_pattern = r'(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}) (.*) (\w+)\.(jpg|mp4)'
    match = re.match(file_pattern, file_name)
    
    if not match:
        return None
    
    datetime_str, file_id, file_username, extension = match.groups()
    
    return {
        "username": username,
        "date": date,
        "datetime": datetime_str,
        "id": file_id,
        "file_username": file_username,
        "extension": extension,
        "full_path": file_key
    }

@st.cache_data(ttl=300)  # Cache les données pendant 5 minutes
def get_all_objects_from_bucket():
    """Récupère tous les objets du bucket R2"""
    try:
        s3 = get_s3_client()
        
        # Liste tous les objets du bucket
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=BUCKET_NAME)
        
        all_objects = []
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    key = obj['Key']
                    # Uniquement récupérer les fichiers, pas les dossiers
                    if not key.endswith('/') and key != 'story':
                        all_objects.append(key)
        
        return all_objects
        
    except ClientError as e:
        st.error(f"Erreur lors de la récupération des objets: {e}")
        return []

@st.cache_data(ttl=300)  # Cache les données pendant 5 minutes
def get_all_files_as_json():
    """Récupère tous les fichiers du bucket et crée un JSON structuré."""
    # Structure de données pour le JSON
    data = {
        "users": {}
    }
    
    # Récupération de tous les fichiers
    all_files = get_all_objects_from_bucket()
    
    # Traitement de chaque fichier
    for file_key in all_files:
        file_info = extract_file_info(file_key)
        
        if file_info:
            username = file_info["username"]
            date = file_info["date"]
            
            # Création de la structure si elle n'existe pas
            if username not in data["users"]:
                data["users"][username] = {}
            
            if date not in data["users"][username]:
                data["users"][username][date] = []
            
            # Ajout des informations du fichier
            data["users"][username][date].append({
                "datetime": file_info["datetime"],
                "id": file_info["id"],
                "filename": f"{file_info['datetime']} {file_info['id']} {file_info['file_username']}.{file_info['extension']}",
                "extension": file_info["extension"],
                "full_path": file_info["full_path"]
            })
    
    return data

@st.cache_data
def generate_download_link(file_path, file_type='image'):
    """Génère un lien de téléchargement présigné pour un fichier."""
    try:
        s3 = get_s3_client()
        
        params = {
            'Bucket': BUCKET_NAME,
            'Key': file_path,
        }
        
        # Ajouter des paramètres spécifiques selon le type de fichier
        if file_type == 'video':
            params['ResponseContentType'] = 'video/mp4'
            params['ResponseContentDisposition'] = f'inline; filename="{os.path.basename(file_path)}"'
        elif file_type == 'image':
            params['ResponseContentType'] = 'image/jpeg'
            params['ResponseContentDisposition'] = f'inline; filename="{os.path.basename(file_path)}"'
        
        url = s3.generate_presigned_url(
            'get_object',
            Params=params,
            ExpiresIn=3600  # Expire après 1 heure
        )
        return url
    except Exception as e:
        st.error(f"Erreur lors de la génération du lien: {e}")
        return None

# Interface Streamlit
st.set_page_config(
    page_title="Story Sauvegarder",
    page_icon="📱",
)

st.title("📱 Story Sauvegarder")

# Chargement des données (anciennement dans la sidebar)
with st.spinner("Chargement des données..."):
    data = get_all_files_as_json()

# Affichage des stats en ligne au lieu de la sidebar
st.button("↻", help="Actualiser les données", on_click=st.cache_data.clear)

# Corps principal
tab1, tab2 = st.tabs(["Explorateur de Stories", "Statistiques"])

with tab1:
    # Sélection d'un utilisateur
    users = list(data["users"].keys())
    
    if not users:
        st.warning("Aucun utilisateur trouvé.")
    else:
        selected_user = st.selectbox("Sélectionner un utilisateur", users)
        
        # Récolter tous les fichiers de l'utilisateur
        all_user_files = []
        
        if selected_user:
            dates = list(data["users"][selected_user].keys())
            dates.sort(reverse=True)  # Tri par ordre décroissant des dates
            dates.insert(0, "Toutes les dates")  # Ajouter l'option "Toutes les dates"
            
            # Titre de la section
            if "selected_date" not in st.session_state:
                st.session_state.selected_date = "Toutes les dates"
                
            # Affichage du titre
            if st.session_state.selected_date == "Toutes les dates":
                st.subheader(f"Toutes les stories de {selected_user}")
            else:
                st.subheader(f"Stories de {selected_user} le {st.session_state.selected_date}")
            
            # Initialisation des filtres en 3 colonnes
            date_col, hour_col, type_col = st.columns(3)
            
            # Colonne 1: Sélection de la date
            with date_col:
                selected_date = st.selectbox("Sélectionner une date", dates)
                st.session_state.selected_date = selected_date
            
            # Préparation des données pour les filtres
            if selected_date == "Toutes les dates":
                # Récupérer tous les fichiers de toutes les dates
                for date in data["users"][selected_user]:
                    for file in data["users"][selected_user][date]:
                        file_copy = file.copy()
                        file_copy["date"] = date  # Ajouter l'info de date
                        all_user_files.append(file_copy)
            else:
                # Récupérer les fichiers de la date sélectionnée
                files = data["users"][selected_user][selected_date]
                for file in files:
                    file_copy = file.copy()
                    file_copy["date"] = selected_date
                    all_user_files.append(file_copy)
            
            # Colonne 2: Filtrer par heure
            with hour_col:
                if all_user_files:
                    # Extraire toutes les heures uniques
                    all_hours = sorted(list(set([file['datetime'].split('_')[1].split('-')[0] for file in all_user_files])))
                    hours_options = ['Toutes les heures'] + all_hours
                    selected_hour = st.selectbox("Filtrer par heure", hours_options)
            
            # Colonne 3: Filtrer par type de fichier
            with type_col:
                file_types = ['Tout les Snaps', 'Snaps Rouge (Image)', 'Snaps Violet (Video)']
                selected_type = st.selectbox("Type de fichier", file_types)
            
            # Ligne de séparation
            st.write("---")
            
            # Appliquer les filtres
            filtered_files = all_user_files
            
            # Filtre par type
            if selected_type == 'Snaps Rouge (Image)':
                filtered_files = [f for f in filtered_files if f['extension'] == 'jpg']
            elif selected_type == 'Snaps Violet (Video)':
                filtered_files = [f for f in filtered_files if f['extension'] == 'mp4']
            
            # Filtre par heure
            if selected_hour != 'Toutes les heures':
                filtered_files = [f for f in filtered_files if f['datetime'].split('_')[1].split('-')[0] == selected_hour]
            
            # Trier par date et heure (les plus récents d'abord)
            filtered_files.sort(key=lambda x: (x['date'], x['datetime']), reverse=True)
            
            # Fonction pour convertir la date en format lisible
            def format_date_fr(date_str):
                try:
                    year, month, day = date_str.split('-')
                    from datetime import datetime
                    date_obj = datetime(int(year), int(month), int(day))
                    # Jour de la semaine en français
                    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
                    mois = ["", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
                    weekday = jours[date_obj.weekday()]
                    return f"{weekday} {int(day)} {mois[int(month)]}"
                except:
                    return date_str
            
            # Fonction pour formater l'heure
            def format_time_fr(time_str):
                try:
                    hour, minute, second = time_str.split('-')
                    return f"{hour}h{minute}"
                except:
                    return time_str
                                
            # Afficher les fichiers dans un tableau avec 3 colonnes
            for file in filtered_files:
                date_col, time_col, content_col = st.columns([1, 1, 3])
                
                # Colonne 1: Date
                with date_col:
                    date_formatted = format_date_fr(file['date'])
                    st.markdown(f"<div style='background-color:#f0f2f6; padding:10px; border-radius:5px;'>{date_formatted}</div>", unsafe_allow_html=True)
                
                # Colonne 2: Heure
                with time_col:
                    time_str = file['datetime'].split('_')[1]
                    time_formatted = format_time_fr(time_str)
                    st.markdown(f"<div style='background-color:#f0f2f6; padding:10px; border-radius:5px;'>{time_formatted}</div>", unsafe_allow_html=True)
                
                # Colonne 3: Contenu (image ou vidéo)
                with content_col:
                    # Générer le lien en fonction du type de fichier
                    file_type = 'video' if file['extension'] == 'mp4' else 'image'
                    download_link = generate_download_link(file['full_path'], file_type)
                    
                    if file['extension'] == 'jpg':
                        if download_link:
                            st.image(download_link, use_container_width=True)
                        else:
                            st.warning("Impossible de charger l'image")
                    else:  # mp4
                        if download_link:
                            # Utiliser un lecteur HTML au lieu de st.video
                            video_html = f"""
                            <video controls width="100%">
                                <source src="{download_link}" type="video/mp4">
                                Votre navigateur ne supporte pas la balise vidéo.
                            </video>
                            """
                            st.markdown(video_html, unsafe_allow_html=True)
                        else:
                            st.warning("Impossible de charger la vidéo")
                
                # Séparateur entre les stories
                st.write("---")

with tab2:
    st.subheader("Statistiques par utilisateur")
    
    # Affichage du nombre d'utilisateurs et de fichiers
    user_count = len(data["users"])
    total_files = sum(len(files) for user in data["users"].values() for files in user.values())
    
    metric_col1, metric_col2 = st.columns(2)
    metric_col1.metric("Nombre d'utilisateurs", user_count)
    metric_col2.metric("Nombre total de fichiers", total_files)
    
    # Préparation des données pour le graphique
    stats_data = []
    for user, dates in data["users"].items():
        for date, files in dates.items():
            img_count = len([f for f in files if f['extension'] == 'jpg'])
            vid_count = len([f for f in files if f['extension'] == 'mp4'])
            
            stats_data.append({
                "Utilisateur": user,
                "Date": date,
                "Images": img_count,
                "Vidéos": vid_count,
                "Total": img_count + vid_count
            })
    
    if stats_data:
        df = pd.DataFrame(stats_data)
        
        # Tableau de statistiques
        st.dataframe(df)
        
        # Graphique pour visualiser les données
        st.subheader("Nombre de stories par utilisateur")
        st.bar_chart(df.groupby("Utilisateur")[["Images", "Vidéos"]].sum())
        
        # Distribution par date
        st.subheader("Distribution des stories par date")
        st.line_chart(df.groupby("Date")["Total"].sum()) 