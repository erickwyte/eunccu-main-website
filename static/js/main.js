(function ($, window, document) {
    'use strict';

    if (!$) return;

    $(window).on('load', function () {
        $('body').addClass('loaded');
    });

    $(function () {
        var header = $('#header');
        if (!header.length) return;

        $('.header-height').css('height', header.outerHeight() + 'px');
        $(window).on('scroll', function () {
            header.toggleClass('navbar-fixed-top', $(window).scrollTop() >= 100);
        });
    });

    // Lightweight hero slideshow: Nivo Slider's JavaScript is not shipped with this project.
    // A native opacity transition avoids the old plugin's heavy slice effects and keeps captions visible.
    (function initHeroSlider() {
        var slider = document.getElementById('main-slider');
        if (!slider) return;

        var slides = Array.prototype.slice.call(slider.querySelectorAll('img'));
        var captions = slides.map(function (slide) {
            return document.querySelector(slide.getAttribute('title'));
        });
        if (slides.length < 2 || captions.some(function (caption) { return !caption; })) return;

        var currentIndex = 0;
        var reducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        function showSlide(nextIndex) {
            slides[currentIndex].classList.remove('is-active');
            captions[currentIndex].classList.remove('is-active');
            currentIndex = nextIndex;
            slides[currentIndex].classList.add('is-active');
            captions[currentIndex].classList.add('is-active');
        }

        if (!reducedMotion) {
            window.setInterval(function () {
                showSlide((currentIndex + 1) % slides.length);
            }, 7000);
        }
    }());

    // Optional effects are enabled only when their plugin is actually loaded.
    if ($.fn.slicknav && $('#mainmenu').length) $('#mainmenu').slicknav({ prependTo: '.bottom-header', label: '', allowParentLinks: true });
    if ($.fn.counterUp) $('.counter').counterUp({ delay: 10, time: 1000 });
    if ($.fn.owlCarousel && $('#event-carousel').length) $('#event-carousel').owlCarousel({ loop: true, margin: 15, nav: true, dots: false, responsive: { 0: { items: 1 }, 768: { items: 2 } } });
    if ($.fn.imagesLoaded && $.fn.isotope && $('.gallery-items').length) $('.gallery-items').imagesLoaded(function () { $('.gallery-items').isotope({ itemSelector: '.single-item', layoutMode: 'masonry' }); });
    if (window.smoothScroll && typeof window.smoothScroll.init === 'function') window.smoothScroll.init({ offset: 60 });
    if ($.fn.venobox) $('.img-popup').venobox({ numeratio: true, infinigall: true });
    if (window.WOW) new window.WOW().init();

    $(window).on('scroll', function () {
        $('#scroll-to-top').toggle($(this).scrollTop() > 100);
    });
})(window.jQuery, window, document);
