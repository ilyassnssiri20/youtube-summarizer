# YouTube Video Summarizer

Une petite application web qui résume automatiquement une vidéo YouTube en français. Le backend utilise une approche *map-reduce* avec un LLM via Groq pour générer un résumé concis à partir des sous-titres.

## Structure du projet

```text
Posdcast Summerizer/
├── backend/
│   ├── api.py              # API FastAPI (point d'entrée du backend)
│   └── resume_youtube.py   # Logique de résumé (récupération sous-titres + LLM)
└── frontend/
    ├── package.json
    ├── vite.config.js
    └── src/               # Application React
```

## Fonctionnalités

- Récupère les sous-titres YouTube (français/anglais)
- Découpe le transcript en morceaux et résume chaque morceau
- Fusionne les résumés pour obtenir un résumé final cohérent
- Interface simple React avec rendu Markdown du résumé

## Prérequis

- Python 3.10+
- Node.js 18+
- Une clé API [Groq](https://console.groq.com/keys)

## Installation

### 1) Cloner le projet

```bash
git clone <url-du-repo>
cd "Posdcast Summerizer"
```

### 2) Configurer le backend avec `venv`

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Sur macOS/Linux
source venv/bin/activate
# Sur Windows (cmd)
# venv\Scripts\activate
# Sur Windows (PowerShell)
# .\venv\Scripts\Activate.ps1

# Installer les dépendances
pip install fastapi "uvicorn[standard]" python-dotenv langchain-core langchain-openai langchain-text-splitters youtube-transcript-api
```

### 3) Configurer les variables d'environnement

Créer un fichier `.env` dans le dossier `backend/` :

```bash
cd backend
touch .env
```

Ajouter votre clé Groq dans `.env` :

```env
GROQ_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

Le modèle utilisé est `openai/gpt-oss-20b` via `https://api.groq.com/openai/v1` (configuré dans `backend/resume_youtube.py`).

### 4) Installer le frontend

```bash
cd ../frontend
npm install
```

## Lancer l'application (développement)

Ouvrir deux terminaux dans la racine du projet.

### Terminal 1 - Backend (FastAPI)

```bash
# Activer venv si pas déjà fait
source venv/bin/activate  # macOS/Linux

# Lancer depuis le dossier backend
cd backend
uvicorn api:app --reload --port 8000
```

L'API sera accessible sur `http://localhost:8000`. L'endpoint principal est `POST /api/summarize` avec un body `{ "url": "..." }`.

### Terminal 2 - Frontend (Vite)

```bash
cd frontend
npm run dev
```

L'application sera accessible sur `http://localhost:5173`. Le frontend fait un appel vers `/api/summarize` et Vite proxifie vers le backend en dev (voir `vite.config.js`).

## Utilisation

1. Ouvrir `http://localhost:5173`
2. Coller l'URL d'une vidéo YouTube (formats classiques, shorts, embed supportés)
3. Cliquer sur "Résumer" - le résumé s'affiche en Markdown

## Remarques

- Si la vidéo n'a pas de sous-titres (ou dans les langues `fr`/`en`), le résumé échouera.
- Le traitement peut prendre un peu de temps pour les vidéos longues (découpage + résumés par morceau + fusion).
- CORS est configuré pour `http://localhost:5173` uniquement.
