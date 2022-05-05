sideBarButton = $('#side-bar-button');
scrollTopButton = $('#top-of-page-button');
sideBar = $('#side-bar');

function isMobileWidth() {
    return $('.mobile-button').is(':visible');
}

if(isMobileWidth()/*$(window).innerWidth()< 769*/){
    
    sideBar.removeClass('side-bar');
    sideBar.addClass('mobile-side-bar');
    sideBar.addClass('hide');
    var t = ($(window).innerHeight() - sideBar.innerHeight())/2;
    var l = ($(window).innerWidth() - sideBar.innerWidth())/2;
    sideBar.css({'top':t + 'px','left':l +'px'});
}



var sideButtonActive = false;

sideBarButton.on('click', function(){
    
    if(!sideButtonActive){
        t = ($(window).innerHeight() - sideBar.innerHeight())/2;
        l = ($(window).innerWidth() - sideBar.innerWidth())/2;
        
        sideBar.css({'top':t  + 'px','left':l +'px'});
        // sideBar.css({'top':0 + 'px','left':0 +'px'});

        $('body').css({'overflow-y' : ' hidden'})
        $('.text-box').css({'color': 'transparent',
            'text-shadow': '0 0 5px rgba(0,0,0,0.5)'})

        
        //sideBar.css({'display': 'block'})
        sideBarButton.text('close');
        sideBar.removeClass('hide');
        sideBar.addClass('show');
        sideButtonActive = true;
        return
        
    }

    // sideBar.fadeOut();
    $('body').css({'overflow-y' : ' scroll'})
    $('.text-box').css({'color': 'black',
        'text-shadow': 'none'})

    sideBar.removeClass('show');
    sideBar.addClass('hide');
    


    sideBarButton.text('list');

    sideButtonActive = false;
    
})


scrollTopButton.on('click', function(){
    window.scrollTo(0,0);
})

$('.text-box').on('click', function (){
    if(sideButtonActive){
        sideBar.removeClass('show')
        sideBar.addClass('hide');

        $('body').css({'overflow-y' : ' scroll'})
        $('.text-box').css({'color': 'black',
            'text-shadow': 'none'})


        sideBarButton.text('list');

        sideButtonActive = false;
        
    }
})



$(window).resize(function(){
    if(isMobileWidth()/*$(window).innerWidth()< 769*/){

        t = ($(window).innerHeight() - sideBar.innerHeight())/2;
        l = ($(window).innerWidth() - sideBar.innerWidth())/2;
        sideBar.css({'top':t  + 'px','left':l +'px'});

        sideBar.removeClass('side-bar');
        sideBar.addClass('mobile-side-bar');
        sideBar.removeClass('show');
        sideBar.addClass('hide');


        if(sideButtonActive){
            //sideBar.fadeOut();
            $('body').css({'overflow-y' : ' scroll'})
            $('.text-box').css({'color': 'black',
                'text-shadow': 'none'})
    
    
            sideBarButton.text('list');
    
            sideButtonActive = false;
        }

        

    }
    else{
        
        sideBar.removeClass('mobile-side-bar');
        sideBar.removeClass('hide');

        sideBar.addClass('side-bar');
        sideBar.css({'top':'1rem','left':'0'});
        
        $('.text-box').css({'color': 'black',
        'text-shadow': 'none'});

       
    }
})


