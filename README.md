# Test technique – Pipeline Data

Pipeline de traitement de données répondant au cahier des charges : récupération depuis une API et un fichier CSV, transformation/enrichissement, stockage SQLite et envoi des premiers enregistrements vers une API externe. Le code est conçu pour traiter des **données volumineuses** en utilisant le **datastream** (flux par chunks) afin d’éviter de charger tout le JSON en mémoire.

**Documentation API** : [http://localhost:8000/docs](http://localhost:8000/docs) *(à lancer après démarrage du serveur)*

## Installation des dépendances

```bash
python -m venv venv
source venv/bin/activate   # Linux / macOS
# ou : venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

## Exécution

**Commande unique** (depuis la racine du projet) :

```bash
python src/main.py
```

Cela lance le pipeline ETL et l’API REST. L’API est disponible sur http://localhost:8000 (docs : http://localhost:8000/docs).

Modes alternatifs :

```bash
python src/main.py api          # API uniquement
python src/main.py pipeline     # Pipeline uniquement
```

### Via Docker

```bash
docker compose up --build
```

---

## Correspondance avec le travail demandé

### 1. Ingestion

- **API HTTP** : récupération des posts depuis https://jsonplaceholder.typicode.com/posts via `fetch_posts_stream`.
- **Fichier CSV** : lecture de `data/users.csv` (colonnes `userId`, `name`, `email`) via `load_users_map`.

### 2. Transformation

- Jointure posts ↔ users via `userId`.
- Champ ajouté : `title_length` (longueur du champ `title`).
- Champ ajouté : `ingested_at` (timestamp au moment de l’ingestion).

### 3. Stockage

- Table SQLite `posts_enriched` avec les colonnes : `id`, `user_id`, `email`, `title`, `body`, `title_length`, `ingested_at`.

### 4. Envoi vers une API externe

- Envoi des **10 premiers enregistrements** vers une API HTTP.
- Données envoyées : `id`, `userId` (→ `user_id`), `email`, `title`, `title_length` (et `body`, `ingested_at`).

**Implémentation** : l’API externe de l’énoncé est simulée par la route `save-posts` de l’API REST. À la fin du pipeline, le premier chunk (10 enregistrements) est envoyé en POST vers cette route, qui enregistre les données dans `data/POST-{date}.json` (ex. `data/POST-2026-02-16-16-09-51.json`).

---

## Arborescence

```
.
├── src/
│   ├── main.py                 # Point d'entrée
│   ├── core/                   # Logique métier (modèles, transformation)
│   ├── providers/              # Sources (API, CSV)
│   ├── storage/                # Persistance SQLite
│   ├── integrations/           # Webhook / envoi vers API externe
│   ├── rest_api/               # API FastAPI
│   │   └── routes/             # Endpoints (enriched-posts, save-posts, duplicate-posts)
│   └── shared/                 # Config, logger
├── data/                       # DB, users.csv, POST-*.json, logs
├── tests/
├── Dockerfile
└── docker-compose.yml
```

---

## Explication du flux

### Séparation pipeline / REST

Le projet distingue clairement deux parties :

- **Pipeline ETL** : extraction (API + CSV), transformation (enrichissement), chargement (SQLite), puis envoi du premier chunk vers l’API externe. Exécutable seul avec `python src/main.py pipeline`.
- **API REST (FastAPI)** : tient les routes de consultation (`enriched-posts`, détail par id) et la route `save-posts`. Exécutable seul avec `python src/main.py api`.

Par défaut (`python src/main.py`), les deux tournent ensemble : le pipeline s’exécute en arrière-plan pendant que l’API sert les requêtes.

### Flux détaillé

1. **Point d’entrée** : `main.py` initialise les composants (users CSV, repo SQLite, webhook).
2. **Extraction** : `load_users_map(CSV)` → dictionnaire `{ userId → User }` ; `fetch_posts_stream(API)` → générateur de chunks de `Post`.
3. **Transformation** : `stream_enrichment(posts_generator, users_map)` → chunks d’`EnrichedPost` (jointure, `title_length`, `ingested_at`).
4. **Stockage** : chaque chunk est persistant immédiatement via `repo.save_enriched_posts(chunk)`.
5. **Envoi externe** : à la fin, `send_first_chunk_to_external(repo)` récupère le premier chunk en base et l’envoie en POST vers `save-posts`.

### Envoi vers l’API externe : appel interne

L’énoncé demande d’envoyer les 10 premiers enregistrements vers une API externe (ex. webhook.site). Pour un projet auto-suffisant, l’appel « externe » a été redirigé vers une **API interne** : la route `save-posts` de l’API REST.

- À chaque passage du pipeline, le premier chunk est envoyé en POST vers `save-posts`.
- Cette route enregistre les données reçues dans `data/POST-{date}.json`.
- **Conséquence** : à chaque redémarrage du serveur (ou à chaque exécution du pipeline), un nouveau fichier `POST-*.json` est créé avec le chunk envoyé. L’historique des envois est donc tracé dans `data/`.

L’API FastAPI sert donc à la fois pour la consultation des données et pour recevoir cet « envoi externe », sans dépendre d’un service tiers.

---

## Choix techniques

- **Datastream / streaming** : le code est pensé pour ingérer des données volumineuses sans saturer la RAM. Les posts sont traités par chunks (générateurs Python, `yield`), jamais chargés intégralement en mémoire.
- **Pydantic** : modèles `User`, `Post`, `EnrichedPost` pour validation et typage.
- **API REST** : FastAPI pour consulter les données et simuler l’API externe (`save-posts`).

## Tests

```bash
pytest tests/
pytest tests/test_transform.py
```
