from templates import app
from templates.src.utils import load_config
config = load_config()
#Load this config object for development mode
app.config.from_object('configurations.DevelopmentConfig')
app.run(host='0.0.0.0', port=config['local_port'])
