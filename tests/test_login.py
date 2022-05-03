from prphish.models import User
import pytest


# test get pages are protected by login
@pytest.mark.parametrize(
    "page, expected",
    [('/adduser',  b"Add user"), ('/getresponses', b'Reports'),
     ('manageemails', b'Email Manager'), ('sendemail', b'Send Campaign'),
     ('/templatemanager', b'Template Manager'), ('addtemplate', b'Add Template')],
)
def test_protected_page(client, auth, page, expected):
    response = client.get(page)
    # we are redirected to login if not logged
    assert "/login" in response.headers.get('Location')
    auth.login()
    response = client.get(page)
    # We are in the Add user page
    assert expected in response.data


# test post pages are protected by login
@pytest.mark.parametrize(
    "page, expected",
    [('/addtemplate',  b"Template Manager"), ('sendemail',
                                              b'Send Campaign'), ('/responses', b'Reports'),
     ('/responsesIndividual', b'Reports')],
)
def test_protected_post(client, auth, page, expected):
    response = client.post(page)
    # we are redirected to login if not logged
    assert "/login" in response.headers.get('Location')
    auth.login()
    response = client.post(page, follow_redirects=True)
    # We are in the Add user page
    assert expected in response.data


def test_add_user(app, client, auth):
    app.app_context().push()
    # user is not in the db
    assert User.query.filter_by(email='name@domain.com').first() == None
    auth.login()
    response = client.post(
        '/adduser',
        data={'email': 'name@domain.com', 'name': 'name',  'password': 'password'}, follow_redirects=True)
    assert b"Test your user base without risk." in response.data
    # user has been added to the db
    assert User.query.filter_by(email='name@domain.com').first()
