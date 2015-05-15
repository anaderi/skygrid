from flask import request, g

UID_HEADER = 'HTTP_X_AUTH_UID'
LOGIN_HEADER = 'HTTP_X_AUTH_LOGIN'
EMAIL_HEADER = 'HTTP_X_AUTH_EMAIL'
FULLNAME_HEADER = 'HTTP_X_AUTH_FULLNAME'

required_headers = (
    UID_HEADER,
    LOGIN_HEADER,
    EMAIL_HEADER,
    FULLNAME_HEADER,
)


def check_headers(headers):
    for header_name in required_headers:
        if header_name not in headers:
            return False

    g.user = headers[LOGIN_HEADER]
    return True
