from flask import Flask, render_template, url_for
app = Flask(__name__)

posts = [

    {
        'author': 'Fabian Gunzinger',
        'title': 'First post',
        'content': 'This is my first post',
        'date': 'April 20, 2020',
    },
    {
        'author': 'Molly Janz',
        'title': 'Second post',
        'content': 'This is my first post',
        'date': 'April 21, 2020',
    }

]


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', posts=posts)


@app.route('/about/')
def about():
    return render_template('about.html', title='About')


if __name__ == '__main__':
    app.run(debug=True)

