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

## Event details
District, date, time, venue and address are edited on the control page under **Event details**, then **Update wall**. They are saved in `event.json`.

## Guests
Edit guests on the control page: **Edit** on a guest to change it or delete it, **+ Add guest** for a new one. Changes are saved to `guests.csv` and show on the wall right away.
Photos: put transparent PNGs in the `photos` folder and pick them in the guest's Photo dropdown.

You can still edit `guests.csv` in Excel (columns `active, honorific, name, position, photo`), but close Excel before saving from the control page.

## Controls
- **Control page:** click a guest to put it on air, Prev/Next, Blackout.
- **Keyboard (on the board itself):** ← → change guest, 1–9 jump, B blackout, F fullscreen.
- **URL options:** `?guest=2` lock to one guest · `?fit=cover|contain|stretch` · `?bg=transparent` for keying.

## Other files
- `config.js` – header text, seals, footer links, fit mode.
- `assets/seal-left.png`, `assets/seal-right.png` – cropped from the poster; replace with the original hi-res seals for a sharper LED image.
- `cutout.py` – removes photo backgrounds: `pip install "rembg[cpu]"` then `python cutout.py raw/*.jpg`.
