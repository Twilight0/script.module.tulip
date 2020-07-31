# -*- coding: utf-8 -*-

'''
    Tulip library
    Author Twilight0

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/GPL-3.0-only for more information.
'''


from __future__ import absolute_import

import re, hashlib, time, os
from ast import literal_eval as evaluate
try:
    from tulip import control
except Exception:
    control = None
from tulip.compat import str, database


# noinspection PyUnboundLocalVariable
def get(function_, time_out, *args, **table):

    try:

        response = None

        f = repr(function_)
        f = re.sub(r'.+\smethod\s|.+function\s|\sat\s.+|\sof\s.+', '', f)

        a = hashlib.md5()
        for i in args:
            a.update(str(i))
        a = str(a.hexdigest())

    except Exception:

        pass

    try:
        table = table['table']
    except Exception:
        table = 'rel_list'

    try:

        if control:
            control.makeFile(control.dataPath)
            dbcon = database.connect(control.cacheFile)
        else:
            db_file = os.path.join(os.path.curdir, 'cache.db')
            dbcon = database.connect(db_file)

        dbcur = dbcon.cursor()
        dbcur.execute("SELECT * FROM {tn} WHERE func = '{f}' AND args = '{a}'".format(tn=table, f=f, a=a))
        match = dbcur.fetchone()

        try:
            response = evaluate(match[2].encode('utf-8'))
        except AttributeError:
            response = evaluate(match[2])

        t1 = int(match[3])
        t2 = int(time.time())
        update = (abs(t2 - t1) / 3600) >= int(time_out)
        if not update:
            return response

    except Exception:

        pass

    try:

        r = function_(*args)
        if (r is None or r == []) and response is not None:
            return response
        elif r is None or r == []:
            return r

    except Exception:
        return

    try:

        r = repr(r)
        t = int(time.time())
        dbcur.execute(
            "CREATE TABLE IF NOT EXISTS {} (""func TEXT, ""args TEXT, ""response TEXT, ""added TEXT, ""UNIQUE(func, args)"");".format(table)
        )
        dbcur.execute("DELETE FROM {0} WHERE func = '{1}' AND args = '{2}'".format(table, f, a))
        dbcur.execute("INSERT INTO {} Values (?, ?, ?, ?)".format(table), (f, a, r, t))
        dbcon.commit()

    except Exception:
        pass

    try:
        return evaluate(r.encode('utf-8'))
    except Exception:
        return evaluate(r)


# noinspection PyUnboundLocalVariable
def timeout(function_, *args, **table):

    try:
        response = None

        f = repr(function_)
        f = re.sub(r'.+\smethod\s|.+function\s|\sat\s.+|\sof\s.+', '', f)

        a = hashlib.md5()
        for i in args:
            a.update(str(i))
        a = str(a.hexdigest())
    except Exception:
        pass

    try:
        table = table['table']
    except Exception:
        table = 'rel_list'

    try:

        if control:

            control.makeFile(control.dataPath)
            dbcon = database.connect(control.cacheFile)

        else:

            db_file = os.path.join(os.path.curdir, 'cache.db')
            dbcon = database.connect(db_file)

        dbcur = dbcon.cursor()
        dbcur.execute("SELECT * FROM {tn} WHERE func = '{f}' AND args = '{a}'".format(tn=table, f=f, a=a))
        match = dbcur.fetchone()
        return int(match[3])

    except Exception:

        return


def clear(table=None, withyes=False, notify=True, file_=None, label_yes_no=30401, label_success=30402):

    if file_ is None:
        if control:
            file_ = control.cacheFile
        else:
            file_ = os.path.join(os.path.curdir, 'cache.db')

    try:
        if control:
            control.idle()

        if table is None:
            table = ['rel_list', 'rel_lib']
        elif not type(table) == list:
            table = [table]

        if withyes and control:

            try:
                yes = control.yesnoDialog(control.lang(label_yes_no).encode('utf-8'), '', '')
            except Exception:
                yes = control.yesnoDialog(control.lang(label_yes_no), '', '')

            if not yes:
                return

        dbcon = database.connect(file_)
        dbcur = dbcon.cursor()

        for t in table:
            try:
                dbcur.execute("DROP TABLE IF EXISTS {0}".format(t))
                dbcur.execute("VACUUM")
                dbcon.commit()
            except Exception:
                pass

        if control and notify:
            control.infoDialog(control.lang(label_success).encode('utf-8'))
    except Exception:
        pass


def delete(withyes=True, label_yes_no=30401, label_success=30402):

    if withyes:

        yes = control.yesnoDialog(control.lang(label_yes_no).encode('utf-8'), '', '')

        if not yes:
            return

    else:

        pass

    control.deleteFile(control.cacheFile)

    control.infoDialog(control.lang(label_success).encode('utf-8'))
