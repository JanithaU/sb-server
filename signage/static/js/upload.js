//$(document).ready(function() {

	$('#upload').on('submit', function(event) {

		event.preventDefault();

		var formData = new FormData($('form')[0]);

		$.ajax({
			xhr : function() {
				var xhr = new window.XMLHttpRequest();

				xhr.upload.addEventListener('progress', function(e) {

					if (e.lengthComputable) {

						//console.log('Bytes Loaded: ' + e.loaded);
						//console.log('Total Size: ' + e.total);
						//console.log('Percentage Uploaded: ' + (e.loaded / e.total))

						var percent = Math.round((e.loaded / e.total) * 100);

						$('#progressBar').attr('aria-valuenow', percent).css('width', percent + '%').text(percent + '%');

					}

				});

				return xhr;
			},
			type : 'POST',
			url : '/media/add',
			data : formData,
			processData : false,
			contentType : false,
			success : function(response) {
				console.log(response.Valid)
				if (response.Valid){
					alert( "File Uploaded !" );
					top.location.href = '/media';
				}
				else{
					alert(" Upload Error ! \n "+  response.error);
				}


			},
			error: function() { 
                    alert( "File Error" );
                    top.location.href = '/media'; 
            }
		});

	});

//});
