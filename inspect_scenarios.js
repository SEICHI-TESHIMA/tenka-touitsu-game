import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Extract SCENARIOS_DATA
# Find SCENARIOS_DATA = [...]
m = re.search(r'window\.SCENARIOS_DATA\s*=\s*(\[.*?\]);\s*(?:window\.|$)', text, re.DOTALL)
if not m:
    # try without window or until next var
    m = re.search(r'window\.SCENARIOS_DATA\s*=\s*(\[.*?)(?=window\.[A-Z0-9_]+\s*=)', text, re.DOTALL)

# Let's inspect scenarios by year or id
import js2py # or let's use node or python regex
# Since it's JS, let's run node to inspect SCENARIOS_DATA cleanly!
