"""Minimal end-to-end MCP client for IamCarla: OAuth 2.1 with PKCE, then tools/list.

    python pkce_client.py [--base https://iamcarla.it]

Steps: discover the authorization server, register a public client, open the consent page in your
browser (sign in as the owner and type the pairing code from your collaboratore), exchange the
code, call initialize and tools/list. Requires only the standard library.

MIT licence.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import http.server
import json
import secrets
import sys
import threading
import urllib.parse
import urllib.request
import webbrowser

REDIRECT_PORT = 8765
REDIRECT_URI = f'http://127.0.0.1:{REDIRECT_PORT}/callback'


def _json(url: str, data: dict | None = None, form: bool = False, headers: dict | None = None) -> dict:
    body = None
    hdrs = {'Accept': 'application/json', **(headers or {})}
    if data is not None:
        if form:
            body = urllib.parse.urlencode(data).encode()
            hdrs['Content-Type'] = 'application/x-www-form-urlencoded'
        else:
            body = json.dumps(data).encode()
            hdrs['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, data=body, headers=hdrs, method='POST' if body is not None else 'GET')
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors='replace')
        raise SystemExit(f'{exc.code} from {url}: {detail[:400]}') from None


def _wait_for_code(expected_state: str) -> str:
    result: dict = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            result.update({k: v[0] for k, v in query.items()})
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write('Puoi chiudere questa finestra. / You can close this window.'.encode())

        def log_message(self, *_args):
            pass

    server = http.server.HTTPServer(('127.0.0.1', REDIRECT_PORT), Handler)
    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()
    thread.join(timeout=900)
    server.server_close()
    if 'error' in result:
        raise SystemExit(f"authorization refused: {result['error']}")
    if result.get('state') != expected_state or 'code' not in result:
        raise SystemExit('no authorization code received (timeout or state mismatch)')
    return result['code']


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', default='https://iamcarla.it')
    args = parser.parse_args()
    base = args.base.rstrip('/')
    mcp_url = base + '/mcp'

    meta = _json(base + '/.well-known/oauth-authorization-server')
    print('authorization server:', meta['issuer'])

    client = _json(meta['registration_endpoint'], {
        'client_name': 'IamCarla example client',
        'redirect_uris': [REDIRECT_URI],
        'token_endpoint_auth_method': 'none',
        'grant_types': ['authorization_code', 'refresh_token'],
    })
    client_id = client['client_id']
    print('registered client:', client_id)

    verifier = secrets.token_urlsafe(48)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b'=').decode()
    state = secrets.token_urlsafe(16)
    authorize_url = meta['authorization_endpoint'] + '?' + urllib.parse.urlencode({
        'response_type': 'code', 'client_id': client_id, 'redirect_uri': REDIRECT_URI,
        'code_challenge': challenge, 'code_challenge_method': 'S256', 'state': state,
        'scope': 'read', 'resource': mcp_url,
    })
    print('opening the consent page; sign in as the owner and enter the pairing code:')
    print(authorize_url)
    webbrowser.open(authorize_url)
    code = _wait_for_code(state)

    tokens = _json(meta['token_endpoint'], {
        'grant_type': 'authorization_code', 'client_id': client_id, 'code': code,
        'redirect_uri': REDIRECT_URI, 'code_verifier': verifier, 'resource': mcp_url,
    }, form=True)
    access = tokens['access_token']
    print('access token obtained; scope:', tokens.get('scope'))

    def rpc(method: str, params: dict | None = None, req_id: int = 1) -> dict:
        return _json(mcp_url, {'jsonrpc': '2.0', 'id': req_id, 'method': method, 'params': params or {}},
                     headers={'Authorization': f'Bearer {access}'})

    init = rpc('initialize', {'protocolVersion': '2025-06-18', 'capabilities': {},
                              'clientInfo': {'name': 'pkce-example', 'version': '1.0'}})
    info = init['result']['serverInfo']
    print(f"server: {info['name']} {info['version']}")
    tools = rpc('tools/list', req_id=2)['result']['tools']
    print(f'{len(tools)} tools available, for example:')
    for t in tools[:10]:
        print(' -', t['name'])
    sys.exit(0)


if __name__ == '__main__':
    main()
