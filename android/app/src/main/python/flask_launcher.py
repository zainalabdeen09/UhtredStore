import os
import sys
import threading


def start_server(data_dir):
    os.environ["UHTRED_DATA_DIR"] = os.path.join(data_dir, "data")

    import flask_app
    app = flask_app.create_app()

    def run_flask():
        app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)

    thread = threading.Thread(target=run_flask, daemon=True)
    thread.start()
