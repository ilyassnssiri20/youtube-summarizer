"""
API qui expose le script de résumé YouTube au frontend React.

Lancer avec :  uvicorn api:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from resume_youtube import summarize_video

app = FastAPI(title="Résumeur YouTube")

# Autorise le frontend Vite (port 5173 par défaut) à appeler l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["POST"],
    allow_headers=["*"],
)


class SummarizeRequest(BaseModel):
    url: str


class SummarizeResponse(BaseModel):
    summary: str


# "def" (et non "async def") : la fonction est bloquante, FastAPI la lance
# donc dans un thread à part et ne gèle pas le serveur pendant le résumé.
@app.post("/api/summarize", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest):
    try:
        summary = summarize_video(request.url)
    except ValueError as error:
        # URL invalide
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        # Pas de sous-titres, clé API invalide, problème réseau...
        raise HTTPException(status_code=500, detail=str(error))

    return SummarizeResponse(summary=summary)





import logging

logger = logging.getLogger(__name__)

@app.post("/api/summarize", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest):
    try:
        summary = summarize_video(request.url)
        return SummarizeResponse(summary=summary)

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception:
        logger.exception("Erreur pendant le résumé")
        raise HTTPException(
            status_code=500,
            detail="Impossible de résumer cette vidéo. Réessayez plus tard."
        )