from peewee import SqliteDatabase, Model, CharField, DateTimeField
from os import path, environ

import subprocess
import logging
import glob
import re


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


MORSEWEB_ROOT = path.realpath(__file__).rsplit("morseweb", 1)[0]

MORSEWEB_DATA = path.join(path.dirname(MORSEWEB_ROOT), "morseweb/webapp/static/json")
MORSE_DATA = path.join(environ.get("MORSE_ROOT", "/"), "share/morse/data")

RESOURCES = [MORSE_DATA] + environ.get("MORSE_RESOURCE_PATH", "").split(":")
RESOURCES = [path.join(resource, "**/*.blend")
             for resource in RESOURCES if resource]

EXPLORE_COMMAND = "blender -b -P {} -- {} 2> /dev/null"
EXPLORE_SCRIPT = path.join(MORSEWEB_ROOT, "utils/explore.py")

EXPORT_COMMAND = "blender -b --addons io_three -P {} -- {} -n {} -o {} 2> /dev/null"
EXPORT_SCRIPT = path.join(MORSEWEB_ROOT, "utils/export.py")

DB = SqliteDatabase(path.join(MORSEWEB_ROOT, "blender-models.db"))


class BlenderModel(Model):
    name = CharField()
    path = CharField()
    last_update = DateTimeField()

    @classmethod
    def update_or_insert(cls, name, path, last_update):
        defaults = {"last_update": last_update}
        name = name.lower()

        obj, _ = cls.get_or_create(name=name, path=path, defaults=defaults)
        obj.last_update = last_update
        obj.save()

    def __repr__(self):
        s = "BlenderModel('{}', '{}', {})"
        return s.format(self.name, self.path, self.last_update)

    class Meta:
        database = DB


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
    query = BlenderModel.select().where(BlenderModel.path << resources)

    resources_old = set(obj.path for obj in query
                                 if obj.last_update == updates[obj.path] )
    resources_new = set(resources) - resources_old
    models_old = [(obj.name, obj.path) for obj in query]

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

    for obj in BlenderModel.select().where(BlenderModel.name << model_names):
        resource = path.join(MORSEWEB_DATA, obj.name + ".json")

        if (not path.isfile(resource)) or \
           (obj.last_update > path.getmtime(resource)):
            paths.append(obj.path)
            names.append(obj.name)

    if paths:
        command = EXPORT_COMMAND.format(EXPORT_SCRIPT, " ".join(paths),
                                        " ".join(names), MORSEWEB_DATA)
        subprocess.run(command, shell=True)


def init():
    DB.connect()

    if not BlenderModel.table_exists():
        DB.create_table(BlenderModel)

    for pathname in RESOURCES:
        populate(pathname)
