function updateDashboard(){
    console.log("updateDashboard called");
    var route= "/meter/updateDashboard";
    $.ajax({
      url:route,
      type:'GET',
     
      success:
      function(result){
        console.log("Ajax request successful");
        $('#vol').text('Voltage: ' + result['voltage']);
        $('#cur').text('Current: ' + result['current']);
        $('#pwr').text('Power: ' + result['power']);
        $('#eng').text('Energy: ' + result['energy']);
        $('#cst').text('Cost: ' + result['cost']);
        $('#utc').text('Unixtime: ' + result['unixtime']);
        /*$('#total-ener').html(result['TotalEnergy']+'<sub>kWh</sub>');
        $('#total-car-cre').html(result['CarbonCredit'] + '<sub>(c)</sub>');
        $('#energy-incr').text(result['EnergyIncrease']+ '%');
        $('#carbon-incr').text(result['EnergyIncrease'] + '%');*/
      },
      error: function(xhr, status, error) {
        console.error("Ajax request failed:", status, error);
    }
    });
}

setInterval(updateDashboard, 5000);
