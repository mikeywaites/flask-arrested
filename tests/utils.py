def assertResponse(resp, exp_resp):

    assert all(
        [
            resp.response == exp_resp.response,
            resp.headers == exp_resp.headers,
            resp.mimetype == exp_resp.mimetype,
            resp.status == exp_resp.status,
        ]
    )
