

def test_basic(app):

    with app.test_client() as c:

        resp = c.get('/')
        print resp.data
        assert resp.status_code == 200
