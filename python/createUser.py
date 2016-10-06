import base64
import sqlite3
from datetime import date
from http import cookies

from Crypto.Cipher import AES
from passlib.hash import sha256_crypt

import utils


def handleCreateUser(request):
    conn = sqlite3.connect('famdb.db', detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    login = request.rfile.readline().decode().replace("\n", "")
    email = request.rfile.readline().decode().replace("\n", "")
    passw = request.rfile.readline().decode().replace("\n", "")
    c.execute('''select * from users where login = ?''', [login])
    if c.fetchone() is None:
        c.execute('''insert into users (login, password, email, lastLogin, permissionLevel) values (?, ?, ?, ?, ?)''',
                  [login, sha256_crypt.encrypt(passw), email, date.today(), 0])
        c.execute('''select * from users where login = ?''', [login])
        user = c.fetchone()
        cookie = cookies.SimpleCookie()
        cookie['sessionId'] = bytes.decode(
            base64.b64encode(AES.new(utils.sessionGenKey).encrypt(user['id'].to_bytes(16, byteorder='big'))))
        request.send_response(200)
        request.send_header('set-cookie', cookie.output(header=''))
        request.end_headers()
        conn.commit()
        conn.close()
    return
