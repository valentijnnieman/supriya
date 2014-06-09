class ServerOptions(object):
    r'''SuperCollider server option configuration.

    ::

        >>> from supriya import controllib
        >>> options = controllib.ServerOptions()

    '''

    ### CLASS VARIABLES ###

    __slots__ = (
        '_audio_bus_channel_count',
        '_block_size',
        '_buffer_count',
        '_control_bus_channel_count',
        '_hardware_buffer_size',
        '_initial_node_id',
        '_input_bus_channel_count',
        '_input_device',
        '_input_stream_mask',
        '_load_synth_definitions',
        '_maximum_node_count',
        '_maximum_synth_definition_count',
        '_memory_locking',
        '_memory_size',
        '_output_bus_channel_count',
        '_output_device',
        '_output_stream_mask',
        '_protocol',
        '_random_number_generator_count',
        '_remote_control_volume',
        '_restricted_path',
        '_sample_rate',
        '_verbosity',
        '_wire_buffer_count',
        '_zero_configuration',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        audio_bus_channel_count=128,
        block_size=64,
        buffer_count=1024,
        control_bus_channel_count=4096,
        hardware_buffer_size=None,
        initial_node_id=1000,
        input_bus_channel_count=8,
        input_device=None,
        input_stream_mask=False,
        load_synth_definitions=True,
        maximum_node_count=1024,
        maximum_synth_definition_count=1024,
        memory_locking=False,
        memory_size=8192,
        output_bus_channel_count=8,
        output_device=None,
        output_stream_mask=False,
        protocol='udp',
        random_number_generator_count=64,
        remote_control_volume=False,
        restricted_path=None,
        sample_rate=None,
        verbosity=0,
        wire_buffer_count=64,
        zero_configuration=False,
        ):
        self._audio_bus_channel_count = int(audio_bus_channel_count)
        self._block_size = int(block_size)
        self._buffer_count = int(buffer_count)
        self._control_bus_channel_count = int(control_bus_channel_count)
        self._control_bus_channel_count = int(control_bus_channel_count)
        self._hardware_buffer_size = hardware_buffer_size
        self._initial_node_id = int(initial_node_id)
        self._input_bus_channel_count = int(input_bus_channel_count)
        self._input_device = input_device
        self._input_stream_mask = bool(input_stream_mask)
        self._load_synth_definitions = load_synth_definitions
        self._maximum_node_count = int(maximum_node_count)
        self._maximum_synth_definition_count = int(maximum_synth_definition_count)
        self._memory_locking = bool(memory_locking)
        self._memory_size = int(memory_size)
        self._output_bus_channel_count = int(output_bus_channel_count)
        self._output_device = output_device
        self._output_stream_mask = bool(output_stream_mask)
        self._protocol = protocol
        self._random_number_generator_count = int(random_number_generator_count)
        self._remote_control_volume = remote_control_volume
        self._restricted_path = restricted_path
        self._sample_rate = sample_rate
        self._verbosity = int(verbosity)
        self._wire_buffer_count = int(wire_buffer_count)
        self._zero_configuration = bool(zero_configuration)

    ### PUBLIC METHODS ###

    def as_options_string(self, port=57110):
        result = []

        if self.protocol == 'tcp':
            result.append('-t')
        else:
            result.append('-u')
        result.append(str(port))

        result.append('-a')
        result.append(
            self.private_audio_bus_channel_count +
            self.input_bus_channel_count +
            self.output_bus_channel_count
            )

        if self.control_bus_channel_count != 4096:
            result.append('-c {}'.format(self.control_bus_channel_count))

        if self.input_bus_channel_count != 8:
            result.append('-i {}'.format(self.input_bus_channel_count))

        if self.output_bus_channel_count != 8:
            result.append('-o {}'.format(self.output_bus_channel_count))

        if self.buffer_count != 1024:
            result.append('-b {}'.format(self.buffer_count))

        if self.maximum_node_count != 1024:
            result.append('-n {}'.format(self.maximum_node_count))

        if self.maximum_synth_definition_count != 1024:
            result.append('-d {}'.format(self.maximum_synth_definition_count))

        if self.block_size != 64:
            result.append('-z {}'.format(self.block_size))

        if self.hardware_buffer_size is not None:
            result.append('-Z {}'.format(int(self.hardware_buffer_size)))

        if self.memory_size != 8192:
            result.append('-m {}'.format(self.memory_size))

        if self.random_number_generator_count != 64:
            result.append('-r {}'.format(self.random_number_generator_count))

        if self.wire_buffer_count != 64:
            result.append('-w {}'.format(self.wire_buffer_count))

        if self.sample_rate is not None:
            result.append('-S {}'.format(int(self.sample_rate)))

        if not self.load_synth_definitions:
            result.append('-D 0')

        if self.input_stream_mask:
            result.append('-I {}'.format(self.input_stream_mask))

        if self.output_stream_mask:
            result.append('-O {}'.format(self.output_stream_mask))

        if 0 < self.verbosity:
            result.append('-v {}'.format(self.verbosity))

        if not self.zero_configuration:
            result.append('-R 0')

        if self.restricted_path is not None:
            result.append('-P {}'.format(self.restricted_path))

        if self.memory_locking:
            result.append('-L')

        options_string = ' '.join(str(x) for x in result)
        return options_string

    ### PUBLIC PROPERTIES ###

    @property
    def audio_bus_channel_count(self):
        return self._audio_bus_channel_count

    @property
    def block_size(self):
        return self._block_size

    @property
    def buffer_count(self):
        return self._buffer_count

    @property
    def control_bus_channel_count(self):
        return self._control_bus_channel_count

    @property
    def first_private_bus_id(self):
        return self.output_bus_channel_count + self.input_bus_channel_count

    @property
    def hardware_buffer_size(self):
        return self._hardware_buffer_size

    @property
    def initial_node_id(self):
        return self._initial_node_id

    @property
    def input_bus_channel_count(self):
        return self._input_bus_channel_count

    @property
    def input_device(self):
        return self._input_device

    @property
    def input_stream_mask(self):
        return self._input_stream_mask

    @property
    def load_synth_definitions(self):
        return self._load_synth_definitions

    @property
    def maximum_node_count(self):
        return self._maximum_node_count

    @property
    def maximum_synth_definition_count(self):
        return self._maximum_synth_definition_count

    @property
    def memory_locking(self):
        return self._memory_locking

    @property
    def memory_size(self):
        return self._memory_size

    @property
    def output_bus_channel_count(self):
        return self._output_bus_channel_count

    @property
    def output_device(self):
        return self._output_device

    @property
    def output_stream_mask(self):
        return self._output_stream_mask

    @property
    def private_audio_bus_channel_count(self):
        private_audio_bus_channel_count = self.audio_bus_channel_count
        private_audio_bus_channel_count -= self.input_bus_channel_count
        private_audio_bus_channel_count -= self.output_bus_channel_count
        return private_audio_bus_channel_count

    @property
    def protocol(self):
        return self._protocol

    @property
    def random_number_generator_count(self):
        return self._random_number_generator_count

    @property
    def remote_control_volume(self):
        return self._remote_control_volume

    @property
    def restricted_path(self):
        return self._restricted_path

    @property
    def sample_rate(self):
        return self._sample_rate

    @property
    def verbosity(self):
        return self._verbosity

    @property
    def wire_buffer_count(self):
        return self._wire_buffer_count

    @property
    def zero_configuration(self):
        return self._zero_configuration