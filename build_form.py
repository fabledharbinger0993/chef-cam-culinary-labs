"""
Weekly Kitchen Board (PDF) generator.

This is the source of truth for the printable form. The slot names, header
labels, and colors are drawn as real text/shapes -- they are NOT form fields,
so they can't be retyped in Preview/Acrobat. To change any of them, edit the
values below and rerun: `python3 build_form.py`

QUICK TWEAKS
------------
- SLOTS (list below)         -> add/remove/rename a row on the board
- DAYS / DAY_KEYS (below)    -> add/remove/rename a day column
- FILL / ACCENT / colors     -> the blue-green field tint and section banding
- Any label_field(...) call  -> wording of a header field (e.g. "Anchor protein:")
- checkbox(...) calls        -> the GO column checkboxes

Requires: pip install reportlab (already installed in this environment).
Output: weekly_kitchen_board.pdf, next to this script.
"""

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas

PAGE_W, PAGE_H = landscape(letter)  # 792 x 612
MARGIN = 28

FILL = colors.HexColor("#E7F7F5")
BORDER = colors.HexColor("#5B9FB6")
INK = colors.HexColor("#153447")
ACCENT = colors.HexColor("#1F6F8B")
SECONDARY_ACCENT = colors.HexColor("#2F9E8F")
GRID_LINE = colors.HexColor("#BDD9E2")
ROW_STRIPE = colors.HexColor("#F3FBFC")
CELL_RADIUS = 6
CELL_INSET = 1.25

SLOTS = [
    "Appetizer / Side",
    "Salad",
    "Entree Salad + Protein",
    "Vegetarian Dish",
    "Special Sandwich",
    "Composed Dish",
    "Flatbread",
]
DAYS = ["WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]
DAY_KEYS = ["wed", "thu", "fri", "sat"]

c = canvas.Canvas("weekly_kitchen_board.pdf", pagesize=landscape(letter))
form = c.acroForm


def text(x, y, s, size=8, font="Helvetica", color=INK):
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawString(x, y, s)


def rounded_box(x, y, w, h, fill, border=BORDER, line_width=0.75, radius=CELL_RADIUS):
    c.setFillColor(fill)
    c.setStrokeColor(border)
    c.setLineWidth(line_width)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)


def field(name, x, y, w, h, size=9, tooltip=""):
    rounded_box(x, y, w, h, FILL)
    form.textfield(
        name=name,
        tooltip=tooltip or name,
        x=x + CELL_INSET, y=y + CELL_INSET,
        width=w - (2 * CELL_INSET), height=h - (2 * CELL_INSET),
        borderStyle="solid",
        borderWidth=0,
        borderColor=BORDER,
        fillColor=FILL,
        textColor=INK,
        fontSize=size,
        forceBorder=True,
        relative=False,
    )


def checkbox(name, x, y, size=10, tooltip=""):
    rounded_box(x, y, size, size, colors.white, border=SECONDARY_ACCENT, radius=2.5)
    form.checkbox(
        name=name,
        tooltip=tooltip or name,
        x=x + 0.75, y=y + 0.75, size=size - 1.5,
        buttonStyle="check",
        borderStyle="solid",
        borderWidth=0,
        borderColor=SECONDARY_ACCENT,
        fillColor=colors.white,
        forceBorder=True,
        checked=False,
    )


def label_field(x, y, label, label_w, field_w, name, h=15, lsize=7.5, fsize=9):
    text(x, y + 4, label, size=lsize, font="Helvetica-Bold")
    field(name, x + label_w, y, field_w, h, size=fsize)
    return x + label_w + field_w


# ---------- Header band ----------
y = PAGE_H - MARGIN  # 584, top

# Title row
row_h = 20
y0 = y - row_h
text(MARGIN, y0 + 5, "WEEKLY KITCHEN BOARD", size=15, font="Helvetica-Bold", color=ACCENT)
text(MARGIN + 235, y0 + 6, "slots stay fixed \u2014 only the dish name changes", size=8.5, font="Helvetica-Oblique")
label_field(PAGE_W - MARGIN - 200, y0 + 2, "Week of:", 45, 155, "week_of", h=15)
y = y0

# Anchors row 1
row_h = 20
y0 = y - row_h
x = MARGIN
x = label_field(x, y0 + 2, "Team (2\u20136):", 70, 34, "team_size")
x += 14
x = label_field(x, y0 + 2, "Anchor protein:", 82, 150, "anchor_protein")
x += 14
x = label_field(x, y0 + 2, "Anchor veg base:", 90, 150, "anchor_veg")
y = y0

# Anchors row 2
row_h = 20
y0 = y - row_h
x = MARGIN
x = label_field(x, y0 + 2, "Sauce / dressing:", 90, 130, "anchor_sauce")
x += 12
x = label_field(x, y0 + 2, "Bread / dough:", 78, 130, "anchor_bread")
x += 12
remaining_w = (PAGE_W - MARGIN) - x - 70
x = label_field(x, y0 + 2, "Carries over from last week:", 145, remaining_w, "carryover_note")
y = y0

y -= 6  # gap

# ---------- Grid ----------
SLOT_COL_W = 150
GO_COL_W = 38
DAY_COL_W = (PAGE_W - 2 * MARGIN - SLOT_COL_W - GO_COL_W) / 4.0

col_x = [MARGIN + SLOT_COL_W + i * DAY_COL_W for i in range(4)]
go_x = MARGIN + SLOT_COL_W + 4 * DAY_COL_W

# column header row
hdr_h = 14
y0 = y - hdr_h
text(MARGIN, y0 + 3, "SLOT", size=8, font="Helvetica-Bold", color=colors.white)
for i, d in enumerate(DAYS):
    text(col_x[i] + 4, y0 + 3, d, size=8, font="Helvetica-Bold", color=colors.white)
text(go_x + 2, y0 + 3, "GO", size=7.5, font="Helvetica-Bold", color=colors.white)
c.setFillColor(ACCENT)
c.roundRect(MARGIN, y0, PAGE_W - 2 * MARGIN, hdr_h, 4, fill=1, stroke=0)
# redraw text on top of the accent bar (rect draw order fix)
text(MARGIN, y0 + 3, "SLOT", size=8, font="Helvetica-Bold", color=colors.white)
for i, d in enumerate(DAYS):
    text(col_x[i] + 4, y0 + 3, d, size=8, font="Helvetica-Bold", color=colors.white)
text(go_x + 2, y0 + 3, "GO", size=7.5, font="Helvetica-Bold", color=colors.white)
grid_top = y0 + hdr_h
y = y0

ROW_H = 32
FIELD_H = 20
for si, slot in enumerate(SLOTS):
    y0 = y - ROW_H
    # zebra striping
    if si % 2 == 0:
        c.setFillColor(ROW_STRIPE)
        c.rect(MARGIN, y0, PAGE_W - 2 * MARGIN, ROW_H, fill=1, stroke=0)
    text(MARGIN + 3, y0 + ROW_H / 2.0 - 3, slot, size=8.5, font="Helvetica-Bold")
    for i in range(4):
        field(f"dish_{si}_{DAY_KEYS[i]}", col_x[i] + 3, y0 + (ROW_H - FIELD_H) / 2.0,
              DAY_COL_W - 8, FIELD_H, size=8.5,
              tooltip=f"{slot} \u2014 {DAYS[i]}")
    checkbox(f"go_{si}", go_x + (GO_COL_W - 10) / 2.0, y0 + (ROW_H - 10) / 2.0, size=10,
              tooltip=f"{slot} travels well as grab-and-go this week")
    c.setStrokeColor(GRID_LINE)
    c.setLineWidth(0.5)
    c.line(MARGIN, y0, PAGE_W - MARGIN, y0)
    y = y0

# outer grid border
c.setStrokeColor(BORDER)
c.setLineWidth(1)
c.rect(MARGIN, y, PAGE_W - 2 * MARGIN, grid_top - y, fill=0, stroke=1)
for xline in [MARGIN + SLOT_COL_W, go_x] + col_x[1:]:
    c.line(xline, y, xline, grid_top)

y -= 6  # gap

# ---------- Service debrief strip ----------
hdr_h = 14
y0 = y - hdr_h
c.setFillColor(SECONDARY_ACCENT)
c.roundRect(MARGIN, y0, PAGE_W - 2 * MARGIN, hdr_h, 4, fill=1, stroke=0)
text(MARGIN + 3, y0 + 3, "SERVICE DEBRIEF \u2014 fill at close, before anyone leaves", size=8, font="Helvetica-Bold", color=colors.white)
y = y0

deb_label_w = 95
deb_col_w = (PAGE_W - 2 * MARGIN - deb_label_w) / 4.0

row_h = 20
y0 = y - row_h
text(MARGIN, y0 + 5, "Sold out \u2192", size=8, font="Helvetica-Bold")
for i in range(4):
    field(f"soldout_{DAY_KEYS[i]}", MARGIN + deb_label_w + i * deb_col_w + 3, y0 + 2,
          deb_col_w - 8, 15, size=8.5, tooltip=f"What sold out on {DAYS[i]}")
y = y0

row_h = 20
y0 = y - row_h
text(MARGIN, y0 + 5, "Kill list \u2192", size=8, font="Helvetica-Bold")
for i in range(4):
    field(f"kill_{DAY_KEYS[i]}", MARGIN + deb_label_w + i * deb_col_w + 3, y0 + 2,
          deb_col_w - 8, 15, size=8.5, tooltip=f"What should not come back, {DAYS[i]}")
y = y0

row_h = 20
y0 = y - row_h
label_field(MARGIN, y0 + 2, "Plate cost / price flag this week:", 195, PAGE_W - 2 * MARGIN - 195,
            "platecost_note", h=15)
y = y0

y -= 8  # gap

# ---------- Notes ----------
hdr_h = 14
y0 = y - hdr_h
text(MARGIN, y0 + 3, "Notes / lesson-plan follow-ups:", size=8, font="Helvetica-Bold")
y = y0

notes_h = y - (MARGIN + 20)
rounded_box(MARGIN, MARGIN + 20, PAGE_W - 2 * MARGIN, notes_h, FILL)
form.textfield(
    name="notes_field", tooltip="Notes / lesson-plan follow-ups",
    x=MARGIN + CELL_INSET, y=MARGIN + 20 + CELL_INSET,
    width=PAGE_W - 2 * MARGIN - (2 * CELL_INSET), height=notes_h - (2 * CELL_INSET),
    borderStyle="solid", borderWidth=0, borderColor=BORDER,
    fillColor=FILL, textColor=INK, fontSize=9,
    fieldFlags="multiline", forceBorder=True, relative=False,
)

# ---------- Sign-off ----------
label_field(PAGE_W - MARGIN - 220, MARGIN, "Instructor initials:", 105, 90, "instructor_initials", h=14)
text(MARGIN, MARGIN + 4, "Guthrie Entertainment \u2014 Cameron Kelly", size=7, font="Helvetica-Oblique",
     color=colors.HexColor("#6C8C96"))

c.showPage()
c.save()
print("done")
