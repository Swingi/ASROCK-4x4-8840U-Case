import os
import sys

PROJECT_DIR = r"D:/Download/ASROCK Box 4x4 8840U/repo/ASROCK-4x4-8840U-Case-main"
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

for module_name in ("bottom", "lid", "filter_tray", "filter_panels", "config"):
    if module_name in sys.modules:
        del sys.modules[module_name]

from build_bottom import build as build_bottom
from build_lid import build as build_lid
from build_filter_tray import build as build_filter_tray
from build_filter_panels import build as build_filter_panels


def build_all():
    print("=== ASROCK 4x4 complete build ===")
    bottom_doc, bottom_obj = build_bottom()
    lid_doc, lid_obj = build_lid()
    tray_doc, tray_obj = build_filter_tray()
    filter_doc, filter_objs = build_filter_panels()
    print("=== Build complete ===")
    return (bottom_doc, bottom_obj, lid_doc, lid_obj,
            tray_doc, tray_obj, filter_doc, filter_objs)


if __name__ == "__main__":
    build_all()
