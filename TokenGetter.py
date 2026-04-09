import requests
import json
import pandas as pd
import os

# --- CONFIGURACIÓN ---
CLIENT_ID = '72adddd741314a92af76440b1874e674'
CLIENT_SECRET = 'e8bc9ff538634274a66b4eba47d954f0'
REDIRECT_URI = 'https://127.0.0.1:8080/callback'
TOKEN_FILE = 'spotify_tokens.json'

def obtener_token_valido():
    if not os.path.exists(TOKEN_FILE):
        print("❌ Error: No existe el archivo de tokens. Ejecuta primero la autenticación.")
        return None
    
    with open(TOKEN_FILE, 'r') as f:
        tokens = json.load(f)
    
    # Aquí iría tu lógica de refresco si el token ha expirado
    return tokens.get('access_token')

def fetch_web_api(endpoint, method, token, body=None):
    url = f'https://api.spotify.com/{endpoint}' # URL estándar de Spotify
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.request(method, url, headers=headers, json=body)
    return response.json()

def generar_dataset():
    token = obtener_token_valido()
    if not token: return

    print("[INFO] 1/2: Obteniendo Top Tracks...")
    data = fetch_web_api('v1/me/top/tracks?time_range=long_term&limit=20', 'GET', token)
    
    if 'items' in data:
        track_ids = [item['id'] for item in data['items']]
        ids_string = ",".join(track_ids)
        
        print("[INFO] 2/2: Obteniendo Audio Features (IA)...")
        features_data = fetch_web_api(f'v1/audio-features?ids={ids_string}', 'GET', token)
        features_list = features_data.get('audio_features', [])

        canciones = []
        for i, item in enumerate(data['items']):
            # Buscamos los detalles técnicos
            feat = features_list[i] if i < len(features_list) and features_list[i] else {}
            
            canciones.append({
                'Nombre': item.get('name', 'Desconocido'),
                'Artistas': ", ".join([a.get('name') for a in item.get('artists', [])]),
                'Popularidad': item.get('popularity', 0),
                'Energia': feat.get('energy', 0),
                'Bailabilidad': feat.get('danceability', 0),
                'Valencia': feat.get('valence', 0),
                'Tempo': feat.get('tempo', 0),
                'Album': item.get('album', {}).get('name', 'N/A')
            })
        
        df = pd.DataFrame(canciones)
        df.to_csv("mis_top_tracks.csv", index=False)
        print(f"✅ ÉXITO: Generado 'mis_top_tracks.csv' con {len(df)} filas.")
    else:
        print("❌ Error en la respuesta de Spotify.")

if __name__ == "__main__":
    generar_dataset()