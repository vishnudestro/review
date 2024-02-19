from flask import Flask, Response, redirect, render_template

app = Flask(__name__)

@app.route('/jinja')
def jinja():
    data = [15, '15', 'Python is good','Python, Java, php, SQL, C++']
    return render_template("index.html", data = data)

if __name__ == "__main__":
    app.run(debug = True)