from typing import Annotated, Literal, Any

from fastapi import APIRouter
from fastapi import Query
from fastapi import HTTPException, status
from pydantic import BaseModel, Field

from app.utils.module_loading import import_string

from app.routers.translate.translators import GoogleTranslator

Translate_Engine_Map = {
    "ollama": "app.routers.translate.translators.OllamaTranslator",
    "google": "app.routers.translate.translators.GoogleTranslator",
    "deepl": "app.routers.translate.translators.DeeplTranslator",
}


router = APIRouter()


def get_enginee(engine) -> Any:
    try:
        _enginee = Translate_Engine_Map[engine]
    except KeyError as err:
        raise Exception(
            f"{engine} translator engine can not be support"
        ) from err
    klass = import_string(_enginee)
    return klass


class TranslateParams(BaseModel):
    sl: Literal["en"] = Field(default="en")
    tl: Literal["es", "zh-hans", "zh-hant", "jp", "ko"] = Field(default="es")
    a: Literal["google", "deepl", "ollama"] = Field(
        default="google", description="choose a engine for translate"
    )
    text: str = Field(max_length=5000)


class TranslatedResult(BaseModel):
    target_lang: str = Field()
    text: str = Field()


@router.post("/translate/", tags=["translate"])
async def translate(
    query: Annotated[TranslateParams, Query()] = None
) -> TranslatedResult:

    try:
        engine = get_enginee(query.a)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
        )
    agent = engine(target=query.tl)
    _target_text = await agent.translate(text=query.text)

    return TranslatedResult(target_lang=query.tl, text=_target_text)