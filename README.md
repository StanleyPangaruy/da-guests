# District Assembly – LED wall browser source

## Run it
1. Install Python 3 (nothing else needed).
2. In this folder: `python serve.py`
3. Browser source URL: `http://localhost:8080/`
   - **OBS / Streamlabs:** Add → Browser → URL above, width **1920**, height **972** (or your LED canvas size – the design scales to fit).
   - **vMix:** Add Input → Web Browser → same URL.
   - **Plain Chrome on the LED PC:** open the URL, press **F** for fullscreen.
4. Operator control page (any phone/laptop on the same network): `http://<PC-IP>:8080/control.html`
   (serve.py prints the exact LAN address when it starts.)

> Opening `index.html` by double-click won't work – browsers block reading the CSV from a file path. Always use serve.py.

## guests.csv
| column | example | notes |
|---|---|---|
| active | yes | `no` hides the row without deleting it |
| honorific | KGG. ATTY. | shown before the name |
| name | ADRIAN DONALD SEGUI | auto-shrinks to fit two lines |
| position | Municipal Councilor | |
| district | DISTRICT CHAMPACA | text on the red/blue band |
| date | 2026-05-08 | `YYYY-MM-DD` → weekday is computed automatically. Any other text is shown as typed (use `\|` for the divider). |
| time | 8 AM | |
| venue | CENTER FOR EXCELLENCE COVERED COURT | |
| address | Brgy. Talolong, Lopez, Quezon | wrap in quotes if it has commas (Excel does this for you) |
| photo | photos/segui.png | transparent PNG, waist-up. Leave blank for none. |
| event_title | *(optional)* | overrides "District Assembly" for that row |

Edit in Excel/Google Sheets → save as CSV. The board picks up changes within ~10 s, no refresh needed.

## Controls
- **Control page:** click a guest to put it on air, Prev/Next, Auto-rotate on/off, seconds per guest, Blackout.
- **Keyboard (on the board itself):** ← → change guest, 1–9 jump, Space pause, B blackout, F fullscreen.
- **URL options:** `?guest=2` lock to one guest · `?interval=8` rotate speed · `?fit=cover|contain|stretch` · `?bg=transparent` for keying.

## Other files
- `config.js` – header text, seals, footer links, rotate speed, fit mode.
- `assets/seal-left.png`, `assets/seal-right.png` – cropped from the poster; replace with the original hi-res seals for a sharper LED image.
- `cutout.py` – removes photo backgrounds: `pip install "rembg[cpu]"` then `python cutout.py raw/*.jpg`.
