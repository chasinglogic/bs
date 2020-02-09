"""Contains functions for loading BS tools and builders"""

from os import getenv
from functools import wraps
from pkg_resources import iter_entry_points

from bs.builder import Builder


class PluginFailure(Exception):
    """Thrown when a plugin failed to implement the API correctly"""

    pass


def cached_loader(fn):
    """Memoizer for the various plugin loading functions."""
    result = None

    @wraps(fn)
    def cached(*args, **kwargs):
        nonlocal result
        force_reload = kwargs.pop("force_reload", False)
        if result is not None and not force_reload:
            return result
        result = fn(*args, **kwargs)
        return result

    return cached


def load_builders(bs):
    """Load the available builders on this system."""
    builders = {}
    enabled_builders = getenv("BS_BUILDERS", bs.get("BUILDERS", []))

    for builder in iter_entry_points("bs.builders"):
        if enabled_builders and builder.name not in builder:
            continue

        loaded = builder.load()
        try:
            builder_impl = getattr(loaded, builder.name)
        except AttributeError:
            raise PluginFailure(
                "Builder {} does not define a function of that name.".format(
                    builder.name
                )
            )

        if not issubclass(builder_impl, Builder):
            raise PluginFailure(
                "Builder {} exports a builder but it does not subclass bs.builder.Builder".format(
                    builder.name
                )
            )

        setup = getattr(loaded, "setup", None)
        if not callable(setup):
            raise PluginFailure(
                "Builder {} did not provide a setup function.".format(builder.name)
            )

        if setup(bs):
            builders[builder.name] = builder_impl

    return builders
