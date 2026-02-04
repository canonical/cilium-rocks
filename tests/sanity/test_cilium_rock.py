#
# Copyright 2026 Canonical, Ltd.
#

import shlex

import pytest
from k8s_test_harness.util import docker_util, fips_util
from test_util import config, rock

IMAGE_NAME = "cilium"
IMAGE_BASE = f"ghcr.io/canonical/{IMAGE_NAME}"
IMAGE_ENTRYPOINT = "cilium-agent --version"


def get_cilium_params():
    return rock.get_rock_test_param(IMAGE_NAME, config.IMAGE_ARCH)


@pytest.mark.parametrize("rock_param", get_cilium_params(), ids=rock.rock_param_id)
def test_executable(image_version):
    rock.run_image(IMAGE_NAME, image_version, IMAGE_ENTRYPOINT, config.IMAGE_ARCH)


@pytest.mark.parametrize("rock_param", get_cilium_params(), ids=rock.rock_param_id)
def test_pebble_executable(image_version):
    rock.check_pebble(
        IMAGE_NAME, image_version, config.PEBBLE_VERSION, config.IMAGE_ARCH
    )


@pytest.mark.parametrize("GOFIPS", [0, 1], ids=lambda v: f"GOFIPS={v}")
@pytest.mark.parametrize("rock_param", get_cilium_params(), ids=rock.rock_param_id)
def test_fips(rock_param: rock.RockTestParam, GOFIPS):
    rockcraft_yaml_path = config.REPO_PATH / rock_param.path / "rockcraft.yaml"
    rockcraft_yaml = rockcraft_yaml_path.read_text()

    # TODO: Remove this once this is solved: https://bugs.launchpad.net/go-snap/+bug/2131731
    if GOFIPS == 1 and not fips_util.is_fips_rock(rockcraft_yaml):
        pytest.skip("This version of the ROCK is not built for FIPS")

    entrypoint = shlex.split(IMAGE_ENTRYPOINT)

    docker_env = ["-e", f"GOFIPS={GOFIPS}"]
    process = docker_util.run_in_docker(
        rock_param.image, entrypoint, check_exit_code=False, docker_args=docker_env
    )

    expected_returncode, expected_error = fips_util.fips_expectations(
        rockcraft_yaml, GOFIPS
    )

    assert (
        process.returncode == expected_returncode
    ), f"Return code mismatch for {entrypoint} in image {rock_param.image}, stderr: {process.stderr}"
    assert (
        expected_error in process.stderr
    ), f"Error message mismatch for {entrypoint} in image {rock_param.image}, stderr: {process.stderr}"
