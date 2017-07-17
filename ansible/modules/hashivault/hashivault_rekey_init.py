#!/usr/bin/env python
DOCUMENTATION = '''
---
module: hashivault_rekey_init
version_added: "1.3.2"
short_description: Hashicorp Vault rekey init module
description:
    - Module to start rekey Hashicorp Vault.
options:
    url:
        description:
            - url for vault
        default: to environment variable VAULT_ADDR
    verify:
        description:
            - verify TLS certificate
        default: to environment variable VAULT_SKIP_VERIFY
    authtype:
        description:
            - "authentication type to use: token, userpass, github, ldap"
        default: token
    token:
        description:
            - token for vault
        default: to environment variable VAULT_TOKEN
    username:
        description:
            - username to login to vault.
        default: False
    password:
        description:
            - password to login to vault.
        default: False
    secret_shares:
        description:
            - specifies the number of shares to split the master key into.
        default: 5
    secret_threshold:
        description:
            - specifies the number of shares required to reconstruct the master key.
        default: 3
    pgp_keys:
        description:
            - specifies an array of PGP public keys used to encrypt the output unseal keys.
        default: []
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_rekey_init:
        secret_shares: 7
        secret_threshold: 4
'''


def main():
    argspec = hashivault_argspec()
    argspec['secret_shares'] = dict(required=False, type='int', default=5)
    argspec['secret_threshold'] = dict(required=False, type='int', default=3)
    argspec['pgp_keys'] = dict(required=False, type='list', default=[])
    argspec['backup'] = dict(required=False, type='bool', default=False)
    module = hashivault_init(argspec)
    result = hashivault_rekey_init(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


from ansible.module_utils.basic import *
from ansible.module_utils.hashivault import *


@hashiwrapper
def hashivault_rekey_init(params):
    client = hashivault_client(params)
    # Check if rekey is on-going, exit if there is a rekey in progress
    status = client.rekey_status
    if status['started']: 
        return {'changed': False}
    secret_shares = params.get('secret_shares')
    secret_threshold = params.get('secret_threshold')
    pgp_keys = params.get('pgp_keys')
    backup = params.get('backup')
    return {'status': client.start_rekey(secret_shares, secret_threshold, pgp_keys, backup), 'changed': True}

if __name__ == '__main__':
    main()
