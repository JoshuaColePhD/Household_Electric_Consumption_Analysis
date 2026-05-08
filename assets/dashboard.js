const metrics = [
  { horizon: 1, model: "random_forest", label: "Random Forest", mae: 0.08085515320764022, rmse: 0.2093840697776981, r2: 0.9453929468673391 },
  { horizon: 1, model: "linear_regression_scaled", label: "Linear Regression", mae: 0.08902328204312136, rmse: 0.22077912628199878, r2: 0.9392875879504414 },
  { horizon: 1, model: "baseline_persistence", label: "Persistence", mae: 0.0719155385951728, rmse: 0.2215135779429908, r2: 0.9388829799558955 },
  { horizon: 1, model: "baseline_mean", label: "Mean Baseline", mae: 0.7263420337757702, rmse: 0.9009362113036126, r2: -0.010996267951310701 },
  { horizon: 15, model: "random_forest", label: "Random Forest", mae: 0.3365586524455166, rmse: 0.5624738588240282, r2: 0.6059382230852819 },
  { horizon: 15, model: "linear_regression_scaled", label: "Linear Regression", mae: 0.35584606961007886, rmse: 0.6041426312068705, r2: 0.5453904128062321 },
  { horizon: 15, model: "baseline_persistence", label: "Persistence", mae: 0.38070203810746117, rmse: 0.6990698446786281, r2: 0.39130355947851225 },
  { horizon: 15, model: "baseline_mean", label: "Mean Baseline", mae: 0.7263376868682708, rmse: 0.9009351252759109, r2: -0.010989542854073608 },
  { horizon: 60, model: "random_forest", label: "Random Forest", mae: 0.502209073814607, rmse: 0.7326503927251177, r2: 0.33142691210788966 },
  { horizon: 60, model: "linear_regression_scaled", label: "Linear Regression", mae: 0.5573471374972353, rmse: 0.778654366241589, r2: 0.2448299389861225 },
  { horizon: 60, model: "baseline_mean", label: "Mean Baseline", mae: 0.7263243846078832, rmse: 0.9009312565805235, r2: -0.010970833350488318 },
  { horizon: 60, model: "baseline_persistence", label: "Persistence", mae: 0.5902272443342638, rmse: 0.9515875367358767, r2: -0.12785380240365263 },
];

const modelOrder = ["random_forest", "linear_regression_scaled", "baseline_persistence", "baseline_mean"];
const modelNames = Object.fromEntries(metrics.map((metric) => [metric.model, metric.label]));
const accent = {
  random_forest: "#07946e",
  linear_regression_scaled: "#175cd3",
  baseline_persistence: "#d97706",
  baseline_mean: "#697586",
};

const state = {
  horizon: 15,
  model: "random_forest",
  scenario: "normal",
};

const selectedTitle = document.querySelector("#selectedTitle");
const selectedNarrative = document.querySelector("#selectedNarrative");
const maeValue = document.querySelector("#maeValue");
const rmseValue = document.querySelector("#rmseValue");
const r2Value = document.querySelector("#r2Value");
const chartHorizonLabel = document.querySelector("#chartHorizonLabel");
const barChart = document.querySelector("#barChart");
const lineChart = document.querySelector("#lineChart");

function formatMetric(value) {
  return Number(value).toFixed(3);
}

function getMetric(horizon, model) {
  return metrics.find((metric) => metric.horizon === Number(horizon) && metric.model === model);
}

function setActiveButtons() {
  document.querySelectorAll("[data-horizon]").forEach((button) => {
    button.classList.toggle("active", Number(button.dataset.horizon) === state.horizon);
  });
  document.querySelectorAll("[data-model]").forEach((button) => {
    button.classList.toggle("active", button.dataset.model === state.model);
  });
  document.querySelectorAll("[data-scenario]").forEach((button) => {
    button.classList.toggle("active", button.dataset.scenario === state.scenario);
  });
}

function scenarioText(metric) {
  const horizonCopy = {
    1: "At a 1-minute horizon, the signal is so autocorrelated that persistence remains a serious benchmark.",
    15: "At a 15-minute horizon, recent usage still matters, but feature-based modeling starts to separate itself from simple persistence.",
    60: "At a 60-minute horizon, the forecasting task is meaningfully harder, and the nonlinear model retains the strongest RMSE profile.",
  };

  const scenarioCopy = {
    normal: "Typical household rhythm keeps the interpretation centered on recurring daily load patterns.",
    spike: "Evening spikes widen the practical uncertainty because high-demand events are real behavior, not cleanup errors.",
    overnight: "Overnight load tends to be calmer, which is why short-horizon baselines can look deceptively strong.",
  };

  const modelCopy =
    metric.model === "random_forest"
      ? "Random Forest is the strongest overall choice by RMSE across the evaluated horizons."
      : metric.model === "baseline_persistence"
        ? "Persistence is included as a demanding baseline, especially for very short forecasts."
        : metric.model === "linear_regression_scaled"
          ? "Linear Regression gives a transparent middle ground between simple baselines and nonlinear modeling."
          : "The mean baseline anchors the comparison and shows why temporal information matters.";

  return `${horizonCopy[metric.horizon]} ${scenarioCopy[state.scenario]} ${modelCopy}`;
}

function renderSummary() {
  const metric = getMetric(state.horizon, state.model);

  selectedTitle.textContent = `${state.horizon}-minute ${metric.label} forecast`;
  selectedNarrative.textContent = scenarioText(metric);
  maeValue.textContent = formatMetric(metric.mae);
  rmseValue.textContent = formatMetric(metric.rmse);
  r2Value.textContent = formatMetric(metric.r2);
  chartHorizonLabel.textContent = `${state.horizon} min`;
}

function renderBarChart() {
  const horizonMetrics = modelOrder.map((model) => getMetric(state.horizon, model));
  const maxRmse = Math.max(...horizonMetrics.map((metric) => metric.rmse));

  barChart.innerHTML = horizonMetrics
    .map((metric) => {
      const width = Math.max(5, (metric.rmse / maxRmse) * 100);
      const isSelected = metric.model === state.model;
      return `
        <button type="button" class="bar-row ${isSelected ? "selected" : ""}" data-bar-model="${metric.model}" aria-label="Select ${metric.label}">
          <span class="bar-label">${metric.label}</span>
          <span class="bar-track">
            <span class="bar-fill" style="width:${width}%; background:${isSelected ? accent[metric.model] : "#b6c4d2"}"></span>
          </span>
          <span class="bar-value">${formatMetric(metric.rmse)}</span>
        </button>
      `;
    })
    .join("");
}

function renderLineChart() {
  const width = 660;
  const height = 292;
  const padding = { top: 34, right: 28, bottom: 42, left: 48 };
  const plotW = width - padding.left - padding.right;
  const plotH = height - padding.top - padding.bottom;
  const horizons = [1, 15, 60];
  const maxRmse = 1;
  const x = (horizon) => padding.left + (horizons.indexOf(horizon) / (horizons.length - 1)) * plotW;
  const y = (rmse) => padding.top + (1 - rmse / maxRmse) * plotH;

  const series = modelOrder
    .map((model) => {
      const dimmed = model !== state.model;
      const selectedModelPoints = horizons.map((horizon) => {
        const metric = getMetric(horizon, model);
        return { x: x(horizon), y: y(metric.rmse) };
      });
      const points = horizons
        .map((horizon, index) => `${selectedModelPoints[index].x},${selectedModelPoints[index].y}`)
        .join(" ");
      const areaPoints = [
        `${selectedModelPoints[0].x},${height - padding.bottom}`,
        ...selectedModelPoints.map((point) => `${point.x},${point.y}`),
        `${selectedModelPoints[selectedModelPoints.length - 1].x},${height - padding.bottom}`,
      ].join(" ");

      const circles = horizons
        .map((horizon) => {
          const metric = getMetric(horizon, model);
          const selected = model === state.model && horizon === state.horizon;
          return `
            <circle
              class="line-point ${selected ? "selected" : ""}"
              data-point-model="${model}"
              data-point-horizon="${horizon}"
              cx="${x(horizon)}"
              cy="${y(metric.rmse)}"
              r="${selected ? 7 : 5}"
              fill="${accent[model]}"
              stroke="${selected ? "#fff" : "transparent"}"
              stroke-width="${selected ? 3 : 0}"
            >
              <title>${metric.label}, ${horizon} min: RMSE ${formatMetric(metric.rmse)}</title>
            </circle>
          `;
        })
        .join("");

      return `
        <g class="line-series ${dimmed ? "dimmed" : ""}">
          ${
            model === state.model
              ? `<polygon points="${areaPoints}" fill="${accent[model]}" opacity="0.11"></polygon>`
              : ""
          }
          <polyline points="${points}" fill="none" stroke="${accent[model]}" stroke-width="${dimmed ? 2 : 4}" stroke-linecap="round" stroke-linejoin="round" />
          ${circles}
        </g>
      `;
    })
    .join("");

  const grid = [0, 0.25, 0.5, 0.75, 1]
    .map((tick) => {
      const yy = y(tick);
      return `
        <line x1="${padding.left}" y1="${yy}" x2="${width - padding.right}" y2="${yy}" stroke="#e5ebf1" />
        <text class="axis-text" x="8" y="${yy + 4}">${tick.toFixed(2)}</text>
      `;
    })
    .join("");

  const xAxis = horizons
    .map((horizon) => `<text class="axis-text" x="${x(horizon) - 12}" y="${height - 12}">${horizon}m</text>`)
    .join("");

  const legend = modelOrder
    .map((model, index) => {
      const lx = padding.left + index * 138;
      return `
        <g class="legend-item" data-legend-model="${model}">
          <circle cx="${lx}" cy="16" r="5" fill="${accent[model]}" />
          <text class="axis-text" x="${lx + 11}" y="20">${modelNames[model]}</text>
        </g>
      `;
    })
    .join("");

  const activeMetric = getMetric(state.horizon, state.model);
  lineChart.innerHTML = `
    <svg class="line-svg" viewBox="0 0 ${width} ${height}" aria-hidden="true">
      ${grid}
      ${series}
      ${xAxis}
      ${legend}
    </svg>
    <div class="chart-tooltip">
      <span style="color:${accent[state.model]}">●</span>
      ${activeMetric.label} at ${state.horizon} min: RMSE ${formatMetric(activeMetric.rmse)}
    </div>
  `;
}

function updateDashboard() {
  setActiveButtons();
  renderSummary();
  renderBarChart();
  renderLineChart();
}

document.querySelector("#horizonControls").addEventListener("click", (event) => {
  const button = event.target.closest("[data-horizon]");
  if (!button) return;
  state.horizon = Number(button.dataset.horizon);
  updateDashboard();
});

document.querySelector("#modelControls").addEventListener("click", (event) => {
  const button = event.target.closest("[data-model]");
  if (!button) return;
  state.model = button.dataset.model;
  updateDashboard();
});

document.querySelector("#scenarioControls").addEventListener("click", (event) => {
  const button = event.target.closest("[data-scenario]");
  if (!button) return;
  state.scenario = button.dataset.scenario;
  updateDashboard();
});

barChart.addEventListener("click", (event) => {
  const button = event.target.closest("[data-bar-model]");
  if (!button) return;
  state.model = button.dataset.barModel;
  updateDashboard();
});

lineChart.addEventListener("click", (event) => {
  const point = event.target.closest("[data-point-model], [data-legend-model]");
  if (!point) return;
  if (point.dataset.pointModel) {
    state.model = point.dataset.pointModel;
    state.horizon = Number(point.dataset.pointHorizon);
  } else {
    state.model = point.dataset.legendModel;
  }
  updateDashboard();
});

updateDashboard();
