$(document).ready(function(){
    let dp = document.getElementById("dummy_parent");
    let var_prueba = null;
    
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
            data.submit();
          },
          chunkdone: function (e, data) { // Called after uploading each chunk
            if (form_data.length < 2) {
              form_data.push(
                {"name": "upload_id", "value": data.result.upload_id}
              );
            }
            $("#messages").append($('<p>').text(JSON.stringify(data.result)));
            var progress = parseInt(data.loaded / data.total * 100.0, 10);
            $("#progress").text(Array(progress).join("=") + "> " + progress + "%");
          },
          done: function (e, data) { // Called when the file has completely uploaded
            $.ajax({
              type: "POST",
              url: "{% url 'api_chunked_upload_complete' %}",
              data: {
                csrfmiddlewaretoken: csrf,
                upload_id: data.result.upload_id,
                md5: md5
              },
              dataType: "json",
          success: function(data) {
                $("#messages").append($('<p>').text(JSON.stringify(data)));
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
