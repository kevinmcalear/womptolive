const form = document.getElementById("signup");
const thanks = document.getElementById("thanks");
const seats = document.getElementById("seats");

const KEY = "womp-institute-signups";

function encode(data) {
  return Object.keys(data)
    .map((k) => encodeURIComponent(k) + "=" + encodeURIComponent(data[k]))
    .join("&");
}

function remaining() {
  const n = JSON.parse(localStorage.getItem(KEY) || "[]").length;
  return Math.max(7, 18 - n);
}

if (seats) seats.textContent = String(remaining());

if (form) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = Object.fromEntries(new FormData(form).entries());
    if (payload.company) return;

    const list = JSON.parse(localStorage.getItem(KEY) || "[]");
    list.push({ ...payload, at: new Date().toISOString() });
    localStorage.setItem(KEY, JSON.stringify(list));

    try {
      await fetch("/", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: encode({ "form-name": "seminar", ...payload }),
      });
    } catch (err) {
      // Local preview still confirms; Netlify collects when deployed.
    }

    form.hidden = true;
    thanks.hidden = false;
    if (seats) seats.textContent = String(remaining());
    thanks.scrollIntoView({ behavior: "smooth", block: "center" });
  });
}
