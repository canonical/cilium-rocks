#
# Copyright 2025 Canonical, Ltd.
#

import shlex
from pathlib import Path

import pytest
import yaml
from k8s_test_harness.util import docker_util, env_util, fips_util

TEST_PATH = Path(__file__)
REPO_PATH = TEST_PATH.parent.parent.parent
IMAGE_NAME = "cilium"
IMAGE_BASE = f"ghcr.io/canonical/{IMAGE_NAME}"
IMAGE_ENTRYPOINT = "cilium-agent --version"


def _image_versions():
    all_rockcrafts = REPO_PATH.glob("**/cilium/rockcraft.yaml")
    yamls = [yaml.safe_load(rock.read_bytes()) for rock in all_rockcrafts]
    return [rock["version"] for rock in yamls]


@pytest.mark.parametrize("image_version", _image_versions())
def test_executable(image_version):
    image = env_util.get_build_meta_info_for_rock_version(
        IMAGE_NAME, image_version, "amd64"
    ).image
    docker_util.run_entrypoint_and_assert(
        image, IMAGE_ENTRYPOINT, expect_stdout_contains=image_version
    )


@pytest.mark.parametrize("image_version", _image_versions())
def test_pebble_executable(image_version):
    image = env_util.get_build_meta_info_for_rock_version(
        IMAGE_NAME, image_version, "amd64"
    ).image
    docker_util.run_entrypoint_and_assert(
        image, "/bin/pebble version", expect_stdout_contains="v1.18.0"
    )


@pytest.mark.parametrize("GOFIPS", [0, 1], ids=lambda v: f"GOFIPS={v}")
@pytest.mark.parametrize("image_version", _image_versions())
def test_fips(image_version, GOFIPS):
    image = env_util.get_build_meta_info_for_rock_version(
        IMAGE_NAME, image_version, "amd64"
    ).image
    entrypoint = shlex.split(IMAGE_ENTRYPOINT)

    docker_env = ["-e", f"GOFIPS={GOFIPS}"]
    process = docker_util.run_in_docker(
        image, entrypoint, check_exit_code=False, docker_args=docker_env
    )

    rockcraft_yaml = (REPO_PATH / image_version / "cilium" / "rockcraft.yaml").read_text().lower()
    expected_returncode, expected_error = fips_util.fips_expectations(
        rockcraft_yaml, GOFIPS
    )

    assert (
        process.returncode == expected_returncode
    ), f"Return code mismatch for {entrypoint} in image {image}, stderr: {process.stderr}"
    assert (
        expected_error in process.stderr
    ), f"Error message mismatch for {entrypoint} in image {image}, stderr: {process.stderr}"
