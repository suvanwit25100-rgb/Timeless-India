# Ethics note and consent form

## Why this is in the project

The Digital Humanities syllabus (M2 and M5) asks for an explicit ethics position. This project works with:

- **Colonial directories** that recorded European firms in detail and left most Indian residents and shops out. Taking them as the whole truth would reproduce that gap.
- **Oral history** from present-day shopkeepers in Chowringhee, Bowbazar, Kumartuli and Chitpur. Their memories are personal, often political, and sometimes commercial-sensitive.
- **Photos and 3D scans** of shop-fronts and signboards that belong to real, named businesses still in operation.

## Rules the project follows

1. **No uncertain data stated as fact.** Rows marked `fuzzy` or `unmatched` in the parser output stay marked all the way through the map UI; the viewer sees the confidence pill.
2. **Named the archive's limits in the UI.** The sidebar says in plain words that Indian Black Town streets are under-recorded. The viewer does not have to dig to find that out.
3. **CARE-style consent for oral history.** Collective interest of the trade community matters as much as individual consent. A translator who speaks Bengali is present for every interview.
4. **Right to withdraw.** A speaker may ask for their clip to be removed from the map at any time. The audio file is then deleted from `data/audio/` and the GeoJSON pin updated.
5. **No commercial-sensitive detail.** Prices, supplier names, debts, family disputes are left out, even when spoken on tape.
6. **Public-domain images only** for pre-1947 photos (Bourne & Shepherd, Johnston & Hoffmann, out of copyright). Modern photos are the student's own or used with signed consent.

## Consent form (print and sign two copies)

---

**Kolkata Palimpsest - oral history consent**

Project: Kolkata Palimpsest - Colonial Calcutta, street by street.
Student: Suvanwit Mandal, Digital Humanities minor, IIIT Naya Raipur.

I, _________________________ (name), of _________________________ (shop / address), agree that:

- the student may record my spoken answers about this shop and this street;
- parts of the recording, with my words translated into English where needed, may be placed as an audio pin on a public web map, with my name shown as I give it below;
- my name on the map will appear as: __________________________________;
- I may, at any later date, ask for my clip to be removed; the student will then delete the file within seven days;
- I understand that no price, supplier, debt, family or legal detail I say will appear on the map, even if the recording keeps it.

Signed: _________________________    Date: _____________

Student signature: _________________________    Date: _____________

Translator (if used): _________________________    Date: _____________

---

## Data handling

- Raw recordings live in `data/audio/raw/<YYYY-MM-DD>-<slug>/`. Nothing from `raw/` is published.
- Trimmed clips meant for the map live in `data/audio/pub/`. Only files with a signed, scanned consent form (filed in `data/audio/consent/`) land there.
- Transcripts, with the consent-form scan name, live beside the clip as `<slug>.md`.
