#
# Copyright 2026 Canonical, Ltd.
#

from dataclasses import dataclass
from typing import List

from k8s_test_harness.util import docker_util, env_util


@dataclass
class RockTestParam:
    name: str
    version: str
    path: str
    arch: str
    image: str

    @property
    def variant(self) -> str:
        parts = self.path.rstrip("/").split("/")
        if parts[-1] == self.name:
            return ""
        return parts[-1]

    @property
    def display_id(self) -> str:
        if self.variant:
            return f"{self.version}-{self.variant}"
        return self.version


def get_rock_test_param(
    rock_name: str,
    arch: str,
) -> List[RockTestParam]:
    all_metas = env_util.get_rocks_meta_info_from_env()

    params = []
    for meta in all_metas:
        if meta.name != rock_name:
            continue
        if meta.arch != arch:
            continue

        param = RockTestParam(
            name=meta.name,
            version=meta.version,
            path=meta.rock_dir,
            arch=meta.arch,
            image=meta.image,
        )
        params.append(param)

    params.sort(key=lambda p: (p.version, p.variant))

    return params


def rock_param_id(param: RockTestParam) -> str:
    return param.display_id


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


def run_image_direct(image: str, image_version: str, image_entrypoint: str):
    """Run entrypoint on image directly without version lookup."""
    docker_util.run_entrypoint_and_assert(
        image, image_entrypoint, expect_stdout_contains=image_version
    )


def check_pebble_direct(image: str, pebble_version: str = None):
    """Check pebble on image. If version provided, validate it; otherwise just check pebble runs."""
    expected = pebble_version if pebble_version else "client"
    docker_util.run_entrypoint_and_assert(
        image, "/bin/pebble version", expect_stdout_contains=expected
    )
