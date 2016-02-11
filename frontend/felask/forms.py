# -*- coding: utf-8 -*-

""" Factory and blueprints patterns """

##################################################
# Security redirect back with Flask-wtf
# http://flask.pocoo.org/snippets/63/

from flask import request, url_for, redirect, flash
from flask.ext.wtf import Form
from wtforms import StringField, \
    HiddenField, PasswordField  # , \ validators
from wtforms.validators import DataRequired, EqualTo, Length
# from wtforms.validators import Email, Required
from wtforms_alchemy import model_form_factory
try:  # python3
    from urllib.parse import urlparse, urljoin
except:  # python2
    from urlparse import urlparse, urljoin
from .basemodel import MyModel


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


def get_redirect_target():
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target


class RedirectForm(Form):

    next = HiddenField()

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        if not self.next.data:
            self.next.data = get_redirect_target() or ''

    def redirect(self, endpoint='index', **values):
        if is_safe_url(self.next.data):
            return redirect(self.next.data)
        target = get_redirect_target()
        return redirect(target or url_for(endpoint, **values))


##################################################
# https://exploreflask.com/forms.html
class FlaskForm(RedirectForm):

    def validate(self):
        rv = RedirectForm.validate(self)
        # flash("Validating!", 'warning')
        if not rv:
            flash("Failed", 'danger')
            return False
        return True

ModelForm = model_form_factory(FlaskForm)

# CUSTOM VALIDATOR
# def my_length_check(form, field):
#     if len(field.data) > 5:
#         raise ValidationError('Field must be less than 50 characters')
# INSIDE THE FORM
#     #some = StringField('Some', validators=[Required(), my_length_check])


###########################
class DataForm(ModelForm):
    class Meta:
        model = MyModel

#     def validate(self):
#         rv = FlaskForm.validate(self)
# # Note:
# # Add code here to make db operations
#         return rv
###########################


##################################################
# ORIGINALS
class RegisterForm(Form):
    name = StringField(
        'Username', validators=[DataRequired(), Length(min=6, max=25)]
    )
    email = StringField(
        'Email', validators=[DataRequired(), Length(min=6, max=40)]
    )
    password = PasswordField(
        'Password', validators=[DataRequired(), Length(min=6, max=40)]
    )
    confirm = PasswordField(
        'Repeat Password',
        [DataRequired(),
         EqualTo('password', message='Passwords must match')]
    )


class ForgotForm(Form):
    email = StringField('Email',
                        validators=[DataRequired(), Length(min=6, max=40)])
