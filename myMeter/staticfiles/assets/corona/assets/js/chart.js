$(function() {
    'use strict';
    //$("#lineChart").attr('height', '70px'); // Adjust height as needed
    //$("#lineChart").attr('width', '100%'); // Adjust width as needed
  
    var options = {
      scales: {
        yAxes: [{
          ticks: {
            beginAtZero: true
          },
          gridLines: {
            color: "rgba(204, 204, 204,0.1)"
          }
        }],
        xAxes: [{
          gridLines: {
            color: "rgba(204, 204, 204,0.1)"
          }
        }]
      },
      legend: {
        display: false
      },
      elements: {
        point: {
          radius: 0
        }
      }
    };

     // Dynamic data variables
  var lineChart;
  
  function fetchData() {
       $.ajax({
         url: '/meter/LoadLineChart', // Update this URL to match your Django URL pattern
         type: 'GET',
         success: function(response) {
         updateChart(response);
         },
         error: function(error) {
           console.log('Error fetching data:', error);
         }
       });
  }
   
  function updateChart(data) {
       if (lineChart) {
         lineChart.data.labels = data.labels;
         lineChart.data.datasets[0].data = data.data;
         lineChart.update();
       }
  }

    
  if ($("#lineChart").length) {
      var lineChartCanvas = $("#lineChart").get(0).getContext("2d");
      lineChart = new Chart(lineChartCanvas, {
        type: 'line',
        data: {
          labels: [],
          datasets: [{
            label: 'Energy Consumption',
            data: [],
            backgroundColor: [
              'rgba(255, 99, 132, 0.2)',
              'rgba(54, 162, 235, 0.2)',
              'rgba(255, 206, 86, 0.2)',
              'rgba(75, 192, 192, 0.2)',
              'rgba(153, 102, 255, 0.2)',
              'rgba(255, 159, 64, 0.2)'
            ],
            borderColor: [
              'rgba(255,99,132,1)',
              'rgba(54, 162, 235, 1)',
              'rgba(255, 206, 86, 1)',
              'rgba(75, 192, 192, 1)',
              'rgba(153, 102, 255, 1)',
              'rgba(255, 159, 64, 1)'
            ],
            borderWidth: 1,
            fill: false
          }]
        },
        options: options
      });
  
      fetchData(); // Initial fetch
      setInterval(fetchData, 5000); // Fetch new data every 5 seconds
  }

  //======================================================================//

  //  GUAGE UPDATES=============================================================
// Chart instances
// Ensure that the DOM is fully loaded before running the script
$(document).ready(function() {
  // Chart instances
  var voltageGaugeChart, currentGaugeChart, powerGaugeChart;

  function createGaugeChart(chartId, fillColor) {
      var gaugeChartCanvas = $("#" + chartId).get(0).getContext("2d");
      return new Chart(gaugeChartCanvas, {
          type: 'doughnut',
          data: {
              datasets: [{
                  data: [0, 100],
                  backgroundColor: [fillColor, "#e0e0e0"],
                  borderWidth: 0
              }]
          },
          options: {
              responsive: true,
              maintainAspectRatio: true,
              rotation: 1 * Math.PI, // Half circle
              circumference: 1 * Math.PI, // Half circle
              cutoutPercentage: 80, // Inner radius
              tooltips: { enabled: false },
              legend: { display: false },
              plugins: {
                  datalabels: { display: false }
              }
          }
      });
  }

  // Function to update the gauge data
  function updateGauge(chart, value) {
      if (chart) {
          chart.data.datasets[0].data = [value, 100 - value];
          chart.update();
      }
  }

  // Function to fetch and update data
  function updateDashboard() {
      $.ajax({
          url: "/meter/updateDashboard", // Ensure this matches your Django URL pattern
          type: 'GET',
          success: function(result) {
              console.log("Ajax request successful");

              // Update the gauges
              updateGauge(voltageGaugeChart, result.voltageGuageFill);
              updateGauge(currentGaugeChart, result.currentGuageFill);
              updateGauge(powerGaugeChart, result.powerGuageFill);

              // Update data
              $('#vol').html(result['voltage']+'<bold>V</bold>');
              $('#cur').html(result['current']+'<bold>A</bold>');
              $('#pwr').html(result['power']+'<bold>W</bold>');
              $('#pwr2').html(result['power']+'<bold>W</bold>');
              $('#eng').html(result['energy']+'<bold>kWh</bold>');
              $('#eng2').html(result['energy']+'<bold>kWh</bold>');
              $('#pwf').html(result['powerfactor']);
              $('#cst').html('<bold>NGN</bold>'+result['cost']);
              $('#cst2').html('<bold>NGN</bold>'+result['cost']);
              $('#utc').html(result['unixtime']);
              $('#utc2').html(result['unixtime']);
              $('#utc3').html(result['unixtime']);
              $('#utc4').html(result['unixtime']);
              $('#volchg').html(result['voltage_change']);
              $('#curchg').html(result['current_change']);
              $('#pwrchg').html(result['power_change']+'<sub>%</sub>');
              $('#engchg').html(result['energy_change']+'<sub>%</sub>');
              $('#pwfchg').html(result['powerfactor_change']+'<sub>%</sub>');
              $('#cstchg').html(result['cost_change']+'<sub>%</sub>');
          },
          error: function(xhr, status, error) {
              console.error("Ajax request failed:", status, error);
          }
      });
  }

  // Initialize Voltage Gauge Chart
  if ($("#VoltagegaugeChart").length) {
      voltageGaugeChart = createGaugeChart("VoltagegaugeChart", "#FF0000");
  }

  // Initialize Current Gauge Chart
  if ($("#CurrentgaugeChart").length) {
      currentGaugeChart = createGaugeChart("CurrentgaugeChart", "#00FF00");
  }

  // Initialize Power Gauge Chart
  if ($("#PowergaugeChart").length) {
      powerGaugeChart = createGaugeChart("PowergaugeChart", "#0000FF");
  }

  // Initial fetch and start interval to update data
  updateDashboard();
  setInterval(updateDashboard, 2000);
});

//===========================================================================
/*
  function updateDashboard(){
    //console.log("updateDashboard called");
    var route= "/meter/updateDashboard";
    $.ajax({
      url:route,
      type:'GET',
     
      success:
      function(result){
        console.log("Ajax request successful");
      },
      error: function(xhr, status, error) {
        console.error("Ajax request failed:", status, error);
    }
    });
}

setInterval(updateDashboard, 8000);

  var VoltagegaugeData = {
      datasets: [{
          data: [75, 25], // Example: 75% filled, 25% empty
          backgroundColor: ["#FF0000", "#e0e0e0"], // Filled part and empty part colors
          borderWidth: 0
      }]
  };
  
  var VoltagegaugeOptions = {
      responsive: true,
      maintainAspectRatio: true,
      rotation: 1 * Math.PI, // Half circle
      circumference: 1 * Math.PI, // Half circle
      cutoutPercentage: 80, // Inner radius
      tooltips: { enabled: false },
      legend: { display: false },
      plugins: {
          datalabels: {
              display: false
          }
      }
  };
  
  var VoltagegaugeNeedlePlugin = {
    afterDraw: function(chart) {
        var ctx = chart.chart.ctx;
        var value = chart.data.datasets[0].data[0];
        var angle = Math.PI - (Math.PI * value / 100); // Reverse the needle angle calculation
        var radius = chart.outerRadius - (chart.outerRadius - chart.innerRadius) / 2;
        var x = chart.chart.width / 2;
        var y = chart.chart.height - chart.chart.height / 10;

        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(angle);
        ctx.beginPath();
        ctx.moveTo(0, -radius);
        ctx.lineTo(0, 10);
        ctx.lineWidth = 2;
        ctx.strokeStyle = "#FFFFFF"; // Needle color
        ctx.stroke();
        ctx.restore();

        // Needle base
        ctx.beginPath();
        ctx.arc(x, y, 5, 0, Math.PI * 2);
        ctx.fillStyle = "#FFFFFF"; // Needle base color
        ctx.fill();
    }
};

var CurrentgaugeData = {
  datasets: [{
      data: [30, 70], // Example: 75% filled, 25% empty
      backgroundColor: ["#00FF00", "#e0e0e0"], // Filled part and empty part colors
      borderWidth: 0
  }]
};

var CurrentgaugeOptions = {
  responsive: true,
  maintainAspectRatio: true,
  rotation: 1 * Math.PI, // Half circle
  circumference: 1 * Math.PI, // Half circle
  cutoutPercentage: 80, // Inner radius
  tooltips: { enabled: false },
  legend: { display: false },
  plugins: {
      datalabels: {
          display: false
      }
  }
};

var CurrentgaugeNeedlePlugin = {
afterDraw: function(chart) {
    var ctx = chart.chart.ctx;
    var value = chart.data.datasets[0].data[0];
    var angle = Math.PI - (Math.PI * value / 100); // Reverse the needle angle calculation
    var radius = chart.outerRadius - (chart.outerRadius - chart.innerRadius) / 2;
    var x = chart.chart.width / 2;
    var y = chart.chart.height - chart.chart.height / 10;

    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);
    ctx.beginPath();
    ctx.moveTo(0, -radius);
    ctx.lineTo(0, 10);
    ctx.lineWidth = 2;
    ctx.strokeStyle = "#FFFFFF"; // Needle color
    ctx.stroke();
    ctx.restore();

    // Needle base
    ctx.beginPath();
    ctx.arc(x, y, 5, 0, Math.PI * 2);
    ctx.fillStyle = "#FFFFFF"; // Needle base color
    ctx.fill();
}
};
var PowergaugeData = {
  datasets: [{
      data: [60, 30], // Example: 75% filled, 25% empty
      backgroundColor: ["#0000FF", "#e0e0e0"], // Filled part and empty part colors
      borderWidth: 0
  }]
};

var PowergaugeOptions = {
  responsive: true,
  maintainAspectRatio: true,
  rotation: 1 * Math.PI, // Half circle
  circumference: 1 * Math.PI, // Half circle
  cutoutPercentage: 80, // Inner radius
  tooltips: { enabled: false },
  legend: { display: false },
  plugins: {
      datalabels: {
          display: false
      }
  }
};

var PowergaugeNeedlePlugin = {
afterDraw: function(chart) {
    var ctx = chart.chart.ctx;
    var value = chart.data.datasets[0].data[0];
    var angle = Math.PI - (Math.PI * value / 100); // Reverse the needle angle calculation
    var radius = chart.outerRadius - (chart.outerRadius - chart.innerRadius) / 2;
    var x = chart.chart.width / 2;
    var y = chart.chart.height - chart.chart.height / 10;

    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);
    ctx.beginPath();
    ctx.moveTo(0, -radius);
    ctx.lineTo(0, 10);
    ctx.lineWidth = 2;
    ctx.strokeStyle = "#FFFFFF"; // Needle color
    ctx.stroke();
    ctx.restore();

    // Needle base
    ctx.beginPath();
    ctx.arc(x, y, 5, 0, Math.PI * 2);
    ctx.fillStyle = "#FFFFFF"; // Needle base color
    ctx.fill();
}
}; 
*/

/*

if ($("#VoltagegaugeChart").length) {
      var gaugeChartCanvas = $("#VoltagegaugeChart").get(0).getContext("2d");
      var gaugeChart = new Chart(gaugeChartCanvas, {
          type: 'doughnut',
          data: VoltagegaugeData,
          options: VoltagegaugeOptions,
          plugins: [VoltagegaugeNeedlePlugin]
      });
  }

if ($("#CurrentgaugeChart").length) {
    var gaugeChartCanvas = $("#CurrentgaugeChart").get(0).getContext("2d");
    var gaugeChart = new Chart(gaugeChartCanvas, {
        type: 'doughnut',
        data: CurrentgaugeData,
        options: CurrentgaugeOptions,
        plugins: [CurrentgaugeNeedlePlugin]
    });
}

if ($("#PowergaugeChart").length) {
  var gaugeChartCanvas = $("#PowergaugeChart").get(0).getContext("2d");
  var gaugeChart = new Chart(gaugeChartCanvas, {
      type: 'doughnut',
      data: PowergaugeData,
      options: PowergaugeOptions,
      plugins: [PowergaugeNeedlePlugin]
  });
}
   */ 
  });
  