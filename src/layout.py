# ==========================================
# DASHBOARD
# ==========================================

DASHBOARD_WIDTH = 1100
DASHBOARD_HEIGHT = 690

# ==========================================
# VIDEO
# ==========================================

VIDEO_WIDTH = 460
VIDEO_HEIGHT = 260

VIDEO_LEFT_X = 30
VIDEO_LEFT_Y = 80

VIDEO_RIGHT_X = 610
VIDEO_RIGHT_Y = VIDEO_LEFT_Y

# ==========================================
# HEADER
# ==========================================
#TITLE_X = 100
TITLE_Y = 35

#CAMERA_X = 880
CAMERA_Y = TITLE_Y + 15

LEFT_TITLE_X = VIDEO_LEFT_X
LEFT_TITLE_Y = VIDEO_LEFT_Y - 5

RIGHT_TITLE_X = VIDEO_RIGHT_X
RIGHT_TITLE_Y = LEFT_TITLE_Y

# ==========================================
# LINES
# ==========================================
LINE_HEADER = CAMERA_Y + 5

LINE_VIDEO = VIDEO_LEFT_Y + VIDEO_HEIGHT + 10

LINE_INFO = LINE_VIDEO + 30

LINE_PANEL = LINE_INFO + 30

LINE_MIDDLE = DASHBOARD_WIDTH // 2


# ==========================================
# SYSTEM INFORMATION
# ==========================================

INFO_Y = LINE_VIDEO + 20

FRAME_LABEL_X = 110
FRAME_VALUE_X = 200

FPS_LABEL_X = 410
FPS_VALUE_X = 480

RESOLUTION_LABEL_X = 690
RESOLUTION_VALUE_X = 860


# ==========================================
# VEHICLE PANEL
# ==========================================

VEHICLE_TITLE_X = 200
VEHICLE_TITLE_Y = LINE_INFO + 20


VEHICLE_LABEL_X = 60
VEHICLE_VALUE_X = 220

VEHICLE_START_Y = VEHICLE_TITLE_Y + 50
VEHICLE_ROW_GAP = 30


# Garis Total
TOTAL_LINE_START_X = VEHICLE_LABEL_X 
TOTAL_LINE_END_X = 260
TOTAL_LINE_Y = VEHICLE_START_Y + (5 * VEHICLE_ROW_GAP)

# Posisi tulisan TOTAL
TOTAL_Y = TOTAL_LINE_Y + 25

# ==========================================
# TRAFFIC ANALYSIS
# ==========================================

ANALYSIS_TITLE_X = 750
ANALYSIS_TITLE_Y = VEHICLE_TITLE_Y

ANALYSIS_LABEL_X = 600
ANALYSIS_VALUE_X = 780

ANALYSIS_START_Y = ANALYSIS_TITLE_Y + 60
ANALYSIS_ROW_GAP = 40

# Garis Status
STATUS_LINE_START_X = 600
STATUS_LINE_END_X = 880
STATUS_LINE_Y = ANALYSIS_START_Y + (3 * ANALYSIS_ROW_GAP)

# Tulisan STATUS
STATUS_LABEL_Y = STATUS_LINE_Y + 25
STATUS_VALUE_Y = STATUS_LABEL_Y


# ==========================================
# FOOTER
# ==========================================
FOOTER_LINE_Y = DASHBOARD_HEIGHT - 25

FOOTER_LINE_START_X = 0
FOOTER_LINE_END_X = DASHBOARD_WIDTH

#FOOTER_X = DASHBOARD_WIDTH //2 - ()
FOOTER_Y = DASHBOARD_HEIGHT - 10



# ==========================================
# COLORS
# ==========================================

WHITE = (255,255,255)
BLACK = (0,0,0)
GREEN = (0,255,0)
YELLOW = (0,255,255)
RED = (0,0,255)
GRAY = (170,170,170)


# ==========================================
# FONT SCALE
# ==========================================

FONT_TITLE = 1.0
FONT_SUBTITLE = 0.5
FONT_TEXT = 0.6
FONT_VALUE = 0.65
FONT_STATUS = 0.8
FONT_FOOTER = 0.45


# ==========================================
# THICKNESS
# ==========================================

THICKNESS_BORDER = 2

THICKNESS_LINE = 1

THICKNESS_TITLE = 2

THICKNESS_TEXT = 2

THICKNESS_STATUS = 1

THICKNESS_FOOTER = 1


# Vertical Divider
MID_LINE_START_Y = LINE_INFO
MID_LINE_END_Y = FOOTER_LINE_Y

# ==========================================
# YOLO DETECTION
# ==========================================

BOX_COLOR = (0, 255, 0)

LABEL_BG_COLOR = (0, 170, 0)

LABEL_TEXT_COLOR = WHITE

BOX_THICKNESS = 2

CORNER_LENGTH = 15

LABEL_PADDING = 5