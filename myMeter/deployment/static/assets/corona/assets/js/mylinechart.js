$(function() {
    'use strict';
  
    var lineChart;
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
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1,
            fill: false
          }]
        },
        options: options
      });
  
      fetchData(); // Initial fetch
      setInterval(fetchData, 5000); // Fetch new data every 5 seconds
    }
  });
  