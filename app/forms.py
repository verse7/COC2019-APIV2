from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired, Email


# class GenericForm(FlaskForm):
#     field1 = StringField('field1', validators=[InputRequired()])
#     field2 = TextAreaField('field2', validators=[InputRequired()])
#     field3 = FileField('field3', validators=[FileRequired(),  FileAllowed(['jpg','jpeg', 'png', 'Only images are accepted!'])])
    
class RegistrationForm(FlaskForm):
    class Meta:
      csrf = False
    firstname = StringField('firstname', validators=[InputRequired()])
    lastname = StringField('lastname', validators=[InputRequired()])
    email = StringField('email', validators=[Email(), InputRequired()])
    password = StringField('password', validators=[InputRequired()])


class LoginForm(FlaskForm):
    class Meta:
        csrf = False
    email = StringField('email', validators=[Email(), InputRequired()])
    password = StringField('password', validators=[InputRequired()])


class GroupForm(FlaskForm):
    class Meta:
        csrf = False
    name = StringField('name', validators=[InputRequired()])


class JSONField(StringField):
    def _value(self):
        return json.dumps(self.data) if self.data else ''
    
    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = json.loads(valuelist[0])
            except ValueError:
                raise ValueError('This field contains invalid JSON')
        else:
            self.data = None
    
    def pre_validate(self, form):
        super().pre_validate(form)
        if self.data:
            try:
                json.dumps(self.data)
            except TypeError:
                raise ValueError('This field contains invalid JSON')


class EventForm(FlaskForm):
    class Meta:
        csrf = False
    image = FileField('photo', validators=[FileAllowed(['jpg','jpeg', 'Only jpeg images are accepted!'])])
    details = JSONField('details', validators=[InputRequired()])