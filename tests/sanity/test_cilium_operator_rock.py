#
# Copyright 2025 Canonical, Ltd.
#

import shlex
from pathlib import Path

import pytest
from k8s_test_harness.util import docker_util, env_util, fips_util

TEST_PATH = Path(__file__)
REPO_PATH = TEST_PATH.parent.parent.parent
IMAGE_NAME = "cilium-operator-generic"
IMAGE_BASE = f"ghcr.io/canonical/{IMAGE_NAME}"
IMAGE_ENTRYPOINT = "cilium-operator-generic --version"


@pytest.mark.parametrize(
    "image_version", env_util.image_versions_in_repo(IMAGE_NAME, REPO_PATH)
)
def test_executable(image_version):
    image = env_util.get_build_meta_info_for_rock_version(
        IMAGE_NAME, image_version, "amd64"
    ).image
    docker_util.run_entrypoint_and_assert(
        image, IMAGE_ENTRYPOINT, expect_stdout_contains=image_version
    )


@pytest.mark.parametrize(
    "image_version", env_util.image_versions_in_repo(IMAGE_NAME, REPO_PATH)
)
def test_pebble_executable(image_version):
    image = env_util.get_build_meta_info_for_rock_version(
        IMAGE_NAME, image_version, "amd64"
    ).image
    docker_util.run_entrypoint_and_assert(
        image, "/bin/pebble version", expect_stdout_contains="v1.18.0"
    )


@pytest.mark.parametrize("GOFIPS", [0, 1], ids=lambda v: f"GOFIPS={v}")
@pytest.mark.parametrize(
    "image_version", env_util.image_versions_in_repo(IMAGE_NAME, REPO_PATH)
)
def test_fips(image_version, GOFIPS):
    image = env_util.get_build_meta_info_for_rock_version(
        IMAGE_NAME, image_version, "amd64"
    ).image
    entrypoint = shlex.split(IMAGE_ENTRYPOINT)

    rockcraft_yaml = (
        (REPO_PATH / image_version / "cilium-operator-generic" / "rockcraft.yaml")
        .read_text()
        .lower()
    )

    # TODO: Remove this skip logic once the non-FIPS images with go <= 1.22 could be run
    # with GOFIPS=1
    if GOFIPS == 1 and not fips_util.is_fips_rock(rockcraft_yaml):
        pytest.skip("Skipping because this version of rock is not built for FIPS")

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
