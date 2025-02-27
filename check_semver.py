#!/usr/bin/env python
import re
import sys

# 1.0.0-alpha+001
semver_regex= r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"  # noqa: E501

if __name__ == "__main__":
    tag_name=sys.argv[1]

    m = re.match(semver_regex, tag_name)
    assert m is not None, f"Invalid tag format: {tag_name}"
    for gpe_name in ["major", "minor", "patch", "prerelease", "buildmetadata"]:
        print(f"{gpe_name}: {m.group(gpe_name)}")  # noqa: T201

