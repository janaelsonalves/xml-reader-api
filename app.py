from flask import Flask, jsonify
from flask_cors import CORS, cross_origin

from reader import get_data, search_files_by_username, searchFilesByVolume, get_all_volumes, get_all_files, get_all_trustees, search_file_by_id

app = Flask(__name__)
# cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

delay = 60

@app.route("/")
@cross_origin()
def index():
    return jsonify({"message": "Index"})

# Endpoints to volumes queries
@app.route("/api/volumes")
@cross_origin()
def getVolumes():
    volumes = get_all_volumes()
    return jsonify(volumes), 200

# Endpoints to files queries
@app.route("/api/files")
@cross_origin()
def getFiles():
    files = get_all_files()
    return jsonify(files), 200

@app.route("/api/files/<id>")
@cross_origin()
def get_file_by_id(id):
    file = search_file_by_id(id)
    return jsonify(file), 200 

@app.route("/api/files/volume/<volume>")
@cross_origin()
def getFilesByVolume(volume):
    files = searchFilesByVolume(volume)
    return jsonify(files), 200


# Endpoints to trustees queries
@app.route("/api/trustees")
@cross_origin()
def getTrustees():
    trustees = get_all_trustees()
    return jsonify(trustees), 200


@app.route("/api/trustees/username/<username>")
@cross_origin()
def get_files_by_username(username):    
    trustee = search_files_by_username(username)
    return jsonify(trustee), 200
    # return jsonify(db.get("trustees"))


if __name__ == "__main__":
    app.run(debug=True)