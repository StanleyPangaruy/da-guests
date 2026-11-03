// ─────────────────────────────────────────────────────────────
//  Board settings — edit freely, then refresh the browser source.
//  Per-guest details (name, district, date, venue, photo) live in guests.csv.
// ─────────────────────────────────────────────────────────────
window.BOARD_CONFIG = {
  province: "PROVINCE OF QUEZON",
  municipality: "MUNICIPALITY OF LOPEZ",
  eventTitle: "District Assembly",        // can be overridden per row (event_title column)

  sealLeft:  "assets/seal-left.png",       // swap in hi-res PNGs with transparent background
  sealRight: "assets/seal-right.png",

  footer: [
    { img: "assets/icon-web.png",      text: "livelopez.gov.ph" },
    { icon: "video",                   text: "Municipality of Lopez, Quezon" },
    { img: "assets/icon-facebook.png", text: "municipalityoflopez,quezon" },
    { icon: "camera",    text: "municipalityoflopezquezon" }
  ],

  csv: "guests.csv",
  csvRefreshSeconds: 10,  // re-read guests.csv so edits show up live
  fit: "contain",         // contain | cover | stretch  (how the 1920×972 design fills the LED canvas)
  background: "#ffffff"   // colour around the design when fit = contain
};
