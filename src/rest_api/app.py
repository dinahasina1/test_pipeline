from fastapi import FastAPI

from src.rest_api.routes import enriched_post, enriched_posts, save_posts
app = FastAPI()



@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(enriched_posts.router)
app.include_router(enriched_post.router)
app.include_router(save_posts.router)
