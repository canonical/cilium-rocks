#
# Copyright 2025 Canonical, Ltd.
#

from k8s_test_harness.util import docker_util, env_util


def run_image(image_name, image_version, image_entrypoint, arch):
    image = env_util.get_build_meta_info_for_rock_version(
        image_name, image_version, arch
    ).image
    docker_util.run_entrypoint_and_assert(
        image, image_entrypoint, expect_stdout_contains=image_version
    )


def check_pebble(image_name, image_version, pebble_version, arch):
    image = env_util.get_build_meta_info_for_rock_version(
        image_name, image_version, arch
    ).image
    docker_util.run_entrypoint_and_assert(
        image, "/bin/pebble version", expect_stdout_contains=pebble_version
    )
