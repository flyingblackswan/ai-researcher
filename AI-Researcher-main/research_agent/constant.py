from .config import settings

DOCKER_WORKPLACE_NAME = settings.DOCKER_WORKPLACE_NAME
GITHUB_AI_TOKEN = settings.GITHUB_AI_TOKEN
AI_USER = settings.AI_USER
LOCAL_ROOT = settings.LOCAL_ROOT
DEBUG = settings.DEBUG
DEFAULT_LOG = settings.DEFAULT_LOG
LOG_PATH = settings.LOG_PATH
EVAL_MODE = settings.EVAL_MODE
BASE_IMAGES = settings.BASE_IMAGES
COMPLETION_MODEL = settings.COMPLETION_MODEL
EMBEDDING_MODEL = settings.EMBEDDING_MODEL
CHEEP_MODEL = settings.CHEEP_MODEL
GPUS = settings.GPUS
PLATFORM = settings.PLATFORM
FN_CALL = settings.FN_CALL
API_BASE_URL = settings.API_BASE_URL
ADD_USER = settings.ADD_USER
NON_FN_CALL = settings.NON_FN_CALL

NOT_SUPPORT_SENDER = ["mistral", "groq"]
MUST_ADD_USER = ["deepseek/deepseek-reasoner", "o1-mini"]
NOT_SUPPORT_FN_CALL = ["o1-mini", "deepseek/deepseek-reasoner"]
NOT_USE_FN_CALL = [ "deepseek/deepseek-chat"] + NOT_SUPPORT_FN_CALL

if EVAL_MODE:
    DEFAULT_LOG = False
