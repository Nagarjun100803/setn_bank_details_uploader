from pydantic_settings import BaseSettings
from datetime import date


class Settings(BaseSettings):

    db_name: str 
    db_host: str 
    db_username: str 
    db_password: str 
    db_port: int 
    admin_username: str 
    admin_password: str

    base_url: str 
    smtp_server: str 
    smtp_port: int 
    sender_email: str 
    sender_password: str

    start_date: date 
    end_date: date

    class Config:
        env_file = ".env"


settings = Settings()
