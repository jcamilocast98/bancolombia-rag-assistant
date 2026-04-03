from fastapi import APIRouter, Depends
from .schemas.chat_schemas import ChatRequestSchema, ChatResponseSchema
from ....infrastructure.config.dependencies import get_chat_use_case
from ...middleware.security import verify_api_key
from ....application.use_cases.process_chat_message import ProcessChatMessageUseCase
from ....application.dto.chat_dto import ChatRequestDTO

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    dependencies=[Depends(verify_api_key)]
)

@router.post("", response_model=ChatResponseSchema)
async def process_chat(
    request_data: ChatRequestSchema,
    use_case: ProcessChatMessageUseCase = Depends(get_chat_use_case)
):
    dto = ChatRequestDTO(
        session_id=request_data.session_id,
        message=request_data.message
    )
    result = await use_case.execute(dto)
    return ChatResponseSchema(reply=result.reply, sources=result.sources)
