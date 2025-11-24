#
# Copyright 2025 Canonical, Ltd.
#

import shlex

import pytest
from k8s_test_harness.util import docker_util, env_util, fips_util
from test_util import config, rock

IMAGE_NAME = "cilium-operator-generic"
IMAGE_BASE = f"ghcr.io/canonical/{IMAGE_NAME}"
IMAGE_ENTRYPOINT = "cilium-operator-generic --version"


@pytest.fixture
def skip_if_nonfips(GOFIPS, image_version):
    rockcraft_yaml = (
        (
            config.REPO_PATH
            / image_version
            / "cilium-operator-generic"
            / "rockcraft.yaml"
        )
        .read_text()
        .lower()
    )

    if GOFIPS == 1 and not fips_util.is_fips_rock(rockcraft_yaml):
        pytest.skip("Skipping because this version of rock is not built for FIPS")


@pytest.mark.parametrize(
    "image_version", env_util.image_versions_in_repo(IMAGE_NAME, config.REPO_PATH)
)
def test_executable(image_version):
    rock.run_image(IMAGE_NAME, image_version, IMAGE_ENTRYPOINT, config.IMAGE_ARCH)


@pytest.mark.parametrize(
    "image_version", env_util.image_versions_in_repo(IMAGE_NAME, config.REPO_PATH)
)
def test_pebble_executable(image_version):
    rock.check_pebble(IMAGE_NAME, image_version, "v1.18.0", config.IMAGE_ARCH)


@pytest.mark.parametrize("GOFIPS", [0, 1], ids=lambda v: f"GOFIPS={v}")
@pytest.mark.parametrize(
    "image_version", env_util.image_versions_in_repo(IMAGE_NAME, config.REPO_PATH)
)
def test_fips(skip_if_nonfips, image_version, GOFIPS):
    image = env_util.get_build_meta_info_for_rock_version(
        IMAGE_NAME, image_version, config.IMAGE_ARCH
    ).image
    entrypoint = shlex.split(IMAGE_ENTRYPOINT)

    rockcraft_yaml = (
        (
            config.REPO_PATH
            / image_version
            / "cilium-operator-generic"
            / "rockcraft.yaml"
        )
        .read_text()
        .lower()
    )

    docker_env = ["-e", f"GOFIPS={GOFIPS}"]
    process = docker_util.run_in_docker(
        image, entrypoint, check_exit_code=False, docker_args=docker_env
    )

    expected_returncode, expected_error = fips_util.fips_expectations(
        rockcraft_yaml, GOFIPS
    )

    assert (
        process.returncode == expected_returncode
    ), f"Return code mismatch for {entrypoint} in image {image}, stderr: {process.stderr}"
    assert (
        expected_error in process.stderr
    ), f"Error message mismatch for {entrypoint} in image {image}, stderr: {process.stderr}"
