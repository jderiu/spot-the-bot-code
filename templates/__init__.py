from flask import Flask
import templates.src.api.dialogue_system_names as dialogue_system_names
import templates.src.api.dialogue as dialogue
import templates.src.api.leaderboard as leaderboard

app = Flask(__name__,
 	static_folder = './public',
 	template_folder="./static")

from templates.src.views import hello_blueprint
# register the blueprints
app.register_blueprint(hello_blueprint)

API_MODULES = [dialogue_system_names, dialogue, leaderboard]


def register_route(url_path, name, fn, methods=['GET']):
    """
    Registers the given `fn` function as the handler, when Flask receives a
    request to `url_path`.
    """
    app.add_url_rule(url_path, name, fn, methods=methods)


# Register all modules stored in API_MODULES
for api_module in API_MODULES:
    for r in api_module.routes:
        register_route(r['url'], r['name'], r['fn'], r['methods'])
