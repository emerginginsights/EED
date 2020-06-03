import os

from eed import create_app

frontend_folder_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'EED-FrontEnd')

app = create_app(static_folder=frontend_folder_path, static_url_path='')

if __name__ == '__main__':
    app.run(debug=True)
