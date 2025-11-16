import os
import boto3
from dotenv import load_dotenv

load_dotenv()

s3_client = boto3.client(
    's3',
    endpoint_url=os.getenv("R2_ENDPOINT_URL"),
    aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY"),
    region_name='auto'
)

# Configuration CORS qui autorise VOTRE domaine ngrok ET les requêtes locales
cors_configuration = {
    'CORSRules': [
        {
            'AllowedHeaders': ['*'],
            'AllowedMethods': ['GET', 'POST', 'PUT', 'DELETE'],
            # On ajoute explicitement votre domaine ngrok ici
            'AllowedOrigins': [
                'https://vicarious-cucullately-davian.ngrok-free.dev',
                'http://127.0.0.1:8000', # Pour les tests locaux
                'http://localhost:8000'     # Pour les tests locaux
            ],
            'MaxAgeSeconds': 3000,
            'ExposeHeaders': ['ETag']
        }
    ]
}

try:
    # On supprime d'abord l'ancienne configuration (bonne pratique)
    s3_client.delete_bucket_cors(Bucket=os.getenv("R2_BUCKET_NAME"))
    print("Ancienne configuration CORS supprimée.")
except s3_client.exceptions.ClientError as e:
    # Si l'erreur est "No such CORS configuration", ce n'est pas grave
    if 'NoSuchCORSConfiguration' in str(e):
        print("Aucune ancienne configuration CORS à supprimer.")
    else:
        print(f"Erreur en supprimant l'ancienne config: {e}")

try:
    s3_client.put_bucket_cors(
        Bucket=os.getenv("R2_BUCKET_NAME"),
        CORSConfiguration=cors_configuration
    )
    print("✅ NOUVELLE configuration CORS appliquée avec succès !")
except Exception as e:
    print(f"❌ Erreur lors de l'application de la configuration CORS: {e}")