from bs.errors import UserError
from bs.builder import Builder


BUILDER_MAPPING = {
    ".c": "CC",
    ".cpp": "CXX",
}


class Program(Builder):
    """Find the best builder for creating an executable based on sources."""

    def get_command(self):
        if not self.sources:
            return []

        suffix = get_suffix(self.sources[0].get_suffix())
        try:
            builder = BUILDER_MAPPING[suffix]
        except KeyError:
            raise UserError(
                "Tried to use Program builder with uknown file type: {}".format(suffix)
            )

        instance = builder(self.bs, self.targets, self.sources, **self.overrides)
        return instance.get_command()
