from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.routers import admin, auth, student, teacher, ws
from app.security import LoginRequired

app = FastAPI(title="Умная очередь на сдачу")
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

for module in (auth, teacher, student, admin, ws):
    app.include_router(module.router)


@app.exception_handler(LoginRequired)
def login_required(request: Request, exc: LoginRequired) -> RedirectResponse:
    return RedirectResponse(request.url_for("login"), status_code=303)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
