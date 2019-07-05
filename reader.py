import json
import re
import os
import time

from xml.dom.minidom import parse

__xml_jur = "/Users/janaelsonalves/Documents/trustees_jur.xml"
__xml_adm = "/Users/janaelsonalves/Documents/trustees_adm.xml"
__xml_ged = "/Users/janaelsonalves/Documents/trustees_ged.xml"

__all_files = dict()
__all_trustees = dict()
__all_volumes = dict(adm="1", ged="2", jur="3")

db = dict(volumes=__all_volumes, files=__all_files,
          trustees=__all_trustees, last_updated=None)

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)


def get_json_from_xml(xml_file):

    dom = parse(xml_file)
    files = dom.getElementsByTagName("file")

    # Handle names of volumes
    path = os.path.basename(xml_file)
    volume = re.search('_(.*?).xml', path).group(1)
    volumeId = __all_volumes[volume]

    for f in files:
        try:

            # Handle files
            zid = f.getElementsByTagName("zid")[0]
            path = f.getElementsByTagName("path")[0]
            file_id = getText(zid.childNodes) + "_" + volumeId

            __all_files[file_id] = {
                "path": path.childNodes[0].data,
                "volume": volume
            }

            # Handle trustees
            trustees = f.getElementsByTagName("trustee")

            for trustee in trustees:

                trustee_id = trustee.getElementsByTagName("id")[0]
                trustee_name = trustee.getElementsByTagName("name")[0]
                trustee_rights = trustee.getElementsByTagName("rights")[0]
                trustee_rights_value = trustee_rights.getAttribute("value")

                user_id = getText(trustee_id.childNodes)

                if user_id not in __all_trustees.keys():
                    __all_trustees[user_id] = dict(user=getText(
                        trustee_name.childNodes), files=dict())

                # trustee_name_value = getText(trustee_name.childNodes)

                # foundCN = re.search('.CN=(.*?).OU', trustee_name_value)

                # if foundCN:
                #     print("CN: ", foundCN.group(1))
                # else:
                #     print("OU", trustee_name_value)

                """
                {
                    'user': 'xxxxxxxxxx',
                    'zids': {
                        '1': 'rigths',
                        '2': 'rigths',
                        '3': 'rigths',
                    }
                }
                """

                new_dict = dict()

                new_dict[file_id] = trustee_rights_value
                __all_trustees[user_id]["files"].update(new_dict)

                # files_arr = all_trustees[user_id]["files_arr"]
                # files_arr.append({
                #     "id": file_id,
                #     "rights": trustee_rights_value
                # })

        except IndexError as e:
            print("No elements found at node!\n", e)

def get_data(delay=60, key=None):
    if len(db["files"].items()) == 0 or len(db["trustees"].items()) == 0:
        get_json_from_xml(__xml_adm)
        get_json_from_xml(__xml_ged)
        get_json_from_xml(__xml_jur)
        db["last_updated"] = time.time()
        timeFormatted = time.strftime(
            "%d/%m/%Y %H:%M:%S", time.gmtime(db["last_updated"]))
        print("# Gathering data updated at {}.".format(timeFormatted))
    else:
        now = int(time.time())
        interval = now - int(db["last_updated"])
        if interval <= delay:
            timeFormatted = time.strftime(
                "%d/%m/%Y %H:%M:%S", time.gmtime(db["last_updated"]))
            print("# Last data were updated at {}.".format(timeFormatted))
        else:
            get_json_from_xml(__xml_adm)
            get_json_from_xml(__xml_ged)
            get_json_from_xml(__xml_jur)
            db["last_updated"] = time.time()
            timeFormatted = time.strftime(
                "%d/%m/%Y %H:%M:%S", time.gmtime(db["last_updated"]))
            print("# Loading latest data at {}.".format(timeFormatted))
    if key is not None:
        if key in db:
            return db[key]
        else:
            return dict()
    return db


def get_all_volumes():
    return get_data(key="volumes")


def get_all_files():
    return get_data(key="files")


def get_all_trustees():
    return get_data(key="trustees")


def search_files_by_username(username):
    new_trustee = {}
    trusteees = get_data(key="trustees")
    for trustee in trusteees.values():
        name = re.search(username, trustee["user"])
        # foundCN = re.search('.CN=(.*?).OU', trustee_name_value)

        if name:
            files = []
            for (k, v) in trustee["files"].items():
                file_tmp = __all_files[k]
                file_tmp["id"] = k
                file_tmp["rights"] = v
                files.append(file_tmp)
            new_trustee["files"] = files
            new_trustee["name"] = trustee["user"]
            break

    return new_trustee


def search_file_by_id(id):
    file = get_data(key="files").get(id)
    if file is not None:
        return {id: file}
    else:
        return {}


def searchFilesByVolume(volume):
    files_arr = dict()
    files = get_data(key="files")
    for (id, file) in files.items():
        if file["volume"] == volume:
            files_arr[id] = file
    return files_arr


if __name__ == "__main__":

    now = int(time.time())
    limit = now + 30

    while now <= limit:
        get_data()
        now = int(time.time())
        print(now, limit)

    # print("\n## Volumes ##\n")
    # print(all_volumes)
    # print("\n## Files ##\n")
    # print(all_files)
    # print("\n## Trustees ##\n")
    # print(all_trustees)

    # print(db["volumes"])

    # user = searchFilesByUsername("FlavioB")
    # print(user)
