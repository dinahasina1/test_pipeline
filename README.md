# test_pipeline

Test technique présentant un pipeline ETL automatisé qui extrait, enrichit et stocke des données. Combine un traitement performant (API/CSV vers SQLite) et une API REST de consultation, orchestré dans un environnement Docker optimisé. L'architecture met l'accent sur la robustesse, la gestion de la mémoire via le streaming et la facilité de déploiement.

## Utilisation

### En local

```bash
python -m venv venv
source venv/bin/activate   # Linux / macOS
# ou : venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

Point d'entrée unique : `src/main.py`

```bash
cd src
python main.py              # Lance le pipeline + l'API (défaut)
python main.py api          # API uniquement
python main.py pipeline     # Pipeline uniquement
```

L'API est disponible sur http://localhost:8000. Documentation : http://localhost:8000/docs

### Via Docker

```bash
docker compose up --build
```

Les dossiers `data/` et `src/` sont montés en volumes pour garder les données et le hot-reload du code.

## Arborescence

```
.
├── src/
│   ├── main.py                 # Point d'entrée
│   ├── core/                   # Logique métier
│   │   ├── models/             # Modèles Pydantic (User, Post, EnrichedPost)
│   │   └── processing/         # Transformation (stream_enrichment)
│   ├── providers/              # Sources (API JSON, CSV)
│   ├── storage/                # Persistance SQLite
│   ├── integrations/           # Webhook externe
│   ├── rest_api/               # API FastAPI
│   │   └── routes/             # Endpoints (enriched-posts, duplicate, save-posts)
│   └── shared/                 # Config, logger
├── data/                       # DB, logs, users.csv
├── tests/                      # Tests unitaires
├── Dockerfile
└── docker-compose.yml
```

## Tests

```bash
pytest tests/                              # Tous les tests
pytest tests/test_transform.py             # Un module
pytest tests/test_transform.py::TestStreamEnrichment   # Une classe
```

## Pydantic

Les modèles (`User`, `Post`, `EnrichedPost`) utilisent Pydantic pour valider et typer les données. Pydantic vérifie automatiquement les types (int, str, email, etc.), gère les alias de champs (ex. `userId` → `user_id`) et permet la sérialisation JSON. Les données passent toujours par ces modèles, ce qui limite les erreurs et rend le code plus sûr.

---

## Explication du code

### Schémas manipulés

**User** (provenance CSV) — indexé par `id` pour recherche rapide :

```
userId   : int
name     : string
email    : string (format email)
```

**Post** (provenance API JSON) — post brut :

```
id       : int
userId   : int
title    : string
body     : string
```

**EnrichedPost** (fusion Post + User) — format final stocké en base :

```
id           : int
user_id      : int
email        : string (format email)
title        : string
body         : string
title_length : int
ingested_at  : datetime
```

### Flux

Deux usages principaux :

- **Visualisation** : l'API REST expose les données déjà stockées (GET enriched-posts, détail par id, save-posts).
- **Alimentation** : le pipeline ETL extrait, transforme et charge les données dans SQLite.

Grandes lignes du flux d'alimentation :

1. **Point d'entrée** : `main.py` lance le pipeline.
2. **Flux 1** : `load_users_map(CSV)` → dictionnaire `{ userId → User }`.
3. **Flux 2** : `fetch_posts_stream(API, chunk_size)` → générateur de chunks de `Post`.
4. **Mix** : `stream_enrichment(posts_generator, users_map)` → chunks d'`EnrichedPost`.
5. **Enregistrement** : `repo.save_enriched_posts(chunk)` en SQLite. Les 10 premiers partent vers le webhook externe.

Tests unitaires du mix : `tests/test_transform.py`, `tests/test_stream.py`.

### API REST et exercice

La fonctionnalité d'envoi vers l'API externe a été modifiée en **envoi par API REST** pour une mise en situation plus visible. C'est implémenté dans `src/rest_api/routes/duplicate_posts.py`.

**Fonctionnement** : GET `/duplicate-posts/{start_id}/{end_id}` (ex. `/duplicate-posts/1/10`)

1. Récupère les posts entre `start_id` et `end_id` en base.
2. Crée des copies avec de nouveaux IDs (à partir de `max_id + 1`).
3. Sauvegarde les doublons en base via `repo.save_enriched_posts()`.
4. Retourne `{"success": N}`. Les données sont visibles directement en base et via les endpoints de visualisation.

Les autres endpoints servent à **visualiser** les données (même schéma `EnrichedPost` que ci-dessus) : liste des enriched-posts, détail par id. `save-posts` (POST) enregistre des posts reçus en JSON.

### Optimisations sur le flux de données

- **Chunks** : on ne charge pas tout le JSON en mémoire. On traite les posts par blocs (`chunk_size`) pour limiter la RAM.
- **`yield`** : `stream_enrichment` et `fetch_posts_stream` utilisent des générateurs. Chaque chunk est produit et consommé au fil de l'eau, sans reconstruire toute la liste.
- **JSON volumineux** : pour un très gros JSON, on peut passer à `httpx` en mode streaming (`stream=True`) et parser le flux progressivement au lieu de faire un `response.json()` global.
