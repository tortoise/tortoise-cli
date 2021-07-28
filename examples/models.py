from tortoise import Model, fields


class User(Model):
    name = fields.CharField(max_length=20)
    age = fields.IntField()
