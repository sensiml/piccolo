function getClassName(index) {
  return "image-carousel-slide-" + index;
}

function getDotName(index) {
  return "image-carousel-dot-" + index;
}

function plusSlides(index, n) {
  slideIndex[index] += n;
  showSlides(index);
}

function currentSlide(index, n) {
  slideIndex[index] = n;
  showSlides(className);
}

function showSlides(index) {
  className = getClassName(index);
  dotName = getDotName(index);
  var n = slideIndex[index];
  var i;
  var slides = document.getElementsByClassName(className);
  var dots = document.getElementsByClassName(dotName);

  if (n >= slides.length) {
    slideIndex[index] = 0;
  }
  if (n < 0) {
    slideIndex[index] = slides.length - 1;
  }
  for (i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";
  }
  for (i = 0; i < dots.length; i++) {
    dots[i].className = dots[i].className.replace(" image-carousel-active", "");
  }
  slides[slideIndex[index]].style.display = "block";
  dots[slideIndex[index]].className += " image-carousel-active";
}
