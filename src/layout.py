# ==========================================
# DASHBOARD
# ==========================================

DASHBOARD_WIDTH = 960
DASHBOARD_HEIGHT = 670


# ==========================================
# VIDEO UTAMA
# ==========================================
VIDEO_WIDTH = 760
VIDEO_HEIGHT = 428

VIDEO_X = (DASHBOARD_WIDTH - VIDEO_WIDTH) // 2
VIDEO_Y = 85

VIDEO_TITLE_Y = VIDEO_Y - 5


# ==========================================
# HEADER
# ==========================================

TITLE_Y = 35
CAMERA_Y = TITLE_Y + 20


# ==========================================
# GARIS LAYOUT
# ==========================================

LINE_HEADER = CAMERA_Y + 10

LINE_VIDEO = VIDEO_Y + VIDEO_HEIGHT + 10

INFO_Y = LINE_VIDEO + 20
LINE_INFO = LINE_VIDEO + 30

VEHICLE_TITLE_Y = LINE_INFO + 20
ANALYSIS_TITLE_Y = VEHICLE_TITLE_Y

LINE_PANEL = LINE_INFO + 30

LINE_MIDDLE = DASHBOARD_WIDTH // 2


# ==========================================
# SYSTEM INFORMATION
# ==========================================

FRAME_LABEL_X = 100
FRAME_VALUE_X = 200

FPS_LABEL_X = 380
FPS_VALUE_X = 460

RESOLUTION_LABEL_X = 650
RESOLUTION_VALUE_X = 750


# ==========================================
# VEHICLE PANEL
# ==========================================

VEHICLE_TITLE_X = 200

VEHICLE_LABEL_X = 60
VEHICLE_VALUE_X = 220

VEHICLE_START_Y = LINE_PANEL + 28
VEHICLE_ROW_GAP = 22


# Garis sebelum TOTAL
TOTAL_LINE_START_X = VEHICLE_LABEL_X
TOTAL_LINE_END_X = 260
TOTAL_LINE_Y = VEHICLE_START_Y + (5 * VEHICLE_ROW_GAP)

# Posisi tulisan TOTAL
TOTAL_Y = TOTAL_LINE_Y + 25


# ==========================================
# TRAFFIC ANALYSIS
# ==========================================

ANALYSIS_TITLE_X = 750

ANALYSIS_LABEL_X = 600
ANALYSIS_VALUE_X = 780

ANALYSIS_START_Y = LINE_PANEL + 30
ANALYSIS_ROW_GAP = 30


# Garis sebelum STATUS
STATUS_LINE_START_X = 600
STATUS_LINE_END_X = 880
STATUS_LINE_Y = ANALYSIS_START_Y + (3 * ANALYSIS_ROW_GAP)

STATUS_LABEL_Y = STATUS_LINE_Y + 25
STATUS_VALUE_Y = STATUS_LABEL_Y


# ==========================================
# FOOTER
# ==========================================

FOOTER_LINE_Y = DASHBOARD_HEIGHT - 35

FOOTER_LINE_START_X = 0
FOOTER_LINE_END_X = DASHBOARD_WIDTH

FOOTER_Y = DASHBOARD_HEIGHT - 15


# ==========================================
# VERTICAL DIVIDER
# ==========================================

MID_LINE_START_Y = LINE_PANEL
MID_LINE_END_Y = FOOTER_LINE_Y


# ==========================================
# COLORS
# ==========================================

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (0, 255, 255)
RED = (0, 0, 255)
GRAY = (170, 170, 170)


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


# ==========================================
# YOLO DETECTION
# ==========================================

BOX_COLOR = (0, 255, 0)

LABEL_BG_COLOR = (0, 170, 0)
LABEL_TEXT_COLOR = WHITE

BOX_THICKNESS = 2
CORNER_LENGTH = 15
LABEL_PADDING = 5

# ==========================================
# COMPACT SUMMARY PANEL
# ==========================================

# Garis atas panel ringkasan
SUMMARY_LINE_TOP_Y = LINE_INFO

# Judul kelompok
SUMMARY_TITLE_Y = LINE_INFO + 22

# Baris isi
SUMMARY_VALUE_Y = SUMMARY_TITLE_Y + 32

# Garis bawah panel ringkasan
SUMMARY_LINE_BOTTOM_Y = SUMMARY_VALUE_Y + 25


# Batas pembagian panel
SUMMARY_MIDDLE_X = DASHBOARD_WIDTH // 2


# ==========================================
# FOOTER
# ==========================================

FOOTER_LINE_Y = SUMMARY_LINE_BOTTOM_Y

FOOTER_Y = DASHBOARD_HEIGHT - 15


SUMMARY_ROW_1_Y = SUMMARY_TITLE_Y + 28
SUMMARY_ROW_2_Y = SUMMARY_ROW_1_Y + 32

