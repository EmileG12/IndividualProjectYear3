from prphish.models import User
import pytest
from os import path
import os
from prphish.models import EmailTemplate


def getEmailTemplate(name):
    return (open('./testingfiles/emailtemplates/testemail.html', 'rb'), name)


def test_add_template_missing_parameters(app, client, auth):
    auth.login()
    response = client.post(
        '/addtemplate',
        data={}, follow_redirects=True)
    assert b"Template name is mandatory" in response.data


def test_add_template_missing_parameters(app, client, auth):
    auth.login()
    response = client.post(
        '/addtemplate',
        data={'templatename': 'templatename'}, follow_redirects=True)
    assert b"Email body is mandatory" in response.data


def test_add_template_email(app, client, auth):
    auth.login()
    app.app_context().push()

    name = 'templatename'
    emailtemplatename = 'testemail.html'
    savedpath = path.join(app.instance_path,
                          'Templates', emailtemplatename)

    # make sure the entry doesn't exist
    try:
        emailtemplate = EmailTemplate.query.filter_by(name=name)
        if emailtemplate:
            emailtemplate.delete()
        os.remove(savedpath)
    except:
        pass

    response = client.post(
        '/addtemplate',
        data={'templatename': name, 'emailTemplate': getEmailTemplate(emailtemplatename)}, follow_redirects=True)
    assert b"Template Preview" in response.data
    savedpath = path.join(app.instance_path,
                          'Templates', emailtemplatename)
    # check the file is saved
    assert path.exists(savedpath)
    # check the entry in the db exists
    emailtemplate = EmailTemplate.query.filter_by(name=name).first()
    assert emailtemplate
    assert emailtemplate.path == savedpath
