    $(document).ready(function(){
    	// Smart Wizard
  		// $('#wizard').smartWizard();
      function onFinishCallback(){

        $('#wizard').smartWizard('showMessage','Finish Clicked');

        //alert('Finish Clicked');
      }
		});


// first pop up//
$(function(){
var appendthis =  ("<div class='modal-overlay js-modal-close'></div>");
	$('a[data-modal-id]').click(function(e) {
		e.preventDefault();
    $("body").append(appendthis);
    $(".modal-overlay").fadeTo(500, 0.7);
		var modalBox = $(this).attr('data-modal-id');
		$('#'+modalBox).fadeIn($(this).data());

        var radioonhandplan = document.getElementsByName("ohplanselect");
        var ohbasisplan = ''
        var discount = document.getElementById('id_discount').value;
            for(var i=0; i < radioonhandplan.length; i++){
                if(radioonhandplan[i].checked) {
                    // radiocheckedonhandplans = i;
                    plansslected =true;
                    ohbasisplan = radioonhandplan[i].value;
                // alert(ohbasisplan);
                }
            }
        $.ajax({
            url: '/ajax_getselectedonhandplan/',
            data: {
                'discount': discount,
                'plan': ohbasisplan
            },
            dataType: 'json',
            success: function (response_data) {
                console.log(response_data);
                if (response_data.result == 'valid' ){
                    document.getElementById('ohselected_plan').innerHTML = response_data.plan;
                    document.getElementById('ohselected_price').innerHTML ="$ " + response_data.price;
                    document.getElementById('ohselected_basis').innerHTML = response_data.billed;
                    document.getElementById('ohselected_promotion').innerHTML = response_data.promotion;
                        }
                }
        });
	});

$(".js-modal-close").click(function() {

    $(".modal-box").fadeOut(500, function() {

        $(".modal-overlay").remove();

    });
});

$(window).resize(function() {

    $(".modal-box").css({

        top: ($(window).height() - $(".modal-box").outerHeight()) / 2,

        left: ($(window).width() - $(".modal-box").outerWidth()) / 2

    });

});
$(window).resize();
});


//second popup //
$(function(){

var appendthis =  ("<div class='modal-overlay js-modal-close-card-details'></div>");

	$('a[data-modal-id]').click(function(e) {
		e.preventDefault();
    $("body").append(appendthis);
    $(".modal-overlay-details").fadeTo(500, 0.7);
		var modalBox = $(this).attr('data-modal-id');
		$('#'+modalBox).fadeIn($(this).data());
	});

if( document.getElementById('id_firstname').value != '' ||  document.getElementById('id_lastname').value != '' ||
                  document.getElementById('id_email').value != '' ||  document.getElementById('id_compname').value != '' ||
                  document.getElementById('id_addressline1').value != '' ||  document.getElementById('id_addressline2').value != '' ||
                  document.getElementById('id_zipcode').value != '' ||  document.getElementById('id_cardnumber').value != ''
              ){
        // alert(3);
     $(".modal-box").fadeOut(50, function() {
     $(".modal-overlay").remove();
        $(".modal-box-card-details").fadeIn();
          $(".modal-box-card-details").css({
        top: ($(window).height() - $(".modal-box-card-details").outerHeight()) / 2,
        left: ($(window).width() - $(".modal-box-card-details").outerWidth()) / 2
    });
       $(window).resize();
	    });
        // alert(4);
    }

$(".js-modal-close-card-details").click(function() {
    $(".modal-box-card-details").fadeOut(500, function() {
        $(".modal-overlay-details").remove();
    });

    // var appendthis =  ("<div class='modal-overlay js-modal-close'></div>");
    // e.preventDefault();
    // $("body").append(appendthis);
    // $('.modal-box').fadeTo(500, 0.7);
    $('.modal-box').fadeIn();
      $(".modal-box").css({

        top: ($(window).height() - $(".modal-box").outerHeight()) / 2,

        left: ($(window).width() - $(".modal-box").outerWidth()) / 2

    });

    $(window).resize();



});

$(window).resize(function() {
    $(".modal-box-card-details").css({
        top: ($(window).height() - $(".modal-box-card-details").outerHeight()) / 2,
        left: ($(window).width() - $(".modal-box-card-details").outerWidth()) / 2
    });
});

$(window).resize();

});


