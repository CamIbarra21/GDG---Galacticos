from fastapi import APIRouter
from pydantic import BaseModel
from google.genai import types

from app.agents.tutor_agent import root_agent
from app.core.config import settings
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

router = APIRouter(prefix="/api/chat", tags=["chat"])

# NOTA para el MVP: sesiones en memoria (se pierden al reiniciar el server).
# Para producción real, cambiar a un SessionService persistente.
_session_service = InMemorySessionService()
_runner = Runner(
    agent=root_agent, app_name=settings.app_name, session_service=_session_service
)


class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    mode: str


@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    # Crea la sesión si no existe (idempotente para este MVP)
    try:
        await _session_service.create_session(
            app_name=settings.app_name,
            user_id=payload.user_id,
            session_id=payload.session_id,
        )
    except Exception:
        pass  # ya existe, seguimos

    contenido = types.Content(role="user", parts=[types.Part(text=payload.message)])

    respuesta_final = ""
    async for event in _runner.run_async(
        user_id=payload.user_id,
        session_id=payload.session_id,
        new_message=contenido,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            #respuesta_final = event.content.parts[-1].text #Respuesta
            #respuesta_final = event.content.parts[0].text #Razonamiento
            textos = [
                p.text
                for p in event.content.parts
                if getattr(p, "text", None) and not getattr(p, "thought", False)
            ]
            if textos:
                respuesta_final = "\n".join(textos)

    return ChatResponse(reply=respuesta_final, mode=settings.mode)
