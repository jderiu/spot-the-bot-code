import json
import os

_config = None

def load_config():
    global _config
    if _config is not None:
        return _config
    else:
        with open('config/annotation_app.json', 'rt', encoding='utf-8') as conf_file:
            _config = json.load(conf_file)
            return _config