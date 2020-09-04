$(document).ready(function(){
    $("#train").submit(function(e){
      e.preventDefault();


      $.ajax({
        url: '/api/train',
        type: "POST",
        data: new FormData(this),
        contentType: false,
        cache: false, 
        processData: false,
        success: function(data){
        	//do what you want to do if it successful
        	alert("success");

        },
        error: function(){
        	//do what you want to do if it fails
        	alert("fail");
        },
      });

    });
});