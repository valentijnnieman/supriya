import os
import yaml
from unittest import mock
from abjad.tools import stringtools
from abjad.tools import systemtools
from supriya.tools import commandlinetools
from supriya.tools import nonrealtimetools
from commandlinetools_testbase import ProjectPackageScriptTestCase


class Test(ProjectPackageScriptTestCase):

    def test_missing_session(self):
        """
        Handle missing session.
        """
        self.create_project()
        script = commandlinetools.ManageSessionScript()
        command = ['--render', 'test_session']
        with systemtools.RedirectedStreams(stdout=self.string_io):
            with systemtools.TemporaryDirectoryChange(
                str(self.inner_project_path)):
                with self.assertRaises(SystemExit) as context_manager:
                    script(command)
                assert context_manager.exception.code == 1
        self.compare_captured_output(r'''
        Render candidates: 'test_session' ...
            No matching sessions.
        Available sessions:
            No sessions available.
        '''.replace('/', os.path.sep))

    def test_missing_definition(self):
        """
        Handle missing definition.
        """
        self.create_project()
        session_path = self.create_session('test_session')
        definition_path = session_path.joinpath('definition.py')
        definition_path.unlink()
        script = commandlinetools.ManageSessionScript()
        command = ['--render', 'test_session']
        with systemtools.RedirectedStreams(stdout=self.string_io):
            with systemtools.TemporaryDirectoryChange(
                str(self.inner_project_path)):
                with self.assertRaises(SystemExit) as context_manager:
                    script(command)
                assert context_manager.exception.code == 1
        self.compare_captured_output(r'''
            Render candidates: 'test_session' ...
            Rendering test_project/sessions/test_session/
                Importing test_project.sessions.test_session.definition
            Traceback (most recent call last):
              File ".../ProjectPackageScript.py", line ..., in _import_path
                return importlib.import_module(path)
              ...
            ImportError: No module named 'test_project.sessions.test_session.definition'
        '''.replace('/', os.path.sep))

    def test_python_cannot_render(self):
        """
        Handle un-renderables.
        """
        self.create_project()
        session_path = self.create_session('test_session')
        definition_path = session_path.joinpath('definition.py')
        with open(str(definition_path), 'w') as file_pointer:
            file_pointer.write(stringtools.normalize(r'''
            session = None
            '''))
        script = commandlinetools.ManageSessionScript()
        command = ['--render', 'test_session']
        with systemtools.RedirectedStreams(stdout=self.string_io):
            with systemtools.TemporaryDirectoryChange(
                str(self.inner_project_path)):
                with self.assertRaises(SystemExit) as context_manager:
                    script(command)
                assert context_manager.exception.code == 1
        self.compare_captured_output(r'''
            Render candidates: 'test_session' ...
            Rendering test_project/sessions/test_session/
                Importing test_project.sessions.test_session.definition
                Cannot render session of type NoneType.
        '''.replace('/', os.path.sep))

    def test_python_error_on_render(self):
        """
        Handle exceptions inside the Python module on __call__().
        """
        self.create_project()
        session_path = self.create_session('test_session')
        definition_path = session_path.joinpath('definition.py')
        with open(str(definition_path), 'w') as file_pointer:
            file_pointer.write(stringtools.normalize(r'''
            class Foo:
                def __render__(
                    self,
                    output_file_path=None,
                    render_directory_path=None,
                    **kwargs
                    ):
                    raise TypeError('This is fake.')

            session = Foo()
            '''))
        script = commandlinetools.ManageSessionScript()
        command = ['--render', 'test_session']
        with systemtools.RedirectedStreams(stdout=self.string_io):
            with systemtools.TemporaryDirectoryChange(
                str(self.inner_project_path)):
                with self.assertRaises(SystemExit) as context_manager:
                    script(command)
                assert context_manager.exception.code == 1
        self.compare_captured_output(r'''
        Render candidates: 'test_session' ...
        Rendering test_project/sessions/test_session/
            Importing test_project.sessions.test_session.definition
        Traceback (most recent call last):
          File ".../commandlinetools/ProjectSectionScript.py", line ..., in _render_object
            **kwargs
          File ".../soundfiletools/render.py", line ..., in render
            **kwargs
          File
          ".../commandlinetools/test/test_project/test_project/sessions/test_session/definition.py", line ..., in __render__
            raise TypeError('This is fake.')
        TypeError: This is fake.
        '''.replace('/', os.path.sep))

    def test_python_error_on_import(self):
        """
        Handle exceptions inside the Python module on import.
        """
        self.create_project()
        session_path = self.create_session('test_session')
        definition_path = session_path.joinpath('definition.py')
        with open(str(definition_path), 'a') as file_pointer:
            file_pointer.write('\n\nfailure = 1 / 0\n')
        script = commandlinetools.ManageSessionScript()
        command = ['--render', 'test_session']
        with systemtools.RedirectedStreams(stdout=self.string_io):
            with systemtools.TemporaryDirectoryChange(
                str(self.inner_project_path)):
                with self.assertRaises(SystemExit) as context_manager:
                    script(command)
                assert context_manager.exception.code == 1
        self.compare_captured_output(r'''
        Render candidates: 'test_session' ...
        Rendering test_project/sessions/test_session/
            Importing test_project.sessions.test_session.definition
        Traceback (most recent call last):
          File ".../commandlinetools/ProjectPackageScript.py", line ..., in _import_path
            return importlib.import_module(path)
          ...
          File ".../test_project/sessions/test_session/definition.py", line ..., in <module>
            failure = 1 / 0
        ZeroDivisionError: division by zero
        '''.replace('/', os.path.sep))

    def test_supercollider_error(self):
        self.create_project()
        self.create_session('test_session')
        script = commandlinetools.ManageSessionScript()
        command = ['--render', 'test_session']
        mock_path = nonrealtimetools.SessionRenderer.__module__
        mock_path += '._stream_subprocess'
        with systemtools.RedirectedStreams(stdout=self.string_io):
            with systemtools.TemporaryDirectoryChange(
                str(self.inner_project_path)):
                with self.assertRaises(SystemExit) as context_manager:
                    with mock.patch(mock_path) as call_mock:
                        call_mock.return_value = 1
                        script(command)
                assert context_manager.exception.code == 1
        self.compare_captured_output(r'''
        Render candidates: 'test_session' ...
        Rendering test_project/sessions/test_session/
            Importing test_project.sessions.test_session.definition
            Writing session-95cecb2c724619fe502164459560ba5d.osc.
                Wrote session-95cecb2c724619fe502164459560ba5d.osc.
            Rendering session-95cecb2c724619fe502164459560ba5d.osc.
                Command: scsynth -N session-95cecb2c724619fe502164459560ba5d.osc _ session-95cecb2c724619fe502164459560ba5d.aiff 44100 aiff int24
                Rendered session-95cecb2c724619fe502164459560ba5d.osc with exit code 1.
                SuperCollider errored!
            Python/SC runtime: 0 seconds
            Render failed. Exiting.
        '''.replace('/', os.path.sep))

    def test_supercollider_no_output(self):
        self.create_project()
        self.create_session('test_session')
        script = commandlinetools.ManageSessionScript()
        command = ['--render', 'test_session']
        mock_path = nonrealtimetools.SessionRenderer.__module__
        mock_path += '._stream_subprocess'
        with systemtools.RedirectedStreams(stdout=self.string_io):
            with systemtools.TemporaryDirectoryChange(
                str(self.inner_project_path)):
                with self.assertRaises(SystemExit) as context_manager:
                    with mock.patch(mock_path) as call_mock:
                        call_mock.return_value = 0  # no output, but no error
                        script(command)
                assert context_manager.exception.code == 1
        self.compare_captured_output(r'''
        Render candidates: 'test_session' ...
        Rendering test_project/sessions/test_session/
            Importing test_project.sessions.test_session.definition
            Writing session-95cecb2c724619fe502164459560ba5d.osc.
                Wrote session-95cecb2c724619fe502164459560ba5d.osc.
            Rendering session-95cecb2c724619fe502164459560ba5d.osc.
                Command: scsynth -N session-95cecb2c724619fe502164459560ba5d.osc _ session-95cecb2c724619fe502164459560ba5d.aiff 44100 aiff int24
                Rendered session-95cecb2c724619fe502164459560ba5d.osc with exit code 0.
                Output file is missing!
            Python/SC runtime: 0 seconds
            Render failed. Exiting.
        '''.replace('/', os.path.sep))

    def test_success_all_sessions(self):
        self.create_project()
        self.create_session('session_one')
        self.create_session('session_two')
        self.create_session('session_three')
        script = commandlinetools.ManageSessionScript()
        command = ['--render', '*']
        with systemtools.RedirectedStreams(stdout=self.string_io):
            with systemtools.TemporaryDirectoryChange(
                str(self.inner_project_path)):
                try:
                    script(command)
                except SystemExit as e:
                    raise RuntimeError('SystemExit: {}'.format(e.code))
        self.compare_captured_output(r'''
        Render candidates: '*' ...
        Rendering test_project/sessions/session_one/
            Importing test_project.sessions.session_one.definition
            Writing session-95cecb2c724619fe502164459560ba5d.osc.
                Wrote session-95cecb2c724619fe502164459560ba5d.osc.
            Rendering session-95cecb2c724619fe502164459560ba5d.osc.
                Command: scsynth -N session-95cecb2c724619fe502164459560ba5d.osc _ session-95cecb2c724619fe502164459560ba5d.aiff 44100 aiff int24
                Rendered session-95cecb2c724619fe502164459560ba5d.osc with exit code 0.
            Writing test_project/sessions/session_one/render.yml.
                Wrote test_project/sessions/session_one/render.yml.
            Python/SC runtime: 0 seconds
            Rendered test_project/sessions/session_one/
        Rendering test_project/sessions/session_three/
            Importing test_project.sessions.session_three.definition
            Writing session-95cecb2c724619fe502164459560ba5d.osc.
                Skipped session-95cecb2c724619fe502164459560ba5d.osc. File already exists.
            Rendering session-95cecb2c724619fe502164459560ba5d.osc.
                Skipped session-95cecb2c724619fe502164459560ba5d.osc. Output already exists.
            Writing test_project/sessions/session_three/render.yml.
                Wrote test_project/sessions/session_three/render.yml.
            Python/SC runtime: 0 seconds
            Rendered test_project/sessions/session_three/
        Rendering test_project/sessions/session_two/
            Importing test_project.sessions.session_two.definition
            Writing session-95cecb2c724619fe502164459560ba5d.osc.
                Skipped session-95cecb2c724619fe502164459560ba5d.osc. File already exists.
            Rendering session-95cecb2c724619fe502164459560ba5d.osc.
                Skipped session-95cecb2c724619fe502164459560ba5d.osc. Output already exists.
            Writing test_project/sessions/session_two/render.yml.
                Wrote test_project/sessions/session_two/render.yml.
            Python/SC runtime: 0 seconds
            Rendered test_project/sessions/session_two/
        '''.replace('/', os.path.sep))
        assert self.sessions_path.joinpath(
            'session_one',
            'render.aiff',
            ).exists()
        assert self.sessions_path.joinpath(
            'session_two',
            'render.aiff',
            ).exists()
        assert self.sessions_path.joinpath(
            'session_three',
            'render.aiff',
            ).exists()
        assert self.sample(
            str(self.sessions_path.joinpath('session_one', 'render.aiff'))
            ) == {
            0.0:  [2.3e-05] * 8,
            0.21: [0.210295] * 8,
            0.41: [0.410567] * 8,
            0.61: [0.610839] * 8,
            0.81: [0.811111] * 8,
            0.99: [0.991361] * 8,
            }
        assert self.sample(
            str(self.sessions_path.joinpath('session_two', 'render.aiff'))
            ) == {
            0.0:  [2.3e-05] * 8,
            0.21: [0.210295] * 8,
            0.41: [0.410567] * 8,
            0.61: [0.610839] * 8,
            0.81: [0.811111] * 8,
            0.99: [0.991361] * 8,
            }
        assert self.sample(
            str(self.sessions_path.joinpath('session_three', 'render.aiff'))
            ) == {
            0.0:  [2.3e-05] * 8,
            0.21: [0.210295] * 8,
            0.41: [0.410567] * 8,
            0.61: [0.610839] * 8,
            0.81: [0.811111] * 8,
            0.99: [0.991361] * 8,
            }

    def test_success_filtered_sessions(self):
        self.create_project()
        self.create_session('session_one')
        self.create_session('session_two')
        self.create_session('session_three')
        script = commandlinetools.ManageSessionScript()
        command = ['--render', 'session_t*']
        with systemtools.RedirectedStreams(stdout=self.string_io):
            with systemtools.TemporaryDirectoryChange(
                str(self.inner_project_path)):
                try:
                    script(command)
                except SystemExit as e:
                    raise RuntimeError('SystemExit: {}'.format(e.code))
        self.compare_captured_output(r'''
        Render candidates: 'session_t*' ...
        Rendering test_project/sessions/session_three/
            Importing test_project.sessions.session_three.definition
            Writing session-95cecb2c724619fe502164459560ba5d.osc.
                Wrote session-95cecb2c724619fe502164459560ba5d.osc.
            Rendering session-95cecb2c724619fe502164459560ba5d.osc.
                Command: scsynth -N session-95cecb2c724619fe502164459560ba5d.osc _ session-95cecb2c724619fe502164459560ba5d.aiff 44100 aiff int24
                Rendered session-95cecb2c724619fe502164459560ba5d.osc with exit code 0.
            Writing test_project/sessions/session_three/render.yml.
                Wrote test_project/sessions/session_three/render.yml.
            Python/SC runtime: 0 seconds
            Rendered test_project/sessions/session_three/
        Rendering test_project/sessions/session_two/
            Importing test_project.sessions.session_two.definition
            Writing session-95cecb2c724619fe502164459560ba5d.osc.
                Skipped session-95cecb2c724619fe502164459560ba5d.osc. File already exists.
            Rendering session-95cecb2c724619fe502164459560ba5d.osc.
                Skipped session-95cecb2c724619fe502164459560ba5d.osc. Output already exists.
            Writing test_project/sessions/session_two/render.yml.
                Wrote test_project/sessions/session_two/render.yml.
            Python/SC runtime: 0 seconds
            Rendered test_project/sessions/session_two/
        '''.replace('/', os.path.sep))
        assert not self.sessions_path.joinpath(
            'session_one',
            'render.aiff',
            ).exists()
        assert self.sessions_path.joinpath(
            'session_two',
            'render.aiff',
            ).exists()
        assert self.sessions_path.joinpath(
            'session_three',
            'render.aiff',
            ).exists()
        assert self.sample(
            str(self.sessions_path.joinpath('session_two', 'render.aiff'))
            ) == {
            0.0:  [2.3e-05] * 8,
            0.21: [0.210295] * 8,
            0.41: [0.410567] * 8,
            0.61: [0.610839] * 8,
            0.81: [0.811111] * 8,
            0.99: [0.991361] * 8,
            }
        assert self.sample(
            str(self.sessions_path.joinpath('session_three', 'render.aiff'))
            ) == {
            0.0:  [2.3e-05] * 8,
            0.21: [0.210295] * 8,
            0.41: [0.410567] * 8,
            0.61: [0.610839] * 8,
            0.81: [0.811111] * 8,
            0.99: [0.991361] * 8,
            }

    def test_success_one_session(self):
        self.create_project()
        self.create_session('test_session')
        script = commandlinetools.ManageSessionScript()
        command = ['--render', 'test_session']
        with systemtools.RedirectedStreams(stdout=self.string_io):
            with systemtools.TemporaryDirectoryChange(
                str(self.inner_project_path)):
                try:
                    script(command)
                except SystemExit as e:
                    raise RuntimeError('SystemExit: {}'.format(e.code))
        self.compare_captured_output(r'''
        Render candidates: 'test_session' ...
        Rendering test_project/sessions/test_session/
            Importing test_project.sessions.test_session.definition
            Writing session-95cecb2c724619fe502164459560ba5d.osc.
                Wrote session-95cecb2c724619fe502164459560ba5d.osc.
            Rendering session-95cecb2c724619fe502164459560ba5d.osc.
                Command: scsynth -N session-95cecb2c724619fe502164459560ba5d.osc _ session-95cecb2c724619fe502164459560ba5d.aiff 44100 aiff int24
                Rendered session-95cecb2c724619fe502164459560ba5d.osc with exit code 0.
            Writing test_project/sessions/test_session/render.yml.
                Wrote test_project/sessions/test_session/render.yml.
            Python/SC runtime: 0 seconds
            Rendered test_project/sessions/test_session/
        '''.replace('/', os.path.sep))
        self.compare_path_contents(
            self.inner_project_path,
            [
                'test_project/test_project/__init__.py',
                'test_project/test_project/assets/.gitignore',
                'test_project/test_project/distribution/.gitignore',
                'test_project/test_project/etc/.gitignore',
                'test_project/test_project/materials/.gitignore',
                'test_project/test_project/materials/__init__.py',
                'test_project/test_project/project-settings.yml',
                'test_project/test_project/renders/.gitignore',
                'test_project/test_project/renders/session-95cecb2c724619fe502164459560ba5d.aiff',
                'test_project/test_project/renders/session-95cecb2c724619fe502164459560ba5d.osc',
                'test_project/test_project/sessions/.gitignore',
                'test_project/test_project/sessions/__init__.py',
                'test_project/test_project/sessions/test_session/__init__.py',
                'test_project/test_project/sessions/test_session/definition.py',
                'test_project/test_project/sessions/test_session/render.aiff',
                'test_project/test_project/sessions/test_session/render.yml',
                'test_project/test_project/synthdefs/.gitignore',
                'test_project/test_project/synthdefs/__init__.py',
                'test_project/test_project/test/.gitignore',
                'test_project/test_project/tools/.gitignore',
                'test_project/test_project/tools/__init__.py',
                ]
            )
        assert self.sample(
            str(self.sessions_path.joinpath('test_session', 'render.aiff'))
            ) == {
            0.0:  [2.3e-05] * 8,
            0.21: [0.210295] * 8,
            0.41: [0.410567] * 8,
            0.61: [0.610839] * 8,
            0.81: [0.811111] * 8,
            0.99: [0.991361] * 8,
            }

    def test_success_chained(self):
        self.create_project()
        self.create_session('session_one')
        self.create_session(
            'session_two',
            definition_contents=self.chained_session_template.render(
                input_name='session_one',
                input_section_singular='session',
                output_section_singular='session',
                multiplier=0.5,
                ),
            )
        session_three_path = self.create_session(
            'session_three',
            definition_contents=self.chained_session_template.render(
                input_name='session_two',
                input_section_singular='session',
                output_section_singular='session',
                multiplier=-1.0,
                ),
            )

        project_settings_path = self.inner_project_path / 'project-settings.yml'
        with open(str(project_settings_path), 'r') as file_pointer:
            project_settings = file_pointer.read()
        project_settings = project_settings.replace(
            'input_bus_channel_count: 8',
            'input_bus_channel_count: 2',
            )
        project_settings = project_settings.replace(
            'output_bus_channel_count: 8',
            'output_bus_channel_count: 2',
            )
        with open(str(project_settings_path), 'w') as file_pointer:
            file_pointer.write(project_settings)

        self.compare_path_contents(
            self.inner_project_path,
            [
                'test_project/test_project/__init__.py',
                'test_project/test_project/assets/.gitignore',
                'test_project/test_project/distribution/.gitignore',
                'test_project/test_project/etc/.gitignore',
                'test_project/test_project/materials/.gitignore',
                'test_project/test_project/materials/__init__.py',
                'test_project/test_project/project-settings.yml',
                'test_project/test_project/renders/.gitignore',
                'test_project/test_project/sessions/.gitignore',
                'test_project/test_project/sessions/__init__.py',
                'test_project/test_project/sessions/session_one/__init__.py',
                'test_project/test_project/sessions/session_one/definition.py',
                'test_project/test_project/sessions/session_three/__init__.py',
                'test_project/test_project/sessions/session_three/definition.py',
                'test_project/test_project/sessions/session_two/__init__.py',
                'test_project/test_project/sessions/session_two/definition.py',
                'test_project/test_project/synthdefs/.gitignore',
                'test_project/test_project/synthdefs/__init__.py',
                'test_project/test_project/test/.gitignore',
                'test_project/test_project/tools/.gitignore',
                'test_project/test_project/tools/__init__.py']
            )

        script = commandlinetools.ManageSessionScript()
        command = ['--render', 'session_three']
        with systemtools.RedirectedStreams(stdout=self.string_io):
            with systemtools.TemporaryDirectoryChange(
                str(self.inner_project_path)):
                try:
                    script(command)
                except SystemExit as e:
                    raise RuntimeError('SystemExit: {}'.format(e.code))

        self.compare_captured_output(r'''
        Render candidates: 'session_three' ...
        Rendering test_project/sessions/session_three/
            Importing test_project.sessions.session_three.definition
            Writing session-aa1ca9fda49a2dd38a1a2b8a91a76cca.osc.
                Wrote session-aa1ca9fda49a2dd38a1a2b8a91a76cca.osc.
            Rendering session-aa1ca9fda49a2dd38a1a2b8a91a76cca.osc.
                Command: scsynth -N session-aa1ca9fda49a2dd38a1a2b8a91a76cca.osc _ session-aa1ca9fda49a2dd38a1a2b8a91a76cca.aiff 44100 aiff int24 -i 2 -o 2
                Rendered session-aa1ca9fda49a2dd38a1a2b8a91a76cca.osc with exit code 0.
            Writing session-46f9bdbbd13bcf641e2a79917dcc041f.osc.
                Wrote session-46f9bdbbd13bcf641e2a79917dcc041f.osc.
            Rendering session-46f9bdbbd13bcf641e2a79917dcc041f.osc.
                Command: scsynth -N session-46f9bdbbd13bcf641e2a79917dcc041f.osc session-aa1ca9fda49a2dd38a1a2b8a91a76cca.aiff session-46f9bdbbd13bcf641e2a79917dcc041f.aiff 44100 aiff int24 -i 2 -o 2
                Rendered session-46f9bdbbd13bcf641e2a79917dcc041f.osc with exit code 0.
            Writing session-352b87b6c1d447a5be11020a33ceadec.osc.
                Wrote session-352b87b6c1d447a5be11020a33ceadec.osc.
            Rendering session-352b87b6c1d447a5be11020a33ceadec.osc.
                Command: scsynth -N session-352b87b6c1d447a5be11020a33ceadec.osc session-46f9bdbbd13bcf641e2a79917dcc041f.aiff session-352b87b6c1d447a5be11020a33ceadec.aiff 44100 aiff int24 -i 2 -o 2
                Rendered session-352b87b6c1d447a5be11020a33ceadec.osc with exit code 0.
            Writing test_project/sessions/session_three/render.yml.
                Wrote test_project/sessions/session_three/render.yml.
            Python/SC runtime: 0 seconds
            Rendered test_project/sessions/session_three/
        ''')

        self.compare_path_contents(
            self.inner_project_path,
            [
                'test_project/test_project/__init__.py',
                'test_project/test_project/assets/.gitignore',
                'test_project/test_project/distribution/.gitignore',
                'test_project/test_project/etc/.gitignore',
                'test_project/test_project/materials/.gitignore',
                'test_project/test_project/materials/__init__.py',
                'test_project/test_project/project-settings.yml',
                'test_project/test_project/renders/.gitignore',
                'test_project/test_project/renders/session-352b87b6c1d447a5be11020a33ceadec.aiff',
                'test_project/test_project/renders/session-352b87b6c1d447a5be11020a33ceadec.osc',
                'test_project/test_project/renders/session-46f9bdbbd13bcf641e2a79917dcc041f.aiff',
                'test_project/test_project/renders/session-46f9bdbbd13bcf641e2a79917dcc041f.osc',
                'test_project/test_project/renders/session-aa1ca9fda49a2dd38a1a2b8a91a76cca.aiff',
                'test_project/test_project/renders/session-aa1ca9fda49a2dd38a1a2b8a91a76cca.osc',
                'test_project/test_project/sessions/.gitignore',
                'test_project/test_project/sessions/__init__.py',
                'test_project/test_project/sessions/session_one/__init__.py',
                'test_project/test_project/sessions/session_one/definition.py',
                'test_project/test_project/sessions/session_three/__init__.py',
                'test_project/test_project/sessions/session_three/definition.py',
                'test_project/test_project/sessions/session_three/render.aiff',
                'test_project/test_project/sessions/session_three/render.yml',
                'test_project/test_project/sessions/session_two/__init__.py',
                'test_project/test_project/sessions/session_two/definition.py',
                'test_project/test_project/synthdefs/.gitignore',
                'test_project/test_project/synthdefs/__init__.py',
                'test_project/test_project/test/.gitignore',
                'test_project/test_project/tools/.gitignore',
                'test_project/test_project/tools/__init__.py']
            )

        render_yml_file_path = session_three_path / 'render.yml'
        with open(str(render_yml_file_path), 'r') as file_pointer:
            render_yml = yaml.load(file_pointer.read())
        assert render_yml == {
            'render': 'session-352b87b6c1d447a5be11020a33ceadec',
            'source': [
                'session-46f9bdbbd13bcf641e2a79917dcc041f',
                'session-aa1ca9fda49a2dd38a1a2b8a91a76cca',
                ],
            }

        session_three_render_sample = self.sample(
            str(session_three_path / 'render.aiff'),
            rounding=2,
            )

        session_three_source_sample = self.sample(
            str(self.renders_path / '{}.aiff'.format(render_yml['render'])),
            rounding=2,
            )

        assert session_three_render_sample == session_three_source_sample
        assert session_three_render_sample == {
            0.0: [-0.0, -0.0],
            0.21: [-0.11, -0.11],
            0.41: [-0.21, -0.21],
            0.61: [-0.31, -0.31],
            0.81: [-0.41, -0.41],
            0.99: [-0.5, -0.5],
            }

    def test_session_factory(self):
        """
        Handle session factories implemented with __session__().
        """
        self.create_project()
        session_path = self.create_session('test_session')
        definition_path = session_path.joinpath('definition.py')
        with open(str(definition_path), 'w') as file_pointer:
            file_pointer.write(self.session_factory_template.render(
                output_section_singular='session',
                ))
        script = commandlinetools.ManageSessionScript()
        command = ['--render', 'test_session']
        with systemtools.RedirectedStreams(stdout=self.string_io):
            with systemtools.TemporaryDirectoryChange(
                str(self.inner_project_path)):
                try:
                    script(command)
                except SystemExit as e:
                    raise RuntimeError('SystemExit: {}'.format(e.code))
        self.compare_captured_output(r'''
        Render candidates: 'test_session' ...
        Rendering test_project/sessions/test_session/
            Importing test_project.sessions.test_session.definition
            Writing session-95cecb2c724619fe502164459560ba5d.osc.
                Wrote session-95cecb2c724619fe502164459560ba5d.osc.
            Rendering session-95cecb2c724619fe502164459560ba5d.osc.
                Command: scsynth -N session-95cecb2c724619fe502164459560ba5d.osc _ session-95cecb2c724619fe502164459560ba5d.aiff 44100 aiff int24
                Rendered session-95cecb2c724619fe502164459560ba5d.osc with exit code 0.
            Writing test_project/sessions/test_session/render.yml.
                Wrote test_project/sessions/test_session/render.yml.
            Python/SC runtime: 0 seconds
            Rendered test_project/sessions/test_session/
        '''.replace('/', os.path.sep))
        self.compare_path_contents(
            self.inner_project_path,
            [
                'test_project/test_project/__init__.py',
                'test_project/test_project/assets/.gitignore',
                'test_project/test_project/distribution/.gitignore',
                'test_project/test_project/etc/.gitignore',
                'test_project/test_project/materials/.gitignore',
                'test_project/test_project/materials/__init__.py',
                'test_project/test_project/project-settings.yml',
                'test_project/test_project/renders/.gitignore',
                'test_project/test_project/renders/session-95cecb2c724619fe502164459560ba5d.aiff',
                'test_project/test_project/renders/session-95cecb2c724619fe502164459560ba5d.osc',
                'test_project/test_project/sessions/.gitignore',
                'test_project/test_project/sessions/__init__.py',
                'test_project/test_project/sessions/test_session/__init__.py',
                'test_project/test_project/sessions/test_session/definition.py',
                'test_project/test_project/sessions/test_session/render.aiff',
                'test_project/test_project/sessions/test_session/render.yml',
                'test_project/test_project/synthdefs/.gitignore',
                'test_project/test_project/synthdefs/__init__.py',
                'test_project/test_project/test/.gitignore',
                'test_project/test_project/tools/.gitignore',
                'test_project/test_project/tools/__init__.py',
                ]
            )
        assert self.sample(
            str(self.sessions_path.joinpath('test_session', 'render.aiff'))
            ) == {
            0.0:  [2.3e-05] * 8,
            0.21: [0.210295] * 8,
            0.41: [0.410567] * 8,
            0.61: [0.610839] * 8,
            0.81: [0.811111] * 8,
            0.99: [0.991361] * 8,
            }