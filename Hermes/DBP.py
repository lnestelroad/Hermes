#!/usr/bin/env python3

# TODO: Add methods for users to add custom commands to this known list for message verification
commands = {
    'Info_Req': b'u_U',
    'Info_Rep': b'o_O',
    'Registration': b'UwU',
    'Approved': b'OwO',
    'Denied': b'OmO',
    'Update': b'UoU',
    'Acknowledged': b'u.u',
    'Heartbeat': b'<3',
    'Disconnect': b'</3',
    'Exit': b'<\\3',
    'Handler': b'^o^',
    'Pong': b'pong',
    'Ping': b'ping'
}

command_checks = {
    b'u_U': 'Info_Req',
    b'o_O': 'Info_Rep',
    b'UwU': 'Registration',
    b'OwO': 'Approved',
    b'OmO': 'Denied',
    b'UoU': 'Update',
    b'u.u': 'Acknowledged',
    b'<3': 'Heartbeat',
    b'</3': 'Disconnect',
    b'<\\3': 'Exit',
    b'^o^': 'Handler'
}
