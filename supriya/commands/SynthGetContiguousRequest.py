from supriya.commands.Request import Request
from supriya.enums import RequestId


class SynthGetContiguousRequest(Request):

    ### CLASS VARIABLES ###

    __slots__ = ()

    request_id = RequestId.SYNTH_GET_CONTIGUOUS

    ### INITIALIZER ###

    def __init__(self):
        Request.__init__(self)
        raise NotImplementedError

    ### PUBLIC METHODS ###

    def to_osc(self, with_request_name=False):
        raise NotImplementedError
