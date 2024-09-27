from flask import Flask, render_template, request, redirect, url_for, Response
from database import init_db, add_stream, get_streams, delete_stream
from m3u_generator import generate_m3u
from stream_server import streamlink_stream
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
init_db()

@app.route('/')
def index():
    streams = get_streams()
    return render_template('index.html', streams=streams)

@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    url = request.form['url']
    auth = request.form.get('auth', '')
    add_stream(name, url, auth)
    return redirect(url_for('index'))

@app.route('/delete/<int:stream_id>')
def delete(stream_id):
    delete_stream(stream_id)
    return redirect(url_for('index'))

@app.route('/m3u')
def m3u():
    m3u_content = generate_m3u()
    return Response(m3u_content, mimetype='application/vnd.apple.mpegurl')

@app.route('/stream/<int:stream_id>')
def stream(stream_id):
    return streamlink_stream(stream_id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

