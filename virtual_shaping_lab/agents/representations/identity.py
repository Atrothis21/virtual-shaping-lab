# representations/identity.py

class IdentityRepresentation:
    """
    Identity representation.

    Returns the stimulus unchanged.
    Useful for symbolic / discrete experiments.
    """

    def encode(self, stimulus):
        return stimulus
