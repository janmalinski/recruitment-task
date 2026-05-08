const startDateInput = document.getElementById("startDate");
const endDateInput = document.getElementById("endDate");
const getDataButton = document.getElementById("getDataButton");
const tableBody = document.getElementById("tableBody");
const errorBox = document.getElementById("error");
const metaBox = document.getElementById("meta");

function getYesterdayIsoDate() {
  const date = new Date();
  date.setDate(date.getDate() - 1);

  return date.toISOString().slice(0, 10);
}

function setDefaultDates() {
  const yesterday = getYesterdayIsoDate();

  startDateInput.value = yesterday;
  endDateInput.value = yesterday;
  startDateInput.max = yesterday;
  endDateInput.max = yesterday;
}

function buildUrl() {
  const params = new URLSearchParams();

  if (startDateInput.value) {
    params.set("start_date", startDateInput.value);
  }

  if (endDateInput.value) {
    params.set("end_date", endDateInput.value);
  }

  return `/api/v1/cities-scores?${params.toString()}`;
}

function renderRows(results) {
  tableBody.innerHTML = results
    .map((item) => {
      return `
        <tr>
          <td>${item.city}</td>
          <td>${item.country}</td>
          <td>${item.weather.average_temperature.toFixed(2)} °C</td>
          <td>${item.weather.average_wind_speed.toFixed(2)} m/s</td>
          <td>${item.weather.average_relative_humidity.toFixed(2)}%</td>
          <td>${item.weather.average_cloud_cover.toFixed(2)}%</td>
          <td>${item.scores.temperature.toFixed(2)}</td>
          <td>${item.scores.wind_speed.toFixed(2)}</td>
          <td>${item.scores.relative_humidity.toFixed(2)}</td>
          <td>${item.scores.cloud_cover.toFixed(2)}</td>
          <td class="score">${item.scores.total.toFixed(2)}</td>
        </tr>
      `;
    })
    .join("");
}

async function loadData() {
  errorBox.textContent = "";
  metaBox.textContent = "";
  tableBody.innerHTML = "";
  getDataButton.disabled = true;
  getDataButton.textContent = "Loading...";

  try {
    const response = await fetch(buildUrl());
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Failed to load data");
    }

    metaBox.textContent = `Date range: ${data.start_date} — ${data.end_date}`;
    renderRows(data.results);
  } catch (error) {
    errorBox.textContent = error.message;
  } finally {
    getDataButton.disabled = false;
    getDataButton.textContent = "Get Data";
  }
}

getDataButton.addEventListener("click", loadData);

setDefaultDates();
loadData();