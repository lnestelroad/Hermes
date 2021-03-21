#!/usr/bin/env python3

protocols = {
    'Info_Req': b'u_U',
    'Info_Rep': b'o_O',
    'Registration': b'UwU',
    'Approved': b'OwO',
    'Denied': b'OmO',
    'Update': b'UoU',
    'Acknowledged': b'u.u'
}

protocol_checks = {
    b'u_U': 'Info_Req',
    b'o_O': 'Info_Rep',
    b'UwU': 'Registration',
    b'OwO': 'Approved',
    b'OmO': 'Denied',
    b'UoU': 'Update',
    b'u.u': 'Acknowledged'
}
