import os
from typing import Iterator, Optional, Callable, List

import pytest
from _pytest.fixtures import SubRequest
from _pytest.nodes import Node
from vcr import VCR
from vcr.cassette import Cassette
from yaml._yaml import Mark
from contextlib import contextmanager

my_vcr = VCR(record_mode="vcr")


@pytest.fixture
def has_marker(request: SubRequest) -> Callable[[str], Optional[List[Mark]]]:
    """Detect a mark on a test. Return None if not found, a list otherwise."""

    def wrapper(mark_name):
        return list(request.node.iter_markers(name=mark_name))

    return wrapper


def _get_cassette_path(node: Node):
    """Return the cassette path based on the test."""
    module = node.fspath
    return os.path.join(module.dirname, "cassettes", module.purebasename)


@pytest.fixture(autouse=True)
def vcr_detector(request: SubRequest, has_marker) -> Iterator[Optional[Cassette]]:
    """Automatic fixture that allows to use a pytest marker to vcr a test (or test collection)."""
    if has_marker("vcr") and not has_marker("vcr_skip"):
        path = _get_cassette_path(request.node)
        name = f"{request.node.name}.yaml"
        if request.node.cls:
            name = f"{request.node.cls.__name__}.{name}"
        with my_vcr.use_cassette(path=os.path.join(path, name)) as cassette:
            yield cassette
    else:
        yield None


@pytest.fixture(scope="class")
def vcr_setup(request: SubRequest):
    """Fixture that allows vcr recording in a class setup.
    It provides a context manager that will record every network call in a setup cassette.
    Any exception occurred inside the context manager will result in the cassette deletion, if so specified by the
    context manager argument."""

    path = _get_cassette_path(request.node)
    name = f"{request.node.cls.__name__}.__setup__.yaml"
    cassette_path = f"{path}/{name}"

    @contextmanager
    def delete_setup_cassette_on_fail():
        """Delete the cassette on error."""
        try:
            yield
        except Exception as e:
            if os.path.exists(cassette_path):
                os.remove(cassette_path)
            raise e

    @contextmanager
    def combined(delete_on_fail: bool = True):
        """When required, combine the vcrpy context manager with the one that deletes cassette on failure."""
        if delete_on_fail:
            with delete_setup_cassette_on_fail(), my_vcr.use_cassette(
                cassette_path
            ) as a:
                yield a
        else:
            with my_vcr.use_cassette(cassette_path) as a:
                yield a

    return combined


# Decorator used to record cassettes
vcr_record = pytest.mark.vcr
# Decorator used to skip vcr recording
vcr_skip = pytest.mark.vcr_skip
