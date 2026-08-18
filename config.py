# Parametric dimensions for the ASRock 4X4-8840U enclosure.
# Units: mm

BASE_X = 170.0
BASE_Y = 170.0
BASE_THICKNESS = 10.0

# M3 threaded-rod system. Rods sit directly over the four fan mounting positions.
FOOT_HEIGHT = 40.0
FOOT_DIAMETER = 26.0
ROD_OFFSET_X = 22.75
ROD_OFFSET_Y = 22.75
ROD_HOLE_DIAMETER = 3.40       # M3 clearance

# M3 washer + safety/nyloc nut captured in the underside of each foot.
M3_WASHER_OD = 7.20
M3_WASHER_POCKET_DEPTH = 1.20
M3_NUT_AF = 5.50
M3_NUT_POCKET_AF = 6.60
M3_NUT_POCKET_DEPTH = 4.20

# 140 mm fan geometry.
FAN_SIZE = 140.0
FAN_MOUNT_HOLE_SPACING = 124.5
FAN_MOUNT_HOLE_DIAMETER = 4.5
FAN_OPENING_DIAMETER = 140.0

# Bottom ventilation and filter drawer.
LATTICE_X = 150.0
LATTICE_Y = 150.0
LATTICE_SLOT_WIDTH = 3.0
LATTICE_RIB_WIDTH = 3.0
LATTICE_EDGE = 10.0
FILTER_DRAWER_WIDTH = 146.0
FILTER_DRAWER_LENGTH = 154.0
FILTER_DRAWER_THICKNESS = 3.0
FILTER_DRAWER_RAIL_WIDTH = 5.0
FILTER_DRAWER_RAIL_HEIGHT = 4.0
FILTER_DRAWER_CLEARANCE = 0.40
FILTER_DRAWER_STOP = 6.0

# One-piece lid + four side walls.
WALL_THICKNESS = 3.0
WALL_CLEARANCE = 0.30
GUIDE_RAIL_WIDTH = 5.0
GUIDE_HEIGHT = 12.0
GUIDE_EDGE = 5.0
CORNER_POST_SIZE = 12.0
LID_TOP_THICKNESS = 4.0
SIDE_WALL_HEIGHT = 58.0
LID_Z0 = BASE_THICKNESS
LID_TOP_Z = LID_Z0 + SIDE_WALL_HEIGHT
ROD_PASSAGE_DIAMETER = 4.20

# Removable filter frames. The actual filter media is a fine mesh fitted into these frames.
TOP_FILTER_SIZE = 144.0
TOP_FILTER_FRAME_WIDTH = 4.0
TOP_FILTER_FRAME_THICKNESS = 2.5
SIDE_FILTER_FRAME_THICKNESS = 2.5
SIDE_FILTER_CLEARANCE = 0.40

# Mainboard envelope. The board is 104 x 102 mm according to ASRock documentation.
MAINBOARD_X = 104.0
MAINBOARD_Y = 102.0
MAINBOARD_Z = BASE_THICKNESS + 4.0

# I/O openings. These are deliberately parameterized so they can be tuned to the supplied FCStd.
# Front: power button + 2x USB-C + USB-A + audio.
FRONT_IO_WIDTH = 92.0
FRONT_IO_HEIGHT = 24.0
FRONT_IO_Z = 27.0

# Rear: 2x HDMI + dual LAN + 2x USB2 + DC-in.
REAR_IO_WIDTH = 142.0
REAR_IO_HEIGHT = 31.0
REAR_IO_Z = 24.0

# Airflow transition: the walls taper from the 140 mm fan region toward the 104 x 102 mm board,
# then open back toward the lower exhaust region. These values control the transition ribs/baffles.
AIRFLOW_TRANSITION_TOP_Z = LID_TOP_Z - 4.0
AIRFLOW_TRANSITION_BOARD_Z = MAINBOARD_Z + 12.0
AIRFLOW_TRANSITION_BOTTOM_Z = BASE_THICKNESS + 8.0
AIRFLOW_TOP_HALF = FAN_SIZE / 2.0
AIRFLOW_BOARD_HALF_X = MAINBOARD_X / 2.0
AIRFLOW_BOARD_HALF_Y = MAINBOARD_Y / 2.0

OUTPUT_DIR = "output"
