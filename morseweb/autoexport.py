from peewee import SqliteDatabase
from os import path, environ

from models import BlenderModel

import subprocess
import logging
import glob
import re


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


MORSEWEB_ROOT = path.realpath(__file__).rsplit("morseweb", 1)[0]

MORSEWEB_DATA = path.join(path.dirname(MORSEWEB_ROOT), "morseweb/static/json")
MORSE_DATA = path.join(environ.get("MORSE_ROOT", "/"), "share/morse/data")

RESOURCES = [MORSE_DATA] + environ.get("MORSE_RESOURCE_PATH", "").split(":")
RESOURCES = [path.join(resource, "**/*.blend")
             for resource in RESOURCES if resource]

EXPLORE_COMMAND = "blender -b -P {} -- {} 2> /dev/null"
EXPLORE_SCRIPT = path.join(MORSEWEB_ROOT, "utils/explore.py")

EXPORT_COMMAND = "blender -b --addons io_three -P {} -- {} -n {} -o {} 2> /dev/null"
EXPORT_SCRIPT = path.join(MORSEWEB_ROOT, "utils/export.py")


def populate(pathname, is_recursive=True):
    resources = []
    parents = []

    for blend_file in glob.glob(pathname, recursive=is_recursive):
        name = path.splitext(path.basename(blend_file))[0].lower()

        if not name.startswith("morse_default"):
            parents.append((name, blend_file))
            resources.append(blend_file)

    for name, blend_file in explore(resources) + parents:
        last_update = path.getmtime(blend_file)
        BlenderModel.update_or_insert(name, blend_file, last_update)


def explore(resources):
    """
    Return the objects inside the Blender files present in 'resources'.
    """

    updates = {r: path.getmtime(r) for r in resources if path.exists(r)}
    query = BlenderModel.get_models_from_paths(resources)

    resources_old = set(model.path for model in query
                                   if model.last_update == updates[model.path])
    resources_new = set(resources) - resources_old
    models_old = [(model.name, model.path) for model in query]

    if resources_new:
        command = EXPLORE_COMMAND.format(EXPLORE_SCRIPT, " ".join(resources_new))
        out = subprocess.run(command, shell=True, stdout=subprocess.PIPE,
                             universal_newlines=True)

        p = re.compile(r"^#{3}\s(.*)\s(/.*)\s\${3}", re.M)
        models_new = p.findall(out.stdout)
    else:
        models_new = []

    return models_old + models_new


def export(model_names):
    environ["BLENDER_USER_SCRIPTS"] = path.join(MORSEWEB_ROOT, "blender_scripts")

    paths = []
    names = []

    for model in BlenderModel.get_models_from_names(model_names):
        resource = path.join(MORSEWEB_DATA, model.name + ".json")

        if (not path.isfile(resource)) or \
           (model.last_update > path.getmtime(resource)):
            paths.append(model.path)
            names.append(model.name)

    if paths:
        command = EXPORT_COMMAND.format(EXPORT_SCRIPT, " ".join(paths),
                                        " ".join(names), MORSEWEB_DATA)
        subprocess.run(command, shell=True)


def init(dbname="blender-models.db"):
    db = SqliteDatabase(path.join(MORSEWEB_ROOT, dbname))
    db.connect()

    if not BlenderModel.table_exists():
        db.create_table(BlenderModel)

    for pathname in RESOURCES:
        populate(pathname)
