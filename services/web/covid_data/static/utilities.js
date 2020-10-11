var curRegionPieChartUrl = "total_deaths_by_region_at_current_week_json";
var curRegionPieChartTitle = "Total deaths by region";
var curDeathsBarChartUrl = "total_deaths_by_age_and_sex";
var curDeathsBarChartTitle = 'Total deaths by age and sex';

// Callback that creates and populates a data table,
// instantiates the chart, passes in the data and
// draws it.
function drawTimeSeriesChart() {
    let jsonData = $.ajax({
        url: "total_deaths_json",
        dataType: "json",
        async: false
    }).responseText;

    // Create our data table out of JSON data loaded from server.
    let data = new google.visualization.DataTable(jsonData);          // Set chart options
    let options = {
        'title': 'Total deaths time series',
        'height': 500,
        'width': 1000,
    };

    // Instantiate and draw our chart, passing in some options.
    let chart = new google.visualization.LineChart(document.getElementById("time-series-chart"));
    chart.draw(data, options);
}

function drawDeathsBarChart() {
    let jsonData = $.ajax({
        url: curDeathsBarChartUrl,
        dataType: "json",
        async: false
    }).responseText;

    // Create our data table out of JSON data loaded from server.
    let data = new google.visualization.DataTable(jsonData);          // Set chart options

    // Instantiate and draw our chart, passing in some options.
    let chart = new google.visualization.BarChart(document.getElementById("deaths-pie-chart"));
    let options = {
        'title': curDeathsBarChartTitle,
        'height': 500,
        'width': 1000,
        'isStacked': true,
    };
    chart.draw(data, options);
}

function drawRegionPieChart() {
    let jsonData = $.ajax({
        url: curRegionPieChartUrl,
        dataType: "json",
        async: false
    }).responseText;

    // Create our data table out of JSON data loaded from server.
    let data = new google.visualization.DataTable(jsonData);          // Set chart options

    // Instantiate and draw our chart, passing in some options.
    let chart = new google.visualization.PieChart(document.getElementById("regions-pie-chart"));
    let options = {
        'title': curRegionPieChartTitle,
        'height': 500,
        'width': 1000,
        'is3D': true,
    };
    chart.draw(data, options);
}

function sidenavInit() {
    $(".sidenav-js").click(function (event) {
        console.log('sidenav-js clicked!')
        event.preventDefault();
        $(this).addClass("w3-light-green");
        $(this).siblings().removeClass("w3-light-green")
        let new_url = $(this).attr('data-url')
        let args = $(this).attr('data-args')
        if (args !== undefined) {
            let d = $(this).text();
            curRegionPieChartUrl = "deaths_by_region_on_date_json?date=" + d;
            curRegionPieChartTitle = "Total deaths by Region on " + d;
            drawRegionPieChart();
            curDeathsBarChartUrl = "total_deaths_by_age_and_sex?date=" + d;
            curDeathsBarChartTitle = "Deaths by age and sex on " + d;
            drawDeathsBarChart();
        }
        else {
            window.document.location = new_url
        }
    });
}
