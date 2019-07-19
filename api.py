from flask import Flask, jsonify
from flask_cors import cross_origin
from xml.dom.minidom import parse
import os
import re

files = [
    "/Users/janaelsonalves/Documents/trustees_jur.xml",
    "/Users/janaelsonalves/Documents/trustees_adm.xml",
    "/Users/janaelsonalves/Documents/trustees_ged.xml"
]

__all_volumes = dict()
__trustee_info = dict()


def handleVolumeNames():
    # Handle names of volumes
    path = os.path.basename(xml_file)
    volume = re.search('_(.*?).xml', path).group(1)
    volumeId = __all_volumes[volume]


# Get volume name from path
def get_volume_name(path):
    basename = os.path.basename(path)
    volume = re.search('_(.*?).xml', basename).group(1)
    return volume


def get_text(nodelist):
    result = []
    for node in nodelist.childNodes:
        if node.nodeType == node.TEXT_NODE:
            result.append(node.data)
    return ''.join(result)


def get_files_from_xml(dom, tag_name):
    return dom.getElementsByTagName(tag_name)


volumes = dict(adm="1", ged="2", jur="3")

# trustee_info = dict(volumes=volumes, files=dict(), trustees=[])
trustee_info = dict(volumes=volumes, files=dict(), trustees=dict())


def handleFile(file):
    zid = file.getElementsByTagName("zid")[0]
    path = file.getElementsByTagName("path")[0]

    inheritedRightsFilter = file.getElementsByTagName("inheritedRightsFilter")

    obj = {
        "zid": get_text(zid),
        "path": get_text(path)
    }

    if len(inheritedRightsFilter):
        obj["inheritedRightsFilter"] = inheritedRightsFilter[0].getAttribute(
            "value")

    return obj


def handleTrustee(trustees):
    trustees_arr = []
    for trustee in trustees:
        trustee_id = trustee.getElementsByTagName("id")[0]
        trustee_name = trustee.getElementsByTagName("name")[0]
        trustee_rights = trustee.getElementsByTagName("rights")[0]
        trustee_rights_value = trustee_rights.getAttribute("value")
        new_trustee = dict(id=get_text(trustee_id), name=get_text(
            trustee_name), rights=trustee_rights_value)
    return trustees_arr


def create_trustee():
    return None


def read_xml(files=[]):
    print("# Reading xml files from:  {} \n".format(files))
    for file in files:

        volume_name = get_volume_name(file)
        dom = parse(file)

        all_files = dom.getElementsByTagName("file")
        for f in all_files:

            try:
                zid = f.getElementsByTagName("zid")[0]
                path = f.getElementsByTagName("path")[0]

                inheritedRightsFilter = f.getElementsByTagName(
                    "inheritedRightsFilter")

                new_zid = get_text(zid) + "_" + volumes.get(volume_name)

                new_file = {
                    "volume": volume_name.upper(),
                    "zid": new_zid,
                    "path": get_text(path)
                }

                # if len(inheritedRightsFilter):
                #     new_file["inheritedRightsFilter"] = inheritedRightsFilter[0].getAttribute(
                #         "value")

                # new_file = handleFile(f)
                # new_file["volume"] = volume_name.upper()

                trustee_info.get("files")[new_zid] = new_file

                
                # Getting data to each trustee
                trustees = f.getElementsByTagName("trustee")

                for trustee in trustees:

                    trustee_id = trustee.getElementsByTagName("id")[0]
                    trustee_name = trustee.getElementsByTagName("name")[0]
                    trustee_rights = trustee.getElementsByTagName("rights")[0]
                    trustee_rights_value = trustee_rights.getAttribute("value")

                    # name_text = re.search(
                    #     '.CN=(.*?).OU', get_text(trustee_name))
                    # cn = ""
                    # ou = ""
                    # if name_text:
                    #     cn = name_text.group(1)
                    #     ou = get_text(trustee_name)[(name_text.end() - 3):]
                    #     # print("CN: ", cn, " => OU: ", ou)
                    # else:
                    #     ou = get_text(trustee_name)
                    #     # print("OU: ", get_text(trustee_name))


                    trustee_id = get_text(trustee_id)

                    if trustee_id not in trustee_info.get("trustees"):
                        trustee_info.get("trustees")[trustee_id] = {
                            "id": trustee_id, 
                            "name": get_text(trustee_name),
                            "files": []
                        }                        

                    # new_trustee = dict(new_zid=trustee_rights_value)
                    current_file = { "zid": new_zid, "rights": trustee_rights_value}



                    # new_trustee = dict(
                    #     id=get_text(trustee_id),
                    #     user=dict(uid=cn, ou=ou),
                    #     # name=get_text(trustee_name),
                    #     rights=trustee_rights_value,
                    #     zid=new_file["zid"],
                    #     volume=new_file["volume"])

                    trustee_info.get("trustees").get(trustee_id)["files"].append(current_file)
                    # trustee_info.get("trustees").update(current_file)

            except IndexError as e:
                print(e)

            # print(volume_name.upper(), get_text(zid), get_text(path))

        # __trustee_info[volume_name] = dom

def get_all_files():
    return trustee_info.get("files")

def get_all_trustees():
    return trustee_info.get("trustees")

app = Flask(__name__)


class User:

    def __init__(self, username, group):
        self.username = username
        self.group = group


class Trustee:

    def __init__(self, id, user, rights, file):
        self.id = id,
        self.user = user
        self.rights = rights
        self.file = file


class File:

    def __init__(self, zid, path):
        self.zid = zid
        self.path = path
        self.trustees = trustees


class Volume:

    files: list()

    def __init__(self, files):
        self.files = files


@app.route("/api/files")
@cross_origin()
def get_files():
    return jsonify(trustee_info.get("files")), 200


@app.route("/api/files/<zid>")
@cross_origin()
def get_files_by_zid(zid):
    file = trustee_info.get("files").get(zid) or {}
    return jsonify(file), 200


@app.route("/api/files/name/<name>")
@cross_origin()
def get_files_by_name(name):
    files = []
    for file in trustee_info.get("files").values():
        found = re.search(name.lower(), file.get("path").lower())
        if found:
            files.append(file)
    return jsonify(files), 200


@app.route("/api/files/volume/<volume>")
@cross_origin()
def get_files_by_volume(volume):
    files = []
    for file in trustee_info.get("files").values():
        if file.get("volume") == volume.upper():
            files.append(file)
    return jsonify(files), 200


@app.route("/api/trustees")
@cross_origin()
def get_trustees():
    return jsonify(get_all_trustees()), 200


@app.route("/api/trustees/name/<name>")
@cross_origin()
def get_files_by_user(name):
    trustees_files = []
    result = {}
    for trustee in get_all_trustees().values():
        try:
            found = re.search(name.lower(), trustee.get("name").lower())
            if(found):
                files = list()
                for file in trustee.get("files"):
                    current_file = get_all_files().get(file.get("zid"))
                    current_file["rights"] = file.get("rights")
                    files.append(current_file)
                trustee["files"] = files
                trustees_files.append(trustee)
        except Exception as e:
            print("# Exception: ", e)
    return jsonify(trustees_files), 200


# @app.route("/api/trustees/name/<name>")
# @cross_origin()
# def get_trustee_by_username(name):
#     trustees = []
#     for trust in trustee_info.get("trustees"):
#         found = re.search(name, trust.get("name"))
#         found = re.search(name, trust.get("uid"))
#         if found:
#             trustees.append(trust)
#     return jsonify(trustees), 200


# @app.route("/api/trustees/uid/<uid>")
# @cross_origin()
# def get_trustee_by_uid(uid):
#     trustees = []
#     for trust in trustee_info.get("trustees"):
#         found = re.match(uid, trust.get("uid"))
#         if found:
#             trustees.append(trust)
#     return jsonify(trustees), 200

# @app.route("/api/trustees/name/<name>")
# @cross_origin()
# def get_trustee_by_username(name):
#     trustees = []
#     for trustee in trustee_info.get("trustees").values():
#         print("=> ", trustee.get("name"), "\n")
#     return jsonify(trustees or {}), 200


# @app.route("/api/trustees/uid/<uid>")
# @cross_origin()
# def get_trustee_by_uid(uid):
#     trustees = trustee_info.get("trustees").get(uid) or {}
#     return jsonify(trustees), 200



@app.route("/api/volumes")
@cross_origin()
def get_volumes():
    return jsonify(trustee_info.get("volumes")), 200


if __name__ == "__main__":
    read_xml(files)
    app.run(debug=True)
    # # print(trustee_info["trustees"])
    # print("Info")
    # for trust in trustee_info.get("trustees"):
    #     print(trust.keys())
    # # print(__trustee_info)
