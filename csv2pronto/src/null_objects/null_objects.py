from rdflib import BNode, Literal


class NoneLiteral(Literal):
    """Class that represents the `Literal` of a None value."""

    def __bool__(self):
        return False

    def __len__(self):
        return 0

    # Mariano: Declaré esta función en esta clase
    #          para que cada vez que se intente
    #          realizar un replace con un objeto
    #          de este tipo, no incurra en lógica
    #          errónea.
    #
    #          Consultar si está bien
    def replace(*args, **kwargs):
        return None


class NoneNode(BNode):
    """
    Class that represents a `Node` that is None.

    Instances of this class indicate the absence of knowledge.
    Triplets with this class as a subject or object should never be
    considered when building a knowledge graph.
    """

    def __bool__(self):
        return False

    def __len__(self):
        return 0
