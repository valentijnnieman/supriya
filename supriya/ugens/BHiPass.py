from supriya.ugens.BEQSuite import BEQSuite


class BHiPass(BEQSuite):
    """
    A high-pass filter.

    ::

        >>> source = supriya.ugens.In.ar(0)
        >>> bhi_pass = supriya.ugens.BHiPass.ar(
        ...     frequency=1200,
        ...     reciprocal_of_q=1,
        ...     source=source,
        ...     )
        >>> bhi_pass
        BHiPass.ar()

    """

    ### CLASS VARIABLES ###

    __documentation_section__ = 'Filter UGens'

    __slots__ = ()

    _ordered_input_names = (
        'source',
        'frequency',
        'reciprocal_of_q',
        )

    _valid_calculation_rates = None

    ### INITIALIZER ###

    def __init__(
        self,
        calculation_rate=None,
        frequency=1200,
        reciprocal_of_q=1,
        source=None,
        ):
        BEQSuite.__init__(
            self,
            calculation_rate=calculation_rate,
            frequency=frequency,
            reciprocal_of_q=reciprocal_of_q,
            source=source,
            )

    ### PUBLIC METHODS ###

    @classmethod
    def ar(
        cls,
        frequency=1200,
        reciprocal_of_q=1,
        source=None,
        ):
        """
        Constructs an audio-rate BHiPass.

        ::

            >>> source = supriya.ugens.In.ar(0)
            >>> bhi_pass = supriya.ugens.BHiPass.ar(
            ...     frequency=1200,
            ...     reciprocal_of_q=1,
            ...     source=source,
            ...     )
            >>> bhi_pass
            BHiPass.ar()

        Returns ugen graph.
        """
        import supriya.synthdefs
        calculation_rate = supriya.synthdefs.CalculationRate.AUDIO
        ugen = cls._new_expanded(
            calculation_rate=calculation_rate,
            frequency=frequency,
            reciprocal_of_q=reciprocal_of_q,
            source=source,
            )
        return ugen

    # def coeffs(): ...

    # def magResponse(): ...

    # def magResponse2(): ...

    # def magResponse5(): ...

    # def magResponseN(): ...

    # def sc(): ...

    # def scopeResponse(): ...

    ### PUBLIC PROPERTIES ###

    @property
    def frequency(self):
        """
        Gets `frequency` input of BHiPass.

        ::

            >>> source = supriya.ugens.In.ar(0)
            >>> bhi_pass = supriya.ugens.BHiPass.ar(
            ...     frequency=1200,
            ...     reciprocal_of_q=1,
            ...     source=source,
            ...     )
            >>> bhi_pass.frequency
            1200.0

        Returns ugen input.
        """
        index = self._ordered_input_names.index('frequency')
        return self._inputs[index]

    @property
    def reciprocal_of_q(self):
        """
        Gets `reciprocal_of_q` input of BHiPass.

        ::

            >>> source = supriya.ugens.In.ar(0)
            >>> bhi_pass = supriya.ugens.BHiPass.ar(
            ...     frequency=1200,
            ...     reciprocal_of_q=1,
            ...     source=source,
            ...     )
            >>> bhi_pass.reciprocal_of_q
            1.0

        Returns ugen input.
        """
        index = self._ordered_input_names.index('reciprocal_of_q')
        return self._inputs[index]

    @property
    def source(self):
        """
        Gets `source` input of BHiPass.

        ::

            >>> source = supriya.ugens.In.ar(0)
            >>> bhi_pass = supriya.ugens.BHiPass.ar(
            ...     frequency=1200,
            ...     reciprocal_of_q=1,
            ...     source=source,
            ...     )
            >>> bhi_pass.source
            In.ar()[0]

        Returns ugen input.
        """
        index = self._ordered_input_names.index('source')
        return self._inputs[index]