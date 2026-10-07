(function () {
  var SLOT_LABEL = { morning: "아침", lunch: "점심", evening: "저녁" };
  var TOPIC_ORDER = ["love", "money", "work", "health", "people"];
  var app = document.getElementById("app");

  function el(tag, props, children) {
    var n = document.createElement(tag);
    Object.keys(props || {}).forEach(function (k) {
      if (k === "text") n.textContent = props[k];
      else if (k === "class") n.className = props[k];
      else n.setAttribute(k, props[k]);
    });
    (children || []).forEach(function (c) { n.appendChild(c); });
    return n;
  }

  // KST 기준 오늘 날짜(YYYY-MM-DD)
  function todayKst() {
    var parts = new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Seoul" }).format(new Date());
    return parts;
  }

  // 배경색 위에서 글자색(검정/흰색) 고르기
  function inkOn(hex) {
    var n = parseInt(hex.slice(1), 16);
    var lum = (0.299 * (n >> 16) + 0.587 * ((n >> 8) & 255) + 0.114 * (n & 255)) / 255;
    return lum > 0.6 ? "#231f2e" : "#ffffff";
  }

  function renderTopic(box, doc, key) {
    var t = doc.topics[key];
    box.textContent = "";
    var body = t.text ? t.text : t.facts[0];
    var ring = el("div", { class: "ring", role: "img", "aria-label": t.label + " " + t.score + "점" },
      [el("span", { text: String(t.score) })]);
    ring.style.setProperty("--p", t.score);
    box.appendChild(el("div", { class: "topic" }, [ring, el("p", { text: body })]));
    var ul = el("ul", { class: "facts" });
    t.facts.forEach(function (f) { ul.appendChild(el("li", { text: f })); });
    box.appendChild(ul);
  }

  function render(doc) {
    app.textContent = "";
    var stale = doc.date !== todayKst();
    var head = el("header", {}, [
      el("h1", { text: "내 사주 운세" }),
      el("div", { class: "date" }, [
        el("span", { text: doc.date }),
        el("span", { class: "pillar", text: doc.ilgin + " 일" })
      ])
    ]);
    if (stale) head.querySelector(".date").appendChild(el("span", { class: "badge", text: "갱신 전" }));
    app.appendChild(head);

    var chips = el("div", { class: "chips" });
    ["morning", "lunch", "evening"].forEach(function (s) {
      var c = doc.slots[s].color;
      var chip = el("div", { class: "chip", text: SLOT_LABEL[s] + " · " + c.name });
      chip.style.background = c.hex;
      chip.style.color = inkOn(c.hex);
      chips.appendChild(chip);
    });
    app.appendChild(el("section", { class: "card" }, [
      el("h2", { text: "오늘의 운세" }),
      el("p", { class: "overall", text: doc.overall }),
      chips
    ]));

    if (doc.topics) {
      var panel = el("section", { class: "card", id: "panel", role: "tabpanel" });
      var tabs = el("div", { class: "tabs", role: "tablist" });
      TOPIC_ORDER.forEach(function (key, i) {
        var b = el("button", { class: "tab", role: "tab", "aria-selected": i === 0 ? "true" : "false",
          text: doc.topics[key].label });
        b.addEventListener("click", function () {
          Array.prototype.forEach.call(tabs.children, function (x) { x.setAttribute("aria-selected", "false"); });
          b.setAttribute("aria-selected", "true");
          renderTopic(panel, doc, key);
        });
        tabs.appendChild(b);
      });
      app.appendChild(tabs);
      renderTopic(panel, doc, TOPIC_ORDER[0]);
      app.appendChild(panel);
    }

    var slots = el("section", { class: "card" }, [el("h2", { text: "시간대별 흐름" })]);
    ["morning", "lunch", "evening"].forEach(function (s) {
      var d = doc.slots[s];
      var sw = el("div", { class: "swatch" });
      sw.style.background = d.color.hex;
      slots.appendChild(el("div", { class: "slot" }, [
        sw,
        el("div", {}, [
          el("b", { text: SLOT_LABEL[s] }),
          el("p", { text: d.text }),
          el("p", { class: "why", text: d.color.reason })
        ])
      ]));
    });
    app.appendChild(slots);

    var when = new Date(doc.updated_at);
    app.appendChild(el("footer", { text: "마지막 갱신 " + (isNaN(when) ? doc.updated_at : when.toLocaleString("ko-KR", { timeZone: "Asia/Seoul" })) +
      " · 재미로 보는 참고용이에요" }));
  }

  fetch("fortune.json", { cache: "no-cache" })
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(render)
    .catch(function () {
      app.textContent = "";
      app.appendChild(el("p", { class: "state", text: "운세를 불러오지 못했어요. 잠시 후 다시 열어 주세요." }));
    });
})();
