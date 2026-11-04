"""
Résume une vidéo YouTube en français.

Principe (méthode "map-reduce") :
  1. On récupère les sous-titres de la vidéo.
  2. On les découpe en petits morceaux.
  3. On fait résumer chaque morceau par le LLM.
  4. On fusionne tous ces mini-résumés en un résumé final.
"""

import os
import re
from urllib.parse import parse_qs, urlparse

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from youtube_transcript_api import YouTubeTranscriptApi

# Charge les variables du fichier .env (notamment GROQ_API_KEY)
load_dotenv()


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
MODEL_NAME = "openai/gpt-oss-20b"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
MAX_TOKENS = 500

CHUNK_SIZE = 3000      # taille d'un morceau (en caractères)
CHUNK_OVERLAP = 200    # petit recouvrement pour ne pas couper une idée en deux

# Langues de sous-titres essayées dans l'ordre
TRANSCRIPT_LANGUAGES = ["fr", "en"]


# ----------------------------------------------------------------------
# Étape 1 : récupérer le texte de la vidéo
# ----------------------------------------------------------------------
def extract_video_id(url: str) -> str:
    """Extrait l'ID d'une vidéo à partir de son URL.

    Gère les formats courants :
      - https://www.youtube.com/watch?v=ID&t=152s
      - https://youtu.be/ID
      - https://www.youtube.com/shorts/ID
      - https://www.youtube.com/embed/ID
    """
    parsed = urlparse(url)

    # Cas classique : l'ID est dans le paramètre "v"
    video_id = parse_qs(parsed.query).get("v")
    if video_id:
        return video_id[0]

    # Autres cas : l'ID est le dernier morceau du chemin
    match = re.match(r"^/(?:shorts/|embed/)?([\w-]{11})", parsed.path)
    if match:
        return match.group(1)

    raise ValueError(f"Impossible de trouver l'ID de la vidéo dans : {url}")


def get_transcript_text(url: str) -> str:
    """Retourne les sous-titres de la vidéo sous forme d'un seul texte."""
    video_id = extract_video_id(url)

    api = YouTubeTranscriptApi()
    transcript = api.fetch(video_id, languages=TRANSCRIPT_LANGUAGES)

    # On ne garde que le texte (on ignore les timestamps) et on colle le tout
    return " ".join(snippet.text for snippet in transcript)


# ----------------------------------------------------------------------
# Étape 2 : préparer le LLM et découper le texte
# ----------------------------------------------------------------------
def build_llm() -> ChatOpenAI:
    """Crée le client LLM (Groq, via son API compatible OpenAI)."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("La variable GROQ_API_KEY est absente du fichier .env")

    return ChatOpenAI(
        model=MODEL_NAME,
        api_key=api_key,
        base_url=GROQ_BASE_URL,
        max_tokens=MAX_TOKENS,
    )


def split_into_chunks(text: str) -> list[str]:
    """Découpe un long texte en morceaux de taille raisonnable."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    return splitter.split_text(text)


# ----------------------------------------------------------------------
# Étape 3 : résumer
# ----------------------------------------------------------------------
def summarize_chunks(llm: ChatOpenAI, chunks: list[str]) -> list[str]:
    """Résume chaque morceau séparément (étape "map")."""
    prompt = ChatPromptTemplate.from_template(
        "Summarize this transcript segment in French:\n\n{text}"
    )
    chain = prompt | llm

    # batch() envoie les requêtes en parallèle : bien plus rapide qu'une boucle
    results = chain.batch(
    [{"text": chunk} for chunk in chunks],
    config={"max_concurrency": 3},
)
    return [result.content for result in results]


def merge_summaries(llm: ChatOpenAI, summaries: list[str]) -> str:
    """Fusionne les mini-résumés en un résumé final (étape "reduce")."""
    prompt = ChatPromptTemplate.from_template("""
    Tu es un assistant spécialisé dans le résumé de vidéos.

    Résume le passage suivant en français :
    - Identifie les idées principales.
    - Conserve les informations importantes et les exemples utiles.
    - Évite les répétitions.
    - N'ajoute aucune information absente du texte.
    - Utilise des paragraphes et des listes si nécessaire.

    Transcription :
    {text}
    """)
    chain = prompt | llm

    result = chain.invoke({"text": "\n\n".join(summaries)})
    return result.content


def summarize_video(url: str) -> str:
    """Point d'entrée : prend l'URL d'une vidéo, renvoie son résumé en français."""
    transcript = get_transcript_text(url)
    chunks = split_into_chunks(transcript)

    llm = build_llm()
    partial_summaries = summarize_chunks(llm, chunks)

    return merge_summaries(llm, partial_summaries)


# ----------------------------------------------------------------------
# Lancement du script
# ----------------------------------------------------------------------
if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=uZQJUyUTbbs&t=152s"

    try:
        print(summarize_video(video_url))
    except ValueError as error:
        print(f"URL invalide : {error}")
    except Exception as error:
        # Typiquement : vidéo sans sous-titres, clé API invalide, problème réseau...
        print(f"Une erreur est survenue : {error}")