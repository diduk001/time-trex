function readJson(id) {
  const el = document.getElementById(id);
  return el ? JSON.parse(el.textContent) : null;
}

document.addEventListener("DOMContentLoaded", function () {
  const summary = readJson("summary-data");
  const timeline = readJson("timeline-data");

  if (summary && summary.by_activity && summary.by_activity.length) {
    new Chart(document.getElementById("summary-chart"), {
      type: "doughnut",
      data: {
        labels: summary.by_activity.map((a) => a.name),
        datasets: [{
          data: summary.by_activity.map((a) => a.total_seconds / 3600),
          backgroundColor: summary.by_activity.map((a) => a.color || "#6c757d"),
        }],
      },
    });
  }

  if (timeline && timeline.buckets && timeline.buckets.length) {
    new Chart(document.getElementById("timeline-chart"), {
      type: "bar",
      data: {
        labels: timeline.buckets.map((b) => b.period),
        datasets: [{
          label: "Hours",
          data: timeline.buckets.map((b) => b.total_seconds / 3600),
          backgroundColor: "#0d6efd",
        }],
      },
      options: { scales: { y: { beginAtZero: true } } },
    });
  }
});
