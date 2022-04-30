sideBarButton = $('#side-bar-button');
scrollTopButton = $('#top-of-page-button');
sideBar = $('#side-bar');

if($(window).innerWidth() < 769){
sideBar.removeClass('side-bar');
sideBar.addClass('mobile-side-bar');}


let t = ($(window).innerHeight() - sideBar.innerHeight())/2;
let l = ($(window).innerWidth() - sideBar.innerWidth())/2;
sideBar.css({'top':t + 'px','left':l +'px'});

var sideButtonActive = false;

sideBarButton.on('click', function(){
    if(!sideButtonActive){
        $('body').css({'overflow-y' : ' hidden'})
        $('.text-box').css({'color': 'transparent',
            'text-shadow': '0 0 5px rgba(0,0,0,0.5)'})

        sideBarButton.text('close');
        sideBar.fadeIn();
        sideBar.css("display","absolute");
        sideButtonActive = true;
        return
    }

        sideBar.fadeOut();
        $('body').css({'overflow-y' : ' scroll'})
        $('.text-box').css({'color': 'black',
            'text-shadow': 'none'})


        sideBarButton.text('list');

        sideButtonActive = false;
        return
})


scrollTopButton.on('click', function(){
    window.scrollTo(0,0);
})

$('.text-box').on('click', function (){
    if(sideButtonActive){
        sideBar.fadeOut();
        $('body').css({'overflow-y' : ' scroll'})
        $('.text-box').css({'color': 'black',
            'text-shadow': 'none'})


        sideBarButton.text('list');

        sideButtonActive = false;
        
    }
})



$(window).resize(function(){
    if($(window).innerWidth() < 769){

        sideBar.removeClass('side-bar');
        sideBar.addClass('mobile-side-bar');
        $('#side-bar').css({'display': 'none'})

        if(sideButtonActive){
            sideBar.fadeOut();
            $('body').css({'overflow-y' : ' scroll'})
            $('.text-box').css({'color': 'black',
                'text-shadow': 'none'})
    
    
            sideBarButton.text('list');
    
            sideButtonActive = false;
        }

        

    }
    else{
        console.log('heee')
        sideBar.removeClass('mobile-side-bar');
        sideBar.addClass('side-bar');
        $('#side-bar').css({'display': 'block'});
        $('.text-box').css({'color': 'black',
        'text-shadow': 'none'});

       
    }
})


