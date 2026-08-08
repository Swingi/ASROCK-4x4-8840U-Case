# Parametric dimensions for the one-piece printable bottom.
# Units: mm

BASE_X = 170.0
BASE_Y = 170.0
BASE_THICKNESS = 10.0

FOOT_HEIGHT = 40.0
FOOT_DIAMETER = 16.0
FOOT_INSET = 15.0

# Four M4 clearance holes for the threaded rods.
# Taken from the uploaded Noctua Venti.FCStd:
# hole centres are 62.25 mm from the fan centre, giving 22.75 mm
# from each 170 mm bottom edge. The FCStd hole diameter is 4.30 mm.
ROD_HOLE_DIAMETER = 4.30
ROD_HOLE_X = 22.75
ROD_HOLE_Y = 22.75

# Ventilation / lamella field in the bottom plate.
LATTICE_X = 150.0
LATTICE_Y = 150.0
LATTICE_SLOT_WIDTH = 3.0
LATTICE_RIB_WIDTH = 3.0
LATTICE_EDGE = 10.0

# Plug-in wall guide system. The later lid+walls will have tongues
# matching this channel.
WALL_THICKNESS = 3.0
WALL_CLEARANCE = 0.35
GUIDE_RAIL_WIDTH = 4.0
GUIDE_HEIGHT = 8.0
GUIDE_EDGE = 3.0

# Small corner reinforcement where the wall guides meet.
CORNER_POST_SIZE = 10.0

OUTPUT_DIR = "output"
