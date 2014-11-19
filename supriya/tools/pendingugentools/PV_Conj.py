# -*- encoding: utf-8 -*-
from supriya.tools.ugentools.PV_MagSquared import PV_MagSquared


class PV_Conj(PV_MagSquared):
    r'''

    ::

        >>> pv_conj = ugentools.PV_Conj.(
        ...     )
        >>> pv_conj

    '''

    ### CLASS VARIABLES ###

    __documentation_section__ = None

    __slots__ = ()

    _ordered_input_names = ()

    _valid_calculation_rates = None

    ### INITIALIZER ###

    ### PUBLIC METHODS ###

    @classmethod
    def new(
        cls,
        buffer_=None,
        ):
        r'''Constructs a PV_Conj.

        ::

            >>> pv_conj = ugentools.PV_Conj.new(
            ...     buffer_=None,
            ...     )
            >>> pv_conj

        Returns ugen graph.
        '''
        from supriya.tools import synthdeftools
        calculation_rate = None
        ugen = cls._new_expanded(
            calculation_rate=calculation_rate,
            buffer_=buffer_,
            )
        return ugen