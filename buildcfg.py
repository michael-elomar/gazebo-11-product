import dragon
import shutil
from pathlib import Path
import re
import tarfile
import subprocess


workspace_dir = Path(dragon.WORKSPACE_DIR)
dragon_out_dir = Path(dragon.OUT_DIR)
tarball_artifacts_dir = dragon_out_dir / "tarball"
dragon_images_dir = Path(dragon.IMAGES_DIR)
packages_dir = workspace_dir / "packages"


def copytree(src, dst):
    for s in src.glob("**/*"):
        if s.is_dir() or s.is_symlink():
            continue
        path = s.relative_to(src)
        d = dst / path
        dragon.LOGD(f"Copying {s} -> {d}...")
        d.parent.mkdir(parents=True, exist_ok=True)
        d.write_bytes(s.read_bytes())
        shutil.copystat(s, d, follow_symlinks=False)
        dragon.LOGD(f"Copying {s} -> {d}: OK")


def exclude_files(tarinfo_obj):
    if not re.match(r".*\.(git|pyc)", tarinfo_obj.name):
        return tarinfo_obj


def autotests_tarball_hook(task, args):
    sources = [
        workspace_dir / "build",
        workspace_dir / "modules",
        workspace_dir / "products",
        workspace_dir / "setenv",
        dragon_out_dir / "pyenv_root",
        dragon_out_dir / "staging",
    ]

    tarball_artifacts_dir.mkdir(parents=True, exist_ok=True)

    tarball = tarball_artifacts_dir / "autotests_wsp.tar"

    dragon.LOGI(f"Creating tarball {tarball}...")
    with tarfile.open(tarball, "w:") as tar:
        for source in sources:
            path = str(Path("autotests") / source.relative_to(workspace_dir))
            dragon.LOGI(f"Adding {path} to {tarball.name}...")
            tar.add(source, arcname=path, filter=exclude_files)

    dragon.LOGI(f"Compressing tarball {tarball} with pigz...")
    subprocess.run(
        ["pigz", "-f", tarball],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
    )


dragon.add_meta_task(
    name="dependencies",
    desc="Build dependencies before building gz packages",
    subtasks=[
        "alchemy eigen CLI11 freeimage gdal jsoncpp libyaml "
        "libzip sdformat spdlog swig tinyxml2 libwebsockets",
    ],
)

dragon.add_meta_task(
    name="build-gz",
    desc="Build gz packages in the right order",
    subtasks=[
        "alchemy gz-cmake gz-utils gz-msgs gz-tools ",
        "alchemy gz-transport gz-plugin gz-fuel-tools",
        "alchemy gz-math gz-sensors",
        "alchemy gz-physics",
        "alchemy gz-common gz-rendering gz-gui gz-launch gz-sim",
    ],
)


dragon.add_meta_task(
    name="tarball",
    desc="Create autotests tarball",
    posthook=autotests_tarball_hook,
)


dragon.override_meta_task(
    "build",
    subtasks=["dependencies", "build-gz"],
)
