from pydantic import BaseSettings


class TelegramSecrets(BaseSettings):
    api_id: str = "1215125"
    api_hash: str = "dba20f141ba1257614fb466f924eba31"
    bot_token: str = "6200212941:AAH_vIlgbE5_pFNGML_VCPO6JF_zj4WnRso"
