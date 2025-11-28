#
# Copyright 2025 Canonical, Ltd.
#

import os
from pathlib import Path

TEST_PATH = Path(__file__)
REPO_PATH = TEST_PATH.parent.parent.parent.parent


IMAGE_ARCH = os.getenv("CILIUM_IMAGE_ARCH") or "amd64"
PEBBLE_VERSION = os.getenv("CILIUM_PEBBLE_VERSION") or "v1.18.0"
