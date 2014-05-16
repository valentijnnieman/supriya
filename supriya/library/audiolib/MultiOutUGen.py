from supriya.library.audiolib.UGen import UGen


class MultiOutUGen(UGen):

    ### CLASS VARIABLES ###

    __slots__ = (
        '_channel_count',
        '_output_proxies',
        )

    ### INTIALIZER ###

    def __init__(
        self,
        calculation_rate=None,
        special_index=0,
        channel_count=1,
        **kwargs
        ):
        from supriya.library import audiolib
        self._channel_count = int(channel_count)
        UGen.__init__(
            self,
            calculation_rate=calculation_rate,
            special_index=special_index,
            **kwargs
            )
        self._output_proxies = tuple(
            audiolib.OutputProxy(self, i)
            for i in range(len(self))
            )

    ### SPECIAL METHODS ###

    def __getitem__(self, i):
        return self._output_proxies[i]

    def __len__(self):
        return self.channel_count

    ### PRIVATE METHODS ###

    def _get_outputs(self):
        return [self.calculation_rate] * len(self)

    ### PUBLIC PROPERTIES ###

    @classmethod
    def ar(cls, **kwargs):
        from supriya.library import audiolib
        ugen = cls._new(
            calculation_rate=UGen.Rate.AUDIO_RATE,
            special_index=0,
            **kwargs
            )
        output_proxies = []
        if isinstance(ugen, audiolib.UGen):
            output_proxies.extend(ugen[:])
        else:
            for x in ugen:
                output_proxies.extend(x[:])
        result = audiolib.UGenArray(output_proxies)
        return result

    @property
    def channel_count(self):
        return self._channel_count

    @classmethod
    def kr(cls, **kwargs):
        from supriya.library import audiolib
        ugen = cls._new(
            calculation_rate=UGen.Rate.CONTROL_RATE,
            special_index=0,
            **kwargs
            )
        output_proxies = []
        if isinstance(ugen, audiolib.UGen):
            output_proxies.extend(ugen[:])
        else:
            for x in ugen:
                output_proxies.extend(x[:])
        result = audiolib.UgenArray(output_proxies)
        return result

    @property
    def outputs(self):
        return [self.calculation_rate for _ in range(len(self))]
