from flask import Flask

app = Flask(__name__)

@app.route("/")
@app.route("/juri")
def juri():
    return "Hello Juri!"

if __name__ == "__main__":
	app.deburg = True
	app.run(host = '0.0.0.0', port = 5000)


