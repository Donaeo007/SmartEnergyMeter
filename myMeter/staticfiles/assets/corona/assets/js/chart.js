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
  });
  