import yaml

def load_config():
    """
    Loads the configuration from config.yaml.
    """
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

# Load the configuration once and make it available as a global object
settings = load_config()
