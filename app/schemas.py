from marshmallow import Schema, fields, validate

class UserCreateSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=3))
    password = fields.String(required=True, validate=validate.Length(min=8))
    role = fields.String(required=True)  # Can be 'student', 'teacher', or 'admin'

class UserLoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)

class GradeUpdateSchema(Schema):
    pure_maths = fields.Float(required=False, validate=validate.Range(min=0, max=100))
    chemistry = fields.Float(required=False, validate=validate.Range(min=0, max=100))
    biology = fields.Float(required=False, validate=validate.Range(min=0, max=100))
    computer_science = fields.Float(required=False, validate=validate.Range(min=0, max=100))
    physics = fields.Float(required=False, validate=validate.Range(min=0, max=100))
