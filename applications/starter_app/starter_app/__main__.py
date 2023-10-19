from starter_app.environment import Environment
from starter_app.starter_app import create_app

env = Environment.from_env()

if __name__ == "__main__":
    create_app().run(debug=env.use_flask_debug_mode, host="0.0.0.0", port=env.port)
