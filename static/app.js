var train_data = {
    name: "",
    second_name: "",
    nat_id: "",
    Date_of_birth: "",
    parent: "",
    phone: "",
    location: "",
    place_birth: "",
    gender: "",
    file: null
};

var recognize_data = {
    file: null
};


var message = null;
var active_section = null;

function render(){

   // clear form data

   $('.form-item input').val('');
   $('.tabs li').removeClass('active');
   $('.tabs li:first').addClass('active');


   active_section = 'train-content';

    $('#'+active_section).show();


}
function update(){


    if(message){
        // render message

        $('.message').html('<p class="'+_.get(message, 'type')+'">'+_.get(message, 'message')+'</p>');
    }else{
        $('.message').html('');
    }

    $('#train-content, #recognize-content').hide();
    $('#'+active_section).show();



}


$(document).ready(function(){




    // listen for file added

    $('#train #input-file').on('change', function(event){



        //set file object to train_data
        train_data.file = _.get(event, 'target.files[0]', null);


    });


    // listen for name change
    $('#name-field').on('change', function(event){

        train_data.name = _.get(event, 'target.value', '');

    });
     // listen for  second name change
     $('#2name-field').on('change', function(event){

        train_data.second_name = _.get(event, 'target.value', '');

    });
     // listen for  national id change
     $('#nat_id-field').on('change', function(event){

        train_data.nat_id = _.get(event, 'target.value', '');

    });
     // listen for  parents change
     $('#parent-field').on('change', function(event){

        train_data.parent = _.get(event, 'target.value', '');

    });
    // listen for  date of birth change
    $('#DOB-field').on('change', function(event){

        train_data.Date_of_birth = _.get(event, 'target.value', '');

    });
    // listen for  place of birth change
    $('#place_birth-field').on('change', function(event){

        train_data.place_birth = _.get(event, 'target.value', '');

    });
    // listen for  gender change
    $('#gender-field').on('change', function(event){

        train_data.gender = _.get(event, 'target.value', '');

    });
    // listen for location change
    $('#location-field').on('change', function(event){

        train_data.location = _.get(event, 'target.value', '');

    });
     // listen for  phone change
     $('#phone-field').on('change', function(event){

        train_data.phone = _.get(event, 'target.value', '');

    });
    


    // listen tab item click on

    $('.tabs li').on('click', function(e){

        var $this = $(this);


        active_section = $this.data('section');

        // remove all active class

        $('.tabs li').removeClass('active');

        $this.addClass('active');

        message = null;

        update();



    });


    // listen the form train submit

    $('#train').submit(function(event){

        message = null;

        if(train_data.name && train_data.second_name&& train_data.nat_id && train_data.parent && train_data.Date_of_birth && train_data.phone && train_data.location && train_data.place_birth && train_data.gender &&train_data.file){
            // do send data to backend api

            var train_form_data = new FormData();

            train_form_data.append('name', train_data.name);
            train_form_data.append('second_name', train_data.second_name);
            train_form_data.append('nat_id', train_data.nat_id);
            train_form_data.append('parent', train_data.parent);
            train_form_data.append('Date_of_birth', train_data.Date_of_birth);
            train_form_data.append('phone', train_data.phone);
            train_form_data.append('location', train_data.location);
            train_form_data.append('place_birth', train_data.place_birth);
            train_form_data.append('gender', train_data.gender);
            train_form_data.append('file', train_data.file);

            axios.post('/api/train', train_form_data).then(function(response){

                message = {type: 'success', message: 'Training has been done, user with id is: ' + _.get(response, 'data.id')};

                train_data = {name: '', second_name: '',nat_id:'', parent:'',Date_of_birth:'', phone: '', location:'',place_birth: '',gender:'', file: null};
                update();

            }).catch(function(error){


                  message = {type: 'error', message: _.get(error, 'response.data.error.message', 'Unknown error.')}

                  update();
            });

        }else{

            message = {type: "error", message: "Name and face image is required."}



        }
        window.location.href=window.location.href;

        update();
        event.preventDefault();
    });


    // listen for recognize file field change
    $('#recognize-input-file').on('change', function(e){


        recognize_data.file = _.get(e, 'target.files[0]', null);

    });
    // listen for recognition form submit
    $('#recognize').submit(function(e){



        // call to backend
        var recog_form_data = new FormData();
        recog_form_data.append('file', recognize_data.file);

        axios.post('/api/recognize', recog_form_data).then(function(response){


            console.log("We found a user matched with your face image is", response.data);

            message = {type: 'success', message: 'We found a user matched with your face image is: '+ response.data.user.name};

            recognize_data = {file: null};
            update();

        }).catch(function(err){


            message = {type: 'error', message: _.get(err, 'response.data.error.message', 'Unknown error')};

            update();

        });
        e.preventDefault();
    });




// render the app;
render();

});



