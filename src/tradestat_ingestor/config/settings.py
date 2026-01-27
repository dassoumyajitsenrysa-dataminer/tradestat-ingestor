from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    base_url: str
    raw_data_dir: str

    redis_url: str = "redis://localhost:6379/0"
    max_retries: int = 3
    request_delay_min: int = 2
    request_delay_max: int = 4

    user_agent: str
    
    # Git configuration for remote data storage
    git_repo_url: str = ""  # e.g., https://github.com/user/tradestat-data.git
    git_branch: str = "main"  # Default branch
    git_enabled: bool = False  # Enable/disable git push on job completion

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
