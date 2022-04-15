<html>
{% extends "base.html" %}
{% block bodycontent %}
<body>
  <div class="headline">
    Suggestions
  </div>
  <div class="content">
    Your favourite song is not yet included? Help to improve the app!
    <p>
        <form action="config.php">
          Please enter the song name:
          <div class="input-box">
            <input type="text" name="songname" placeholder="song name">
          </div>
          <br>
          Please enter the artist's name:
          <div class="input-box">
            <input type="text" name="artistname" placeholder="artist's name">
          </div>
          <br>
            <input type="submit" value="Sent"> <br>
            Thank you for your submission!
        </form>
        <p>
        ____________________________________________________________

  <div class="headline">
    Contact
  </div>
  <div class="content">
      Viktoria Dorothea Kamps <div> </div>
      William-Watt-Straße 57 <div> </div>
      21339 Lüneburg <div> </div>
      Germany <div> </div>
      +49 157 77****** <div> </div>
      <p>
    <div class="picture">
      <img src="/static/img/map.jpg" width=98%></img>
    </div>
    <p>
    Still have questions or suggestions for improvement? Get into contact: viktoria.kamps@********* <div>
    <p>

</body>
  <div class="footer">&#169; 2022 </div>
{% endblock bodycontent %}


</html>



<?php
    extract($_REQUEST);
    $file=fopen("form-save.txt","a");

    fwrite($file,"songname :");
    fwrite($file, $songname ."\n");
    fwrite($file,"artistname :");
    fwrite($file, $artistname ."\n");
    fclose($file);
    header("location: contact2.php");
 ?>
