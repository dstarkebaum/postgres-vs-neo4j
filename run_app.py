
from src.dash_app import index

def main():
    index.app.run_server(debug=True)


if __name__ == "__main__":
    main()
