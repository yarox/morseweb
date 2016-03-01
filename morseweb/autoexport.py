from peewee import SqliteDatabase, Model, CharField, DateTimeField
from os import path, environ

import subprocess
import logging
import glob


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


MORSEWEB_ROOT = path.realpath(__file__).rsplit("morseweb", 1)[0]

MORSEWEB_DATA = path.join(path.dirname(MORSEWEB_ROOT), "morseweb/web/models")
MORSE_DATA = path.join(environ.get("MORSE_ROOT", "/"), "share/morse/data")

RESOURCES = environ.get("MORSE_RESOURCE_PATH", "").split(":") + [MORSE_DATA]
RESOURCES = [path.join(resource, "**/*.blend")
             for resource in RESOURCES if resource]

EXPORT_COMMAND = "blender -b --addons io_three -P {} -- -f {} -o {}"
EXPORT_SCRIPT = path.join(MORSEWEB_ROOT, "utils/export.py")

DB = SqliteDatabase(path.join(MORSEWEB_ROOT, "blender-models.db"))


class BlenderModel(Model):
    name = CharField(unique=True)
    path = CharField()
    last_update = DateTimeField()

    def __repr__(self):
        return "BlenderModel('{}', {}, {})".format(self.name,
                                                   self.path,
                                                   self.last_update)

    class Meta:
        database = DB


def populate(pathname, recursive=True):
    for resource in glob.glob(pathname, recursive=recursive):
        name = path.splitext(path.basename(resource))[0].lower()
        last_update = path.getmtime(resource)

        if not name.startswith("morse_default"):
            defaults = {"last_update": last_update, "path": resource}
            obj, _ = BlenderModel.get_or_create(name=name, defaults=defaults)

            if obj.last_update != last_update:
                obj.last_update = last_update
                obj.save()


def export(model_names):
    environ["BLENDER_USER_SCRIPTS"] = path.join(MORSEWEB_ROOT, "blender_scripts")

    for obj in BlenderModel.select().where(BlenderModel.name << model_names):
        resource = path.join(MORSEWEB_DATA, obj.name + ".json")

        if (not path.isfile(resource)) or \
           (obj.last_update > path.getmtime(resource)):
            subprocess.run(EXPORT_COMMAND.format(EXPORT_SCRIPT, obj.path,
                                                 MORSEWEB_DATA), shell=True)


def init():
    DB.connect()

    if not BlenderModel.table_exists():
        DB.create_table(BlenderModel)

    for pathname in RESOURCES:
        populate(pathname)
