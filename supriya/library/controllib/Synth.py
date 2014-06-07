from supriya.library.controllib.Node import Node


class Synth(Node):

    ### CLASS VARIABLES ###

    __slots__ = (
        '_synth_definition_name',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        synth_definition_name,
        add_action=None,
        target_node=None,
        ):
        from supriya.library import controllib
        self._synth_definition_name = synth_definition_name
        add_action = add_action or 0
        add_action = controllib.AddAction.from_expr(add_action)
        target_node = controllib.Node.expr_as_target(target_node)
        server = target_node.server
        Node.__init__(
            self,
            server=server,
            )
        if add_action.value < 2:
            self._group = target_node
        else:
            self._group = target_node.group
        message = (
            self.creation_command,
            self.synth_definition_name,
            self.node_id,
            add_action.value,
            target_node.node_id,
            0,
            )
        self._server.send_message(message)

    ### PUBLIC PROPERTIES ###

    @property
    def creation_command(self):
        return 9

    @property
    def synth_definition_name(self):
        return self._synth_definition_name
