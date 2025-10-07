import yaml
from pydantic import BaseModel

class OpenAIConfig(BaseModel):
    text_model: str
    tts_model: str

class GoogleConfig(BaseModel):
    image_model: str

class ProvidersConfig(BaseModel):
    openai: OpenAIConfig
    google: GoogleConfig

class GenerationConfig(BaseModel):
    providers: ProvidersConfig
    story_prompt: str

def load_config(path: str = "generator_config.yaml") -> GenerationConfig:
    """Loads the generation configuration from a YAML file."""
    try:
        with open(path, 'r') as file:
            data = yaml.safe_load(file)
            return GenerationConfig(**data)
    except FileNotFoundError:
        raise Exception(f"Configuration file not found at {path}")
    except Exception as e:
        raise Exception(f"Error parsing configuration file: {e}")

# Load the config once on startup
config = load_config()