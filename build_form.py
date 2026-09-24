"""
Weekly Kitchen Board (PDF) generator.

This is the source of truth for the printable form. The slot names, header
labels, and colors are drawn as real text/shapes -- they are NOT form fields,
so they can't be retyped in Preview/Acrobat. To change any of them, edit the
values below and rerun: `python3 build_form.py`

QUICK TWEAKS
------------
- SLOTS (list below) -> add/remove/rename a row on the board
- DAYS / DAY_KEYS (below) -> add/remove/rename a day column
- FILL / ACCENT / colors -> the blue-green field tint and section banding
- Any label_field(...) call -> wording of a header field (e.g. "Anchor protein:")
- checkbox(...) calls -> the GO column checkboxes / anchor-use checkboxes

THREE PAGES
-----------
Page 1 is the operational board -- what actually gets posted on the wall
during service. It stays close to the original design on purpose: it's meant
to be glanced at while hands are full, not read line by line.

Page 2 is the COSTING, LABOR & WASTE WORKSHEET. It's where the teaching
happens -- food cost math, labor math, prime cost, and an explicit checklist
tying every dish back to the week's four anchor ingredients (the mechanism
that keeps a short shopping list from becoming a wasteful one). It's
deliberately kept off page 1 so the wall board doesn't get cluttered with
numbers nobody needs mid-service.

Page 3 is INVENTORY, YIELD & WASTE: what's on hand by weight, what it really
costs per usable unit after trim, conservative use-by dates, and what got
used vs. tossed. Edit INVENTORY_ROWS / INV_COLS / USE_BY_GUIDE to change it.

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
MUTED = colors.HexColor("#6C8C96")

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

# Short keys for the anchor-use checkbox matrix on page 2.
ANCHORS = [("prot", "Protein"), ("veg", "Veg base"), ("sauce", "Sauce"), ("bread", "Bread/dough")]

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


def banner(x, y, w, h, label, color=ACCENT, size=8, sub=""):
    """Full-width accent bar with a bold left-aligned label (and optional
    right-aligned sub-note), used to head off each worksheet section."""
    c.setFillColor(color)
    c.rect(x, y, w, h, fill=1, stroke=0)
    text(x + 3, y + 3, label, size=size, font="Helvetica-Bold", color=colors.white)
    if sub:
        c.setFont("Helvetica-Oblique", 7)
        c.setFillColor(colors.white)
        c.drawRightString(x + w - 4, y + 3, sub)


# =====================================================================
# PAGE 1 -- the operational board
# =====================================================================

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
carry_label_w = 145
remaining_w = (PAGE_W - MARGIN) - x - carry_label_w
x = label_field(x, y0 + 2, "Carries over from last week:", carry_label_w, remaining_w, "carryover_note")
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
c.setFillColor(ACCENT)
c.rect(MARGIN, y0, PAGE_W - 2 * MARGIN, hdr_h, fill=1, stroke=0)
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
c.rect(MARGIN, y0, PAGE_W - 2 * MARGIN, hdr_h, fill=1, stroke=0)
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
label_field(MARGIN, y0 + 2, "Plate cost flag (see Costing Worksheet, pg 2):", 260, PAGE_W - 2 * MARGIN - 260,
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
text(MARGIN, MARGIN + 4, "Guthrie Entertainment \u2014 Cameron Kelly \u2014 pg. 1 of 3", size=7, font="Helvetica-Oblique",
     color=MUTED)

c.showPage()

# =====================================================================
# PAGE 2 -- Costing, Labor & Waste Worksheet (the teaching page)
# =====================================================================

y = PAGE_H - MARGIN
FULL_W = PAGE_W - 2 * MARGIN

# ---------- Header ----------
row_h = 20
y0 = y - row_h
text(MARGIN, y0 + 5, "COSTING, LABOR & WASTE WORKSHEET", size=14, font="Helvetica-Bold", color=ACCENT)
text(MARGIN + 300, y0 + 6, "do the math before you commit to the board", size=8.5, font="Helvetica-Oblique")
label_field(PAGE_W - MARGIN - 200, y0 + 2, "Week of:", 45, 155, "week_of_pg2", h=15)
y = y0
y -= 4

# ---------- Section A: food cost per dish ----------
hdr_h = 14
y0 = y - hdr_h
banner(MARGIN, y0, FULL_W, hdr_h, "FOOD COST \u2014 one line per dish on this week's board",
       color=ACCENT, sub="target is usually 28\u201335% food cost, unless your program sets otherwise")
y = y0

# column layout: slot name + 5 equal numeric columns
FC_SLOT_W = 150
fc_col_w = (FULL_W - FC_SLOT_W) / 5.0
fc_headers = ["Cost / portion ($)", "Portions made", "Total food cost ($)", "Menu price ($)", "Food cost %"]
fc_tips = [
    "sum of ingredient cost for exactly one plate",
    "how many portions this batch makes",
    "cost per portion \u00d7 portions",
    "what you're charging on the board",
    "total food cost \u00f7 (price \u00d7 portions) \u00d7 100",
]

col_hdr_h = 14
y0 = y - col_hdr_h
c.setFillColor(colors.white)
c.setStrokeColor(GRID_LINE)
c.rect(MARGIN, y0, FULL_W, col_hdr_h, fill=1, stroke=0)
text(MARGIN + 3, y0 + 3, "SLOT", size=7, font="Helvetica-Bold", color=MUTED)
for i, h in enumerate(fc_headers):
    text(MARGIN + FC_SLOT_W + i * fc_col_w + 3, y0 + 3, h, size=6.7, font="Helvetica-Bold", color=MUTED)
fc_grid_top = y0 + col_hdr_h
y = y0

FC_ROW_H = 18
fc_field_names = ["cost", "portions", "totalcost", "price", "fcpct"]
for si, slot in enumerate(SLOTS):
    y0 = y - FC_ROW_H
    if si % 2 == 0:
        c.setFillColor(ROW_STRIPE)
        c.rect(MARGIN, y0, FULL_W, FC_ROW_H, fill=1, stroke=0)
    text(MARGIN + 3, y0 + FC_ROW_H / 2.0 - 3, slot, size=7.5, font="Helvetica-Bold")
    for i, fname in enumerate(fc_field_names):
        field(f"{fname}_{si}", MARGIN + FC_SLOT_W + i * fc_col_w + 3, y0 + 2,
              fc_col_w - 7, FC_ROW_H - 4, size=7.5,
              tooltip=f"{slot} \u2014 {fc_tips[i]}")
    c.setStrokeColor(GRID_LINE)
    c.setLineWidth(0.5)
    c.line(MARGIN, y0, PAGE_W - MARGIN, y0)
    y = y0

c.setStrokeColor(BORDER)
c.setLineWidth(1)
c.rect(MARGIN, y, FULL_W, fc_grid_top - y, fill=0, stroke=1)
for i in range(1, 5):
    xline = MARGIN + FC_SLOT_W + i * fc_col_w
    c.line(xline, y, xline, fc_grid_top)
c.line(MARGIN + FC_SLOT_W, y, MARGIN + FC_SLOT_W, fc_grid_top)

y -= 6  # gap

# ---------- Section B: labor ----------
hdr_h = 14
y0 = y - hdr_h
banner(MARGIN, y0, FULL_W, hdr_h, "LABOR \u2014 what it costs to actually cook the board",
       color=SECONDARY_ACCENT, sub="labor cost = prep hours \u00d7 wage rate")
y = y0

lab_label_w = 130
lab_col_w = (FULL_W - lab_label_w) / 4.0

col_hdr_h = 13
y0 = y - col_hdr_h
text(MARGIN + 3, y0 + 3, "PER DAY", size=7, font="Helvetica-Bold", color=MUTED)
for i, d in enumerate(DAYS):
    text(MARGIN + lab_label_w + i * lab_col_w + 3, y0 + 3, d, size=7, font="Helvetica-Bold", color=MUTED)
y = y0

row_h = 18
y0 = y - row_h
text(MARGIN, y0 + 4, "Prep hours, all cooks \u2192", size=7.5, font="Helvetica-Bold")
for i in range(4):
    field(f"laborhrs_{DAY_KEYS[i]}", MARGIN + lab_label_w + i * lab_col_w + 3, y0 + 2,
          lab_col_w - 8, 14, size=7.5,
          tooltip=f"Total prep hours ahead of {DAYS[i]}, added up across every cook (3 cooks \u00d7 2 hrs = 6)")
y = y0

row_h = 18
y0 = y - row_h
text(MARGIN, y0 + 4, "Wage rate ($/hr) \u2192", size=7.5, font="Helvetica-Bold")
for i in range(4):
    field(f"wage_{DAY_KEYS[i]}", MARGIN + lab_label_w + i * lab_col_w + 3, y0 + 2,
          lab_col_w - 8, 14, size=7.5, tooltip=f"Hourly wage for prep staff, {DAYS[i]}")
y = y0

row_h = 18
y0 = y - row_h
text(MARGIN, y0 + 4, "Labor cost ($) \u2192", size=7.5, font="Helvetica-Bold")
for i in range(4):
    field(f"laborcost_{DAY_KEYS[i]}", MARGIN + lab_label_w + i * lab_col_w + 3, y0 + 2,
          lab_col_w - 8, 14, size=7.5, tooltip=f"Prep hours \u00d7 wage rate, {DAYS[i]}")
y = y0

y -= 6  # gap

# ---------- Section C: anchor use / waste check ----------
hdr_h = 14
y0 = y - hdr_h
banner(MARGIN, y0, FULL_W, hdr_h, "INGREDIENT USE CHECK \u2014 which anchors does each dish lean on?",
       color=ACCENT, sub="a dish with zero checks is buying something this week's list doesn't need")
y = y0

AN_SLOT_W = 260
an_col_w = (FULL_W - AN_SLOT_W) / 4.0

col_hdr_h = 13
y0 = y - col_hdr_h
c.setFillColor(colors.white)
c.rect(MARGIN, y0, FULL_W, col_hdr_h, fill=1, stroke=0)
text(MARGIN + 3, y0 + 3, "SLOT", size=7, font="Helvetica-Bold", color=MUTED)
for i, (key, label) in enumerate(ANCHORS):
    text(MARGIN + AN_SLOT_W + i * an_col_w + 3, y0 + 3, label, size=7, font="Helvetica-Bold", color=MUTED)
an_grid_top = y0 + col_hdr_h
y = y0

AN_ROW_H = 16
for si, slot in enumerate(SLOTS):
    y0 = y - AN_ROW_H
    if si % 2 == 0:
        c.setFillColor(ROW_STRIPE)
        c.rect(MARGIN, y0, FULL_W, AN_ROW_H, fill=1, stroke=0)
    text(MARGIN + 3, y0 + AN_ROW_H / 2.0 - 3, slot, size=7.5, font="Helvetica-Bold")
    for i, (key, label) in enumerate(ANCHORS):
        cx = MARGIN + AN_SLOT_W + i * an_col_w + (an_col_w - 9) / 2.0
        checkbox(f"uses_{key}_{si}", cx, y0 + (AN_ROW_H - 9) / 2.0, size=9,
                 tooltip=f"{slot} uses this week's anchor {label.lower()}")
    c.setStrokeColor(GRID_LINE)
    c.setLineWidth(0.5)
    c.line(MARGIN, y0, PAGE_W - MARGIN, y0)
    y = y0

c.setStrokeColor(BORDER)
c.setLineWidth(1)
c.rect(MARGIN, y, FULL_W, an_grid_top - y, fill=0, stroke=1)
c.line(MARGIN + AN_SLOT_W, y, MARGIN + AN_SLOT_W, an_grid_top)
for i in range(1, 4):
    xline = MARGIN + AN_SLOT_W + i * an_col_w
    c.line(xline, y, xline, an_grid_top)

y -= 6  # gap

# ---------- Section D: labor ratio + reflection ----------
hdr_h = 14
y0 = y - hdr_h
banner(MARGIN, y0, FULL_W, hdr_h, "WEEK TOTALS \u2014 food + labor together is your prime cost",
       color=SECONDARY_ACCENT, sub="prime cost is commonly kept near 60\u201365% of sales")
y = y0

row_h = 18
y0 = y - row_h
x = MARGIN
x = label_field(x, y0 + 2, "Sales ($, price \u00d7 portions sold):", 150, 70, "week_sales", h=14, fsize=8.5)
x += 16
x = label_field(x, y0 + 2, "Food cost ($):", 70, 70, "week_foodcost", h=14, fsize=8.5)
x += 16
x = label_field(x, y0 + 2, "Labor cost ($):", 72, 70, "week_laborcost", h=14, fsize=8.5)
y = y0

row_h = 18
y0 = y - row_h
x = MARGIN
x = label_field(x, y0 + 2, "Labor % = labor \u00f7 sales \u00d7 100 =", 150, 50, "labor_pct_note", h=14, fsize=8.5)
text(x + 3, y0 + 6, "%", size=8.5, font="Helvetica-Bold")
x += 30
x = label_field(x, y0 + 2, "Prime cost % = (food + labor) \u00f7 sales \u00d7 100 =", 212, 50,
                "prime_cost_pct", h=14, fsize=8.5)
text(x + 3, y0 + 6, "%", size=8.5, font="Helvetica-Bold")
y = y0
y -= 5

hdr_h = 12
y0 = y - hdr_h
text(MARGIN, y0 + 2,
     "If this week's ingredient list had to lose one item, what would you drop \u2014 and what covers for it?",
     size=7.5, font="Helvetica-Bold")
y = y0

reflection_bottom = MARGIN + 18
reflection_h = y - reflection_bottom
rounded_box(MARGIN, reflection_bottom, FULL_W, reflection_h, FILL)
form.textfield(
    name="limited_ingredients_reflection", tooltip="Substitution / waste reduction reflection",
    x=MARGIN + CELL_INSET, y=reflection_bottom + CELL_INSET,
    width=FULL_W - (2 * CELL_INSET), height=reflection_h - (2 * CELL_INSET),
    borderStyle="solid", borderWidth=0, borderColor=BORDER,
    fillColor=FILL, textColor=INK, fontSize=8.5,
    fieldFlags="multiline", forceBorder=True, relative=False,
)

# ---------- Footer ----------
text(MARGIN, MARGIN + 4, "Guthrie Entertainment \u2014 Cameron Kelly \u2014 pg. 2 of 3", size=7,
     font="Helvetica-Oblique", color=MUTED)

c.showPage()

# =====================================================================
# PAGE 3 -- Inventory, Yield & Waste
# =====================================================================
# One row per ingredient on hand. Weight + cost + yield % is what turns a
# purchase price into a real cost per usable pound (the number page 2's
# cost / portion depends on); used vs. tossed at week's end is the waste
# record; the use-by guide keeps "use it up" from becoming unsafe.

INVENTORY_ROWS = 18
INV_COLS = [  # (header, field key, width, tooltip) -- widths are scaled to fill the page
    ("INGREDIENT", "item", 150, "what it is"),
    ("STORAGE", "storage", 58, "walk-in, freezer, dry, line"),
    ("ON HAND", "weight", 50, "weight on hand when counted"),
    ("UNIT", "unit", 34, "lb, oz, kg or g"),
    ("$ / UNIT", "unit_cost", 50, "purchase price per unit of weight"),
    ("YIELD %", "yield_pct", 46, "usable weight \u00f7 purchased weight \u00d7 100, after trim"),
    ("IN / PREP", "in_date", 58, "date received, or date prepped / thawed"),
    ("USE BY", "use_by", 58, "conservative use-by date -- see guide below"),
    ("USED", "used", 46, "weight used by end of week"),
    ("TOSSED", "tossed", 46, "weight thrown out by end of week"),
    ("INIT.", "initials", 36, "who counted it"),
]
# Refrigerated at 41F (5C) or below. Days use the SHORT end of the USDA FSIS
# refrigerator ranges; the local health code wins wherever it is stricter.
USE_BY_GUIDE = [
    ("Raw poultry, ground meat, fresh fish / shellfish", "1 day"),
    ("Raw whole cuts: beef, pork, lamb (steaks, chops, roasts)", "3 days"),
    ("Cooked proteins, grains, soups, leftovers", "3 days"),
    ("Hard ceiling, any ready-to-eat item prepped in-house (FDA Food Code)", "7 days"),
]

y = PAGE_H - MARGIN

# ---------- Header ----------
row_h = 20
y0 = y - row_h
text(MARGIN, y0 + 5, "INVENTORY, YIELD & WASTE", size=14, font="Helvetica-Bold", color=ACCENT)
text(MARGIN + 215, y0 + 6, "weigh it, date it, cost it \u2014 then plan the board around what's here",
     size=8.5, font="Helvetica-Oblique")
label_field(PAGE_W - MARGIN - 200, y0 + 2, "Week of:", 45, 155, "week_of_pg3", h=15)
y = y0 - 4

# ---------- Inventory grid ----------
hdr_h = 14
y0 = y - hdr_h
banner(MARGIN, y0, FULL_W, hdr_h, "ON HAND \u2014 count at the start of the week, finish USED / TOSSED at close",
       color=ACCENT, sub="real cost per usable unit = $ / unit \u00f7 (yield % \u00f7 100)")
y = y0

scale = FULL_W / float(sum(col[2] for col in INV_COLS))
inv_x = [MARGIN]
for col in INV_COLS:
    inv_x.append(inv_x[-1] + col[2] * scale)

col_hdr_h = 13
y0 = y - col_hdr_h
for ci, (label, _, _, _) in enumerate(INV_COLS):
    text(inv_x[ci] + 3, y0 + 3, label, size=6.7, font="Helvetica-Bold", color=MUTED)
inv_grid_top = y0 + col_hdr_h
y = y0

INV_ROW_H = 21
INV_FIELD_H = 15
for ri in range(INVENTORY_ROWS):
    y0 = y - INV_ROW_H
    if ri % 2 == 0:
        c.setFillColor(ROW_STRIPE)
        c.rect(MARGIN, y0, FULL_W, INV_ROW_H, fill=1, stroke=0)
    for ci, (label, key, _, tip) in enumerate(INV_COLS):
        field(f"inv_{ri}_{key}", inv_x[ci] + 3, y0 + (INV_ROW_H - INV_FIELD_H) / 2.0,
              inv_x[ci + 1] - inv_x[ci] - 6, INV_FIELD_H, size=7.5,
              tooltip=f"Row {ri + 1} \u2014 {tip}")
    c.setStrokeColor(GRID_LINE)
    c.setLineWidth(0.5)
    c.line(MARGIN, y0, PAGE_W - MARGIN, y0)
    y = y0

c.setStrokeColor(BORDER)
c.setLineWidth(1)
c.rect(MARGIN, y, FULL_W, inv_grid_top - y, fill=0, stroke=1)
for xline in inv_x[1:-1]:
    c.line(xline, y, xline, inv_grid_top)

y -= 6  # gap

# ---------- Waste total ----------
row_h = 18
y0 = y - row_h
x = MARGIN
x = label_field(x, y0 + 2, "Waste ($) = tossed weight \u00d7 $ / unit, all rows (real cost if already trimmed):",
                375, 60, "waste_dollars", h=14, fsize=8.5)
x += 16
label_field(x, y0 + 2, "Biggest toss & why:", 100, PAGE_W - MARGIN - x - 100, "waste_reason", h=14, fsize=8.5)
y = y0

y -= 6  # gap

# ---------- Conservative use-by guide ----------
hdr_h = 14
y0 = y - hdr_h
banner(MARGIN, y0, FULL_W, hdr_h,
       "CONSERVATIVE USE-BY GUIDE \u2014 refrigerated at 41\u00b0F / 5\u00b0C or below",
       color=SECONDARY_ACCENT, sub="in / prep date counts as day 1")
y = y0

guide_col_w = FULL_W / 2.0
line_h = 13
for gi, (item, days) in enumerate(USE_BY_GUIDE):
    gx = MARGIN + (gi % 2) * guide_col_w
    gy = y - line_h * (gi // 2 + 1)
    text(gx + 3, gy + 2, item, size=7.5)
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(ACCENT)
    c.drawRightString(gx + guide_col_w - 8, gy + 2, days)
y -= line_h * ((len(USE_BY_GUIDE) + 1) // 2)
text(MARGIN + 3, y - 10,
     "Shortest end of USDA FSIS refrigerator ranges. Frozen items: date when thawed and restart the clock. "
     "Local health code overrides this guide. When in doubt, throw it out.",
     size=7, font="Helvetica-Oblique", color=MUTED)

# ---------- Footer ----------
text(MARGIN, MARGIN + 4, "Guthrie Entertainment \u2014 Cameron Kelly \u2014 pg. 3 of 3", size=7,
     font="Helvetica-Oblique", color=MUTED)

c.showPage()
c.save()
print("done")
