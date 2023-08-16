import sqlite3
import logging

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'



# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    index.counter += 1
    return render_template('index.html', posts=posts)
index.counter = 0

@app.route('/healthz')
def status():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    #app.logger.info("Status response returned")
    #app.logger.debug(response)
    return response

@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    post  = connection.execute('SELECT COUNT(*) FROM posts').fetchone()
    count = post[0]
    connection.close()
    response = app.response_class(            
            response=json.dumps({"status":"success","code":200,"data":{"db_connection_count": index.counter , "post_count": count}}),
            status=200,
            mimetype='application/json'
    )
    #app.logger.info("Metrics response returned")   
    return response  

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.info('404 - Non existing article is accessed')
      return render_template('404.html'), 404
    else:
      app.logger.info('Article '+ post['title'] + ' retrived')
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('About us page is accessed')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info('New Article '+title+' is created')
            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
   logging.basicConfig(level=logging.INFO, style='{', datefmt='%Y-%m-%d %H:%M:%S', format='{levelname}:{name}:{asctime} {message}')
   app.run(host='0.0.0.0', port='3111')
