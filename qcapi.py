import logging
import requests
import time
import uuid


class QCAPIError(Exception):
    pass


class QCClient(object):
    BASE_URL = 'https://www.quantconnect.com/api/v1'
    logger = logging.getLogger('qcapi.QCAPI')

    def __init__(self, username, password):
        self._auth = (username, password)

    @classmethod
    def from_config(cls, cfg):
        """Initialize a QCClient from a config dictionary."""
        username = cfg['username']
        password = cfg['password']
        return cls(username, password)

    def perform(self, route, *args, **kwargs):
        kwargs.setdefault('auth', self._auth)
        r = requests.post(self.BASE_URL + route, *args, **kwargs)
        r.raise_for_status()
        result = r.json()
        if not result['success']:
            raise QCAPIError(result['errors'])
        return result


class QCBacktest(object):
    logger = logging.getLogger('qcapi.QCBacktest')

    def __init__(self, client, backtest_id):
        self._client = client
        self.id = backtest_id

    def read(self):
        result = self._client.perform(
            '/backtests/read',
            json={'backtestId': self.id})
        return result

    def wait(self, poll_interval_secs=1.0):
        result = None
        progress = "-1"
        while progress == "-1":
            result = self.read()
            progress = result['processingTime']
            self.logger.debug('Progress: %s', progress)
            time.sleep(poll_interval_secs)
        return result

    def delete(self):
        self._client.perform(
            '/backtests/delete',
            json={'backtestId': self.id})


class QCCompile(object):
    def __init__(self, compile_id, log):
        self.id = compile_id
        self.log = log


class QCProject(object):
    logger = logging.getLogger('qcapi.QCProject')

    def __init__(self, client, project_id, name=None):
        self._client = client
        self.id = project_id
        self.name = name

    @classmethod
    def from_config(cls, cfg):
        """Initialize a QCProject from a config."""
        client = QCClient.from_config(cfg)
        project_id = int(cfg['project_id'])
        return cls(client, project_id)

    def update(self, files):
        """Update files in the specified project with new contents.

        Args:
            files list({'name': filename, 'code': file contents})
        """
        data = {'projectId': self.id,
                'files': files}
        self._client.perform('/projects/update', json=data)

    def read(self):
        self.logger.debug('Reading project files for project id: %s', self.id)
        result = self._client.perform(
            '/projects/read',
            json={'projectId': self.id})
        return result['files']

    def compile(self, version_id=357):
        # NOTE: versionId must be included even though it is not documented in the API
        # See: https://www.quantconnect.com/forum/discussion/1018/compile-using-rest-api/p1
        self.logger.debug('Compiling project id: %s', self.id)
        result = self._client.perform(
            '/compiler/create',
            json={'projectId': self.id,
                  'versionId': version_id})
        self.logger.debug('Create compile id: %s', result['compileId'])
        return QCCompile(result['compileId'], result['log'])

    def backtest(self, name=None, compile_id=None, version_id=357):
        if name is None:
            name = str(uuid.uuid4())
        if compile_id is None:
            compile_id = self.compile().id
        data = {'projectId': self.id,
                'compileId': compile_id,
                'backtestName': name,
                'versionId': version_id}
        result = self._client.perform(
            '/backtests/create',
            json=data)
        self.logger.debug('Created backtest id: %s', result['backtestId'])
        return QCBacktest(self._client, result['backtestId'])

    def delete(self):
        data = {'projectId': self.id}
        self._client.perform('/projects/delete', json=data)


class QCAPI(object):
    logger = logging.getLogger('qcapi.QCAPI')

    def __init__(self, client):
        self._client = client

    def create_project(self, name):
        """Create a new project with the given name.

        Args:
            name (str)
        Returns:
            QCProject
        """
        result = self._client.perform(
            '/projects/create',
            json={'projectName': name})
        pid = int(result['projectId'])
        return QCProject(self, pid, name)

    def list_projects(self):
        """Get the list of all projects.

        Returns:
            list(QCProject)
        """
        resp = self._client.perform('/projects/read')
        result = []
        for prj in sorted(resp['projects'], key=lambda p: p['modified']):
            qcprj = QCProject(self._client, int(prj['id']), prj['name'])
            result.append(qcprj)
        return result
