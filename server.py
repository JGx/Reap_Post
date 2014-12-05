import os
import subprocess
from flask import Flask, render_template
from flask import request

app = Flask(__name__)

@app.route('/')
def root():
    return render_template('index.html')

@app.route('/analyze', methods=["POST"])
def analyze():
	image = request.form['image']
	subreddit = request.form['subreddit']
	num_posts = request.form['numPosts']

	subprocess.call(["python", "reappost/scraper.py", 
		"-S", subreddit, 
		"-I", image,
		"-N", num_posts
		"-W", 20])

	return 200

@app.route("/results", methods=["GET"])
def results():
	url = request.args.get("url")
	score = request.args.get("score")
	title = request.args.get("title")
	num_comments = request.args.get("num_comments")
	match = request.args.get("match")

	print match

if __name__ == "__main__":
	app.run()