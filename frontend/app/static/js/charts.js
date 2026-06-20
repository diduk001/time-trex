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
    // Collect all unique activity names across all buckets
    const activitySet = new Set();
    timeline.buckets.forEach((b) => {
      if (b.by_activity) {
        b.by_activity.forEach((activity) => {
          activitySet.add(activity.name);
        });
      }
    });
    const activityNames = Array.from(activitySet);

    // Build a color map from summary data
    const colorMap = {};
    const defaultColors = ["#0d6efd", "#6f42c1", "#20c997", "#fd7e14", "#dc3545"];
    if (summary && summary.by_activity) {
      summary.by_activity.forEach((a) => {
        colorMap[a.name] = a.color || null;
      });
    }

    // Create one dataset per activity
    const datasets = activityNames.map((activityName, index) => {
      const data = timeline.buckets.map((b) => {
        const activity = b.by_activity.find((a) => a.name === activityName);
        return activity ? activity.total_seconds / 3600 : 0;
      });

      const color = colorMap[activityName] || defaultColors[index % defaultColors.length];

      return {
        label: activityName,
        data: data,
        backgroundColor: color,
      };
    });

    new Chart(document.getElementById("timeline-chart"), {
      type: "bar",
      data: {
        labels: timeline.buckets.map((b) => b.period),
        datasets: datasets,
      },
      options: {
        scales: {
          x: { stacked: true },
          y: {
            stacked: true,
            beginAtZero: true,
            title: { display: true, text: "Hours" },
          },
        },
      },
    });
  }
});
