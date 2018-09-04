
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible import constants as C
from ansible.plugins.action import ActionBase
from ansible.utils.vars import merge_hash
from ansible.module_utils._text import to_bytes, to_native, to_text
from ansible.module_utils.basic import FILE_COMMON_ARGUMENTS


from ansible.plugins.action.template import ActionModule as _ActionModule

import pprint
import os
import os.path
import tempfile


class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):

        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(task_vars)

        if self._task.args.get('auto_renew_http'):
            self.setup_renewal()

        args = self._task.args.copy()

        result = super(ActionModule, self).run(tmp, task_vars)

        if not result.get('skipped'):

            wrap_async = self._task.async_val and not self._connection.has_native_async  # noqa: E501

            result = merge_hash(result,
                                self._execute_module(task_vars=args,
                                                     wrap_async=wrap_async))

        if self._task.args.get('auto_renew_http'):
            self.setup_renewal()

        return result

    def setup_renewal(self):
        self._copy_template('certbot.service',
                            '/etc/systemd/system/certbot.service')
        self._copy_template(
            'certbot.timer', '/etc/systemd/system/certbot.timer')

    def _copy_template(self, src, dest):

        # pp = pprint.PrettyPrinter(indent=4)

        mypath = os.path.abspath(
            os.path.join(
                os.path.join(self._original_path, os.pardir),
                os.pardir)
        )

        source = os.path.join(
            mypath,
            'templates',
            src)

        try:
            with open(source, 'r') as f:
                template_data = to_text(f.read())
        except IOError:
            return dict(failed=True, msg='unable to load src file')

        print(template_data)
        templated = self._templar.template(template_data)

        content_tempfile = self._create_content_tempfile(templated)

        self._transfer_file(content_tempfile, dest)

    def _create_content_tempfile(self, content):
        ''' Create a tempfile containing defined content '''
        fd, content_tempfile = tempfile.mkstemp(dir=C.DEFAULT_LOCAL_TMP)
        f = os.fdopen(fd, 'wb')
        content = to_bytes(content)
        try:
            f.write(content)
        except Exception as err:
            os.remove(content_tempfile)
            raise Exception(err)
        finally:
            f.close()
        return content_tempfile


# From copy plugin....

# Supplement the FILE_COMMON_ARGUMENTS with arguments that are specific to file
# FILE_COMMON_ARGUMENTS contains things that are not arguments of file
# so remove those as well
REAL_FILE_ARGS = frozenset(FILE_COMMON_ARGUMENTS.keys()).union(
                          ('state', 'path', '_original_basename',
                           'recurse', 'force',
                           '_diff_peek', 'src')).difference(
                          ('content', 'decrypt', 'backup', 'remote_src',
                           'regexp', 'delimiter',
                           'directory_mode', 'unsafe_writes'))


def _create_remote_file_args(module_args):
    """remove keys that are not relevant to file"""
    return dict((k, v) for k, v in module_args.items() if k in REAL_FILE_ARGS)
