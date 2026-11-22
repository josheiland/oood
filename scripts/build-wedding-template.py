#!/usr/bin/env python3
"""Build website/downloads/wedding-planning-tracker.xlsx, the blank starter tracker from E006.

It is a generic version of the Master Checklist Josh and Mary planned their wedding with: the same
tabs and columns, with their names, vendors and places taken out. Re-run after editing TASKS.
"""
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.formatting.rule import FormulaRule
from openpyxl.worksheet.datavalidation import DataValidation

OUT = Path(__file__).resolve().parents[1] / 'website/downloads/wedding-planning-tracker.xlsx'

NAVY, CREAM, FOAM, BLUE, TINT = '0B2A45', 'FBF1E5', 'FDF8F2', '0A6BB8', 'BDE5FF'
HEAD = Font(name='Arial', bold=True, color=CREAM)
HEAD_FILL = PatternFill('solid', fgColor=NAVY)
BODY = Font(name='Arial', color=NAVY)
WRAP = Alignment(wrap_text=True, vertical='top')

WHEN = ['12+ months', '9 to 12 months', '6 to 9 months', '4 to 6 months', '2 to 4 months',
        '1 month', 'Last 2 weeks', 'Day before', 'After']
STATUS = ['Not started', 'In progress', 'Done', 'Skipping']
PRIORITY = ['High', 'Medium', 'Low']

# (when, category, task, priority, notes)
TASKS = [
    ('12+ months', 'Planning', 'Talk through what matters most to each of you, and what you will happily skip', 'High', 'Do this before anything else. It decides the rest of the list'),
    ('12+ months', 'Planning', 'Set a rough guest count', 'High', ''),
    ('12+ months', 'Budget & payments', 'Set a total budget and who is contributing what', 'High', ''),
    ('12+ months', 'Planning', 'Set up a shared AI project with your preferences, venue packages and this tracker', 'Medium', 'Then every chat starts with the full backstory'),
    ('12+ months', 'Venue & logistics', 'Pick a region and a date range', 'High', ''),
    ('12+ months', 'Venue & logistics', 'Shortlist venues and ask each for its full wedding package', 'High', 'Ask for the full package, not the brochure. The fees live in the details'),
    ('12+ months', 'Venue & logistics', 'Compare packages side by side: base rate, minimums, fees and what is not included', 'High', 'Some venues require their own planner or vendor list. Check before you fall in love'),
    ('12+ months', 'Venue & logistics', 'Tour your top venues with a question list', 'High', 'Ask AI for the questions first-timers forget'),
    ('12+ months', 'Venue & logistics', 'Book the venue', 'High', 'A cheaper quote from another venue is fair to mention'),
    ('12+ months', 'Venue & logistics', 'Look up sunset time on your date', 'Low', ''),
    ('12+ months', 'Planning', 'Start a shared moodboard and a rough color palette', 'Medium', ''),
    ('12+ months', 'Photography & video', 'Book a photographer', 'High', ''),
    ('12+ months', 'Photography & video', 'Decide on a videographer and book one if you want it', 'Medium', ''),
    ('12+ months', 'Entertainment & music', 'Decide band or DJ, then book', 'High', ''),
    ('12+ months', 'Wedding party', 'Choose your wedding party and ask them', 'Medium', ''),
    ('12+ months', 'Attire & beauty', 'Start shopping for the dress or suit', 'Medium', ''),
    ('9 to 12 months', 'Invitations & stationery', 'Collect guest addresses', 'Medium', 'Keep them on the Guest list tab'),
    ('9 to 12 months', 'Invitations & stationery', 'Send save the dates', 'Medium', ''),
    ('9 to 12 months', 'Website', 'Make a wedding website with travel, hotel and RSVP info', 'Medium', ''),
    ('9 to 12 months', 'Accommodations', 'Research hotels for out-of-town guests and set up room blocks', 'Medium', ''),
    ('9 to 12 months', 'Catering & bar', 'Choose a catering package', 'High', ''),
    ('9 to 12 months', 'Florals & decor', 'Book a florist', 'Medium', ''),
    ('9 to 12 months', 'Ceremony', 'Choose your officiant', 'High', ''),
    ('9 to 12 months', 'Ceremony', 'Decide on ceremony style and any religious or premarital requirements', 'Medium', ''),
    ('9 to 12 months', 'Rentals', 'Get quotes for anything the venue does not provide', 'Medium', ''),
    ('9 to 12 months', 'Venue & logistics', 'Look into wedding insurance', 'Low', ''),
    ('9 to 12 months', 'Gifts & registry', 'Start a registry', 'Low', ''),
    ('9 to 12 months', 'Welcome party', 'Decide whether to host a welcome party and book the spot', 'Medium', ''),
    ('9 to 12 months', 'Rehearsal dinner', 'Book the rehearsal dinner venue', 'Medium', ''),
    ('9 to 12 months', 'Day-after breakfast', 'Decide whether to host a breakfast the day after and reserve the spot', 'Low', 'Ours was a casual bagel breakfast on a lawn'),
    ('9 to 12 months', 'Honeymoon', 'Pick a honeymoon destination', 'Low', ''),
    ('6 to 9 months', 'Attire & beauty', 'Order the dress, and check how long production takes', 'High', ''),
    ('6 to 9 months', 'Attire & beauty', 'Decide who does hair and makeup, a pro or you', 'Medium', 'AI can show you looks on a photo of you in your dress'),
    ('6 to 9 months', 'Attire & beauty', 'Book hair and makeup, or schedule practice sessions', 'Medium', ''),
    ('6 to 9 months', 'Transportation', 'Book a shuttle or bus for guests', 'Medium', ''),
    ('6 to 9 months', 'Invitations & stationery', 'Finalize invitation wording and order invitations', 'Medium', ''),
    ('6 to 9 months', 'Catering & bar', 'Do the tasting', 'High', 'Write down or record what you picked. Our venue forgot ours'),
    ('6 to 9 months', 'Catering & bar', 'Choose the bar package and signature cocktails', 'Medium', ''),
    ('6 to 9 months', 'Florals & decor', 'Work through floral details and update the proposal', 'Medium', ''),
    ('6 to 9 months', 'Venue & logistics', 'Choose table shapes and a first layout', 'Medium', ''),
    ('6 to 9 months', 'Florals & decor', 'Choose linens, chairs and lighting', 'Medium', 'Have AI mock up your venue with each option before you pick'),
    ('6 to 9 months', 'Entertainment & music', 'Sort out a sound system for the ceremony', 'Medium', ''),
    ('6 to 9 months', 'Wedding party', 'Share attire details with the wedding party', 'Low', ''),
    ('6 to 9 months', 'Legal & admin', 'Look up marriage license rules where you are getting married', 'High', ''),
    ('6 to 9 months', 'Legal & admin', 'Check whether you need an alcohol or event permit', 'Medium', ''),
    ('6 to 9 months', 'Honeymoon', 'Book flights and hotels', 'Medium', ''),
    ('4 to 6 months', 'Invitations & stationery', 'Mail invitations', 'High', ''),
    ('4 to 6 months', 'Attire & beauty', 'Buy wedding bands', 'High', ''),
    ('4 to 6 months', 'Attire & beauty', 'Get shoes and accessories before the final fitting', 'Medium', ''),
    ('4 to 6 months', 'Attire & beauty', 'Book a suit or tux fitting', 'Medium', ''),
    ('4 to 6 months', 'Catering & bar', 'Finalize the menu', 'High', ''),
    ('4 to 6 months', 'Venue & logistics', 'Make a rain plan for anything outdoors', 'Medium', ''),
    ('4 to 6 months', 'Guest experience', 'Pick a guest book idea', 'Low', ''),
    ('4 to 6 months', 'Guest experience', 'List the small touches you care about, and the ones you will skip', 'Low', ''),
    ('4 to 6 months', 'Rehearsal dinner', 'Set the rehearsal dinner guest list', 'Medium', ''),
    ('4 to 6 months', 'Entertainment & music', 'Book dance lessons if you want them', 'Low', ''),
    ('4 to 6 months', 'Website', 'Post transportation info and the dress code', 'Medium', ''),
    ('2 to 4 months', 'Invitations & stationery', 'Track RSVPs and follow up with stragglers', 'High', ''),
    ('2 to 4 months', 'Venue & logistics', 'Draft the wedding day timeline', 'High', ''),
    ('2 to 4 months', 'Entertainment & music', 'Choose ceremony songs and first dance songs', 'Medium', ''),
    ('2 to 4 months', 'Photography & video', 'Write a photo shot list', 'Medium', ''),
    ('2 to 4 months', 'Invitations & stationery', 'Design menus, signs, programs and place cards', 'Medium', ''),
    ('2 to 4 months', 'Florals & decor', 'Design table numbers', 'Low', ''),
    ('2 to 4 months', 'Speeches', 'Decide who gives toasts and in what order', 'Medium', ''),
    ('2 to 4 months', 'Ceremony', 'Write your vows', 'High', 'Start with a voice memo brain dump, then have AI sort it. You do the writing'),
    ('2 to 4 months', 'Ceremony', 'Walk through the ceremony outline with your officiant', 'Medium', ''),
    ('2 to 4 months', 'Rehearsal dinner', 'Collect meal choices', 'Medium', ''),
    ('2 to 4 months', 'Welcome party', 'Confirm the food', 'Medium', ''),
    ('2 to 4 months', 'Attire & beauty', 'Practice hair and makeup', 'Medium', ''),
    ('2 to 4 months', 'Website', 'Build a weekend page for guests: schedule, map links, who is coming, photo upload', 'Low', ''),
    ('2 to 4 months', 'Gifts & registry', 'Get thank-you gifts for parents, the wedding party and your officiant', 'Low', ''),
    ('2 to 4 months', 'Honeymoon', 'Book activities and reservations', 'Low', ''),
    ('1 month', 'Catering & bar', 'Give the venue your final guest and meal count', 'High', ''),
    ('1 month', 'Catering & bar', 'Confirm bar quantities with the final count', 'Medium', ''),
    ('1 month', 'Venue & logistics', 'Finish the seating chart', 'High', ''),
    ('1 month', 'Venue & logistics', 'Send the venue your final timeline, layout, count and vendor list', 'High', ''),
    ('1 month', 'Venue & logistics', 'Send each vendor their part of the timeline', 'High', ''),
    ('1 month', 'Transportation', 'Confirm the final count and pickup times', 'Medium', ''),
    ('1 month', 'Florals & decor', 'Finalize the floral order with the final count', 'Medium', ''),
    ('1 month', 'Invitations & stationery', 'Print or order signs, menus and place cards', 'Medium', ''),
    ('1 month', 'Photography & video', 'Reconfirm with the final timeline and shot list', 'High', ''),
    ('1 month', 'Entertainment & music', 'Reconfirm date, timeline and load-in with the band or DJ', 'High', ''),
    ('1 month', 'Legal & admin', 'Get the marriage license', 'High', ''),
    ('1 month', 'Budget & payments', 'Confirm final payment amounts with every vendor', 'High', ''),
    ('1 month', 'Wedding party', 'Share the timeline and duties with family and the wedding party', 'Medium', ''),
    ('1 month', 'Speeches', 'Remind toast givers of the order and timing', 'Medium', ''),
    ('1 month', 'Entertainment & music', 'Make playlists for the morning of and the rehearsal dinner', 'Low', ''),
    ('1 month', 'Guest experience', 'Pick someone you trust to collect cards and gifts at the end of the night', 'Medium', ''),
    ('Last 2 weeks', 'Attire & beauty', 'Break in your shoes around the house', 'Low', ''),
    ('Last 2 weeks', 'Attire & beauty', 'Get the dress pressed or steamed', 'Medium', ''),
    ('Last 2 weeks', 'Budget & payments', 'Prepare envelopes for final balances and tips', 'High', ''),
    ('Last 2 weeks', 'Venue & logistics', 'Do a final walkthrough at the venue', 'High', ''),
    ('Last 2 weeks', 'Venue & logistics', 'Pack an emergency kit: stain remover, safety pins, pain reliever', 'Medium', ''),
    ('Last 2 weeks', 'Venue & logistics', 'Pack and label everything you are bringing', 'High', 'The To buy or bring tab is your packing list'),
    ('Last 2 weeks', 'Speeches', 'Prep your thank-you speech', 'Medium', ''),
    ('Last 2 weeks', 'Planning', 'Write notes to the wedding party and the people who helped most', 'Medium', ''),
    ('Last 2 weeks', 'Honeymoon', 'Pack for the honeymoon', 'Medium', ''),
    ('Day before', 'Rehearsal dinner', 'Rehearse the ceremony with family and the wedding party', 'High', ''),
    ('Day before', 'Budget & payments', 'Hand the tip envelopes to your coordinator', 'High', ''),
    ('Day before', 'Florals & decor', 'Drop off decor and signs', 'Medium', ''),
    ('Day before', 'Legal & admin', 'Confirm who has the marriage license and who files it', 'High', ''),
    ('After', 'Gifts & registry', 'Send thank-you notes for gifts', 'High', 'Aim for within two or three months'),
    ('After', 'Planning', 'Thank your vendors and leave reviews', 'Low', ''),
    ('After', 'Photography & video', 'Collect everyone\'s photos in one place', 'Low', ''),
    ('After', 'Attire & beauty', 'Clean or preserve the dress', 'Low', ''),
    ('After', 'Legal & admin', 'Do any name change paperwork', 'Medium', ''),
    ('After', 'Budget & payments', 'Close out the budget', 'Low', ''),
]

PROMPT = ("We're planning our wedding and I've attached a starter tracker. Before you change anything, "
          "interview us one question at a time: the date and place, a rough guest count and budget, which "
          "events we're hosting (a welcome party, a rehearsal dinner, a breakfast the day after), and what we "
          "care about and what we'll skip. Ask about anything first-timers usually forget. Then rewrite the "
          "tracker for us: cut what we're not doing, add what's missing, and give every task a category, a "
          "due date, an owner, a status and a priority")


def header(ws, cols, widths):
    ws.append(cols)
    for i, w in enumerate(widths, 1):
        c = ws.cell(row=1, column=i)
        c.font, c.fill, c.alignment = HEAD, HEAD_FILL, Alignment(vertical='center')
        ws.column_dimensions[c.column_letter].width = w
    ws.row_dimensions[1].height = 24
    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = ws.dimensions
    ws.sheet_view.showGridLines = False


def body(ws, first=2):
    for row in ws.iter_rows(min_row=first, max_row=max(ws.max_row, first)):
        for c in row:
            c.font, c.alignment = BODY, WRAP


def pick(ws, col, options, rows=500):
    dv = DataValidation(type='list', formula1='"' + ','.join(options) + '"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f'{col}2:{col}{rows}')


def main():
    wb = Workbook()

    start = wb.active
    start.title = 'Start here'
    start.sheet_view.showGridLines = False
    start.column_dimensions['A'].width = 4
    start.column_dimensions['B'].width = 110
    lines = [
        ('Wedding planning tracker', Font(name='Arial', bold=True, size=20, color=NAVY)),
        ('A blank version of the tracker we planned our wedding with. From Out of Our Depth, episode 006', Font(name='Arial', size=11, color=BLUE)),
        ('', None),
        ('How to use it', Font(name='Arial', bold=True, size=13, color=NAVY)),
        ('1. Google Sheets: File, then Import, then Upload this file. It also opens in Excel and Numbers', BODY),
        ('2. Before you touch a row, have AI interview you. Paste the prompt below into ChatGPT, Claude or Gemini and attach this file', BODY),
        ('3. Let it cut what you are not doing and add what is missing. Ours grew to a few hundred rows', BODY),
        ('4. Filter Owner to see your own list. Filter When to see what is coming up', BODY),
        ('5. After any vendor call, paste your notes into AI and ask which rows to add, change or mark done', BODY),
        ('', None),
        ('The prompt', Font(name='Arial', bold=True, size=13, color=NAVY)),
        (PROMPT, BODY),
        ('', None),
        ('The tabs', Font(name='Arial', bold=True, size=13, color=NAVY)),
        ('All tasks: every to-do, with when, owner, status and priority', BODY),
        ('Vendors: who you booked, what they cost and what you still owe', BODY),
        ('To buy or bring: everything you need to buy, borrow or pack', BODY),
        ('Guest list: who is invited to what, how likely they are to come, RSVPs and tables', BODY),
        ('Contacts: every name and number you will need that weekend', BODY),
        ('', None),
        ('More prompts and the episode: outofourdepth.com/builds', Font(name='Arial', size=11, color=BLUE)),
    ]
    for i, (text, font) in enumerate(lines, 2):
        c = start.cell(row=i, column=2, value=text)
        if font:
            c.font = font
        c.alignment = Alignment(wrap_text=True, vertical='top')
    start.row_dimensions[13].height = 75

    tasks = wb.create_sheet('All tasks')
    header(tasks, ['When', 'Category', 'Task', 'Due date', 'Owner', 'Status', 'Priority', 'Notes'],
           [16, 22, 62, 12, 14, 13, 10, 52])
    order = {w: i for i, w in enumerate(WHEN)}
    for when, cat, task, pri, note in sorted(TASKS, key=lambda t: order[t[0]]):
        tasks.append([when, cat, task, None, None, 'Not started', pri, note or None])
    body(tasks)
    for r in range(2, tasks.max_row + 1):
        tasks.cell(row=r, column=4).number_format = 'm/d/yyyy'
    pick(tasks, 'A', WHEN)
    pick(tasks, 'F', STATUS)
    pick(tasks, 'G', PRIORITY)
    last = tasks.max_row + 200
    tasks.conditional_formatting.add(f'A2:H{last}', FormulaRule(formula=['$F2="Done"'], font=Font(color='8A97A5', strike=True)))
    tasks.conditional_formatting.add(f'A2:H{last}', FormulaRule(formula=['$F2="Skipping"'], font=Font(color='8A97A5')))
    tasks.conditional_formatting.add(f'G2:G{last}', FormulaRule(formula=['$G2="High"'], fill=PatternFill('solid', fgColor=TINT)))

    vendors = wb.create_sheet('Vendors')
    header(vendors, ['Vendor', 'Category', 'Contact', 'Total', 'Paid so far', 'Still owed', 'Next payment due', 'Who pays', 'What is included', 'Notes'],
           [24, 20, 26, 12, 12, 12, 16, 12, 40, 40])
    for r in range(2, 32):
        vendors.cell(row=r, column=6, value=f'=IF(D{r}="","",D{r}-E{r})')
        for col in (4, 5, 6):
            vendors.cell(row=r, column=col).number_format = '$#,##0'
        vendors.cell(row=r, column=7).number_format = 'm/d/yyyy'
    vendors.cell(row=33, column=3, value='Total').font = Font(name='Arial', bold=True, color=NAVY)
    for col, letter in ((4, 'D'), (5, 'E'), (6, 'F')):
        c = vendors.cell(row=33, column=col, value=f'=SUM({letter}2:{letter}32)')
        c.font, c.number_format = Font(name='Arial', bold=True, color=NAVY), '$#,##0'
    body(vendors)

    items = wb.create_sheet('To buy or bring')
    header(items, ['Item', 'For', 'Where from', 'Cost', 'Buy by', 'Who pays', 'Status'], [30, 30, 20, 10, 12, 14, 16])
    for r in range(2, 200):
        items.cell(row=r, column=4).number_format = '$#,##0'
        items.cell(row=r, column=5).number_format = 'm/d/yyyy'
    pick(items, 'G', ['To buy', 'Bought', 'Packed'])
    body(items)

    guests = wb.create_sheet('Guest list')
    header(guests, ['Name', 'Household', 'Email', 'Address', 'Likely to come', 'Welcome party', 'Rehearsal dinner',
                    'Wedding', 'Breakfast after', 'RSVP', 'Meal', 'Dietary needs', 'Table', 'Gift', 'Thank-you sent'],
           [24, 18, 26, 34, 14, 14, 15, 10, 15, 10, 12, 16, 8, 20, 14])
    pick(guests, 'E', ['High', 'Medium', 'Low'], 1000)
    for col in 'FGHI':
        pick(guests, col, ['Invited'], 1000)
    pick(guests, 'J', ['Yes', 'No', 'Waiting'], 1000)
    pick(guests, 'O', ['Yes'], 1000)
    guests.cell(row=2, column=17, value='Expected guests').font = Font(name='Arial', bold=True, color=NAVY)
    guests.cell(row=3, column=17, value='High counts 1, medium 0.5, low 0.1. A rough guess until RSVPs arrive').font = Font(name='Arial', size=9, color=BLUE)
    guests.cell(row=2, column=18, value='=COUNTIF(E2:E1000,"High")+0.5*COUNTIF(E2:E1000,"Medium")+0.1*COUNTIF(E2:E1000,"Low")').font = Font(name='Arial', bold=True, color=NAVY)
    guests.column_dimensions['Q'].width = 18
    body(guests)

    contacts = wb.create_sheet('Contacts')
    header(contacts, ['Name', 'Role', 'Phone', 'Email', 'Notes'], [24, 22, 16, 28, 44])
    for role in ['Partner 1', 'Partner 2', 'Venue coordinator', 'Officiant', 'Photographer', 'Videographer',
                 'Band or DJ', 'Florist', 'Caterer', 'Transportation', 'Hair and makeup', 'Day-of point person']:
        contacts.append([None, role, None, None, None])
    body(contacts)

    wb.active = 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    print(OUT, len(TASKS), 'tasks')


if __name__ == '__main__':
    main()
