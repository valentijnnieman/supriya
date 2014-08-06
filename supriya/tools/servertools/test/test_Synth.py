# -*- encoding: utf-8 -*-
import pytest
from supriya import synthdefs
from supriya.tools import servertools
from abjad.tools import systemtools


@pytest.fixture(scope='function')
def server(request):
    def server_teardown():
        server.quit()
    server = servertools.Server().boot()
    request.addfinalizer(server_teardown)
    return server


def test_Synth_01(server):

    group = servertools.Group().allocate()

    synth_a = servertools.Synth(synthdefs.test)
    synth_a.allocate(
        target_node=group,
        )
    synth_b = servertools.Synth(synthdefs.test)
    synth_b.allocate(
        target_node=group,
        )

    server_state = str(server.query_remote_nodes(include_controls=True))
    assert systemtools.TestManager.compare(
        server_state,
        r'''
        NODE TREE 0 group
            1 group
                1000 group
                    1002 test
                        amplitude: 1.0, frequency: 440.0
                    1001 test
                        amplitude: 1.0, frequency: 440.0
        '''
        ), server_state
    assert synth_a['frequency'].get() == 440.0
    assert synth_a['amplitude'].get() == 1.0
    assert synth_b['frequency'].get() == 440.0
    assert synth_b['amplitude'].get() == 1.0

    synth_a.controls['frequency'].set(443)
    synth_a.controls['amplitude'].set(0.5)

    server_state = str(server.query_remote_nodes(include_controls=True))
    assert systemtools.TestManager.compare(
        server_state,
        r'''
        NODE TREE 0 group
            1 group
                1000 group
                    1002 test
                        amplitude: 1.0, frequency: 440.0
                    1001 test
                        amplitude: 0.5, frequency: 443.0
        '''
        ), server_state
    assert synth_a['frequency'].get() == 443.0
    assert synth_a['amplitude'].get() == 0.5
    assert synth_b['frequency'].get() == 440.0
    assert synth_b['amplitude'].get() == 1.0

    synth_b.controls['frequency', 'amplitude'] = 441, 0.25

    server_state = str(server.query_remote_nodes(include_controls=True))
    assert systemtools.TestManager.compare(
        server_state,
        r'''
        NODE TREE 0 group
            1 group
                1000 group
                    1002 test
                        amplitude: 0.25, frequency: 441.0
                    1001 test
                        amplitude: 0.5, frequency: 443.0
        '''
        ), server_state
    assert synth_a['frequency'].get() == 443.0
    assert synth_a['amplitude'].get() == 0.5
    assert synth_b['frequency'].get() == 441.0
    assert synth_b['amplitude'].get() == 0.25

    bus_a = servertools.Bus(rate='control')
    bus_a.allocate()
    bus_b = servertools.Bus(rate='audio')
    bus_b.allocate()
    synth_a['frequency'].set(bus_a)
    synth_b['amplitude'].set(bus_b)

    server_state = str(server.query_remote_nodes(include_controls=True))
    assert systemtools.TestManager.compare(
        server_state,
        r'''
        NODE TREE 0 group
            1 group
                1000 group
                    1002 test
                        amplitude: a16, frequency: 441.0
                    1001 test
                        amplitude: 0.5, frequency: c0
        '''
        ), server_state
    assert synth_a['frequency'].get() == bus_a
    assert synth_a['amplitude'].get() == 0.5
    assert synth_b['frequency'].get() == 441.0
    assert synth_b['amplitude'].get() == bus_b


def test_Synth_02(server):

    synth = servertools.Synth(synthdefs.test)
    synth['frequency'].set(443)
    synth['amplitude'].set(0.5)

    assert synth['frequency'].get() == 443
    assert synth['amplitude'].get() == 0.5

    synth.allocate()

    server_state = str(server.query_remote_nodes(include_controls=True))
    assert systemtools.TestManager.compare(
        server_state,
        r'''
        NODE TREE 0 group
            1 group
                1000 test
                    amplitude: 0.5, frequency: 443.0
        ''',
        ), server_state

    synth.free()

    assert synth['frequency'].get() == 443
    assert synth['amplitude'].get() == 0.5

    control_bus = servertools.Bus(0, rate='control')
    audio_bus = servertools.Bus(0, rate='audio')

    synth['frequency'].set(control_bus)
    synth['amplitude'].set(audio_bus)

    assert synth['frequency'].get() == control_bus
    assert synth['amplitude'].get() == audio_bus

    synth.allocate()

    server_state = str(server.query_remote_nodes(include_controls=True))
    assert systemtools.TestManager.compare(
        server_state,
        r'''
        NODE TREE 0 group
            1 group
                1001 test
                    amplitude: a0, frequency: c0
        ''',
        ), server_state

    synth.free()

    assert synth['frequency'].get() == control_bus
    assert synth['amplitude'].get() == audio_bus