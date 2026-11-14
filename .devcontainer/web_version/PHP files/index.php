<?php 
  session_start(); 

  if (!isset($_SESSION['username'])) {
  	$_SESSION['msg'] = "You must log in first";
  	header('location: login.php');
  }
  if (isset($_GET['logout'])) {
  	session_destroy();
  	unset($_SESSION['username']);
  	header("location: login.php");
  }
?>
<!DOCTYPE html>
<html>
<head>
	<!-- Required meta tags -->
	<meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="home.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">


  <!-- Bootstrap CSS -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Fredoka+One&family=Merriweather&family=Montserrat&family=Nunito:wght@200;300;400;600;700&family=Readex+Pro&family=Sacramento&display=swap');
  </style>
	<title>Home</title>
	<link rel="stylesheet" type="text/css" href="../home.css">
</head>
<body>

<div class="header">
	<!--h2>Home Page</h2-->
</div>
<nav class="navbar navbar-expand-lg navbar-light bg-">
    <div class="container-fluid">
      <a class="navbar-brand" href="#">
        <img src="../logo.jpg" width="30px" height="30px" class="d-inline-block align-top" alt="">
          Agriculture
      </a>
      <div class="collapse navbar-collapse" id="navbarSupportedContent">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li class="nav-item">
            <a class="nav-link active" aria-current="page" href="index.php">Home</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="../Soil.html">Soil</a>
          </li>
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="" id="navbarDropdown" role="button"
              data-bs-toggle="dropdown" aria-expanded="false">
              Crops
            </a>
            <ul class="dropdown-menu" aria-labelledby="navbarDropdown">
              <li><a id="Sugarcane" class="dropdown-item" href="../sugarcane.html">Sugarcane</a></li>
              <li><a id="Wheat" class="dropdown-item" href="../wheat.html">Wheat</a></li>
              <li><a id="rice" class="dropdown-item" href="../rice.html">Rice</a></li>
            </ul>
          </li>
        </ul>
		<p>Welcome <strong><?php echo $_SESSION['username']; ?></strong></p>
    	<p> <a href="index.php?logout='1'" style="color: red;">logout</a> </p>
        <!--form class="d-flex">
          <button id="login" class="btn btn-outline-success mx-4 btn-sm" type="submit"><a
              href="../projectagri/PHP files/login.php">Login</a></button>
          <button id="signup" class="btn btn-outline-success mx-4 btn-sm" type="submit"><a
              href="../projectagri/PHP files/register.php">signup</a></button>
        </form-->
      </div>
    </div>
  </nav>
      <h1 id="heading"><span></span></h1>
      <!--img src="index.jpg" class="img-fluid"--> 
    </div>
    
    <div class="CSSgal">

      <!-- Don't wrap targets in parent -->
      <s id="s1"></s> 
      <s id="s2"></s>
      <s id="s3"></s>
    
      <div class="slider">
        <div style="background-image: url('../image1.jpg');">
          <h2></h2>
        </div>
        <div style="background-image:url('../image2.jpg');">
          <h2></h2>
        </div>
        <div style="background-image:url('../image3.jpg');">
          <h2></h2>
        </div>
       
      </div>
      
      <div class="prevNext">
        <div><a href="#s1"></a><a href="#s2"></a></div>
        <div><a href="#s2"></a><a href="#s3"></a></div>
        <div><a href="#s3"></a><a href="#s1"></a></div>
        
      </div>
    
      <div class="bullets">
        <a href="#s1"></a>
        <a href="#s2"></a>
        <a href="#s3"></a>
        
      </div>
    
    </div>

<br>
<br>
<br>

 <div class="row row-cols-1 row-cols-md-5 justify-content-center g-2 hover-zoom">
   <div class="col">
     <div class="card">
       <img src="../img/cart1.jpg" class="card-img-top"  alt="...">
       <div class="card-body">
         <h5 class="card-title">Organic Fertilizers</h5>
         <p class="card-text">The organic fertilizer production line is commonly used to process different fermented organic substance into bio-organic fertilizer. It adopts one-step molding technology. Animal manure and agricultural waste are recycled as the main raw materials, thus manure or dung waste is not only creating economic benefits for the enterprise, but also making a great contribution to environmental projects for mankind.</p>
       </div>
     </div>
   </div>
   <div class="col">
     <div class="card">
       <img src="../img/cart2.jpg" class="card-img-top" alt="...">
       <div class="card-body">
         <h5 class="card-title">Chemical Fertilizers</h5>
         <p class="card-text">Chemical fertilizers have been widely used to achieve maximum productivity in conventional agricultural systems. The continuous and excessive utilization of chemical fertilizers plays a major role, directly and/or indirectly,in changing environmental.Sustainable agriculture is advanced where the maximum output is gained at the minimal cost. Beneficial microbes have been successfully used in sustainable agriculture</p>
       </div>
     </div>
   </div>
   <div class="col">
     <div class="card">
       <img src="../card3.jpg" class="card-img-top" alt="...">
       <div class="card-body">
         <h5 class="card-title">Economics</h5>
         <p class="card-text">Agricultural economics is an applied field of economics concerned with the application of economic theory in optimizing the production and distribution of food and fiber products. Agricultural economics began as a branch of economics that specifically dealt with land usage.Economic development also requires a growing labour force. In an agricultural country most of the workers needed must come from the rural population.</p>
       </div>
     </div>
   </div>
   <div class="col">
     <div class="card">
       <img src="../card4.jpg" class="card-img-top" alt="...">
       <div class="card-body">
         <h5 class="card-title">Equipment</h5>
         <p class="card-text">Agricultural machinery relates to the mechanical structures and devices used in farming or other agriculture.From hand tools and power tools to tractors and the countless kinds of farm implements that they tow or operate.Equipment are used in both organic and nonorganic farming.Tractors do the majority of work on a modern farm. They are used to push implements—machines that till the ground,plant seed.</p>
       </div>
     </div>
   </div>
 </div>

 <br>
 <br>

 <div class="row row-cols-1 row-cols-md-5 g-4 justify-content-center">
  <div class="col">
    <div class="card">
      <img src="../img/cart5.jpg" class="card-img-top" alt="...">
    </div>
  </div>
  <div class="col">
    <div class="card">
      <img src="../img/cart6.jpg" class="card-img-top" alt="...">
    </div>
  </div>
  <div class="col">
    <div class="card">
      <img src="../img/cart7.jpg" class="card-img-top" alt="...">
    </div>
  </div>
  <div class="col">
    <div class="card">
      <img src="../img/cart8.jpg" class="card-img-top" alt="...">
    </div>
  </div>
</div>


<br>
<br>
<br>

 <footer id="footer" class="footer">

   <div class="container">
     <div class="row gy-3">
       <div class="col-lg-3 col-md-6 d-flex">
         <i class="bi bi-geo-alt icon"></i>
         <div>
           <h4>Address</h4>
           <p>
             Shrigonda 
             <br>Janglewadi 413726<br>
           </p>
         </div>

       </div>

       <div class="col-lg-3 col-md-6 footer-links d-flex">
         <i class="bi bi-telephone icon"></i>
         <div>
           <h4>Contact</h4>
           <p>
             <strong>Phone:</strong>+91 8805464445<br>
             <strong>Email:</strong> sourabhrode022@gmail.com<br>
           </p>
         </div>
       </div>

       <div class="col-lg-3 col-md-6 footer-links d-flex">
         <i class="bi bi-clock icon"></i>
         <div>
           <h4>Opening Hours</h4>
           <p>
             <strong>Mon-Sat: </strong>10AM - 6PM<br>
             <strong>Sunday:</strong>  Closed
           </p>
         </div>
       </div>

       <div class="col-lg-3 col-md-6 footer-links">
         <h4>Follow Us</h4>
         <div class="social-links d-flex">
           <a href="#" class="twitter"><i class="fa fa-twitter"></i></a>
           <a href="#" class="facebook"><i class="fa fa-facebook"></i></a>
           <a href="#" class="instagram"><i class="fa fa-instagram"></i></a>
           <a href="#" class="linkedin"><i class="fa fa-linkedin"></i></a>
         </div>
       </div>

     </div>
   </div>

   <div class="container">
     <div class="copyright">
       &copy; Copyright <strong><span>Agriculture</span></strong>. All Rights Reserved
     </div>
     <div class="credits">
       <!-- All the links in the footer should remain intact. -->
       <!-- You can delete the links only if you purchased the pro version. -->
       <!-- Licensing information: https://bootstrapmade.com/license/ -->
       <!-- Purchase the pro version with working PHP/AJAX contact form: https://bootstrapmade.com/yummy-bootstrap-restaurant-website-template/ -->
       Designed by <a href="https://bootstrapmade.com/">Sourabh</a>
     </div>
   </div>

 </footer>

 <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.2/dist/umd/popper.min.js" integrity="sha384-IQsoLXl5PILFhosVNubq5LC7Qb9DXgDA9i+tQ8Zj3iwWAwPtgFTxbJ8NT4GN1R8p" crossorigin="anonymous"></script>
   <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.min.js" integrity="sha384-cVKIPhGWiC2Al4u+LWgxfKTRIcfu0JTxR+EQDz/bgldoEyl4H0zUF0QKbrJ0EcQF" crossorigin="anonymous"></script>



	
<div class="content">
  	<!-- notification message -->
  	<?php if (isset($_SESSION['success'])) : ?>
      <div class="error success" >
      	<h3>
          <?php 
          	echo $_SESSION['success']; 
          	unset($_SESSION['success']);
          ?>
      	</h3>
      </div>
  	<?php endif ?>

    <!-- logged in user information -->
    <?php  if (isset($_SESSION['username'])) : ?>
    	<!--p>Welcome <strong><!?php echo $_SESSION['username']; ?></strong></p-->
    	<!--p> <a href="index.php?logout='1'" style="color: red;">logout</a> </p-->
    <?php endif ?>
</div>

</body>
</html>