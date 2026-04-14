with open('dashboard.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacements = [
    ('.stApp { background: linear-gradient(135deg, #0D0D1A 0%, #111827 50%, #0D0D1A 100%); }', '.stApp { background: #FFFFFF; color: #111827; }'),
    ('background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);', 'background: #FFFFFF;'),
    ('background: linear-gradient(135deg, #1F2937 0%, #111827 100%);', 'background: #F9FAFB;'),
    ('background: linear-gradient(180deg, #0D0D1A 0%, #111827 100%) !important;', 'background: #F3F4F6 !important;'),
    ('color: #F9FAFB;', 'color: #111827;'),
    ('color:#F9FAFB;', 'color:#111827;'),
    ('color: #9CA3AF;', 'color: #4B5563;'),
    ('color:#9CA3AF;', 'color:#4B5563;'),
    ('color: #D1D5DB;', 'color: #374151;'),
    ('template="plotly_dark"', 'template="plotly_white"'),
    ('paper_bgcolor="#0F0F23"', 'paper_bgcolor="#FFFFFF"'),
    ('plot_bgcolor="#0F0F23"', 'plot_bgcolor="#FFFFFF"'),
    ('color="white"', 'color="#111827"'),
    ('rgba(255,255,255,0.1)', 'rgba(0,0,0,0.1)'),
    ('font=dict(color="white")', 'font=dict(color="#111827")')
]

for old, new in replacements:
    content = content.replace(old, new)

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Theme successfully updated.")
