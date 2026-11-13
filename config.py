# import os
# from dotenv import load_dotenv

# load_dotenv()


# class Config:
#     SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
#     APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "YOUR_APIFY_TOKEN")
#     APIFY_ACTOR_ID = os.environ.get("APIFY_ACTOR_ID", "harvestapi/linkedin-post-search")
#     SF_INSTANCE_URL = os.environ.get("SF_INSTANCE_URL", "https://your-instance.salesforce.com")
#     SF_ACCESS_TOKEN = os.environ.get("SF_ACCESS_TOKEN", "YOUR_SF_TOKEN")
#     PROMPT_TEMPLATE_NAME = os.environ.get("PROMPT_TEMPLATE_NAME", "LinkedIn_Lead_Extractor")
#     SF_API_VERSION = os.environ.get("SF_API_VERSION", "v62.0")


# class DevelopmentConfig(Config):
#     DEBUG = True


# class ProductionConfig(Config):
#     DEBUG = False


# def get_config():
#     env = os.environ.get("FLASK_ENV", "development")
#     return ProductionConfig if env == "production" else DevelopmentConfig


# import os
# from dotenv import load_dotenv

# load_dotenv()


# class Config:
#     SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
#     APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "YOUR_APIFY_TOKEN")
#     APIFY_ACTOR_ID = os.environ.get("APIFY_ACTOR_ID", "harvestapi/linkedin-post-search")
    
#     # Salesforce Configuration
#     SF_INSTANCE_URL = os.environ.get("SF_INSTANCE_URL", "https://your-instance.my.salesforce.com")
    
  
#     SF_CLIENT_ID = os.environ.get("SF_CLIENT_ID", "YOUR_SF_CLIENT_ID")
#     SF_CLIENT_SECRET = os.environ.get("SF_CLIENT_SECRET", "YOUR_SF_CLIENT_SECRET")
    
#     PROMPT_TEMPLATE_NAME = os.environ.get("PROMPT_TEMPLATE_NAME", "LinkedIn_Lead_Extractor")
#     SF_API_VERSION = os.environ.get("SF_API_VERSION", "v62.0")


# class DevelopmentConfig(Config):
#     DEBUG = True


# class ProductionConfig(Config):
#     DEBUG = False


# def get_config():
#     env = os.environ.get("FLASK_ENV", "development")
#     return ProductionConfig if env == "production" else DevelopmentConfig


import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # Anthropic
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

    # Salesforce
    SF_INSTANCE_URL = os.environ.get("SF_INSTANCE_URL", "https://your-instance.my.salesforce.com")
    SF_CLIENT_ID = os.environ.get("SF_CLIENT_ID")
    SF_CLIENT_SECRET = os.environ.get("SF_CLIENT_SECRET")
    SF_API_VERSION = os.environ.get("SF_API_VERSION", "v62.0")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


def get_config():
    env = os.environ.get("FLASK_ENV", "development")
    config_cls = ProductionConfig if env == "production" else DevelopmentConfig
    if not config_cls.ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")
    return config_cls