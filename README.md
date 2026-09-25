# chef-cam-culinary-labs

A weekly kitchen board for culinary students: plan a menu around a short
ingredient list, cost it, cost the labor to prep it, and track inventory,
yield and waste. It comes in two forms that share the same three pages.

## Web form (phones and laptops)

`web/index.html` is a self-contained page with no build step. It:

- does the math as students type: food cost %, labor cost, prime cost,
  real cost per usable unit after trim, waste dollars and use-by dates
- saves each week in the browser, keeps a list of past weeks, and can
  start a new week that carries over whatever inventory is left
- exports and imports a backup file, and prints or saves as a PDF

Open the file directly in a browser to try it. It is published to GitHub
Pages by `.github/workflows/pages.yml` on every push to `main`. One-time
setup: in the repo's Settings -> Pages, set Source to "GitHub Actions".

The QR code at `web/qr.png` opens the published form. To regenerate it,
for example if the address changes:

```bash
python3 make_qr.py [url]
```

## Printable PDF

A fillable three-page PDF of the same board:

```bash
pip install -r requirements.txt
python3 build_form.py
```
