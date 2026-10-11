# Open questions — rev 0.3

Decided: 56×100, two Ø4 lanyard holes, INTENT logo white centred + summit tagline, power switch on the battery box (SW5 pads DNP), team names on the back, 14×14 mm QR reserve on the back, add-ons: audio jack + IR + 3×AAA power path. BOM deltas explained in `00-bom/bom-deltas-he.md`.

Still open (none blocks the KiCad stage — I'll use the defaults):
1. Logo rendering on silkscreen: JLC rasterises fine lines ≥ 0.15 mm; the small "BY PALO ALTO NETWORKS" at 40 mm logo width is ≈ 1.1 mm tall — readable, borderline. Default: keep it, or drop it and keep only the big INTENT wordmark if the fab preview looks muddy.
2. Battery box: wired 3×AAA box **with** switch and JST-PH 2.0 lead — I'll put a reference part in `04-fab/order-spec.md`; you confirm the supplier.
3. QR: send the repo URL when ready; it goes on the silkscreen as vector art, no layout change.
4. Logo usage: the Palo Alto Networks wordmark is a trademark — confirm you have permission to print it on the badge (you supplied the brand file, so presumably yes).
