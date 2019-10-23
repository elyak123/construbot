$(document).ready(function(){
    let dp = document.getElementById("dummy_parent");
    
    function cargar_elementos(){
        $("#inputGroupFile01").click();
        var md5 = "",
        csrf = $("input[name='csrfmiddlewaretoken']")[1].value,
        form_data = [{"name": "csrfmiddlewaretoken", "value": csrf}];
        function calculate_md5(file, chunk_size) {
          var slice = File.prototype.slice || File.prototype.mozSlice || File.prototype.webkitSlice,
              chunks = chunks = Math.ceil(file.size / chunk_size),
              current_chunk = 0,
              spark = new SparkMD5.ArrayBuffer();
          function onload(e) {
            spark.append(e.target.result);  // append chunk
            current_chunk++;
            if (current_chunk < chunks) {
              read_next_chunk();
            } else {
              md5 = spark.end();
            }
          };
          function read_next_chunk() {
            var reader = new FileReader();
            reader.onload = onload;
            var start = current_chunk * chunk_size,
                end = Math.min(start + chunk_size, file.size);
            reader.readAsArrayBuffer(slice.call(file, start, end));
          };
          read_next_chunk();
        }
        $("#inputGroupFile01").fileupload({
          url: "/core/chunk_upload/",
          dataType: "json",
          maxChunkSize: 100000, // Chunks of 100 kB
          formData: form_data,
          add: function(e, data) { // Called before starting upload
            $("#messages").empty();
            // If this is the second file you're uploading we need to remove the
            // old upload_id and just keep the csrftoken (which is always first).
            form_data.splice(1);
            calculate_md5(data.files[0], 100000);  // Again, chunks of 100 kB
            $('.dummy-progreso').toggleClass("d-none");
            $(this).parent().find(".custom-file-label")[0].innerText = data.fileInput.val().replace(/C:\\fakepath\\/i, '');
            data.submit();
          },
          chunkdone: function (e, data) { // Called after uploading each chunk
            if (form_data.length < 2) {
              form_data.push(
                {"name": "upload_id", "value": data.result.upload_id}
              );
            }
            //$("#messages").append($('<p>').text(JSON.stringify(data.result)));
            var progress = parseInt(data.loaded / data.total * 100.0, 10);
            $('.progress-bar').attr('aria-valuenow', progress).css('width', progress+'%');
            $("#dummy-progreso-progress").text("Progreso: "+progress + " %");
            //$("#progress").text(Array(progress).join("=") + "> " + progress + "%");

          },
          done: function (e, data) { // Called when the file has completely uploaded
            $.ajax({
              type: "POST",
              url: "/proyectos/file_chunk_complete/",
              data: {
                csrfmiddlewaretoken: csrf,
                upload_id: data.result.upload_id,
                md5: md5
              },
              dataType: "json",
              success: function(data) {
                //$("#messages").append($('<p>').text(JSON.stringify(data)));
                $('#id_relacion_id_archivo').attr('value', JSON.parse(data).chunked_id)
                $('.dummy-progreso').toggleClass("d-none");
                $('.progress-bar').attr('aria-valuenow', 0).css('width', 0+'%');
              }
            });
          },
        });
    }

    $("#dummy_file").on("click", function(ev){
        $.ajax({
            url: '/proyectos/get_file_chunk_form/',
            type: 'GET',
            success: function(response){
                dp.innerHTML = response;
                cargar_elementos();
            },
        });
        
    });
});
