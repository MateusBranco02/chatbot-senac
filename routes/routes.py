from fastapi import APIRouter
from controllers.chatbot_controller import getHealth, processar_pergunta


router = APIRouter(prefix='/api', tags=['api'])


router.get('/health')(getHealth)
router.post('/pergunta')(processar_pergunta)
