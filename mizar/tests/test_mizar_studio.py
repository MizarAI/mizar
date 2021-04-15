import os
import shutil
from functools import wraps

import pytest

from mizar.api import Mizar
from mizar.studio import MizarStudio


@pytest.fixture()
def mizar_studio():
    mizar = Mizar()
    return MizarStudio(mizar, path="./mizar_studio_test")


def delete_test_folder(f):
    @wraps(f)
    def _delete_test_folder(*args, **kwargs):

        try:
            return f(*args, **kwargs)
        finally:
            shutil.rmtree("./mizar_studio_test")

    return _delete_test_folder


@delete_test_folder
def test_mizar_studio_folder_creation(mizar_studio):
    assert os.path.isdir("./mizar_studio_test")
