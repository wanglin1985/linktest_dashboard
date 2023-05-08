from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Email, Regexp

from modules import User


class RegistForm(FlaskForm):
    user_name = StringField(
        label="UserName",
        validators=[
            DataRequired("username required")
        ],
        description="user name",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "username",
        }
    )
    email = StringField(
        label="Email",
        validators=[
            DataRequired("email required"),
            Email("Incorrect email format!")
        ],
        description="email",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "input email",
        }
    )
    # phone = StringField(
    #     label="phone",
    #     validators=[
    #         DataRequired("phone！"),
    #         Regexp("1[3458]\\d{9}", message="incorrect phone format！")
    #     ],
    #     description="phone",
    #     render_kw={
    #         "class": "form-control input-lg",
    #         "placeholder": "input phone",
    #     }
    # )
    pwd = PasswordField(
        label="Password",
        validators=[
            DataRequired("input password！")
        ],
        description="password",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "input password",
        }
    )
    repwd = PasswordField(
        label="Re-enter Password",
        validators=[
            DataRequired("Re-enter password"),
            EqualTo('pwd', message="Two passwords not match！")
        ],
        description="PasswordConfirm",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "confirm password",
        }
    )
    submit = SubmitField(
        'submit',
        render_kw={
            "class": "btn btn-lg btn-primary btn-block",
        }
    )

    def validate_user_name(self, field):
        user_name = field.data
        user_name = User.query.filter_by(user_name=user_name).count()
        if user_name == 1:
            raise ValidationError("UserName already exists")

    def validate_email(self, field):
        email = field.data
        user = User.query.filter_by(email=email).count()
        if user == 1:
            raise ValidationError("Email already exists！")


class LoginForm(FlaskForm):
    name = StringField(
        label="Account",
        validators=[
            DataRequired("Please input your account!")
        ],
        description="Account",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "Input username",
        }
    )
    pwd = PasswordField(
        label="Password",
        validators=[
            DataRequired("Please input password")
        ],
        description="Password",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "input password",
        }
    )
    submit = SubmitField(
        'Login',
        render_kw={
            "class": "btn btn-lg btn-primary btn-block",
        }
    )
