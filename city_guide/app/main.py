from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1 import health, places, poi, profile, prompts, quiz, routes

app = FastAPI(title="City Guide API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(quiz.router)
app.include_router(profile.router)
app.include_router(prompts.router)
app.include_router(routes.router)
app.include_router(poi.router)
app.include_router(places.router)
