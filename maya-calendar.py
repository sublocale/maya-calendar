#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author  :  Aleksandr Tishin /Mystic-Mirage/
# Email   :  <aleksandr.tishin@gmail.com>

# License :  Public Domain

from datetime import datetime
from re import sub

import sys
from getopt import getopt

from _strptime import TimeRE

from os import path
import gettext

l10n_dir = path.join(path.realpath(path.dirname(sys.argv[0])), 'locale')
if not path.isdir(l10n_dir):
    l10n_dir = None
gettext.install('mayanc', l10n_dir)
N_ = lambda x: x

gmt = 584283
tl = 584285

default_cor = gmt
default_fmt = '%C, %Z %H' # == %b.%k.%t.%w.%i, %z2 %z3 %h2 %h3
default_sce = 1

def todaydatetuple():
    return datetime.today().timetuple()[:3]

def getmayandays(g_tuple = todaydatetuple(), cor = default_cor, bc = False):
    i_year = 0
    if bc and g_tuple == (1, 2, 29):
        g_date = datetime(1, 3, 1)
        i_year = 1
    else:
        g_date = datetime(*g_tuple)
    if bc:
        if g_date < datetime(1, 3, 1) or g_date >= datetime(2, 1, 1):
            i_year = 1
        return ((g_date - datetime(g_date.year, 12, 31)).days \
                - datetime(g_date.year, 1, 1).toordinal() \
                + 1721426 - cor - i_year) % 1872000
    else:
        return (g_date.toordinal() + 1721425 - cor)

def getlongcount(m_days, scenario = default_sce):
    d = m_days % 1872000
    result = []
    for i in (144000, 7200, 360, 20, 1):
        t, d = divmod(d, i)
        result.append(t)
    if scenario == 1 and not any(result) or \
            scenario == 2 and not result[0]:
        result[0] = 13
    return tuple(result)

def gettzolkin(m_days):
    return ((m_days % 1872000 + 19) % 20, (m_days + 3) % 13 + 1)

def gethaab(m_days):
    return divmod((m_days + 348) % 365, 20)

def getlord(m_days):
    return (m_days + 8) % 9 + 1

tzolkinlist = (N_("Imix'"), N_("Ik'"), N_("Ak'b'al"), N_("K'an"), \
        N_("Chikchan"), N_("Kimi"), N_("Manik'"), N_("Lamat"), \
        N_("Muluk"), N_("Ok"), N_("Chuwen"), N_("Eb'"), N_("B'en"), \
        N_("Ix"), N_("Men"), N_("K'ib'"), N_("Kab'an"), \
        N_("Etz'nab'"), N_("Kawak"), N_("Ajaw"))

haablist = (N_("Pop"), N_("Wo"), N_("Sip"), N_("Sotz'"), N_("Tzek"), \
        N_("Xul"), N_("Yaxk'"), N_("Mol"), N_("Ch'en"), N_("Yax"), \
        N_("Sac"), N_("Keh"), N_("Mak"), N_("K'ank'in"), N_("Muwan"), \
        N_("Pax"), N_("K'ayab'"), N_("Kumk'u"), N_("Wayeb'"))

lordlist = (N_("G1"), N_("G2"), N_("G3"), N_("G4"), N_("G5"), \
        N_("G6"), N_("G7"), N_("G8"), N_("G9"))

def getmayandatetuple(g_tuple = todaydatetuple(), cor = default_cor, \
        scenario = default_sce, bc = False):
    days = getmayandays(g_tuple, cor, bc)
    return getlongcount(days, scenario) + gettzolkin(days) + \
            gethaab(days) + (getlord(days),)

def getmayandate(g_tuple = todaydatetuple(), cor = default_cor, \
        fmt = default_fmt, scenario = default_sce, bc = False):
    m_tuple = getmayandatetuple(g_tuple, cor, scenario, bc)
    for s, r in map(lambda x, y: ('%' + x, str(y)), \
            ('C', 'Z', 'H', 'b', 'k', 't', 'w', 'i', 'z1', 'z2', \
                'h1', 'h2', 'l', 'z3', 'h3', 'L'), \
            ('%b.%k.%t.%w.%i', '%z2 %z3', '%h2 %h3') + m_tuple + \
                (_(tzolkinlist[m_tuple[5]]), _(haablist[m_tuple[7]]), \
                _(lordlist[m_tuple[9] - 1]))):
        fmt = sub(s, r, fmt)
    return fmt

def strpdate(data_string, format = '%Y-%m-%d', bc = False):
    _TimeRE_cache = TimeRE()
    _regex_cache = {}
    try:
        format_regex = _TimeRE_cache.compile(format)
    # KeyError raised when a bad format is found; can be specified as
    # \\, in which case it was a stray % but with a space after it
    except KeyError as err:
        bad_directive = err.args[0]
        if bad_directive == "\\":
            bad_directive = "%"
        del err
        raise ValueError("'%s' is a bad directive in format '%s'" %
                            (bad_directive, format))
    # IndexError only occurs when the format string is "%"
    except IndexError:
        raise ValueError("stray %% in format '%s'" % format)
    _regex_cache[format] = format_regex
    found = format_regex.match(data_string)
    if not found:
        raise ValueError("time data %r does not match format %r" %
                         (data_string, format))
    if len(data_string) != found.end():
        raise ValueError("unconverted data remains: %s" %
                          data_string[found.end():])
    date = list(todaydatetuple())
    found_dict = found.groupdict()
    for group_key in found_dict.keys():
        if group_key == 'y':
            date[0] = int(found_dict['y'])
            if date[0] <= 68:
                date[0] += 2000
            else:
                date[0] += 1900
        elif group_key == 'Y':
            date[0] = int(found_dict['Y'])
        elif group_key == 'm':
            date[1] = int(found_dict['m'])
        elif group_key == 'd':
            date[2] = int(found_dict['d'])
    if not (bc and date == [1, 2, 29]):
        datetime(*date)
    return tuple(date)

if __name__ == '__main__':
    correlation = default_cor
    gformat = '%Y-%m-%d'
    gdate = datetime.today().strftime(gformat)
    mformat = default_fmt
    scen = default_sce
    befc = False
    optlist, args = getopt(sys.argv[1:], 'c:d:g:f:s:', \
            ['gmt', 'tl', 'baktun', 'katun', 'tun', 'winal', \
            'kin', 'tzol1', 'tzol2', 'tzol3', 'haab1', 'haab2', \
            'haab3', 'lord1', 'lord2', 'long', 'tzol', 'haab', 'bc', \
            'no-l10n'])
    for p, v in optlist:
        if p == '-c':
            if v == 'gmt':
                correlation = gmt
            elif v == 'tl':
                correlation = tl
            else:
                correlation = int(v)
        elif p == '--gmt':
            correlation = gmt
        elif p == '--tl':
            correlation = tl
        elif p == '-d':
            gdate = v
        elif p == '-g':
            gformat = v
        elif p == '-f':
            mformat = v
        elif p == '-s':
            scen = int(v)
        elif p == '--baktun':
            mformat = '%b'
        elif p == '--katun':
            mformat = '%k'
        elif p == '--tun':
            mformat = '%t'
        elif p == '--winal':
            mformat = '%w'
        elif p == '--kin':
            mformat = '%i'
        elif p == '--tzol1':
            mformat = '%z1'
        elif p == '--tzol2':
            mformat = '%z2'
        elif p == '--tzol3':
            mformat = '%z3'
        elif p == '--haab1':
            mformat = '%h1'
        elif p == '--haab2':
            mformat = '%h2'
        elif p == '--haab3':
            mformat = '%h3'
        elif p == '--lord1':
            mformat = '%l'
        elif p == '--lord2':
            mformat = '%L'
        elif p == '--long':
            mformat = '%C'
        elif p == '--tzol':
            mformat = '%Z'
        elif p == '--haab':
            mformat = '%H'
        elif p == '--bc':
            befc = True
        elif p == '--no-l10n':
            _ = N_
    print(getmayandate(strpdate(gdate, gformat, befc), \
            correlation, mformat, scen, befc))
