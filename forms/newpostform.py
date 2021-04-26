from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileRequired, FileField


class NewPostForm(FlaskForm):
    description = TextAreaField('Описание', validators=[DataRequired()])
    media = FileField('Фотография', validators=[FileRequired('')])
    submit = SubmitField('Выложить')
