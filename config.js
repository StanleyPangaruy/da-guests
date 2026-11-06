// ─────────────────────────────────────────────────────────────
//  Board settings — edit freely, then refresh the browser source.
//  Per-guest details (name, district, date, venue, photo) live in guests.csv.
// ─────────────────────────────────────────────────────────────
window.BOARD_CONFIG = {
  province: "PROVINCE OF QUEZON",
  municipality: "MUNICIPALITY OF LOPEZ",
  eventTitle: "District Assembly",        // can be overridden per row (event_title column)

  sealLeft:  "logo/quezon.webp",           // hi-res seals with transparent background
  sealRight: "logo/lopez.png",
  backdrop: "background/backdrop.jpg",   // background photo behind everything ("" = dotted background)

  footer: [
    { img: "assets/icon-web.png",      text: "livelopez.gov.ph" },
    { icon: "video",                   text: "Municipality of Lopez, Quezon" },
    { img: "assets/icon-facebook.png", text: "municipalityoflopez,quezon" },
    { icon: "camera",    text: "municipalityoflopezquezon" }
  ],

  csv: "guests.csv",
  csvRefreshSeconds: 10,  // re-read guests.csv so edits show up live
  halfBody: 1.15,         // guest photos are cut at about the waist; lower = cut higher, higher = show more
  fit: "contain",         // contain = stretch the layout to the screen shape (no bars) | cover | stretch
  background: "#ffffff"   // colour around the design when fit = contain
};
