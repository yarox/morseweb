from peewee import SqliteDatabase, Model, CharField, DateTimeField
from os import path


MORSEWEB_ROOT = path.realpath(__file__).rsplit("morseweb", 1)[0]
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

    @classmethod
    def get_models_from_names(cls, names):
        return cls.select().where(cls.name << names)

    @classmethod
    def get_models_from_paths(cls, paths):
        return cls.select().where(cls.path << paths)

    @classmethod
    def get_models_from_environment(cls, environment):
        return cls.select().where((cls.path == environment.path) &
                                  (cls.name != environment.name))

    def __repr__(self):
        s = "BlenderModel('{}', '{}', {})"
        return s.format(self.name, self.path, self.last_update)

    class Meta:
        database = DB
