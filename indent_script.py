with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

tab_start_idx = 0
for i, line in enumerate(lines):
    if line.startswith('# ---------------------------------------------------------') and lines[i+1].startswith('# BIAS AUDIT ENGINE'):
        tab_start_idx = i
        break

footer_idx = 0
for i, line in enumerate(lines):
    if line.startswith('# ---------------------------------------------------------') and lines[i+1].startswith('# FOOTER'):
        footer_idx = i
        break

new_lines = lines[:tab_start_idx]

new_lines.append('tab_dashboard, tab_shap, tab_mitigation, tab_chat = st.tabs([\n')
new_lines.append('    "Dashboard", \n')
new_lines.append('    "Deep Explainability (SHAP)", \n')
new_lines.append('    "Bias Mitigation Lab", \n')
new_lines.append('    "Aura Chat Agent"\n')
new_lines.append('])\n\n')

new_lines.append('with tab_dashboard:\n')
for i in range(tab_start_idx, footer_idx):
    if lines[i].strip() == '':
        new_lines.append('\n')
    else:
        new_lines.append('    ' + lines[i])

new_lines.extend(lines[footer_idx:])

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Done!')
