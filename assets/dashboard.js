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
  random_forest: "#0d9f75",
  linear_regression_scaled: "#1463ff",
  baseline_persistence: "#e1862f",
  baseline_mean: "#8a96a8",
};

const horizonSelect = document.querySelector("#horizonSelect");
const modelSelect = document.querySelector("#modelSelect");
const scenarioSelect = document.querySelector("#scenarioSelect");
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

function scenarioText(metric, scenario) {
  const scenarioCopy = {
    normal: "For a typical usage rhythm, this model gives a grounded estimate of expected forecast error without pretending the household signal is perfectly smooth.",
    spike: "In a spike-prone evening setting, expect wider practical uncertainty because high-demand events are real behavior rather than noise to discard.",
    overnight: "During lower-load overnight periods, short-horizon autocorrelation is especially useful, which is why persistence remains competitive at the shortest horizon.",
  };

  const modelCopy =
    metric.model === "random_forest"
      ? "The Random Forest result shows the strongest RMSE profile for this horizon."
      : metric.model === "baseline_persistence"
        ? "The persistence baseline is intentionally included as a tough, honest comparator."
        : "This model is useful as a comparison point against both simple baselines and nonlinear modeling.";

  return `${scenarioCopy[scenario]} ${modelCopy}`;
}

function renderSummary() {
  const horizon = Number(horizonSelect.value);
  const model = modelSelect.value;
  const scenario = scenarioSelect.value;
  const metric = getMetric(horizon, model);

  selectedTitle.textContent = `${horizon}-minute ${metric.label} forecast`;
  selectedNarrative.textContent = scenarioText(metric, scenario);
  maeValue.textContent = formatMetric(metric.mae);
  rmseValue.textContent = formatMetric(metric.rmse);
  r2Value.textContent = formatMetric(metric.r2);
  chartHorizonLabel.textContent = `${horizon} min`;
}

function renderBarChart() {
  const horizon = Number(horizonSelect.value);
  const selectedModel = modelSelect.value;
  const horizonMetrics = modelOrder.map((model) => getMetric(horizon, model));
  const maxRmse = Math.max(...horizonMetrics.map((metric) => metric.rmse));

  barChart.innerHTML = horizonMetrics
    .map((metric) => {
      const width = Math.max(6, (metric.rmse / maxRmse) * 100);
      return `
        <div class="bar-row ${metric.model === selectedModel ? "selected" : ""}">
          <span class="bar-label">${metric.label}</span>
          <div class="bar-track">
            <div class="bar-fill" style="width:${width}%; background:${metric.model === selectedModel ? accent[metric.model] : "#b6c4d2"}"></div>
          </div>
          <span class="bar-value">${formatMetric(metric.rmse)}</span>
        </div>
      `;
    })
    .join("");
}

function renderLineChart() {
  const width = 620;
  const height = 270;
  const padding = { top: 20, right: 26, bottom: 40, left: 46 };
  const plotW = width - padding.left - padding.right;
  const plotH = height - padding.top - padding.bottom;
  const horizons = [1, 15, 60];
  const maxRmse = 1;
  const x = (horizon) => padding.left + (horizons.indexOf(horizon) / (horizons.length - 1)) * plotW;
  const y = (rmse) => padding.top + (1 - rmse / maxRmse) * plotH;

  const series = modelOrder
    .map((model) => {
      const points = horizons.map((horizon) => {
        const metric = getMetric(horizon, model);
        return `${x(horizon)},${y(metric.rmse)}`;
      });
      return `
        <polyline points="${points.join(" ")}" fill="none" stroke="${accent[model]}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
        ${horizons
          .map((horizon) => {
            const metric = getMetric(horizon, model);
            return `<circle cx="${x(horizon)}" cy="${y(metric.rmse)}" r="4" fill="${accent[model]}" />`;
          })
          .join("")}
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
      const lx = padding.left + index * 126;
      return `
        <circle cx="${lx}" cy="14" r="4" fill="${accent[model]}" />
        <text class="axis-text" x="${lx + 9}" y="18">${modelNames[model]}</text>
      `;
    })
    .join("");

  lineChart.innerHTML = `
    <svg class="line-svg" viewBox="0 0 ${width} ${height}" aria-hidden="true">
      ${grid}
      ${series}
      ${xAxis}
      ${legend}
    </svg>
  `;
}

function updateDashboard() {
  renderSummary();
  renderBarChart();
  renderLineChart();
}

[horizonSelect, modelSelect, scenarioSelect].forEach((control) => {
  control.addEventListener("change", updateDashboard);
});

updateDashboard();
