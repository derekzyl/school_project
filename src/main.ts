import * as d3 from "d3";
import { sliderBottom } from "d3-simple-slider";

// Aggregate data by country
interface CovidData {
  dateRep: any;
  day: string;
  month: string;
  year: string;
  cases: number;
  deaths: number;
  countriesAndTerritories: string;
  geoId: string;
  countryterritoryCode: string;
  popData2019: number;
  continentExp: string;
  Cumulative_number_for_14_days_of_COVID_19_cases_per_100000: string;
}

d3.json("http://localhost:8000/get-file").then((json: any) => {
  const jsonData: CovidData[] = json;
  const aggregatedData = Array.from(
    d3.group(jsonData, (d) => d.countriesAndTerritories)
  );

  // Format the date
  const parseDate = d3.timeParse("%d/%m/%Y");
  jsonData.forEach((d) => {
    d.dateRep = parseDate(d.dateRep ?? " ");
  });

  // Set up the slider
  const startDate = d3.min(jsonData, (d) => d.dateRep);
  const endDate = d3.max(jsonData, (d) => d.dateRep);

  const slider = sliderBottom()
    .min(startDate)
    .max(endDate)
    .step(24 * 60 * 60 * 1000) // One day step
    .width(600)
    .on("onchange", (val) => updateChart(val));

  // Create the SVG container
  const svg = d3
    .select("#chart-container")
    .append("svg")
    .attr("width", 1800)
    .attr("height", 500)
    .append("g")
    .attr("transform", "translate(50,50)");

  // Add the slider to the SVG container
  const sliderSvg = d3
    .select("#chart-container")
    .append("svg")
    .attr("width", 1800)
    .attr("height", 100)
    .append("g")
    .attr("transform", "translate(50,50)");

  sliderSvg.append("g").attr("transform", "translate(0,-10)").call(slider);
  // Add the bottom axis to show country names
  const bottomAxis = svg
    .append("g")
    .attr("class", "bottom-axis")
    .attr("transform", "translate(0, 400)");

  function updateBottomAxis(data: CovidData[]) {
    const countries = Array.from(
      new Set(data.map((d) => d.countriesAndTerritories))
    );

    const axisScale = d3.scaleBand().domain(countries).range([0, 1500]); // Adjust the range based on your SVG width

    const axis = d3.axisBottom(axisScale);

    // Update the bottom axis
    bottomAxis.transition().duration(500).call(axis);

    // Add or update the axis labels
    bottomAxis
      .selectAll(".tick text")
      .data(countries)
      .text((d) => d)
      .attr(
        "transform",
        (d) =>
          `translate(${
            axisScale(d) + axisScale.bandwidth() / 2
          }, 10) rotate(45)`
      )
      .style("text-anchor", "start")
      .style("cursor", "pointer")
      .on("mouseover", (_event, d) => showDetails(d))
      .on("mouseout", hideDetails);
  }

  // Create color scale for countries
  const colorScale = d3.scaleOrdinal(d3.schemeCategory10);

  // Initialize play state
  let isPlaying = false;
  let animationInterval: any;

  // Add a play/pause button
  const playButton = d3
    .select("#chart-container")
    .append("button")
    .text("Play")
    .on("click", togglePlay);

  // Function to toggle play/pause
  /**
   * The function `togglePlay` toggles between playing and pausing an animation, updating a chart with
   * a new value every second until reaching the end date.
   */
  function togglePlay() {
    isPlaying = !isPlaying;
    playButton.text(isPlaying ? "Pause" : "Play");

    if (isPlaying) {
      // Start animation
      animationInterval = d3.interval(() => {
        const currentValue = slider.value();
        const newValue = new Date(currentValue.getTime() + 24 * 60 * 60 * 1000); // Increment by one day
        if (newValue <= new Date(endDate ?? "")) {
          slider.value(newValue);
          updateChart(newValue);
        } else {
          // Stop animation when reaching the end
          togglePlay();
        }
      }, 1000); // Change the interval as needed
    } else {
      // Pause animation
      animationInterval.stop();
    }
  }

  // Function to update the chart based on the selected date
  function updateChart(selectedDate: any) {
    const filteredData = jsonData.filter((d) => {
      const date = new Date(d.dateRep);
      return date.getTime() === selectedDate.getTime();
    });

    // Bind filtered data to bars
    const bars = svg.selectAll(".bar").data(filteredData, (d: any) => {
      return d.countriesAndTerritories;
    });

    // Enter new bars
    const svgWidth = 1500;

    bars
      .enter()
      .append("rect")
      .attr("class", "bar")
      .attr("x", (d, i) => (i * svgWidth) / filteredData.length) // Adjust the x position
      .attr("width", svgWidth / filteredData.length - 2) // Adjust the width and spacing
      .attr("y", (d) => 400 - d.cases)
      .attr("height", (d) => d.cases)
      .attr("fill", (d) => colorScale(d.countriesAndTerritories))
      .on("mouseover", showDetails)
      .on("mouseout", hideDetails);

    // Update existing bars
    bars
      .attr("x", (d, i) => (i * svgWidth) / filteredData.length) // Adjust the x position
      .attr("width", svgWidth / filteredData.length - 2) // Adjust the width and spacing
      .attr("y", (d) => 400 - d.cases)
      .attr("height", (d) => d.cases)
      .attr("fill", (d) => colorScale(d.countriesAndTerritories));

    // Remove bars for countries that are not in the filtered data
    bars.exit().remove();

    // Update bottom axis
    updateBottomAxis(filteredData);
    updateVerticalAxis(filteredData);
  }
  const tooltip = d3
    .select("body")
    .append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);
  const yAxis = svg
    .append("g")
    .attr("class", "y-axis")
    .attr("transform", "translate(0,0)");

  // Function to show details on hover
  function showDetails(dx) {
    // console.log(d.target.__data__, "inside gjere");
    // console.log(d3.event.target.__data__, "inside d3 gjere");
    const d = dx.target.__data__;
    // Create tooltip text

    const tooltipText = `${d.countriesAndTerritories}: Cases - ${d.cases}, Deaths - ${d.deaths}`;
    // Display tooltip
    tooltip.transition().duration(200).style("opacity", 0.9);
    tooltip
      .html(tooltipText)
      .style("left", dx.event.pageX + "px")
      .style("top", dx.event.pageY - 28 + "px");
  }

  /**
   * The function updates the vertical axis of a chart based on the maximum number of cases in the
   * provided data.
   * @param {CovidData[]} data - The `data` parameter is an array of objects representing CovidData.
   * Each object in the array should have a property called `cases` which represents the number of
   * Covid cases.
   */
  function updateVerticalAxis(data: CovidData[]) {
    const maxCases = d3.max(data, (d) => d.cases) || 0;

    const yScale = d3.scaleLinear().domain([0, maxCases]).range([400, 0]);

    const axis = d3.axisLeft(yScale);

    // Update the vertical axis
    yAxis.transition().duration(500).call(axis);

    // Add or update the label
    let label: any = svg.select(".y-axis-label");

    if (label.empty()) {
      label = svg
        .append("text")
        .attr("class", "y-axis-label")
        .attr("transform", "rotate(-90)")
        .attr("x", -200)
        .attr("y", 15)
        .style("text-anchor", "middle")
        .text("Number of Cases");
    }
  }
  updateVerticalAxis(jsonData);
  updateBottomAxis(jsonData);
  // Function to hide details on mouseout
  function hideDetails() {
    // Hide tooltip
    tooltip.transition().duration(500).style("opacity", 0);
  }
});
