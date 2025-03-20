from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SubmitField, PasswordField, SelectField, FileField, MultipleFileField, HiddenField
from wtforms.validators import DataRequired, NumberRange, Email, Length, ValidationError, Optional
from flask_wtf.file import FileAllowed

class AdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    telegram_id = IntegerField('Telegram ID', validators=[DataRequired()])
    username = StringField('Имя пользователя', validators=[Optional(), Length(min=2, max=100)])
    first_name = StringField('Имя', validators=[DataRequired(), Length(min=2, max=100)])
    last_name = StringField('Фамилия', validators=[Optional(), Length(min=2, max=100)])
    submit = SubmitField('Сохранить')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class CourseForm(FlaskForm):
    name = StringField('Название курса', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    min_age = IntegerField('Минимальный возраст', validators=[DataRequired(), NumberRange(min=6, max=18)])
    max_age = IntegerField('Максимальный возраст', validators=[DataRequired(), NumberRange(min=6, max=18)])
    tags = StringField('Теги (через запятую)', validators=[DataRequired()])
    submit = SubmitField('Сохранить курс')

    def validate_max_age(self, field):
        if field.data < self.min_age.data:
            raise ValidationError('Максимальный возраст должен быть больше минимального')

class DistrictForm(FlaskForm):
    name = StringField('Название района', validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Сохранить')

class LocationForm(FlaskForm):
    address = StringField('Адрес', validators=[DataRequired(), Length(min=5, max=200)])
    submit = SubmitField('Сохранить')

    def __init__(self, district_id=None, *args, **kwargs):
        super(LocationForm, self).__init__(*args, **kwargs)
        self._district_id = district_id

    @property
    def district_id(self):
        return self._district_id

class NewsCategoryForm(FlaskForm):
    name = StringField('Название категории', validators=[DataRequired(), Length(min=2, max=50)])
    slug = StringField('Slug (для URL)', validators=[DataRequired(), Length(min=2, max=50)])
    description = TextAreaField('Описание', validators=[Optional()])
    submit = SubmitField('Сохранить категорию')

class NewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired(), Length(min=3, max=255)])
    category_id = SelectField('Категория', coerce=int, validators=[Optional()])
    tags = StringField('Теги', validators=[Optional()])
    content = TextAreaField('Содержание', validators=[DataRequired(), Length(min=10)])
    images = MultipleFileField('Изображения', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Разрешены только изображения!')
    ])
    submit = SubmitField('Сохранить новость')

class NewsCommentForm(FlaskForm):
    news_id = HiddenField('ID новости', validators=[DataRequired()])
    parent_id = HiddenField('ID родительского комментария')
    content = TextAreaField('Комментарий', validators=[DataRequired(), Length(min=2)])
    submit = SubmitField('Отправить комментарий')