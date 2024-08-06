function updateDashboard(){
    //console.log("updateDashboard called");
    var route= "/meter/updateDashboard";
    $.ajax({
      url:route,
      type:'GET',
     
      success:
      function(result){
        console.log("Ajax request successful");
        $('#vol').html(result['voltage']);
        $('#cur').html(result['current']);
        $('#pwr').html(result['power']);
        $('#eng').html(result['energy']);
        $('#pwf').html(result['powerfactor']);
        $('#cst').html(result['cost']);
        $('#utc').html(result['unixtime']);
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

setInterval(updateDashboard, 8000);
